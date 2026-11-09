"""Uygulama genel görünümü. Renkler ui/theme.py'deki token'lardan gelir (WCAG AA kontrastı testle denetlenir)."""

from ui.theme import LIGHT

FONT_SCALES = {"Küçük": 0.9, "Normal": 1.0, "Büyük": 1.15, "Çok büyük": 1.3}

_STYLESHEET = """
QMainWindow, QWidget#root, QDialog, QMessageBox {{ background: {bg}; }}
QLabel, QCheckBox, QRadioButton {{ color: {text}; }}
QToolTip {{ background: {surface}; color: {text}; border: 1px solid {border}; }}

QFrame#header {{ background: {surface}; border-bottom: 1px solid {border}; }}
QLabel#appTitle {{ font-size: {title_px}px; font-weight: 600; color: {title}; }}
QLabel#appSubtitle {{ font-size: {small}px; color: {muted}; }}

QLabel#statusLabel {{ font-size: {body_s}px; color: {text}; }}
QLabel#statusDot {{ min-width: 12px; max-width: 12px; min-height: 12px; max-height: 12px;
                   border-radius: 6px; }}
QLabel#statusDot[state="not_loaded"] {{ background: #9A9A9A; }}
QLabel#statusDot[state="loading"]    {{ background: #C77700; }}
QLabel#statusDot[state="ready"]      {{ background: #2E7D32; }}
QLabel#statusDot[state="generating"] {{ background: #1565C0; }}
QLabel#statusDot[state="error"]      {{ background: #C62828; }}

QFrame#sidebar {{ background: {sidebar}; }}
QSplitter::handle {{ background: {splitter}; }}
QSplitter::handle:horizontal {{ width: 2px; }}
QSplitter::handle:hover {{ background: {splitter_hover}; }}
QLabel#sidebarTitle {{ font-size: {small}px; font-weight: 600; color: {muted}; }}
QLabel#sidebarNote {{ font-size: {small}px; color: {muted}; }}
QListWidget#conversationList {{ background: transparent; border: none; font-size: {body_s}px; outline: none; }}
QListWidget#conversationList::item {{ padding: 8px 6px; border-radius: 6px; color: {text}; }}
QListWidget#conversationList::item:selected {{ background: {selection}; color: {text}; }}
QListWidget#conversationList::item:hover {{ background: {hover}; }}

QFrame#disclaimer {{ background: {warn_bg}; border: 1px solid {warn_border}; border-radius: 8px; }}
QLabel#disclaimerText {{ color: {warn_text}; font-size: {small}px; }}
QFrame#notice {{ background: {error_bg}; border: 1px solid {error_border}; border-radius: 8px; }}
QLabel#noticeText {{ color: {error_text}; font-size: {body_s}px; }}

QScrollArea#messages {{ border: none; background: transparent; }}
QWidget#messagesInner, QWidget#welcome {{ background: transparent; }}
QLabel#welcomeTitle {{ font-size: {welcome}px; font-weight: 600; color: {title}; }}
QLabel#welcomeText {{ font-size: {body}px; color: {muted}; }}
QPushButton#exampleButton {{ background: {surface}; color: {text}; border: 1px solid {input_border};
                            border-radius: 10px; padding: 10px 14px; font-size: {body_s}px; text-align: left; }}
QPushButton#exampleButton:hover {{ border-color: {title}; background: {hover}; }}

QFrame[role="user"]      {{ background: {user_bg}; border-radius: 12px; }}
QFrame[role="user"] QLabel {{ color: {user_text}; }}
QFrame[role="assistant"] {{ background: {assistant_bg}; border: 1px solid {border}; border-radius: 12px; }}
QFrame[role="assistant"] QLabel {{ color: {assistant_text}; }}
QFrame[role="system"]    {{ background: {system_bg}; border-radius: 8px; }}
QFrame[role="system"] QLabel {{ color: {system_text}; }}
QFrame[role="error"]     {{ background: {error_bg}; border: 1px solid {error_border}; border-radius: 8px; }}
QFrame[role="error"] QLabel {{ color: {error_text}; }}
QFrame[role="warning"]   {{ background: {warn_bg}; border: 1px solid {warn_border}; border-radius: 8px; }}
QFrame[role="warning"] QLabel {{ color: {warn_text}; }}
QFrame[role="emergency"] {{ background: {emergency_bg}; border: 2px solid {emergency_border}; border-radius: 8px; }}
QFrame[role="emergency"] QLabel {{ color: {emergency_text}; font-weight: 600; }}
QLabel#bubbleText {{ font-size: {body}px; }}

QPlainTextEdit#input {{ background: {surface}; border: 1px solid {input_border}; border-radius: 10px;
                       padding: 8px; font-size: {body}px; color: {text}; }}
QPlainTextEdit#input:focus {{ border: 2px solid {title}; }}

QComboBox {{ background: {surface}; color: {text}; border: 1px solid {input_border}; border-radius: 6px;
            padding: 4px 8px; }}
QComboBox QAbstractItemView {{ background: {surface}; color: {text}; selection-background-color: {selection};
                              selection-color: {text}; border: 1px solid {border}; }}

QPushButton {{ border-radius: 8px; padding: 8px 16px; font-size: {body_s}px; background: {surface};
              color: {text}; border: 1px solid {input_border}; }}
QPushButton:hover {{ background: {hover}; }}
QPushButton:disabled {{ color: {disabled_text}; }}
QPushButton#sendButton {{ background: {accent}; color: {accent_text}; font-weight: 600; border: none; }}
QPushButton#sendButton:disabled {{ background: {accent_disabled}; color: {accent_text}; }}
QPushButton#secondaryButton {{ background: {surface}; color: {title}; border: 1px solid {title}; }}
QPushButton#secondaryButton:hover {{ background: {hover}; }}
QPushButton#secondaryButton:disabled {{ color: {disabled_text}; border-color: {border}; }}
QPushButton#dangerButton {{ background: {surface}; color: {danger}; border: 1px solid {danger}; }}
QPushButton#dangerButton:disabled {{ color: {disabled_text}; border-color: {border}; }}
QPushButton:focus {{ outline: none; border: 2px solid {focus}; }}
"""


def build_stylesheet(scale: float = 1.0, colors: dict[str, str] = LIGHT) -> str:
    def px(size: float) -> int:
        return round(size * scale)

    return _STYLESHEET.format(
        title_px=px(22), welcome=px(20), body=px(14), body_s=px(13), small=px(12), **colors
    )
