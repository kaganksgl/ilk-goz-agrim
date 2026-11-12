from config.settings import ModelSettings, load_settings
from inference.engine import LocalModel
from storage.history import ConversationStore
from tests.conftest import FakeLlama
from ui.main_window import EXAMPLE_QUESTIONS, MainWindow
from ui.widgets import MessageBubble, safe_markdown


def make_window(qtbot, tmp_path, factory=None, model_path=None, settings=None):
    window = MainWindow(
        settings=settings or ModelSettings(),
        model=LocalModel(factory or (lambda p, s: FakeLlama())),
        initial_model_path=model_path,
        store=ConversationStore(tmp_path / "history"),
        settings_path=tmp_path / "settings.json",
    )
    qtbot.addWidget(window)
    return window


def ready_window(qtbot, tmp_path, fake_gguf, fake=None, settings=None):
    fake = fake or FakeLlama()
    w = make_window(qtbot, tmp_path, factory=lambda p, s: fake, model_path=fake_gguf, settings=settings)
    qtbot.waitUntil(lambda: w.state == "ready", timeout=5000)
    return w, fake


def ask(qtbot, w, text):
    w.input.setPlainText(text)
    w.send_message()
    qtbot.waitUntil(lambda: w.state == "ready", timeout=5000)


def roles(window):
    return [b.role for b in window.bubbles()]


# ---- model durumu -----------------------------------------------------------
def test_no_model_shows_clear_state_and_never_answers(qtbot, tmp_path):
    w = make_window(qtbot, tmp_path)
    assert w.state == "not_loaded"
    assert w.status_label.text() == "Model yüklenmedi"
    assert not w.notice.isHidden()
    assert "Model bulunamadı" in w.notice_label.text()

    w.input.setPlainText("Merhaba")
    w.send_message()  # Enter ile tetiklenmiş gibi
    assert w.bubbles() == []
    assert "Model yüklenmediği için" in w.notice_label.text()
    w.close()


def test_missing_file_reports_error(qtbot, tmp_path):
    w = make_window(qtbot, tmp_path, model_path=tmp_path / "yok.gguf")
    qtbot.waitUntil(lambda: w.state == "error", timeout=5000)
    assert "bulunamadı" in w.notice_label.text()
    w.close()


def test_retry_loads_model_once_file_is_in_place(qtbot, tmp_path):
    # Tek model: dosya seçilemez; kullanıcı dosyayı yerine koyup "Yeniden dene"ye basar.
    path = tmp_path / "model.gguf"
    w = make_window(qtbot, tmp_path, factory=lambda p, s: FakeLlama(), model_path=path)
    qtbot.waitUntil(lambda: w.state == "error", timeout=5000)
    assert w.retry_button.isEnabled() and not hasattr(w, "choose_button")
    path.write_bytes(b"GGUF" + b"\x00" * 64)
    w.retry_button.click()
    qtbot.waitUntil(lambda: w.state == "ready", timeout=5000)
    assert w.notice.isHidden()
    w.close()


def test_load_error_reports_error(qtbot, tmp_path, fake_gguf):
    def boom(_p, _s):
        raise RuntimeError("bozuk dosya")

    w = make_window(qtbot, tmp_path, factory=boom, model_path=fake_gguf)
    qtbot.waitUntil(lambda: w.state == "error", timeout=5000)
    assert "Model yüklenemedi" in w.notice_label.text()
    assert "bozuk dosya" in w.notice_label.text()
    w.close()


def test_successful_load_hides_notice_and_names_model(qtbot, tmp_path, fake_gguf):
    w, _ = ready_window(qtbot, tmp_path, fake_gguf)
    assert w.notice.isHidden()
    assert "fake" in w.status_label.text()
    w.close()


