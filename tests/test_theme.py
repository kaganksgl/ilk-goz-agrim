import re

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication, QCheckBox, QLabel

from config.settings import ModelSettings, load_settings
from inference.engine import LocalModel
from storage.history import ConversationStore
from tests.conftest import FakeLlama
from ui.main_window import MainWindow
from ui.style import build_stylesheet
from ui.theme import DARK, LIGHT, PALETTES, TEXT_PAIRS, UI_PAIRS, contrast_ratio, effective_scheme, qt_palette


@pytest.mark.parametrize("name", ["light", "dark"])
def test_theme_text_contrast_meets_wcag_aa(name):
    colors = PALETTES[name]
    low = [(f, b, round(contrast_ratio(colors[f], colors[b]), 2)) for f, b in TEXT_PAIRS if contrast_ratio(colors[f], colors[b]) < 4.5]
    assert low == []


@pytest.mark.parametrize("name", ["light", "dark"])
def test_theme_borders_meet_non_text_contrast(name):
    colors = PALETTES[name]
    assert all(contrast_ratio(colors[f], colors[b]) >= 3.0 for f, b in UI_PAIRS)


def test_themes_define_the_same_tokens():
    assert set(LIGHT) == set(DARK)


@pytest.mark.parametrize("colors", [LIGHT, DARK])
def test_stylesheet_has_no_unfilled_placeholders(colors):
    sheet = build_stylesheet(1.0, colors)
    assert not re.search(r"\{[a-z_]+\}", sheet)
    assert colors["bg"] in sheet and colors["text"] in sheet


def test_effective_scheme():
    assert effective_scheme("light", Qt.ColorScheme.Dark) == "light"
    assert effective_scheme("dark", Qt.ColorScheme.Light) == "dark"
    assert effective_scheme("system", Qt.ColorScheme.Dark) == "dark"
    assert effective_scheme("system", Qt.ColorScheme.Light) == "light"
    assert effective_scheme("system", Qt.ColorScheme.Unknown) == "light"


def make_window(qtbot, tmp_path, theme="system"):
    w = MainWindow(
        settings=ModelSettings(theme=theme),
        model=LocalModel(lambda p, s: FakeLlama()),
        initial_model_path=None,
        store=ConversationStore(tmp_path / "history"),
        settings_path=tmp_path / "settings.json",
    )
    qtbot.addWidget(w)
    return w


def _readable(widget) -> float:
    widget.ensurePolished()
    fg = widget.palette().color(QPalette.WindowText if isinstance(widget, QLabel) else QPalette.ButtonText)
    return fg


@pytest.mark.parametrize("theme", ["light", "dark", "system"])
def test_settings_dialog_text_is_readable_on_dark_system(qtbot, tmp_path, theme):
    """Hata: Windows koyu moddayken ayarlar penceresinde metinler siyah arka planda siyah kalıyordu."""
    app = QApplication.instance()
    original = app.palette()
    app.setPalette(qt_palette({**DARK}))  # işletim sisteminin koyu paletini taklit et
    try:
        w = make_window(qtbot, tmp_path, theme)
        dialog = w.make_settings_dialog()
        qtbot.addWidget(dialog)
        dialog.show()
        dialog.ensurePolished()
        background = dialog.palette().color(QPalette.Window).name()
        texts = dialog.findChildren(QLabel) + dialog.findChildren(QCheckBox)
        assert texts
        for widget in texts:
            widget.ensurePolished()
            role = QPalette.WindowText
            fg = widget.palette().color(role).name()
            assert contrast_ratio(fg, background) >= 4.5, (theme, widget.text(), fg, background)
        dialog.close()
        w.close()
    finally:
        app.setPalette(original)


def test_choosing_dark_theme_applies_and_persists(qtbot, tmp_path):
    w = make_window(qtbot, tmp_path, "light")
    assert w.color_scheme == "light" and LIGHT["bg"] in w.styleSheet()
    dialog = w.make_settings_dialog()
    qtbot.addWidget(dialog)
    dialog.theme_combo.setCurrentText("Koyu")
    w.apply_settings_dialog(dialog)
    assert w.color_scheme == "dark"
    assert DARK["bg"] in w.styleSheet() and LIGHT["bg"] not in w.styleSheet()
    assert QApplication.instance().palette().color(QPalette.Window) == QColor(DARK["bg"])
    assert load_settings(tmp_path / "settings.json").theme == "dark"

    dialog = w.make_settings_dialog()
    qtbot.addWidget(dialog)
    assert dialog.theme_combo.currentText() == "Koyu"
    dialog.theme_combo.setCurrentText("Açık")
    w.apply_settings_dialog(dialog)
    assert w.color_scheme == "light"
    w.close()


def test_font_scale_keeps_theme(qtbot, tmp_path):
    w = make_window(qtbot, tmp_path, "dark")
    w.change_font_scale(+1)
    assert DARK["bg"] in w.styleSheet() and "font-size: 16px" in w.styleSheet()
    w.close()
