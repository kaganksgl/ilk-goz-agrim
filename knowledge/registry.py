"""Kaynak kaydı ve bilgi tabanına giriş denetimi.

İki aşama vardır:
1. **İnceleme kuyruğu** (`pilot/review_queue.jsonl`): lisansı kaynağın kendi beyanıyla doğrulanmış
   ama henüz uzman incelemesinden geçmemiş parçalar. Uygulama bunları **kullanmaz**.
2. **Bilgi tabanı** (`pilot/chunks.jsonl`): lisansı doğrulanmış **ve** uzmanca onaylanmış parçalar.

Bu kurallar yalnızca belgelere değil koda da yazılıdır: `check_chunks`, koşulları sağlamayan bir
kaynağa ait tek bir parça bile görürse hata verir.

Kullanım:
    python -m knowledge.registry            # kaydı denetle ve özetle
    python -m knowledge.registry --build    # kuyruğu ve bilgi tabanını denetleyip manifesti yaz
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REGISTRY_PATH = ROOT / "sources" / "registry.json"
PILOT_DIR = ROOT / "pilot"

REQUIRED_FIELDS = (
    "source_id",
    "title",
    "author_or_organization",
    "original_url",
    "publication_date",
    "last_verified_date",
    "language",
    "license_name",
    "license_url",
    "commercial_use_allowed",
    "adaptation_allowed",
    "attribution_requirements",
    "medical_topic",
    "expert_review_status",
    "inclusion_status",
    "notes",
    # Proje ekleri
    "noncommercial_use_allowed",
    "share_alike",
    "translation_required",
    "license_evidence",
)

INCLUDED = "dahil"
AWAITING_EXPERT = "uzman_incelemesi_bekliyor"
INCLUSION_STATUSES = {
    INCLUDED,
    AWAITING_EXPERT,
    "izin_bekliyor",
    "lisans_doğrulanmadı",
    "kapsam_dışı",
    "erişilemiyor",
    "önerilmiyor",
}
USE_VALUES = {"evet", "hayır", "izin_gerekli", "doğrulanmadı"}
REVIEW_STATUSES = {"incelenmedi", "inceleniyor", "onaylandı", "reddedildi"}
TOPICS = set(range(1, 11))
EMERGENCY_TOPIC = 10
CHUNK_CATEGORIES = {"genel", "acil"}
CHUNK_FIELDS = ("chunk_id", "source_id", "text", "topic", "category", "location", "license", "attribution")

# Kaynağın kendi beyanıyla (license_evidence) doğrulanmadan hiçbir kayda yazılamayacak ifadeler.
FORBIDDEN_CLAIMS = ("telifsiz", "telif sorunu yok", "telif sorunu bulunmuyor", "copyright free", "public domain", "kamu malı")


class RegistryError(ValueError):
    pass


def load_document(path: Path = REGISTRY_PATH) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_registry(path: Path = REGISTRY_PATH) -> list[dict]:
    return list(load_document(path)["sources"])


def app_is_commercial(path: Path = REGISTRY_PATH) -> bool:
    """Proje kararı; bilinmiyorsa en kısıtlayıcı varsayım (ticari) kullanılır."""
    return bool(load_document(path).get("project_policy", {}).get("app_commercial", True))


def license_verified(record: dict, app_commercial: bool) -> bool:
    """Lisans, kaynağın kendi beyanıyla doğrulanmış ve bu uygulamanın kullanımına izin veriyor mu?"""
    use_ok = record.get("commercial_use_allowed") == "evet" or (
        not app_commercial and record.get("noncommercial_use_allowed") == "evet"
    )
    return (
        bool(record.get("license_name"))
        and bool(record.get("license_url"))
        and bool(record.get("license_evidence"))
        and use_ok
        and record.get("adaptation_allowed") == "evet"
        and record.get("attribution_requirements") not in (None, "doğrulanmadı")
    )


def is_approved(record: dict, app_commercial: bool) -> bool:
    """Bir kaynağın uygulamanın bilgi tabanına girebilmesi için gereken koşulların tamamı."""
    return (
        record.get("inclusion_status") == INCLUDED
        and record.get("expert_review_status") == "onaylandı"
        and license_verified(record, app_commercial)
    )


def validate(records: list[dict], app_commercial: bool) -> list[str]:
    problems: list[str] = []
    seen: set[str] = set()
    for record in records:
        sid = record.get("source_id", "<kimliksiz>")
        missing = [f for f in REQUIRED_FIELDS if f not in record]
        if missing:
            problems.append(f"{sid}: eksik alanlar {missing}")
            continue
        if sid in seen:
            problems.append(f"{sid}: yinelenen kimlik")
        seen.add(sid)
        if record["inclusion_status"] not in INCLUSION_STATUSES:
            problems.append(f"{sid}: geçersiz inclusion_status {record['inclusion_status']!r}")
        for field in ("commercial_use_allowed", "noncommercial_use_allowed", "adaptation_allowed"):
            if record[field] not in USE_VALUES:
                problems.append(f"{sid}: geçersiz {field} {record[field]!r}")
        if record["expert_review_status"] not in REVIEW_STATUSES:
            problems.append(f"{sid}: geçersiz expert_review_status {record['expert_review_status']!r}")
        if not set(record["medical_topic"]) <= TOPICS:
            problems.append(f"{sid}: geçersiz konu kodu {record['medical_topic']}")
        if record["inclusion_status"] == INCLUDED and not is_approved(record, app_commercial):
            problems.append(f"{sid}: 'dahil' işaretli ama lisans/uzman onayı koşulları eksik")
        if record["inclusion_status"] == AWAITING_EXPERT and not license_verified(record, app_commercial):
            problems.append(f"{sid}: '{AWAITING_EXPERT}' işaretli ama lisansı doğrulanmamış")
        if record["license_name"] is None and (
            record["commercial_use_allowed"] != "doğrulanmadı" or record["noncommercial_use_allowed"] != "doğrulanmadı"
        ):
            problems.append(f"{sid}: lisans bilinmiyorken kullanım koşulları tahmin edilmiş")
        if not record["license_evidence"]:
            text = json.dumps(record, ensure_ascii=False).lower()
            for claim in FORBIDDEN_CLAIMS:
                if claim in text:
                    problems.append(f"{sid}: kaynak beyanı olmadan iddia içeriyor: {claim!r}")
    return problems


def check_chunks(chunks: list[dict], records: list[dict], app_commercial: bool, require_expert: bool) -> None:
    """Her parçanın uygun bir kaynaktan, eksiksiz atıf ve lisans bilgisiyle geldiğini doğrular.

    `require_expert=True` bilgi tabanı içindir; `False` yalnızca inceleme kuyruğu içindir.
    """
    by_id = {r["source_id"]: r for r in records}
    seen: set[str] = set()
    for chunk in chunks:
        cid = chunk.get("chunk_id", "<kimliksiz>")
        for field in CHUNK_FIELDS:
            if not chunk.get(field) and chunk.get(field) != 0:
                raise RegistryError(f"{cid}: eksik alan {field!r}")
        if cid in seen:
            raise RegistryError(f"{cid}: yinelenen parça kimliği")
        seen.add(cid)
        source = by_id.get(chunk["source_id"])
        if source is None:
            raise RegistryError(f"{cid}: kayıtta olmayan kaynak {chunk['source_id']!r}")
        allowed = is_approved(source, app_commercial) if require_expert else license_verified(source, app_commercial)
        if not allowed:
            stage = "bilgi tabanına" if require_expert else "inceleme kuyruğuna"
            raise RegistryError(
                f"{cid}: {chunk['source_id']} uygun değil (durum: {source['inclusion_status']}); {stage} eklenemez"
            )
        if chunk["license"] != source["license_name"]:
            raise RegistryError(f"{cid}: parçanın lisansı kaynağın lisansıyla aynı değil")
        if chunk["topic"] not in source["medical_topic"]:
            raise RegistryError(f"{cid}: konu {chunk['topic']} kaynağın konuları arasında değil")
        if chunk["category"] not in CHUNK_CATEGORIES:
            raise RegistryError(f"{cid}: geçersiz kategori {chunk['category']!r}")
        # Acil durum bilgisi ayrı tutulur ve yalnızca 10 numaralı konuya ait olabilir.
        if (chunk["category"] == "acil") != (chunk["topic"] == EMERGENCY_TOPIC):
            raise RegistryError(f"{cid}: acil kategorisi yalnızca {EMERGENCY_TOPIC} numaralı konuyla kullanılabilir")


def load_chunks(path: Path) -> list[dict]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def build_pilot(pilot_dir: Path = PILOT_DIR, registry_path: Path = REGISTRY_PATH) -> dict:
    records = load_registry(registry_path)
    commercial = app_is_commercial(registry_path)
    problems = validate(records, commercial)
    if problems:
        raise RegistryError("Kaynak kaydı geçersiz:\n" + "\n".join(problems))
    knowledge = load_chunks(pilot_dir / "chunks.jsonl")
    queue = load_chunks(pilot_dir / "review_queue.jsonl")
    check_chunks(knowledge, records, commercial, require_expert=True)
    check_chunks(queue, records, commercial, require_expert=False)
    by_id = {r["source_id"]: r for r in records}
    used = sorted({c["source_id"] for c in knowledge + queue})
    manifest = {
        "built": date.today().isoformat(),
        "app_commercial": commercial,
        "approved_sources": sorted(r["source_id"] for r in records if is_approved(r, commercial)),
        "license_verified_sources": sorted(r["source_id"] for r in records if license_verified(r, commercial)),
        "chunk_count": len(knowledge),
        "review_queue_count": len(queue),
        "emergency_chunk_count": sum(c["category"] == "acil" for c in knowledge),
        # Uygulama, bilgi tabanındaki her kaynak için bu atıf ve lisans bildirimlerini göstermek zorundadır.
        "notices": {sid: by_id[sid]["attribution_requirements"] for sid in used},
        "share_alike_sources": [sid for sid in used if by_id[sid]["share_alike"]],
    }
    (pilot_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main(argv: list[str] | None = None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true", help="kuyruğu ve bilgi tabanını denetle, manifesti yaz")
    args = parser.parse_args(argv)
    records = load_registry()
    commercial = app_is_commercial()
    problems = validate(records, commercial)
    print(f"uygulama ticari mi: {commercial}")
    print(f"{len(records)} kaynak: {dict(Counter(r['inclusion_status'] for r in records))}")
    print(f"lisansı doğrulanmış: {sum(license_verified(r, commercial) for r in records)}, "
          f"bilgi tabanına onaylı: {sum(is_approved(r, commercial) for r in records)}")
    if problems:
        print("SORUNLAR:\n" + "\n".join(problems))
        return 1
    if args.build:
        print(json.dumps(build_pilot(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