# ---- sohbet -----------------------------------------------------------------
def test_streams_answer_and_saves_history(qtbot, tmp_path, fake_gguf):
    w, _ = ready_window(qtbot, tmp_path, fake_gguf)
    assert w.stack.currentIndex() == 0  # karşılama ekranı
    w.input.setPlainText("Selam")
    assert w.send_button.isEnabled()
    w.send_message()
    qtbot.waitUntil(lambda: w.state == "ready", timeout=5000)

    assert w.stack.currentIndex() == 1
    assert roles(w) == ["user", "assistant"]
    assert w.bubbles()[-1].text() == "Merhaba"
    saved = ConversationStore(tmp_path / "history").load(w.conversation_id)
    assert saved == [{"role": "user", "content": "Selam"}, {"role": "assistant", "content": "Merhaba"}]
    assert w.conversation_list.count() == 1
    assert w.conversation_list.item(0).text() == "Selam"
    w.close()


def test_example_question_is_sent(qtbot, tmp_path, fake_gguf):
    w, fake = ready_window(qtbot, tmp_path, fake_gguf)
    w.example_buttons[1].click()
    qtbot.waitUntil(lambda: w.state == "ready", timeout=5000)
    assert w.bubbles()[0].text() == EXAMPLE_QUESTIONS[1]
    assert fake.calls[0][0][-1]["content"].endswith(EXAMPLE_QUESTIONS[1])
    w.close()


def test_generation_error_is_shown(qtbot, tmp_path, fake_gguf):
    w, _ = ready_window(qtbot, tmp_path, fake_gguf, fake=FakeLlama(error=RuntimeError("çöktü")))
    w.input.setPlainText("Selam")
    w.send_message()
    qtbot.waitUntil(lambda: w.bubbles() and w.bubbles()[-1].role == "error", timeout=5000)
    assert "Cevap üretilirken" in w.bubbles()[-1].text()
    assert w.history == []
    w.close()


# ---- konu denetimi ----------------------------------------------------------
def test_off_topic_question_is_refused_without_generation(qtbot, tmp_path, fake_gguf):
    w, fake = ready_window(qtbot, tmp_path, fake_gguf, fake=FakeLlama(topic="ILGISIZ"))
    ask(qtbot, w, "Python'da liste nasıl sıralanır?")
    assert roles(w) == ["user", "warning"]
    assert "konuları dışında" in w.bubbles()[-1].text()
    assert fake.calls == []  # cevap üretimi hiç başlamadı
    assert w.history == []  # konu dışı soru sonraki isteklere bağlam olarak gitmez
    w.close()


def test_relevant_question_passes_history_to_guard(qtbot, tmp_path, fake_gguf):
    w, fake = ready_window(qtbot, tmp_path, fake_gguf)
    ask(qtbot, w, "Bebeğim kaç saat uyumalı?")
    check_messages = fake.choose_calls[0][0]
    assert "Son mesaj: Bebeğim kaç saat uyumalı?" in check_messages[-1]["content"]
    sent = fake.calls[0][0]
    assert sent[0]["role"] == "system" and "ilk çocukları" in sent[0]["content"]
    # Soruya uyan bilgi kartı yalnızca modele giden son mesaja eklenir …
    assert sent[-1]["role"] == "user" and sent[-1]["content"].endswith("Soru: Bebeğim kaç saat uyumalı?")
    assert "doğrulanmış bilgiler" in sent[-1]["content"] and "14–17 saat" in sent[-1]["content"]
    # … ekranda ve geçmişte kullanıcının yazdığı metin olduğu gibi kalır.
    assert w.history[0] == {"role": "user", "content": "Bebeğim kaç saat uyumalı?"}
    assert "doğrulanmış" not in w.bubbles()[0].text()
    assert w.bubbles()[-1].role == "assistant"
    w.close()


def test_guard_can_be_disabled(qtbot, tmp_path, fake_gguf):
    w, fake = ready_window(
        qtbot, tmp_path, fake_gguf, fake=FakeLlama(topic="ILGISIZ"), settings=ModelSettings(topic_guard_enabled=False)
    )
    ask(qtbot, w, "Selam")
    assert fake.choose_calls == []
    assert w.bubbles()[-1].text() == "Merhaba"
    w.close()


