import pytest

from inference.text_fixes import fix_text


@pytest.mark.parametrize("wrong, right", [
    ("doktorunuza veya ebeğinize danışın", "doktorunuza veya ebenize danışın"),
    ("doktorunuz veya ebeğiniz verebilir", "doktorunuz veya ebeniz verebilir"),
    ("doktorunuza veya ebeünüze danışın", "doktorunuza veya ebenize danışın"),
    ("doktorunuza veya ebebinize danışın", "doktorunuza veya ebenize danışın"),
    ("doktorunuza veya ebevinize danışın", "doktorunuza veya ebenize danışın"),
    ("doktorunuz veya ebehanız yorumlayabilir", "doktorunuz veya ebeniz yorumlayabilir"),
    ("doktorunuz veya ebeiniz verebilir", "doktorunuz veya ebeniz verebilir"),
    ("doktorunuza veya ebe'nize danışınız", "doktorunuza veya ebenize danışınız"),
    ("doktorunuz veya ebe'nizle konuşun", "doktorunuz veya ebenizle konuşun"),
    ("bir doktora veya ebe'ye danışmalısınız", "bir doktora veya ebeye danışmalısınız"),
    ("doktorunuza veya ebebe danışın", "doktorunuza veya ebeye danışın"),
    ("doktorunuza veya ebeveyninize danışın", "doktorunuza veya ebenize danışın"),
    ("doktorunuza veya ebeveyinize danışın", "doktorunuza veya ebenize danışın"),
    ("Ebeğinize sorun.", "Ebenize sorun."),
])
def test_wrong_forms_are_fixed(wrong, right):
    assert fix_text(wrong) == right


@pytest.mark.parametrize("text", [
    "doktorunuza veya ebenize danışın",
    "doktorunuz veya ebeniz",
    "doktorunuza veya ebelerinize danışınız",
    "ebeveynlik zor bir süreçtir",
    "Ebeveyninizin desteği önemlidir.",  # gerçekten ebeveyn kastediliyor
    "ebeveynle birlikte",
    "ebeye danışın",
    "Gebelikte beslenme",  # 'ebe' kelime içinde
])
def test_correct_text_is_untouched(text):
    assert fix_text(text) == text


def test_duplicate_trailing_referral_is_removed():
    text = "Lütfen bu konuda mutlaka doktorunuza danışın.  \n\nDoktorunuza veya ebenize danışın."
    assert fix_text(text) == "Lütfen bu konuda mutlaka doktorunuza danışın."


def test_lone_trailing_referral_becomes_a_sentence():
    text = "Ek sıvı genellikle gerekmez.  \n\ndoktorunuza veya ebenize danışın"
    assert fix_text(text) == "Ek sıvı genellikle gerekmez.\n\nDoktorunuza veya ebenize danışın."


def test_referral_inside_text_is_untouched():
    text = "Endişeniz varsa doktorunuza veya ebenize danışın. Ayrıca bol su için."
    assert fix_text(text) == text
