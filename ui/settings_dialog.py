"""Kullanıcının değiştirebileceği ayarlar.

Konu denetimi ve üretim parametreleri bilinçli olarak burada yer almaz; bunlar güvenlik ve
kalite ayarlarıdır ve config/ altında yönetilir.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from config.settings import ModelSettings
from ui.style import FONT_SCALES
from ui.theme import THEME_CHOICES


def nearest_scale_name(scale: float) -> str:
    return min(FONT_SCALES, key=lambda name: abs(FONT_SCALES[name] - scale))


class SettingsDialog(QDialog):
    def __init__(
        self,
        settings: ModelSettings,
        model_path: str | None,
        data_dir: Path | None,
        conversation_count: int,
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Ayarlar")
        self.setMinimumWidth(460)
        self._settings = settings
        self.delete_all_requested = False

        form = QFormLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(list(THEME_CHOICES))
        self.theme_combo.setCurrentText(next((k for k, v in THEME_CHOICES.items() if v == settings.theme), "Sistem"))
        self.theme_combo.setAccessibleName("Tema")
        self.theme_combo.setToolTip("Sistem: Windows'un açık/koyu ayarını izler")
        form.addRow("Tema:", self.theme_combo)

        self.font_combo = QComboBox()
        self.font_combo.addItems(list(FONT_SCALES))
        self.font_combo.setCurrentText(nearest_scale_name(settings.font_scale))
        self.font_combo.setAccessibleName("Metin boyutu")
        form.addRow("Metin boyutu:", self.font_combo)

        self.history_check = QCheckBox("Sohbetleri bu bilgisayara kaydet")
        self.history_check.setChecked(settings.save_history)
        form.addRow("Geçmiş:", self.history_check)

        self.delete_all_button = QPushButton(f"Kayıtlı tüm sohbetleri sil ({conversation_count})")
        self.delete_all_button.setObjectName("dangerButton")
        self.delete_all_button.setEnabled(conversation_count > 0)
        self.delete_all_button.clicked.connect(self._on_delete_all)
        form.addRow("", self.delete_all_button)

        model_label = QLabel(Path(model_path).name if model_path else "Yüklü model yok")
        model_label.setToolTip(model_path or "")
        model_label.setWordWrap(True)
        form.addRow("Model:", model_label)
        if data_dir is not None:
            data_label = QLabel(str(data_dir))
            data_label.setWordWrap(True)
            form.addRow("Veri klasörü:", data_label)

        note = QLabel(
            "Tüm veriler yalnızca bu bilgisayarda tutulur. Uygulama internete veri göndermez."
        )
        note.setWordWrap(True)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("Kaydet")
        buttons.button(QDialogButtonBox.Cancel).setText("Vazgeç")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(note)
        layout.addWidget(buttons)

    def confirm(self, title: str, text: str) -> bool:
        return QMessageBox.question(self, title, text) == QMessageBox.Yes

    def _on_delete_all(self) -> None:
        if self.confirm("Tüm sohbetleri sil", "Kayıtlı tüm sohbetler kalıcı olarak silinsin mi?"):
            self.delete_all_requested = True
            self.delete_all_button.setEnabled(False)
            self.delete_all_button.setText("Kaydettiğinizde tüm sohbetler silinecek")

    def result_settings(self) -> ModelSettings:
        return replace(
            self._settings,
            font_scale=FONT_SCALES[self.font_combo.currentText()],
            theme=THEME_CHOICES[self.theme_combo.currentText()],
            save_history=self.history_check.isChecked(),
        )