# ---- geçmiş -----------------------------------------------------------------
def test_new_conversation_and_reopen(qtbot, tmp_path, fake_gguf):
    w, fake = ready_window(qtbot, tmp_path, fake_gguf)
    ask(qtbot, w, "Birinci soru")
    first_id = w.conversation_id

    w.new_conversation()
    assert w.history == [] and w.bubbles() == [] and w.stack.currentIndex() == 0
    assert w.conversation_id != first_id
    ask(qtbot, w, "İkinci soru")
    assert w.conversation_list.count() == 2

    w.open_conversation(first_id)
    assert [b.text() for b in w.bubbles()] == ["Birinci soru", "Merhaba"]
    ask(qtbot, w, "Devam sorusu")
    # Açılan sohbete devam edilir: önceki mesajlar modele bağlam olarak gider.
    assert [m["content"] for m in fake.calls[-1][0][1:]] == ["Birinci soru", "Merhaba", "Devam sorusu"]
    assert len(ConversationStore(tmp_path / "history").load(first_id)) == 4
    w.close()


def test_delete_conversation_asks_for_confirmation(qtbot, tmp_path, fake_gguf, monkeypatch):
    w, _ = ready_window(qtbot, tmp_path, fake_gguf)
    ask(qtbot, w, "Silinecek soru")
    w.conversation_list.setCurrentRow(0)

    monkeypatch.setattr(w, "confirm", lambda *a: False)
    w.delete_selected_conversation()
    assert w.conversation_list.count() == 1

    monkeypatch.setattr(w, "confirm", lambda *a: True)
    w.delete_selected_conversation()
    assert w.conversation_list.count() == 0
    assert ConversationStore(tmp_path / "history").list_ids() == []
    assert w.bubbles() == []  # açık olan sohbet silindiyse ekran temizlenir
    w.close()


def test_history_saving_can_be_turned_off(qtbot, tmp_path, fake_gguf):
    w, _ = ready_window(qtbot, tmp_path, fake_gguf, settings=ModelSettings(save_history=False))
    ask(qtbot, w, "Kaydedilmemeli")
    assert ConversationStore(tmp_path / "history").list_ids() == []
    assert "kapalı" in w.history_note.text()
    w.close()


# ---- ayarlar ----------------------------------------------------------------
def test_settings_dialog_applies_and_persists(qtbot, tmp_path, fake_gguf, monkeypatch):
    w, _ = ready_window(qtbot, tmp_path, fake_gguf)
    ask(qtbot, w, "Bir soru")
    dialog = w.make_settings_dialog()
    dialog.font_combo.setCurrentText("Büyük")
    dialog.history_check.setChecked(False)
    monkeypatch.setattr(dialog, "confirm", lambda *a: True)
    dialog.delete_all_button.click()
    w.apply_settings_dialog(dialog)

    assert ConversationStore(tmp_path / "history").list_ids() == []
    assert w.bubbles() == []
    saved = load_settings(tmp_path / "settings.json")
    assert saved.font_scale == 1.15 and saved.save_history is False
    assert "font-size: 16px" in w.styleSheet()  # 14 px * 1.15
    w.close()


def test_font_scale_shortcuts_are_bounded(qtbot, tmp_path):
    w = make_window(qtbot, tmp_path)
    for _ in range(5):
        w.change_font_scale(+1)
    assert w.settings.font_scale == 1.3
    for _ in range(5):
        w.change_font_scale(-1)
    assert w.settings.font_scale == 0.9
    w.close()


# ---- biçimlendirme ----------------------------------------------------------
def test_markdown_is_rendered_but_html_is_not(qtbot):
    assert safe_markdown("a<b> & ![x](C:/r.png)") == "a&lt;b&gt; &amp; !\\[x](C:/r.png)"
    bubble = MessageBubble("assistant", "**Kalın** <script>x</script>")
    qtbot.addWidget(bubble)
    assert bubble.text() == "**Kalın** <script>x</script>"
    doc_text = bubble.label.text()
    assert "&lt;script&gt;" in doc_text

    from PySide6.QtGui import QTextDocument

    doc = QTextDocument()
    doc.setMarkdown(doc_text)
    assert doc.toPlainText() == "Kalın <script>x</script>"


def test_user_text_is_plain(qtbot):
    bubble = MessageBubble("user", "**yıldız** <b>")
    qtbot.addWidget(bubble)
    assert bubble.label.text() == "**yıldız** <b>"


# ---- acil durum ---------------------------------------------------------------
EMERGENCY_TEXT = "32 haftalık hamileyim, çok şiddetli baş ağrım var ve gözlerim bulanık görüyor"


