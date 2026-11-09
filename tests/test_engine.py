import threading

import pytest

from config.settings import ModelSettings
from inference.engine import LocalModel, build_messages, validate_model_file
from inference.errors import (
    GenerationError,
    InvalidModelFileError,
    ModelLoadError,
    ModelNotConfiguredError,
    ModelNotFoundError,
    ModelNotLoadedError,
)
from tests.conftest import FakeLlama

S = ModelSettings()


def test_validate_none_and_missing(tmp_path):
    with pytest.raises(ModelNotConfiguredError):
        validate_model_file(None)
    with pytest.raises(ModelNotFoundError):
        validate_model_file(tmp_path / "yok.gguf")


def test_validate_rejects_wrong_extension_and_magic(tmp_path):
    txt = tmp_path / "model.bin"
    txt.write_bytes(b"GGUF")
    with pytest.raises(InvalidModelFileError):
        validate_model_file(txt)
    bad = tmp_path / "bad.gguf"
    bad.write_bytes(b"NOPE1234")
    with pytest.raises(InvalidModelFileError):
        validate_model_file(bad)


def test_user_messages_are_turkish_and_nonempty():
    for cls in (ModelNotConfiguredError, ModelNotFoundError, InvalidModelFileError, ModelLoadError):
        assert cls().user_message.strip()


def test_backend_exception_becomes_load_error(fake_gguf):
    def boom(_path, _settings):
        raise ValueError("Failed to load model from file")

    model = LocalModel(boom)
    with pytest.raises(ModelLoadError) as info:
        model.load(fake_gguf, S)
    assert "Failed to load" in info.value.detail
    assert not model.is_loaded


def test_generate_before_load_fails():
    with pytest.raises(ModelNotLoadedError):
        list(LocalModel(lambda p, s: FakeLlama()).stream_chat([], S))


def test_stream_tokens(fake_gguf):
    fake = FakeLlama(["Mer", "ha", "ba", "!"])
    model = LocalModel(lambda p, s: fake)
    model.load(fake_gguf, S)
    assert model.is_loaded and model.model_path == fake_gguf
    assert list(model.stream_chat([{"role": "user", "content": "selam"}], S)) == ["Mer", "ha", "ba", "!"]
    assert fake.calls[0] == ([{"role": "user", "content": "selam"}], S)


def test_cancel_stops_stream(fake_gguf):
    model = LocalModel(lambda p, s: FakeLlama(["a", "b", "c", "d"]))
    model.load(fake_gguf, S)
    cancel = threading.Event()
    out = []
    for tok in model.stream_chat([], S, cancel):
        out.append(tok)
        cancel.set()
    assert out == ["a"]


def test_context_overflow_has_clear_message(fake_gguf):
    model = LocalModel(lambda p, s: FakeLlama(error=ValueError("Requested tokens exceed context window")))
    model.load(fake_gguf, S)
    with pytest.raises(GenerationError) as info:
        list(model.stream_chat([], S))
    assert "bağlam" in info.value.user_message


def test_reload_closes_previous(fake_gguf):
    first, second = FakeLlama(), FakeLlama()
    backends = iter([first, second])
    model = LocalModel(lambda p, s: next(backends))
    model.load(fake_gguf, S)
    model.load(fake_gguf, S)
    assert first.closed and not second.closed


def test_build_messages_trims_and_starts_with_user():
    history = [
        {"role": "user", "content": "1"},
        {"role": "assistant", "content": "2"},
        {"role": "user", "content": "3"},
        {"role": "assistant", "content": "4"},
        {"role": "user", "content": "5"},
    ]
    msgs = build_messages("sistem", history, max_history=4)
    assert msgs[0] == {"role": "system", "content": "sistem"}
    assert [m["content"] for m in msgs[1:]] == ["3", "4", "5"]


def test_choose_validates_answer(fake_gguf):
    model = LocalModel(lambda p, s: FakeLlama(topic="BELKI"))
    model.load(fake_gguf, S)
    with pytest.raises(GenerationError):
        model.choose([], ("ILGILI", "ILGISIZ"))


def test_choose_before_load_fails():
    with pytest.raises(ModelNotLoadedError):
        LocalModel().choose([], ("A", "B"))


def test_history_is_trimmed_in_blocks_so_prefix_stays_stable():
    """Pencere her turda kaymamalı; yoksa önbellek hiç tutmaz."""
    def first_kept(n):
        history = [{"role": "user" if i % 2 == 0 else "assistant", "content": str(i)} for i in range(n)]
        return build_messages("s", history, max_history=20)[1]["content"]

    # 21–30 mesaj arasında başlangıç sabit kalır; ardından bir blok daha atılır.
    assert {first_kept(n) for n in range(21, 31)} == {"10"}
    assert first_kept(31) == "20"
    for n in range(1, 61):
        kept = len(build_messages("s", [{"role": "user", "content": "x"}] * n, max_history=20)) - 1
        assert kept <= 20
