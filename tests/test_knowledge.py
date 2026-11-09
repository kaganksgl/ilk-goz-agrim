import json

import pytest

from knowledge.ingest import Passage, clean, is_garbled, to_chunks
from knowledge.registry import (
    FORBIDDEN_CLAIMS,
    REQUIRED_FIELDS,
    RegistryError,
    app_is_commercial,
    build_pilot,
    check_chunks,
    is_approved,
    license_verified,
    load_chunks,
    load_registry,
    validate,
)

RECORDS = load_registry()
BY_ID = {r["source_id"]: r for r in RECORDS}
COMMERCIAL = app_is_commercial()


def open_record(**overrides):
    """CC BY-NC-SA gibi açık, ticari olmayan bir lisansa sahip, uzmanca onaylanmış örnek kaynak."""
    record = {
        "source_id": "TEST-001",
        "title": "Test",
        "author_or_organization": "Test kurumu",
        "original_url": "https://example.org/x.pdf",
        "publication_date": "2026",
        "last_verified_date": "2026-10-27",
        "language": "tr",
        "license_name": "CC BY-NC-SA 3.0 IGO",
        "license_url": "https://creativecommons.org/licenses/by-nc-sa/3.0/igo/",
        "commercial_use_allowed": "hayır",
        "noncommercial_use_allowed": "evet",
        "adaptation_allowed": "evet",
        "attribution_requirements": "Önerilen atıf",
        "medical_topic": [5, 10],
        "expert_review_status": "onaylandı",
        "inclusion_status": "dahil",
        "notes": "",
        "share_alike": True,
        "translation_required": False,
        "license_evidence": "künye alıntısı",
    }
    record.update(overrides)
    return record


def chunk(**overrides):
    item = {
        "chunk_id": "c1",
        "source_id": "TEST-001",
        "text": "…",
        "topic": 5,
        "category": "genel",
        "location": "s. 3",
        "license": "CC BY-NC-SA 3.0 IGO",
        "attribution": "Önerilen atıf",
    }
    item.update(overrides)
    return item


# ---- gerçek kayıt -------------------------------------------------------------
def test_project_is_non_commercial():
    assert COMMERCIAL is False


def test_real_registry_is_valid_and_complete():
    assert validate(RECORDS, COMMERCIAL) == []
    assert len(RECORDS) == 62
    for record in RECORDS:
        assert all(field in record for field in REQUIRED_FIELDS)


def test_nothing_is_approved_without_expert_review():
    assert [r["source_id"] for r in RECORDS if is_approved(r, COMMERCIAL)] == []
    assert all(r["expert_review_status"] == "incelenmedi" for r in RECORDS)


def test_license_verified_sources_are_exactly_the_open_ones():
    verified = sorted(r["source_id"] for r in RECORDS if license_verified(r, COMMERCIAL))
    assert verified == ["NIH-001", "WHO-001", "WHO-002", "WHO-003", "WHO-004", "WHO-005", "WHO-006"]
    for sid in verified:
        assert BY_ID[sid]["inclusion_status"] == "uzman_incelemesi_bekliyor"


def test_nc_licence_would_not_be_enough_for_a_commercial_app():
    assert license_verified(BY_ID["WHO-001"], app_commercial=False)
    assert not license_verified(BY_ID["WHO-001"], app_commercial=True)
    assert license_verified(BY_ID["NIH-001"], app_commercial=True)


def test_rights_reserved_documents_still_need_permission_for_free_app():
    for sid in ("TOK-014", "TOK-016", "GOP-010", "TOK-007", "UNI-002"):
        record = BY_ID[sid]
        assert record["inclusion_status"] == "izin_bekliyor"
        assert record["noncommercial_use_allowed"] == "izin_gerekli"
        assert not license_verified(record, app_commercial=False)


def test_unknown_license_is_never_guessed():
    for record in RECORDS:
        if record["license_name"] is None:
            assert record["commercial_use_allowed"] == "doğrulanmadı"
            assert record["noncommercial_use_allowed"] == "doğrulanmadı"
            assert record["adaptation_allowed"] == "doğrulanmadı"
            assert record["license_evidence"] is None


def test_copyright_free_claims_only_with_source_evidence():
    for record in RECORDS:
        text = json.dumps(record, ensure_ascii=False).lower()
        if any(c in text for c in FORBIDDEN_CLAIMS):
            assert record["license_evidence"], record["source_id"]


def test_translated_who_sources_carry_disclaimer_requirement():
    for record in RECORDS:
        if record["source_id"].startswith("WHO") and record["translation_required"]:
            assert "Bu tercüme, Dünya Sağlık Örgütü" in record["attribution_requirements"]


# ---- doğrulama kuralları ------------------------------------------------------
def test_included_without_expert_approval_is_rejected():
    problems = validate([open_record(expert_review_status="incelenmedi")], False)
    assert any("koşulları eksik" in p for p in problems)


def test_awaiting_expert_requires_verified_licence():
    problems = validate([open_record(inclusion_status="uzman_incelemesi_bekliyor", license_evidence=None)], False)
    assert any("lisansı doğrulanmamış" in p for p in problems)


