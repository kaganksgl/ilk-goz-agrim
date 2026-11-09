"""Sohbet ekranında kullanılan küçük bileşenler."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QFrame, QLabel, QPlainTextEdit, QSizePolicy, QVBoxLayout

from inference.text_fixes import clean_answer

ACCESSIBLE_ROLE_NAMES = {
    "user": "Sizin mesajınız",
    "assistant": "Asistan cevabı",
    "warning": "Konu uyarısı",
    "error": "Hata",
    "emergency": "Acil durum uyarısı",
}


def safe_markdown(text: str) -> str:
    """Model çıktısını Markdown olarak gösterilebilir hale getirir.

    Qt'nin Markdown okuyucusu satır içi HTML'i yorumlar ve resim sözdizimiyle yerel dosya
    yükleyebilir. Model çıktısı güvenilir olmadığından HTML karakterleri kaçışlanır ve
    resimler sıradan metne çevrilir; kalın, liste, başlık gibi biçimler korunur.
    """
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return text.replace("![", "!\\[")


class ChatInput(QPlainTextEdit):
    """Enter gönderir, Shift+Enter yeni satır ekler."""

    submitted = Signal()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key_Return, Qt.Key_Enter) and not (event.modifiers() & Qt.ShiftModifier):
            self.submitted.emit()
            return
        super().keyPressEvent(event)


class MessageBubble(QFrame):
    def __init__(self, role: str, text: str = ""):
        super().__init__()
        self.role = role
        self._raw = ""
        self.setProperty("role", role)
        self.label = QLabel()
        self.label.setObjectName("bubbleText")
        # Yalnızca asistan cevapları biçimlendirilir; diğer her şey düz metindir.
        self.label.setTextFormat(Qt.MarkdownText if role == "assistant" else Qt.PlainText)
        self.label.setOpenExternalLinks(False)
        self.label.setWordWrap(True)
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        self.label.setAccessibleName(ACCESSIBLE_ROLE_NAMES.get(role, "Bilgi"))
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.addWidget(self.label)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.set_text(text)

    def text(self) -> str:
        """Ham metin (Markdown işaretleri dahil)."""
        return self._raw

    def displayed_text(self) -> str:
        return self.label.text()

    def set_text(self, text: str) -> None:
        self._raw = text
        # Asistan cevabındaki bilinen yazım hataları düzeltilir ve ilaç/takviye miktarları maskelenir; her
        # çizimde uygulandığı için akış sırasında da geçerlidir.
        self.label.setText(safe_markdown(clean_answer(text)) if self.role == "assistant" else text)

    def append(self, text: str) -> None:
        self.set_text(self._raw + text)
