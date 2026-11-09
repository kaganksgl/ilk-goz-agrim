"""Açık, koyu ve sistem temaları.

Tüm renkler burada token olarak tanımlanır; stil sayfası (ui/style.py) ve Qt paleti bu token'lardan
üretilir. Böylece ayarlar penceresi, açılır listeler ve mesaj kutuları gibi Qt'nin kendi çizdiği
parçalar da aynı temayı kullanır. (Önceki sürümde Windows koyu moddayken ayarlar penceresi koyu sistem
arka planını alıyor ama metinler koyu renge zorlanıyordu: siyah üstüne siyah.)
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette

THEME_CHOICES = {"Sistem": "system", "Açık": "light", "Koyu": "dark"}

LIGHT = {
    "bg": "#FBF7F5", "surface": "#FFFFFF", "sidebar": "#F4ECE8", "border": "#EADFDA", "input_border": "#D9CCC6",
    "text": "#2B2B2B", "muted": "#5C5C5C", "title": "#8A3B5C",
    "accent": "#8A3B5C", "accent_text": "#FFFFFF", "accent_disabled": "#CFB8C2", "disabled_text": "#8A8A8A",
    "selection": "#E4D3DA", "hover": "#EDE0E5", "focus": "#1565C0", "danger": "#A12020",
    "user_bg": "#8A3B5C", "user_text": "#FFFFFF",
    "assistant_bg": "#FFFFFF", "assistant_text": "#2B2B2B",
    "system_bg": "#EEF2F7", "system_text": "#33475B",
    "error_bg": "#FDECEC", "error_border": "#E6A1A1", "error_text": "#8E1B1B",
    "warn_bg": "#FFF4E5", "warn_border": "#F0C27A", "warn_text": "#5A3A00",
    "emergency_bg": "#B71C1C", "emergency_border": "#7F0000", "emergency_text": "#FFFFFF",
    "splitter": "#EADFDA", "splitter_hover": "#C9AEB9",
}

DARK = {
    "bg": "#1B1719", "surface": "#262124", "sidebar": "#211C1F", "border": "#3A3236", "input_border": "#4D4348",
    "text": "#ECE6E8", "muted": "#B9AFB4", "title": "#E39BBB",
    "accent": "#9C4469", "accent_text": "#FFFFFF", "accent_disabled": "#4F3843", "disabled_text": "#8C8186",
    "selection": "#4A3440", "hover": "#3A2C33", "focus": "#64B5F6", "danger": "#F28B8B",
    "user_bg": "#7A3352", "user_text": "#FFFFFF",
    "assistant_bg": "#262124", "assistant_text": "#ECE6E8",
    "system_bg": "#22303C", "system_text": "#C9D6E3",
    "error_bg": "#3B1D1F", "error_border": "#7A3A3D", "error_text": "#F6BDBD",
    "warn_bg": "#3A2E17", "warn_border": "#7A5F2A", "warn_text": "#F3D9A4",
    "emergency_bg": "#B71C1C", "emergency_border": "#FF8A80", "emergency_text": "#FFFFFF",
    "splitter": "#3A3236", "splitter_hover": "#6B5560",
}

PALETTES = {"light": LIGHT, "dark": DARK}


def effective_scheme(choice: str, system_scheme: Qt.ColorScheme) -> str:
    """'system' seçiliyse işletim sisteminin şemasını, değilse seçilen şemayı döndürür."""
    if choice in PALETTES:
        return choice
    return "dark" if system_scheme == Qt.ColorScheme.Dark else "light"


def qt_palette(colors: dict[str, str]) -> QPalette:
    pal = QPalette()
    roles = {
        QPalette.Window: "bg", QPalette.WindowText: "text", QPalette.Base: "surface",
        QPalette.AlternateBase: "sidebar", QPalette.Text: "text", QPalette.Button: "surface",
        QPalette.ButtonText: "text", QPalette.ToolTipBase: "surface", QPalette.ToolTipText: "text",
        QPalette.PlaceholderText: "muted", QPalette.Highlight: "selection", QPalette.HighlightedText: "text",
        QPalette.Link: "focus",
    }
    for role, token in roles.items():
        pal.setColor(role, QColor(colors[token]))
    for role in (QPalette.WindowText, QPalette.Text, QPalette.ButtonText):
        pal.setColor(QPalette.Disabled, role, QColor(colors["disabled_text"]))
    return pal


def contrast_ratio(foreground: str, background: str) -> float:
    """WCAG 2 kontrast oranı."""

    def luminance(hex_color: str) -> float:
        rgb = [int(hex_color[i : i + 2], 16) / 255 for i in (1, 3, 5)]
        lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
        return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]

    hi, lo = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


# Kontrastı denetlenen metin/arka plan çiftleri (testler bu listeyi kullanır).
TEXT_PAIRS = [
    ("text", "bg"), ("text", "surface"), ("text", "sidebar"), ("muted", "bg"), ("muted", "sidebar"),
    ("muted", "surface"), ("title", "bg"), ("title", "surface"), ("accent_text", "accent"),
    ("user_text", "user_bg"), ("assistant_text", "assistant_bg"), ("system_text", "system_bg"),
    ("error_text", "error_bg"), ("warn_text", "warn_bg"), ("emergency_text", "emergency_bg"),
    ("text", "selection"), ("danger", "surface"),
]
# Metin olmayan arayüz parçaları (odak ve vurgu kenarlıkları) için WCAG en az 3:1 ister.
UI_PAIRS = [("title", "surface"), ("title", "bg"), ("focus", "surface"), ("focus", "bg")]
