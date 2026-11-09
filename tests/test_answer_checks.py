import pytest

from inference.answer_checks import bad_start, start_rejector, user_invites_greeting
from inference.engine import LocalModel
from config.settings import ModelSettings
from tests.conftest import FakeLlama


@pytest.mark.parametrize("prefix", [
    "Merhaba! Ben İlk Göz Ağrım uygulamasındaki",
    "Merhaba, ben senin yardımcı asistanınım.",
    "Ben 'İlk Göz Ağrım' uygulamasının yardımcı asistanıyım.",
    "  merhaba ben",
    # 3. büyük testte kaçanlar: 'asistan' 40. karakterden sonra / konuyla ilgili soruya kapsam reddi
    "Ben bir ebeveynlik ve bebek bakımı konusunda yardımcı asistanım. Kardeş kıskançlığı",
    "Bu benim uzmanlık alanım değil. Ben anne adaylarına",
    "Ben bir yapay zekâ asistanıyım ve tıbbi tavsiye veremem.",
    "Maalesef bu konuda yardımcı olamam.",
])
def test_greeting_starts_are_detected(prefix):
    assert bad_start(prefix) is True


@pytest.mark.parametrize("prefix", [
    "Bebekler genellikle 6 ila 10 aylık arasında",
    "Hayır, bebeği banyoda asla yalnız bırakmayın.",
    "Bebeğinizi güvenli uyutmak için en önemli kural",
    "Ben de bu konuda şunu söyleyebilirim: bebekler",  # 'asistan' yok
    "Bu benim de çok sık duyduğum bir soru. Bebekler",
    "Kan tahlilinizdeki hemoglobin değeriyle ilgili bir yorum yapamam.",  # şüpheli başlangıç değil
])
def test_normal_starts_are_accepted(prefix):
    assert bad_start(prefix) is False


def test_undecided_start_waits_for_sentence_end():
    assert bad_start("Ben bir ebeveynlik ve bebek bakımı konus") is None


def test_scope_refusal_is_accepted_for_medication_and_lab_questions():
    assert start_rejector("Emzirirken migren ilacı kullanabilir miyim?")("Maalesef bu konuda bilgi veremem.") is False
    assert start_rejector("Parmak gıdalar nelerdir?")("Bu benim uzmanlık alanım değil.") is True
    # Kendini tanıtma ilaç sorusunda da yeniden üretilir.
    assert start_rejector("Emzirirken migren ilacı kullanabilir miyim?")("Ben bir yapay zekâ asistanıyım.") is True
    # 'hap' yalnızca bütün kelime olarak: hapşırma sorusu ilaç sorusu değil
    assert start_rejector("Bebeğim çok hapşırıyor, neden?")("Maalesef bu konuda yardımcı olamam.") is True


@pytest.mark.parametrize("text, invites", [
    ("Merhaba", True),
    ("Teşekkürler, çok yardımcı oldun", True),
    ("Bu uygulama ne işe yarıyor?", True),
    ("Kendini iki cümleyle tanıt.", True),
    ("ok", True),
    ("Bebeği banyoda yalnız bırakabilir miyim, sadece bir dakika?", False),
    ("Göbek kordonu ne zaman düşer?", False),
    ("Oğlum 2 yaşında.", True),  # soru değil: "hangi konuda yardımcı olabilirim?" doğal bir cevap
    ("bebegim kac aylikken emekler", False),  # soru işareti yok ama soru kelimesi var
    ("Bebeğim gece çok sık uyanıyor.", True),
    ("Epidural nedir?", False),  # kısa ama gerçek bir soru
    ("?", False),
    ("Bebeğimin uykusu hakkında bilgi ver.", False),  # istek
    ("Çok yorgunum, annelik bana çok zor geliyor ve kimse yardım etmiyor", False),  # uzun anlatım
    ("Hamileyim.", True),
])
def test_user_invites_greeting(text, invites):
    assert user_invites_greeting(text) is invites
    assert (start_rejector(text) is None) is invites


