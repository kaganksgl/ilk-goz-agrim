"""Lisansı doğrulanmış PDF'lerden inceleme kuyruğuna parça ekleme.

Yalnızca `registry.license_verified` koşulunu sağlayan kaynaklar kabul edilir. Metin olduğu gibi
(kelimesi kelimesine) alınır; yalnızca boşluklar düzeltilir ve resim içi yazılar atılır. Yazı tipi
kodlaması bozuk çıkan metin hiçbir koşulda alınmaz; tıbbi bilgi tabanına bozuk metin girmemelidir.

Parçalar `pilot/review_queue.jsonl` dosyasına yazılır; uygulama bu dosyayı kullanmaz. Uzman onayından
sonra kayıt güncellenir ve parçalar `pilot/chunks.jsonl` dosyasına taşınır.

Kullanım:
    python -m knowledge.ingest WHO-001 rehber.pdf --topic 8 --pages 26 32 61 172
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from knowledge.registry import (
    PILOT_DIR,
    REGISTRY_PATH,
    RegistryError,
    app_is_commercial,
    check_chunks,
    license_verified,
    load_chunks,
    load_registry,
)

# Bozuk yazı tipi eşlemesinde kelime ortasında büyük harf ya da ù, \, ¿ gibi karakterler çıkıyor
# (ör. "çocuğunuz" yerine "çRFuöunuz").
_GARBLED_WORD = re.compile(r"[ùû\\¿°µ¾]|[a-zçğıöşü][A-ZÇĞİÖŞÜ]")
_KEY_MESSAGE = re.compile(r"^\s*Kilit mesaj\s*\d*\s*$")
# Resim içi yazılar: büyük harfli, ünlemli kısa ifadeler (ör. "BAŞARDIN!").
_ILLUSTRATION = re.compile(r"\s*\b[A-ZÇĞİÖŞÜ]{2,}(?:\s+[A-ZÇĞİÖŞÜ]{2,})*!+")
_MIN_WORDS = 8


@dataclass(frozen=True)
class Passage:
    pdf_page: int
    printed_page: str | None
    text: str


def is_garbled(text: str) -> bool:
    return any(_GARBLED_WORD.search(word) for word in text.split())


def clean(text: str) -> str:
    text = _ILLUSTRATION.sub("", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\s*•\s*", "\n• ", text)
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())


def _printed_page(lines: list[str]) -> str | None:
    for line in lines[:2]:
        if re.fullmatch(r"\s*[0-9ivxlc]+\s*", line, re.I):
            return line.strip()
    return None


def extract_key_messages(pdf_path: Path, pages: list[int] | None = None) -> list[Passage]:
    """'Kilit mesaj' kutularını çıkarır; bozuk ya da çok kısa olanları atar."""
    from pypdf import PdfReader

    reader = PdfReader(str(pdf_path))
    wanted = pages or range(1, len(reader.pages) + 1)
    passages = []
    for number in wanted:
        lines = (reader.pages[number - 1].extract_text() or "").splitlines()
        for i, line in enumerate(lines):
            if not _KEY_MESSAGE.match(line):
                continue
            body = []
            for following in lines[i + 1 :]:
                if _KEY_MESSAGE.match(following) or not following.strip():
                    break
                body.append(following)
            text = clean(" ".join(body))
            if len(text.split()) < _MIN_WORDS or is_garbled(text):
                continue
            passages.append(Passage(number, _printed_page(lines), text))
    return passages


def to_chunks(source: dict, passages: list[Passage], topic: int) -> list[dict]:
    attribution = source.get("suggested_citation") or source["attribution_requirements"]
    chunks = []
    for n, passage in enumerate(passages, 1):
        location = f"s. {passage.printed_page} (PDF s. {passage.pdf_page})" if passage.printed_page else f"PDF s. {passage.pdf_page}"
        chunks.append(
            {
                "chunk_id": f"{source['source_id']}-p{passage.pdf_page}-{n}",
                "source_id": source["source_id"],
                "text": passage.text,
                "topic": topic,
                "category": "acil" if topic == 10 else "genel",
                "location": location,
                "license": source["license_name"],
                "attribution": attribution,
                "verbatim": True,
                # PDF'ten çıkarma noktalama işaretlerini düşürebilir; uzman özgün sayfayla karşılaştırınca True yapılır.
                "extraction_checked": False,
            }
        )
    return chunks


def add_to_review_queue(chunks: list[dict], pilot_dir: Path = PILOT_DIR, registry_path: Path = REGISTRY_PATH) -> int:
    records = load_registry(registry_path)
    queue_path = pilot_dir / "review_queue.jsonl"
    existing = load_chunks(queue_path)
    known = {c["chunk_id"] for c in existing}
    new = [c for c in chunks if c["chunk_id"] not in known]
    check_chunks(existing + new, records, app_is_commercial(registry_path), require_expert=False)
    with queue_path.open("a", encoding="utf-8") as fh:
        for chunk in new:
            fh.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    return len(new)


def main(argv: list[str] | None = None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("source_id")
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--topic", type=int, required=True)
    parser.add_argument("--pages", type=int, nargs="*", help="PDF sayfa numaraları (1'den başlar)")
    args = parser.parse_args(argv)

    records = {r["source_id"]: r for r in load_registry()}
    source = records.get(args.source_id)
    if source is None or not license_verified(source, app_is_commercial()):
        print(f"{args.source_id}: lisansı doğrulanmış bir kaynak değil; işlenmedi.")
        return 1
    passages = extract_key_messages(args.pdf, args.pages)
    try:
        added = add_to_review_queue(to_chunks(source, passages, args.topic))
    except RegistryError as exc:
        print(f"Reddedildi: {exc}")
        return 1
    for p in passages:
        print(f"PDF s.{p.pdf_page}: {p.text}\n")
    print(f"{added} yeni parça inceleme kuyruğuna eklendi.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
