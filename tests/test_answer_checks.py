import pytest

from inference.answer_checks import greeting_rejector, starts_with_greeting, user_invites_greeting
from inference.engine import LocalModel
from config.settings import ModelSettings
from tests.conftest import FakeLlama


@pytest.mark.parametrize("prefix", [
    "Merhaba! Ben İlk Göz Ağrım uygulamasındaki",
    "Merhaba, ben senin yardımcı asistanınım.",
    "Ben 'İlk Göz Ağrım' uygulamasının yardımcı asistanıyım.",
    "  merhaba ben",
])
def test_greeting_starts_are_detected(prefix):
    assert starts_with_greeting(prefix)


@pytest.mark.parametrize("prefix", [
    "Bebekler genellikle 6 ila 10 aylık arasında",
    "Hayır, bebeği banyoda asla yalnız bırakmayın.",
    "Bebeğinizi güvenli uyutmak için en önemli kural",
    "Ben de bu konuda şunu söyleyebilirim: bebekler",  # 'asistan' yok
])
def test_normal_starts_are_accepted(prefix):
    assert not starts_with_greeting(prefix)


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
    assert (greeting_rejector(text) is None) is invites


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
    out = "".join(model.stream_chat([], ModelSettings(), reject_start=starts_with_greeting))
    assert out == GOOD
    assert model.last_retries == 1 and len(fake.calls) == 2


def test_retries_are_bounded_and_last_answer_is_shown(fake_gguf):
    fake = SequenceFake([GREETING])
    model = _model(fake, fake_gguf)
    out = "".join(model.stream_chat([], ModelSettings(), reject_start=starts_with_greeting, retries=2))
    assert out == GREETING  # sonsuz döngü yok; son deneme gösterilir
    assert len(fake.calls) == 3


def test_short_greeting_answer_is_also_checked(fake_gguf):
    fake = SequenceFake(["Merhaba!", GOOD])
    model = _model(fake, fake_gguf)
    assert "".join(model.stream_chat([], ModelSettings(), reject_start=starts_with_greeting)) == GOOD


def test_without_check_stream_is_unchanged(fake_gguf):
    fake = SequenceFake([GREETING])
    model = _model(fake, fake_gguf)
    assert "".join(model.stream_chat([], ModelSettings())) == GREETING
    assert len(fake.calls) == 1
