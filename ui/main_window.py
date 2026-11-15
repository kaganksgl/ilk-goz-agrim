"""İlk Göz Ağrım ana sohbet penceresi."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from config.settings import APP_NAME, APP_VERSION, ModelSettings, save_settings
from inference.engine import LocalModel
from inference.errors import ModelNotConfiguredError, ModelNotLoadedError
from inference.text_fixes import clean_answer
from safety.dose import DOSE_REFUSAL_MESSAGE, is_dose_request
from safety.emergency import detect as detect_emergency
from safety.emergency import emergency_message
from storage.history import ConversationStore
from ui.settings_dialog import SettingsDialog
from ui.style import FONT_SCALES, build_stylesheet
from ui.theme import PALETTES, effective_scheme, qt_palette
from ui.widgets import ChatInput, MessageBubble
from ui.worker import InferenceWorker

DISCLAIMER = (
    "Bu uygulama bir demo sürümüdür ve tıbbi tavsiye vermez. Cevaplar yapay zekâ tarafından "
    "üretilir ve hatalı olabilir. Sağlığınız ve bebeğinizin sağlığıyla ilgili kararlar için "
    "mutlaka doktorunuza veya ebenize danışın. Acil durumlarda 112'yi arayın."
)

WELCOME_TEXT = (
    "Gebelik, doğum, lohusalık, emzirme ve bebek ya da çocuk gelişimiyle ilgili sorularınızı "
    "yazabilirsiniz. Tüm cevaplar bu bilgisayarda, internete bağlanmadan üretilir."
)

EXAMPLE_QUESTIONS = [
    "Gebeliğin ilk aylarında nelere dikkat etmeliyim?",
    "Bebekler kaç aylıkken emeklemeye başlar?",
    "Yenidoğan bir bebeğin uyku düzeni nasıl olur?",
    "Emzirmeye yeni başlayan bir anne nelere dikkat etmeli?",
]

STATUS_TEXT = {
    "not_loaded": "Model yüklenmedi",
    "loading": "Model yükleniyor…",
    "ready": "Hazır",
    "generating": "Cevap üretiliyor…",
    "checking": "Soru değerlendiriliyor…",
    "error": "Model hatası",
}

SCALE_STEPS = sorted(FONT_SCALES.values())


class MainWindow(QMainWindow):
    request_load = Signal(object)
    request_generate = Signal(object)

    def __init__(
        self,
        settings: ModelSettings,
        model: LocalModel,
        initial_model_path: Path | None,
        store: ConversationStore | None = None,
        settings_path: Path | None = None,
    ):
        super().__init__()
        self.settings = settings
        self.store = store
        self.settings_path = settings_path
        self.conversation_id = ConversationStore.new_id()
        self.history: list[dict[str, str]] = []
        self.state = "not_loaded"
        self.model_path: str | None = None
        self._model_file = initial_model_path
        self._current_bubble: MessageBubble | None = None

        self.setWindowTitle(APP_NAME)
        self.resize(1080, 760)
        self.setMinimumSize(720, 520)
        self.color_scheme = "light"
        self._build_ui()
        self._build_shortcuts()
        self.apply_appearance()
        QApplication.instance().styleHints().colorSchemeChanged.connect(self._on_system_scheme_changed)
        self.refresh_conversation_list()

        self._model = model
        self._thread = QThread(self)
        self._worker = InferenceWorker(model, settings)
        self._worker.moveToThread(self._thread)
        self.request_load.connect(self._worker.load)
        self.request_generate.connect(self._worker.generate)
        self._worker.load_started.connect(self._on_load_started)
        self._worker.load_succeeded.connect(self._on_load_succeeded)
        self._worker.load_failed.connect(self._on_load_failed)
        self._worker.token_received.connect(self._on_token)
        self._worker.generation_finished.connect(self._on_generation_finished)
        self._worker.generation_failed.connect(self._on_generation_failed)
        self._worker.checking_topic.connect(lambda: self._set_status_text("checking"))
        self._worker.answer_started.connect(self._on_answer_started)
        self._worker.off_topic.connect(self._on_off_topic)
        self._thread.start()

        if initial_model_path is None:
            self._set_state("not_loaded")
            self.show_notice(ModelNotConfiguredError.user_message)
        else:
            self.load_model(initial_model_path)

    # ---- arayüz kurulumu -------------------------------------------------
    def _build_ui(self) -> None:
        root = QWidget(objectName="root")
        outer = QVBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(self._build_header())

        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(True)
        splitter.addWidget(self._build_sidebar())
        splitter.addWidget(self._build_chat_area())
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([250, 830])
        outer.addWidget(splitter, 1)
        self.setCentralWidget(root)

    def _build_header(self) -> QFrame:
        header = QFrame(objectName="header")
        h = QHBoxLayout(header)
        h.setContentsMargins(20, 12, 20, 12)
        titles = QVBoxLayout()
        title = QLabel(APP_NAME, objectName="appTitle")
        title.setAccessibleName("Uygulama adı: " + APP_NAME)
        subtitle = QLabel(f"Gebelik ve çocuk gelişimi asistanı · çevrimdışı · demo sürümü {APP_VERSION}", objectName="appSubtitle")
        titles.addWidget(title)
        titles.addWidget(subtitle)
        h.addLayout(titles)
        h.addStretch(1)
        self.status_dot = QLabel(objectName="statusDot")
        self.status_label = QLabel(objectName="statusLabel")
        self.status_label.setAccessibleName("Model durumu")
        h.addWidget(self.status_dot)
        h.addWidget(self.status_label)
        h.addSpacing(8)
        self.settings_button = QPushButton("Ayarlar", objectName="secondaryButton")
        self.settings_button.setAccessibleName("Ayarları aç")
        self.settings_button.setToolTip("Ayarlar (Ctrl+,)")
        self.settings_button.clicked.connect(self.open_settings)
        h.addWidget(self.settings_button)
        return header

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame(objectName="sidebar")
        sidebar.setMinimumWidth(180)
        s = QVBoxLayout(sidebar)
        s.setContentsMargins(12, 12, 12, 12)
        s.setSpacing(8)
        self.new_chat_button = QPushButton("+ Yeni sohbet", objectName="secondaryButton")
        self.new_chat_button.setAccessibleName("Yeni sohbet başlat")
        self.new_chat_button.setToolTip("Yeni sohbet (Ctrl+N)")
        self.new_chat_button.clicked.connect(self.new_conversation)
        s.addWidget(self.new_chat_button)
        s.addWidget(QLabel("Geçmiş sohbetler", objectName="sidebarTitle"))
        self.conversation_list = QListWidget(objectName="conversationList")
        self.conversation_list.setAccessibleName("Geçmiş sohbetler")
        self.conversation_list.setWordWrap(True)
        # Uzun başlık satıra sığmayınca yatay kaydırma çubuğu çıkıyor ve metin kırpılıyordu (15.11.2026):
        # liste genişliğe göre yeniden dizilir, başlık alt satıra kayar.
        self.conversation_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.conversation_list.setResizeMode(QListWidget.Adjust)
        self.conversation_list.itemActivated.connect(self._on_conversation_activated)
        self.conversation_list.itemClicked.connect(self._on_conversation_activated)
        s.addWidget(self.conversation_list, 1)
        self.history_note = QLabel(objectName="sidebarNote")
        self.history_note.setWordWrap(True)
        s.addWidget(self.history_note)
        self.delete_button = QPushButton("Sohbeti sil", objectName="dangerButton")
        self.delete_button.setAccessibleName("Seçili sohbeti sil")
        self.delete_button.clicked.connect(self.delete_selected_conversation)
        s.addWidget(self.delete_button)
        return sidebar

    def _build_chat_area(self) -> QWidget:
        area = QWidget()
        body = QVBoxLayout(area)
        body.setContentsMargins(20, 12, 20, 16)
        body.setSpacing(10)

        disclaimer = QFrame(objectName="disclaimer")
        d = QHBoxLayout(disclaimer)
        d.setContentsMargins(12, 8, 12, 8)
        self.disclaimer_label = QLabel("ⓘ  " + DISCLAIMER, objectName="disclaimerText")
        self.disclaimer_label.setWordWrap(True)
        self.disclaimer_label.setAccessibleName("Sağlık bilgilendirmesi")
        d.addWidget(self.disclaimer_label)
        body.addWidget(disclaimer)

        # Model hataları sohbetin içine değil, burada kalıcı olarak gösterilir.
        self.notice = QFrame(objectName="notice")
        n = QHBoxLayout(self.notice)
        n.setContentsMargins(12, 8, 12, 8)
        self.notice_label = QLabel(objectName="noticeText")
        self.notice_label.setWordWrap(True)
        self.notice_label.setTextFormat(Qt.PlainText)
        self.notice_label.setAccessibleName("Model uyarısı")
        self.notice_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        n.addWidget(self.notice_label, 1)
        self.retry_button = QPushButton("Yeniden dene", objectName="secondaryButton")
        self.retry_button.setAccessibleName("Modeli yeniden yüklemeyi dene")
        self.retry_button.clicked.connect(self._retry_load)
        n.addWidget(self.retry_button)
        self.notice.hide()
        body.addWidget(self.notice)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_welcome())
        self.scroll = QScrollArea(objectName="messages")
        self.scroll.setWidgetResizable(True)
        # "Yapışkan" kaydırma: kullanıcı en alttaysa cevabı takip eder; yukarı kaydırdıysa yerinde bırakır.
        self._follow_bottom = True
        self._scrolling_programmatically = False
        bar = self.scroll.verticalScrollBar()
        bar.rangeChanged.connect(self._on_scroll_range_changed)
        bar.valueChanged.connect(self._on_scroll_value_changed)
        self.stack.addWidget(self.scroll)
        self._reset_messages()
        body.addWidget(self.stack, 1)

        input_row = QHBoxLayout()
        self.input = ChatInput(objectName="input")
        self.input.setPlaceholderText("Sorunuzu yazın… (Enter: gönder, Shift+Enter: yeni satır)")
        self.input.setAccessibleName("Mesaj giriş alanı")
        self.input.setFixedHeight(76)
        self.input.submitted.connect(self.send_message)
        self.input.textChanged.connect(self._update_controls)
        buttons = QVBoxLayout()
        self.send_button = QPushButton("Gönder", objectName="sendButton")
        self.send_button.setAccessibleName("Mesajı gönder")
        self.send_button.clicked.connect(self.send_message)
        self.stop_button = QPushButton("Durdur", objectName="secondaryButton")
        self.stop_button.setAccessibleName("Cevap üretimini durdur")
        self.stop_button.setToolTip("Durdur (Esc)")
        self.stop_button.clicked.connect(self.stop_generation)
        buttons.addWidget(self.send_button)
        buttons.addWidget(self.stop_button)
        input_row.addWidget(self.input, 1)
        input_row.addLayout(buttons)
        body.addLayout(input_row)
        return area

    def _build_welcome(self) -> QWidget:
        page = QWidget(objectName="welcome")
        w = QVBoxLayout(page)
        w.addStretch(1)
        title = QLabel("Merhaba! Size nasıl yardımcı olabilirim?", objectName="welcomeTitle")
        title.setAlignment(Qt.AlignCenter)
        w.addWidget(title)
        text = QLabel(WELCOME_TEXT, objectName="welcomeText")
        text.setAlignment(Qt.AlignCenter)
        text.setWordWrap(True)
        w.addWidget(text)
        w.addSpacing(12)
        self.example_buttons: list[QPushButton] = []
        for question in EXAMPLE_QUESTIONS:
            button = QPushButton(question, objectName="exampleButton")
            button.setAccessibleName("Örnek soru: " + question)
            button.clicked.connect(lambda _checked=False, q=question: self.ask_example(q))
            self.example_buttons.append(button)
            row = QHBoxLayout()
            row.addStretch(1)
            row.addWidget(button, 4)
            row.addStretch(1)
            w.addLayout(row)
        w.addStretch(2)
        return page

    def _build_shortcuts(self) -> None:
        shortcuts = {
            "Ctrl+N": self.new_conversation,
            "Esc": self.stop_generation,
            "Ctrl+,": self.open_settings,
            "Ctrl+=": lambda: self.change_font_scale(+1),
            "Ctrl++": lambda: self.change_font_scale(+1),
            "Ctrl+-": lambda: self.change_font_scale(-1),
            "Ctrl+0": lambda: self.set_font_scale(1.0),
        }
        for keys, slot in shortcuts.items():
            QShortcut(QKeySequence(keys), self, activated=slot)

    # ---- durum -----------------------------------------------------------
    def _set_state(self, state: str, detail: str = "") -> None:
        self.state = state
        self.status_dot.setProperty("state", state)
        self.status_dot.style().unpolish(self.status_dot)
        self.status_dot.style().polish(self.status_dot)
        self._set_status_text(state)
        self.status_label.setToolTip(detail)
        self._update_controls()

    def _set_status_text(self, key: str) -> None:
        text = STATUS_TEXT[key]
        if key == "ready" and self.model_path:
            text = f"{text} · {Path(self.model_path).stem}"
        self.status_label.setText(text)
        self.status_dot.setAccessibleName("Durum: " + text)

    def _update_controls(self) -> None:
        busy = self.state in ("loading", "generating")
        has_text = bool(self.input.toPlainText().strip())
        # Model hazır değilken de gönderilebilir: acil durum uyarısı modelden bağımsız çalışır.
        self.send_button.setEnabled(self.state != "generating" and has_text)
        self.stop_button.setEnabled(self.state == "generating")
        self.retry_button.setEnabled(not busy and self._model_file is not None)
        self.settings_button.setEnabled(not busy)
        self.new_chat_button.setEnabled(self.state != "generating")
        self.conversation_list.setEnabled(self.state != "generating")
        self.delete_button.setEnabled(
            self.state != "generating" and self.conversation_list.currentItem() is not None
        )

    def show_notice(self, text: str) -> None:
        self.notice_label.setText(text)
        self.notice.show()

    def hide_notice(self) -> None:
        self.notice.hide()

    # ---- mesaj alanı -----------------------------------------------------
    _FOLLOW_MARGIN_PX = 24  # en alta bu kadar yakınsa "en altta" sayılır

    def _on_scroll_value_changed(self, value: int) -> None:
        if self._scrolling_programmatically:
            return
        bar = self.scroll.verticalScrollBar()
        self._follow_bottom = value >= bar.maximum() - self._FOLLOW_MARGIN_PX

    def _on_scroll_range_changed(self, _minimum: int, maximum: int) -> None:
        if self._follow_bottom:
            self.scroll_to_bottom()

    def scroll_to_bottom(self) -> None:
        bar = self.scroll.verticalScrollBar()
        self._follow_bottom = True
        self._scrolling_programmatically = True
        bar.setValue(bar.maximum())
        self._scrolling_programmatically = False

    def _reset_messages(self) -> None:
        inner = QWidget(objectName="messagesInner")
        self.messages_layout = QVBoxLayout(inner)
        self.messages_layout.setContentsMargins(0, 4, 4, 4)
        self.messages_layout.setSpacing(8)
        self.messages_layout.addStretch(1)
        self.scroll.setWidget(inner)  # önceki mesajlar Qt tarafından silinir
        self._current_bubble = None
        self._follow_bottom = True
        self.stack.setCurrentIndex(0)

    def add_message(self, role: str, text: str) -> MessageBubble:
        if role == "user":
            # Kullanıcı yeni mesaj gönderince, yukarıda okuyor olsa bile görünüm yeni mesaja iner.
            self._follow_bottom = True
        bubble = MessageBubble(role, text)
        row = QHBoxLayout()
        if role == "user":
            row.addStretch(1)
            row.addWidget(bubble, 4)
        elif role == "assistant":
            row.addWidget(bubble, 4)
            row.addStretch(1)
        else:
            row.addWidget(bubble)
        self.messages_layout.insertLayout(self.messages_layout.count() - 1, row)
        self.stack.setCurrentIndex(1)
        return bubble

    def bubbles(self) -> list[MessageBubble]:
        return self.scroll.widget().findChildren(MessageBubble)

    # ---- sohbet listesi --------------------------------------------------
    def refresh_conversation_list(self) -> None:
        self.conversation_list.blockSignals(True)
        self.conversation_list.clear()
        conversations = self.store.list_conversations() if self.store is not None else []
        for info in conversations:
            item = QListWidgetItem(info.title)
            item.setData(Qt.UserRole, info.id)
            item.setToolTip(f"{info.title}\n{info.updated_at.replace('T', ' ')}")
            self.conversation_list.addItem(item)
            if info.id == self.conversation_id:
                self.conversation_list.setCurrentItem(item)
        self.conversation_list.blockSignals(False)
        if not self.settings.save_history:
            self.history_note.setText("Geçmiş kaydı kapalı; yeni sohbetler kaydedilmiyor.")
        elif not conversations:
            self.history_note.setText("Henüz kayıtlı sohbet yok.")
        else:
            self.history_note.setText("")
        self.history_note.setVisible(bool(self.history_note.text()))
        self._update_controls()

    def new_conversation(self) -> None:
        if self.state == "generating":
            return
        self.conversation_id = ConversationStore.new_id()
        self.history = []
        self._reset_messages()
        self.conversation_list.clearSelection()
        self.conversation_list.setCurrentItem(None)
        self._update_controls()
        self.input.setFocus()

    def open_conversation(self, conversation_id: str) -> None:
        if self.state == "generating" or self.store is None:
            return
        try:
            messages = self.store.load(conversation_id)
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, "Sohbet açılamadı", f"Sohbet dosyası okunamadı: {exc}")
            return
        self.conversation_id = conversation_id
        self.history = [m for m in messages if m.get("role") in ("user", "assistant")]
        self._reset_messages()
        for message in self.history:
            self.add_message(message["role"], message["content"])
        self._update_controls()

    def _on_conversation_activated(self, item: QListWidgetItem) -> None:
        conversation_id = item.data(Qt.UserRole)
        if conversation_id != self.conversation_id:
            self.open_conversation(conversation_id)
        self._update_controls()

    def confirm(self, title: str, text: str) -> bool:
        return QMessageBox.question(self, title, text) == QMessageBox.Yes

    def delete_selected_conversation(self) -> None:
        item = self.conversation_list.currentItem()
        if item is None or self.store is None or self.state == "generating":
            return
        if not self.confirm("Sohbeti sil", f"“{item.text()}” sohbeti kalıcı olarak silinsin mi?"):
            return
        conversation_id = item.data(Qt.UserRole)
        self.store.delete(conversation_id)
        if conversation_id == self.conversation_id:
            self.new_conversation()
        self.refresh_conversation_list()

    # ---- ayarlar ---------------------------------------------------------
    def _persist_settings(self) -> None:
        if self.settings_path is not None:
            save_settings(self.settings, self.settings_path)

    def apply_appearance(self) -> None:
        """Tema ve metin boyutunu uygular. Qt'nin renk şeması ve paleti de temaya uyar; böylece
        ayarlar penceresi, açılır listeler ve mesaj kutuları da aynı renkleri kullanır."""
        app = QApplication.instance()
        hints = app.styleHints()
        forced = {"light": Qt.ColorScheme.Light, "dark": Qt.ColorScheme.Dark}.get(self.settings.theme, Qt.ColorScheme.Unknown)
        if hasattr(hints, "setColorScheme") and hints.colorScheme() != forced:
            self._applying_scheme = True
            hints.setColorScheme(forced)  # Unknown: işletim sisteminin şemasına dön
            self._applying_scheme = False
        self.color_scheme = effective_scheme(self.settings.theme, hints.colorScheme())
        colors = PALETTES[self.color_scheme]
        app.setPalette(qt_palette(colors))
        self.setStyleSheet(build_stylesheet(self.settings.font_scale, colors))

    def _on_system_scheme_changed(self, _scheme) -> None:
        # Yalnızca "Sistem" seçiliyken işletim sistemi teması değişince yeniden boya.
        if self.settings.theme == "system" and not getattr(self, "_applying_scheme", False):
            self.apply_appearance()

    def set_font_scale(self, scale: float) -> None:
        self.settings = replace(self.settings, font_scale=scale)
        self.apply_appearance()
        self._persist_settings()

    def change_font_scale(self, step: int) -> None:
        current = min(range(len(SCALE_STEPS)), key=lambda i: abs(SCALE_STEPS[i] - self.settings.font_scale))
        index = max(0, min(len(SCALE_STEPS) - 1, current + step))
        self.set_font_scale(SCALE_STEPS[index])

    def make_settings_dialog(self) -> SettingsDialog:
        return SettingsDialog(
            self.settings,
            self.model_path,
            self.store.directory if self.store is not None else None,
            len(self.store.list_ids()) if self.store is not None else 0,
            self,
        )

    def open_settings(self) -> None:
        if self.state in ("loading", "generating"):
            return
        dialog = self.make_settings_dialog()
        if dialog.exec():
            self.apply_settings_dialog(dialog)

    def apply_settings_dialog(self, dialog: SettingsDialog) -> None:
        new = dialog.result_settings()
        if dialog.delete_all_requested and self.store is not None:
            self.store.delete_all()
            self.new_conversation()
        self.settings = new
        self.apply_appearance()
        self._persist_settings()
        self.refresh_conversation_list()

    # ---- model yükleme ---------------------------------------------------
    def load_model(self, path: Path | str) -> None:
        self._set_state("loading")
        self.request_load.emit(Path(path))

    def _retry_load(self) -> None:
        if self.state in ("loading", "generating") or self._model_file is None:
            return
        self.load_model(self._model_file)

    def _on_load_started(self, path: str) -> None:
        self.hide_notice()
        self.status_label.setToolTip(path)

    def _on_load_succeeded(self, path: str) -> None:
        self.hide_notice()
        self.model_path = path
        self._set_state("ready", path)
        self.input.setFocus()

    def _on_load_failed(self, message: str, detail: str) -> None:
        self.model_path = None
        self._set_state("error", detail)
        self.show_notice(message + (f"\nAyrıntı: {detail}" if detail else ""))

    # ---- sohbet ----------------------------------------------------------
    def ask_example(self, question: str) -> None:
        self.input.setPlainText(question)
        self.send_message()

    def send_message(self) -> None:
        text = self.input.toPlainText().strip()
        if not text or self.state == "generating":
            return
        # Acil belirtiler modele gitmeden, model yüklü olmasa bile sabit kurallarla denetlenir.
        previous = " ".join(m["content"] for m in self.history if m["role"] == "user")[-1000:]
        detections = detect_emergency(text, context=previous)
        if detections:
            self.input.clear()
            self.add_message("user", text)
            self.add_message("emergency", emergency_message(detections))
            return
        # Doz soruları da modele gitmez; model yüklü olmasa bile sabit cevap verilir.
        if is_dose_request(text):
            self.input.clear()
            self.add_message("user", text)
            self.add_message("warning", DOSE_REFUSAL_MESSAGE)
            return
        if self.state == "loading":
            self.show_notice("Model henüz yükleniyor; lütfen yükleme bitince tekrar gönderin.")
            return
        if self.state != "ready":
            # Model yokken asla uydurma bir cevap üretilmez.
            self.show_notice(ModelNotLoadedError.user_message)
            return
        self.input.clear()
        self.add_message("user", text)
        self.history.append({"role": "user", "content": text})
        self._set_state("generating")
        self.request_generate.emit(list(self.history))

    def stop_generation(self) -> None:
        if self.state == "generating":
            self._worker.request_cancel()

    def _on_answer_started(self) -> None:
        self._set_status_text("generating")
        self._current_bubble = self.add_message("assistant", "")

    def _on_off_topic(self, message: str) -> None:
        # Konu dışı soru, sonraki isteklerde modele bağlam olarak gönderilmez.
        if self.history and self.history[-1]["role"] == "user":
            self.history.pop()
        self.add_message("warning", message)
        self._set_state("ready")
        self.input.setFocus()

    def _on_token(self, text: str) -> None:
        if self._current_bubble is not None:
            self._current_bubble.append(text)

    def _on_generation_finished(self, text: str, cancelled: bool) -> None:
        text = clean_answer(text)  # geçmişe ve kayda düzeltilmiş, dozu maskelenmiş metin girer
        bubble, self._current_bubble = self._current_bubble, None
        if bubble is None and cancelled:
            self.add_message("system", "Durduruldu.")
        if bubble is not None and cancelled:
            bubble.append(" … *(durduruldu)*")
        if bubble is not None and not text.strip() and not cancelled:
            bubble.append("*(Model boş bir cevap döndürdü.)*")
        if text.strip():
            self.history.append({"role": "assistant", "content": text})
        else:
            # Cevapsız kalan kullanıcı mesajı bir sonraki istekte iki kez gönderilmesin.
            self.history.pop()
        self._save_history()
        self._set_state("ready")
        self.input.setFocus()

    def _on_generation_failed(self, message: str, detail: str) -> None:
        bubble, self._current_bubble = self._current_bubble, None
        if bubble is not None and not bubble.text():
            bubble.deleteLater()
        if self.history and self.history[-1]["role"] == "user":
            self.history.pop()
        self.add_message("error", message + (f"\n\nAyrıntı: {detail}" if detail else ""))
        self._set_state("ready")

    def _save_history(self) -> None:
        if self.store is None or not self.history or not self.settings.save_history:
            return
        try:
            self.store.save(self.conversation_id, self.history)
        except OSError as exc:
            self.add_message("error", f"Konuşma geçmişi kaydedilemedi: {exc}")
            return
        self.refresh_conversation_list()

    # ---- kapanış ---------------------------------------------------------
    def closeEvent(self, event) -> None:
        self._worker.request_cancel()
        self._thread.quit()
        # Süren bir üretim bir sonraki token'da durur; yükleme ise bitene kadar beklenir.
        self._thread.wait()
        self._model.unload()  # iş parçacığı durduğu için burada güvenle çağrılabilir
        super().closeEvent(event)
