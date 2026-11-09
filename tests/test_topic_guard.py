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
