from config.settings import (
    DEFAULT_MODEL_DIR,
    DEFAULT_SYSTEM_PROMPT,
    MODEL_FILENAME,
    TOPIC_CHECK_PROMPT,
    ModelSettings,
    load_settings,
    model_file,
    save_settings,
)


def test_missing_file_gives_defaults(tmp_path):
    assert load_settings(tmp_path / "yok.json") == ModelSettings()


def test_roundtrip(tmp_path):
    path = tmp_path / "s.json"
    original = ModelSettings(n_ctx=2048, topic_guard_enabled=False)
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


def test_single_model_file(tmp_path):
    assert model_file(tmp_path) == tmp_path / MODEL_FILENAME
    assert model_file().parent == DEFAULT_MODEL_DIR
    assert MODEL_FILENAME.endswith(".gguf")


def test_old_settings_file_with_model_path_is_ignored(tmp_path):
    # Eski sürümler seçilen model yolunu kaydediyordu; artık tek model var ve bu alan yok sayılır.
    path = tmp_path / "s.json"
    path.write_text('{"model_path": "C:/eski/baska-model.gguf", "n_ctx": 2048}', encoding="utf-8")
    loaded = load_settings(path)
    assert loaded.n_ctx == 2048 and not hasattr(loaded, "model_path")