def test_emergency_box_without_model(qtbot, tmp_path):
    """Acil durum uyarısı model yüklenmemişken de gösterilmeli."""
    w = make_window(qtbot, tmp_path)
    w.input.setPlainText(EMERGENCY_TEXT)
    assert w.send_button.isEnabled()
    w.send_button.click()
    assert roles(w) == ["user", "emergency"]
    box = w.bubbles()[-1].text()
    assert "112" in box and "bulanık görme" in box
    assert "yapay zekâ tarafından üretilmedi" in box
    assert w.history == []
    w.close()


def test_emergency_skips_model_entirely(qtbot, tmp_path, fake_gguf):
    w, fake = ready_window(qtbot, tmp_path, fake_gguf)
    w.input.setPlainText("Bebeğim nefes alamıyor, dudakları morardı")
    w.send_message()
    assert roles(w) == ["user", "emergency"]
    assert w.state == "ready"
    assert fake.choose_calls == [] and fake.calls == []  # ne konu denetimi ne cevap üretimi
    assert w.history == []
    assert ConversationStore(tmp_path / "history").list_ids() == []
    w.close()


def test_emergency_while_model_loading(qtbot, tmp_path, fake_gguf):
    import threading

    gate = threading.Event()

    def slow_factory(_p, _s):
        gate.wait(5)
        return FakeLlama()

    w = make_window(qtbot, tmp_path, factory=slow_factory, model_path=fake_gguf)
    assert w.state == "loading"
    w.input.setPlainText("Oğlum çamaşır suyu içti")
    w.send_message()
    assert roles(w) == ["user", "emergency"]
    assert "114" in w.bubbles()[-1].text()
    w.input.setPlainText("Bebekler ne zaman yürür?")
    w.send_message()
    assert "yükleniyor" in w.notice_label.text()
    gate.set()
    qtbot.waitUntil(lambda: w.state == "ready", timeout=5000)
    assert w.notice.isHidden()
    w.close()


def test_normal_question_still_reaches_model(qtbot, tmp_path, fake_gguf):
    # Varsayılan sahte cevap "Merhaba"; selamla başlayan cevap selamlaşmayan soruda yeniden üretilir.
    w, fake = ready_window(qtbot, tmp_path, fake_gguf, fake=FakeLlama(["Emzirirken ", "hassasiyet ", "olabilir."]))
    ask(qtbot, w, "Emzirirken göğsüm ağrıyor, bu normal mi?")
    assert roles(w) == ["user", "assistant"]
    assert len(fake.calls) == 1
    w.close()


# ---- ısınma ---------------------------------------------------------------------
def test_prompts_are_warmed_up_after_load(qtbot, tmp_path, fake_gguf):
    w, fake = ready_window(qtbot, tmp_path, fake_gguf)
    qtbot.waitUntil(lambda: len(fake.warm_calls) == 1, timeout=5000)
    check_prompt, answer_prompt = fake.warm_calls[0]
    assert "ILGISIZ" in check_prompt[-1]["content"]  # konu denetimi istemi
    assert answer_prompt[0]["content"] == ModelSettings().system_prompt
    w.close()


def test_warm_up_failure_does_not_break_the_app(qtbot, tmp_path, fake_gguf):
    fake = FakeLlama()
    fake.warm_error = RuntimeError("ısınma hatası")
    w, _ = ready_window(qtbot, tmp_path, fake_gguf, fake=fake)
    ask(qtbot, w, "Selam")
    assert w.bubbles()[-1].text() == "Merhaba"
    w.close()


def test_known_spelling_errors_are_fixed_in_display_and_history(qtbot, tmp_path, fake_gguf):
    fake = FakeLlama(["Lütfen doktorunuza veya ", "ebeğ", "inize danışın."])
    w, _ = ready_window(qtbot, tmp_path, fake_gguf, fake=fake)
    ask(qtbot, w, "Bebeğim çok ağlıyor")
    bubble = w.bubbles()[-1]
    assert "ebenize" in bubble.displayed_text() and "ebeğinize" not in bubble.displayed_text()
    assert w.history[-1]["content"] == "Lütfen doktorunuza veya ebenize danışın."
    saved = ConversationStore(tmp_path / "history").load(w.conversation_id)
    assert saved[-1]["content"] == "Lütfen doktorunuza veya ebenize danışın."
    w.close()


