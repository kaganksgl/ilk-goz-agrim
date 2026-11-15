import pytest

from config.settings import ModelSettings
from inference.engine import LocalModel
from inference.topic_guard import OFF_TOPIC, RELEVANT, TopicGuard, build_check_messages
from tests.conftest import FakeLlama


def test_check_messages_contain_last_message_and_short_context():
    history = [
        {"role": "user", "content": "Bebeğim 8 aylık."},
        {"role": "assistant", "content": "x" * 1000},
        {"role": "user", "content": "Peki ya uykusu?"},
    ]
    system, user = build_check_messages(history)
    assert system["role"] == "system" and "ILGISIZ" in system["content"]
    assert user["content"].rstrip().endswith("Sınıf (ILGILI veya ILGISIZ):")
    assert "Son mesaj: Peki ya uykusu?" in user["content"]
    assert "Kullanıcı: Bebeğim 8 aylık." in user["content"]
    assert "x" * 301 not in user["content"]  # uzun bağlam kırpılır


def test_check_messages_without_context():
    _, user = build_check_messages([{"role": "user", "content": "Merhaba"}])
    assert "Önceki konuşma" not in user["content"]


def test_last_message_must_be_user():
    with pytest.raises(ValueError):
        build_check_messages([{"role": "assistant", "content": "x"}])


@pytest.mark.parametrize("label, expected", [(RELEVANT, True), (OFF_TOPIC, False)])
def test_guard_maps_label(fake_gguf, label, expected):
    fake = FakeLlama(topic=label)
    model = LocalModel(lambda p, s: fake)
    model.load(fake_gguf, ModelSettings())
    assert TopicGuard(model).is_relevant([{"role": "user", "content": "soru"}]) is expected
    assert fake.choose_calls[0][1] == (RELEVANT, OFF_TOPIC)


def _guard(fake_gguf, label=OFF_TOPIC, **kwargs):
    fake = FakeLlama(topic=label)
    model = LocalModel(lambda p, s: fake)
    model.load(fake_gguf, ModelSettings())
    return TopicGuard(model, **kwargs), fake


@pytest.mark.parametrize("history", [
    ["Nişan gelmesi ne demek?"],
    ["Konak nedir?"],
    ["Hamileyim, 34 haftalığım.", "Uçakla seyahat edebilir miyim?"],  # kartın bağlam koşulu önceki mesajda
])
def test_question_matching_a_card_is_relevant_without_asking_the_model(fake_gguf, history):
    guard, fake = _guard(fake_gguf)
    assert guard.is_relevant([{"role": "user", "content": text} for text in history]) is True
    assert fake.choose_calls == []


@pytest.mark.parametrize("history", [
    ["Python'da bir listeyi nasıl sıralarım?"],
    ["Uçakla seyahat ederken hangi koltuk daha rahat?"],  # gebelik bağlamı yok: kart eşleşmez
    # Önceki soru bir kartla eşleşse de yeni mesajın kendisi eşleşmiyorsa model karar verir.
    ["Bebeğime ne zaman bal verebilirim?", "Şimdi bana bir JavaScript fonksiyonu yaz."],
])
def test_message_without_its_own_card_is_still_classified_by_the_model(fake_gguf, history):
    guard, fake = _guard(fake_gguf)
    assert guard.is_relevant([{"role": "user", "content": text} for text in history]) is False
    assert len(fake.choose_calls) == 1


def test_card_shortcut_can_be_disabled(fake_gguf):
    guard, fake = _guard(fake_gguf, trust_cards=False)
    assert guard.is_relevant([{"role": "user", "content": "Konak nedir?"}]) is False
    assert len(fake.choose_calls) == 1