def test_guessed_use_is_rejected():
    problems = validate(
        [open_record(license_name=None, inclusion_status="lisans_doğrulanmadı", noncommercial_use_allowed="evet")], False
    )
    assert any("tahmin" in p for p in problems)


def test_copyright_free_claim_without_evidence_is_rejected():
    problems = validate([open_record(notes="Telif sorunu yok.", license_evidence=None, inclusion_status="lisans_doğrulanmadı")], False)
    assert any("kaynak beyanı olmadan" in p for p in problems)


# ---- parça denetimi -----------------------------------------------------------
def test_chunk_from_approved_source_is_accepted():
    check_chunks([chunk(), chunk(chunk_id="c2", topic=10, category="acil")], [open_record()], False, require_expert=True)


def test_review_queue_accepts_licence_verified_but_knowledge_base_does_not():
    record = open_record(inclusion_status="uzman_incelemesi_bekliyor", expert_review_status="incelenmedi")
    check_chunks([chunk()], [record], False, require_expert=False)
    with pytest.raises(RegistryError, match="bilgi tabanına"):
        check_chunks([chunk()], [record], False, require_expert=True)


@pytest.mark.parametrize("status", ["izin_bekliyor", "lisans_doğrulanmadı", "kapsam_dışı"])
def test_unlicensed_sources_cannot_even_enter_review_queue(status):
    record = open_record(inclusion_status=status, license_evidence=None, noncommercial_use_allowed="izin_gerekli")
    with pytest.raises(RegistryError, match="inceleme kuyruğuna"):
        check_chunks([chunk()], [record], False, require_expert=False)


def test_real_rights_reserved_source_is_rejected():
    with pytest.raises(RegistryError):
        check_chunks([chunk(source_id="TOK-014", topic=2, license=None)], RECORDS, False, require_expert=False)


def test_chunk_must_carry_licence_and_attribution():
    with pytest.raises(RegistryError, match="attribution"):
        check_chunks([chunk(attribution="")], [open_record()], False, require_expert=True)
    with pytest.raises(RegistryError, match="lisansı"):
        check_chunks([chunk(license="CC BY 4.0")], [open_record()], False, require_expert=True)


def test_emergency_content_is_kept_separate():
    with pytest.raises(RegistryError, match="acil"):
        check_chunks([chunk(topic=10, category="genel")], [open_record()], False, require_expert=True)
    with pytest.raises(RegistryError, match="acil"):
        check_chunks([chunk(topic=5, category="acil")], [open_record()], False, require_expert=True)


def test_build_pilot_refuses_unapproved_knowledge(tmp_path):
    registry = tmp_path / "registry.json"
    registry.write_text(
        json.dumps({"project_policy": {"app_commercial": False}, "sources": [open_record(inclusion_status="uzman_incelemesi_bekliyor", expert_review_status="incelenmedi")]}),
        encoding="utf-8",
    )
    (tmp_path / "chunks.jsonl").write_text(json.dumps(chunk()) + "\n", encoding="utf-8")
    with pytest.raises(RegistryError):
        build_pilot(tmp_path, registry)
    assert not (tmp_path / "manifest.json").exists()


def test_missing_policy_defaults_to_commercial(tmp_path):
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps({"sources": []}), encoding="utf-8")
    assert app_is_commercial(registry) is True


# ---- gerçek pilot -------------------------------------------------------------
def test_real_pilot_state():
    from knowledge.registry import PILOT_DIR

    queue = load_chunks(PILOT_DIR / "review_queue.jsonl")
    assert load_chunks(PILOT_DIR / "chunks.jsonl") == []  # uzman onayı yok, bilgi tabanı boş
    assert len(queue) == 4 and {c["source_id"] for c in queue} == {"WHO-001"}
    check_chunks(queue, RECORDS, COMMERCIAL, require_expert=False)
    for c in queue:
        assert not is_garbled(c["text"])
        assert c["extraction_checked"] is False
        assert "Lisans: CC BY-NC-SA 3.0 IGO" in c["attribution"]


# ---- metin çıkarma ------------------------------------------------------------
def test_garbled_text_is_detected():
    assert is_garbled("çRFuöunuzla Rlumlu ve nazik ses tRnu\\la kRnuùun")
    assert not is_garbled("Çocuklar en iyi sakin ve huzurluyken öğrenirler. İLK göz ağrım")


def test_clean_removes_illustration_text_and_splits_bullets():
    assert clean("• Bir  cümle. • İkinci cümle BAŞARDIN!") == "• Bir cümle.\n• İkinci cümle"


def test_to_chunks_uses_citation_and_marks_emergency():
    source = open_record(suggested_citation="Atıf metni")
    chunks = to_chunks(source, [Passage(5, "3", "metin"), Passage(6, None, "acil metin")], topic=10)
    assert chunks[0]["location"] == "s. 3 (PDF s. 5)" and chunks[1]["location"] == "PDF s. 6"
    assert all(c["category"] == "acil" and c["attribution"] == "Atıf metni" for c in chunks)
