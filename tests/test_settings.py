from pathlib import Path

from config.settings import (
    DEFAULT_SYSTEM_PROMPT,
    TOPIC_CHECK_PROMPT,
    ModelSettings,
    load_settings,
    resolve_model_path,
    save_settings,
)


def test_missing_file_gives_defaults(tmp_path):
    assert load_settings(tmp_path / "yok.json") == ModelSettings()


def test_roundtrip_keeps_turkish_text(tmp_path):
    path = tmp_path / "s.json"
    original = ModelSettings(model_path="C:/modeller/ağrı.gguf", n_ctx=2048, topic_guard_enabled=False)
    save_settings(original, path)
    assert load_settings(path) == original


def test_system_prompt_is_not_persisted(tmp_path):
    """Talimat düzeltmeleri eski ayar dosyası olan kullanıcılara da ulaşmalı."""
    path = tmp_path / "s.json"
    save_settings(ModelSettings(system_prompt="eski talimat"), path)
    assert "eski talimat" not in path.read_text(encoding="utf-8")
    path.write_text('{"system_prompt": "eski talimat"}', encoding="utf-8")
    assert load_settings(path).system_prompt == DEFAULT_SYSTEM_PROMPT


def test_prompts_explain_idiom():
    for prompt in (DEFAULT_SYSTEM_PROMPT, TOPIC_CHECK_PROMPT):
        assert "ilk çocukları" in prompt
        assert "göz sağlığıyla hiçbir ilgisi yoktur" in prompt


def test_unknown_keys_ignored(tmp_path):
    path = tmp_path / "s.json"
    path.write_text('{"n_ctx": 1024, "bilinmeyen": true}', encoding="utf-8")
    assert load_settings(path).n_ctx == 1024


def test_corrupt_file_gives_defaults(tmp_path):
    path = tmp_path / "s.json"
    path.write_text("{bozuk", encoding="utf-8")
    assert load_settings(path) == ModelSettings()


def test_resolve_priority(tmp_path, monkeypatch):
    model_dir = tmp_path / "models"
    model_dir.mkdir()
    (model_dir / "b.gguf").write_bytes(b"GGUF")
    (model_dir / "a.gguf").write_bytes(b"GGUF")

    saved = tmp_path / "secilen.gguf"
    saved.write_bytes(b"GGUF")

    assert resolve_model_path(ModelSettings(), model_dir) == model_dir / "a.gguf"
    assert resolve_model_path(ModelSettings(model_path=str(saved)), model_dir) == saved
    monkeypatch.setenv("ILK_GOZ_AGRIM_MODEL", "env.gguf")
    assert resolve_model_path(ModelSettings(model_path=str(saved)), model_dir) == Path("env.gguf")


def test_stale_saved_path_falls_back_to_model_dir(tmp_path):
    model_dir = tmp_path / "models"
    model_dir.mkdir()
    (model_dir / "yeni.gguf").write_bytes(b"GGUF")
    stale = ModelSettings(model_path=str(tmp_path / "tasindi.gguf"))
    assert resolve_model_path(stale, model_dir) == model_dir / "yeni.gguf"
    # Dizinde de model yoksa kayıtlı yol döner; yükleme açık bir "bulunamadı" hatası verir.
    assert resolve_model_path(stale, tmp_path / "bos") == tmp_path / "tasindi.gguf"


def test_resolve_none_when_no_model(tmp_path):
    assert resolve_model_path(ModelSettings(), tmp_path / "bos") is None
