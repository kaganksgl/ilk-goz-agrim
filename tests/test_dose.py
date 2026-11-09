import pytest

from inference.text_fixes import clean_answer
from safety.dose import REDACTION, is_dose_request, redact_doses


@pytest.mark.parametrize("text", [
    "Hamileyken baş ağrım için kaç miligram parasetamol alabilirim?",
    "3 aylık bebeğime kaç damla D vitamini vermeliyim?",
    "Bebeğime ateş düşürücü şurup kaç ml verilir?",
    "Gebelikte demir hapı dozu ne olmalı?",
    "Gebelikte günde kaç mikrogram folik asit almalıyım?",
    "Doğum sonrası ağrı kesici olarak ne kadar ibuprofen alabilirim?",
    "Bebeğime probiyotik damlasından kaç damla vereyim?",
    "Hamileyken hangi bitki çaylarını ne kadar içebilirim?",
    "bebegime kac ml surup vereyim",
])
def test_dose_questions_are_detected(text):
    assert is_dose_request(text)


@pytest.mark.parametrize("text", [
    "Bebeğim kaç ml mama içmeli?",  # beslenme miktarı
    "Bebek günde kaç kez emzirilmeli?",
    "Gebelikte folik asit neden önemlidir?",  # miktar sorulmuyor
    "Bebekler kaç aylıkken emekler?",
    "Emzirirken antibiyotik kullanabilir miyim?",  # doz değil; modele gider, çıktı maskelenir
    "Bebeğe bal ne zaman verilebilir?",
])
def test_other_questions_are_not_dose_requests(text):
    assert not is_dose_request(text)


def test_amounts_in_drug_sentences_are_redacted():
    text = "Gebelikte genellikle günde 400 mikrogram folik asit önerilir. Bebek her öğünde 90 ml mama içebilir."
    out = redact_doses(text)
    assert "400" not in out and REDACTION in out
    assert "90 ml mama" in out  # ilaç cümlesi değil


@pytest.mark.parametrize("text", [
    "D vitamini damlası 3-4 damla verilir.",
    "Parasetamol 10 ile 15 mg verilir.",
    "Demir takviyesi 1 tablet alınabilir.",
])
def test_various_dose_formats_are_redacted(text):
    assert REDACTION in redact_doses(text)


def test_normal_numbers_are_kept():
    text = "Lohusalık 40 gün sürer. Bebek günde 8-12 kez emzirilir. 6 ayda ek gıdaya başlanır."
    assert redact_doses(text) == text


def test_clean_answer_combines_fixes():
    out = clean_answer("Günde 400 mikrogram folik asit alın. Doktorunuza veya ebeğinize danışın.")
    assert "400" not in out and "ebenize" in out