# ---- doz koruması ---------------------------------------------------------------
def test_dose_question_gets_fixed_answer_without_model(qtbot, tmp_path, fake_gguf):
    w, fake = ready_window(qtbot, tmp_path, fake_gguf)
    w.input.setPlainText("Bebeğime ateş düşürücü şurup kaç ml verilir?")
    w.send_message()
    assert roles(w) == ["user", "warning"]
    assert "doz" in w.bubbles()[-1].text()
    assert fake.calls == [] and fake.choose_calls == []
    assert w.history == []
    w.close()


def test_dose_in_model_answer_is_masked(qtbot, tmp_path, fake_gguf):
    fake = FakeLlama(["Gebelikte günde 400 mikrogram ", "folik asit önerilir."])
    w, _ = ready_window(qtbot, tmp_path, fake_gguf, fake=fake)
    ask(qtbot, w, "Folik asit neden önemli?")
    assert "400" not in w.bubbles()[-1].displayed_text()
    assert "400" not in w.history[-1]["content"]
    w.close()


# ---- kaydırma ---------------------------------------------------------------------
class SlowFake(FakeLlama):
    def stream(self, messages, settings):
        import time

        for tok in self.tokens:
            time.sleep(0.005)
            yield tok


def _long_answer_window(qtbot, tmp_path, fake_gguf):
    tokens = [f"Kelime{i} " if i % 10 else f"Kelime{i}\n\n" for i in range(300)]
    w, _ = ready_window(qtbot, tmp_path, fake_gguf, fake=SlowFake(tokens), settings=ModelSettings(topic_guard_enabled=False))
    w.resize(800, 500)
    w.show()
    return w


def test_view_follows_answer_when_at_bottom(qtbot, tmp_path, fake_gguf):
    w = _long_answer_window(qtbot, tmp_path, fake_gguf)
    ask(qtbot, w, "Uzun anlat")
    qtbot.wait(50)
    bar = w.scroll.verticalScrollBar()
    assert bar.maximum() > 0 and bar.value() == bar.maximum()
    w.close()


def test_view_stays_put_when_user_scrolled_up(qtbot, tmp_path, fake_gguf):
    w = _long_answer_window(qtbot, tmp_path, fake_gguf)
    bar = w.scroll.verticalScrollBar()
    w.input.setPlainText("Uzun anlat")
    w.send_message()
    qtbot.waitUntil(lambda: w._current_bubble is not None and w._current_bubble.text().count("Kelime") > 120, timeout=10000)
    bar.setValue(max(0, bar.maximum() - 300))  # kullanıcı yukarı kaydırır
    position = bar.value()
    qtbot.waitUntil(lambda: w.state == "ready", timeout=10000)
    qtbot.wait(50)
    assert bar.value() == position  # cevap büyümeye devam etse de görünüm kıpırdamaz
    assert bar.maximum() > position + 300

    # Yeni mesaj gönderilince görünüm yeniden en alta iner.
    ask(qtbot, w, "Bir soru daha")
    qtbot.wait(50)
    assert bar.value() == bar.maximum()
    w.close()


def test_greeting_answer_to_real_question_is_regenerated_in_app(qtbot, tmp_path, fake_gguf):
    class Flaky(FakeLlama):
        def stream(self, messages, settings):
            self.calls.append((messages, settings))
            first = len(self.calls) == 1
            yield from (["Merhaba, ben ", "İlk Göz Ağrım'ın ", "yardımcı asistanıyım."] if first
                        else ["Hayır, bebeği ", "banyoda asla ", "yalnız bırakmayın."])

    w, fake = ready_window(qtbot, tmp_path, fake_gguf, fake=Flaky())
    ask(qtbot, w, "Bebeği banyoda yalnız bırakabilir miyim?")
    assert w.bubbles()[-1].text() == "Hayır, bebeği banyoda asla yalnız bırakmayın."
    assert len(fake.calls) == 2
    w.close()