class SequenceFake(FakeLlama):
    """Her çağrıda sıradaki cevabı veren sahte arka uç."""

    def __init__(self, answers):
        super().__init__()
        self.answers = [a.split(" ") for a in answers]

    def stream(self, messages, settings):
        self.calls.append((messages, settings))
        words = self.answers[min(len(self.calls) - 1, len(self.answers) - 1)]
        for i, w in enumerate(words):
            yield w if i == 0 else " " + w


def _model(fake, fake_gguf):
    model = LocalModel(lambda p, s: fake)
    model.load(fake_gguf, ModelSettings())
    return model


GREETING = "Merhaba, ben İlk Göz Ağrım uygulamasının yardımcı asistanıyım, size nasıl yardımcı olabilirim?"
GOOD = "Hayır, bebeği banyoda bir dakika bile olsa asla yalnız bırakmayın; boğulma saniyeler içinde olabilir."


def test_greeting_answer_is_regenerated(fake_gguf):
    fake = SequenceFake([GREETING, GOOD])
    model = _model(fake, fake_gguf)
    out = "".join(model.stream_chat([], ModelSettings(), reject_start=bad_start))
    assert out == GOOD
    assert model.last_retries == 1 and len(fake.calls) == 2


def test_retries_are_bounded_and_last_answer_is_shown(fake_gguf):
    fake = SequenceFake([GREETING])
    model = _model(fake, fake_gguf)
    out = "".join(model.stream_chat([], ModelSettings(), reject_start=bad_start, retries=2))
    assert out == GREETING  # sonsuz döngü yok; son deneme gösterilir
    assert len(fake.calls) == 3


def test_short_greeting_answer_is_also_checked(fake_gguf):
    fake = SequenceFake(["Merhaba!", GOOD])
    model = _model(fake, fake_gguf)
    assert "".join(model.stream_chat([], ModelSettings(), reject_start=bad_start)) == GOOD


def test_without_check_stream_is_unchanged(fake_gguf):
    fake = SequenceFake([GREETING])
    model = _model(fake, fake_gguf)
    assert "".join(model.stream_chat([], ModelSettings())) == GREETING
    assert len(fake.calls) == 1


SELF_INTRO = "Ben bir ebeveynlik ve bebek bakımı konusunda yardımcı asistanım. Kardeş kıskançlığı gibi konularda bilgi verebilirim."


def test_late_self_intro_is_regenerated(fake_gguf):
    fake = SequenceFake([SELF_INTRO, GOOD])
    model = _model(fake, fake_gguf)
    assert "".join(model.stream_chat([], ModelSettings(), reject_start=bad_start)) == GOOD
    assert model.last_retries == 1


def test_undecided_start_is_shown_after_max_prefix(fake_gguf):
    long_start = "Ben " + "çok " * 60 + "uzun bir cümleyle başlıyorum"
    fake = SequenceFake([long_start])
    model = _model(fake, fake_gguf)
    assert "".join(model.stream_chat([], ModelSettings(), reject_start=bad_start)) == long_start
    assert len(fake.calls) == 1


GREETING_PARAGRAPH = "Merhaba, ben bu uygulamanın yardımcı asistanıyım. Size destek olabilirim.\n\n" + GOOD


def test_greeting_paragraph_is_dropped_when_retries_run_out(fake_gguf):
    fake = SequenceFake([GREETING_PARAGRAPH])
    model = _model(fake, fake_gguf)
    assert "".join(model.stream_chat([], ModelSettings(), reject_start=bad_start, retries=2)) == GOOD
    assert len(fake.calls) == 3


def test_greeting_without_paragraph_break_is_still_shown(fake_gguf):
    fake = SequenceFake([GREETING])
    model = _model(fake, fake_gguf)
    assert "".join(model.stream_chat([], ModelSettings(), reject_start=bad_start, retries=1)) == GREETING


def test_bu_konuda_start():
    # 10.11.2026: "Bebeğin göbeğine bozuk para bağlamak göbek fıtığını önler mi?" sorusunda kaçtı
    assert bad_start("Bu konuda size yardımcı olamam. Benim uzmanlık alanım gebelik") is True
    assert bad_start("Bu konuda bilinmesi gereken en önemli şey: göbeğe para bağlanmaz.") is False
