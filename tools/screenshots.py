"""README'deki ekran görüntülerini gerçek uygulama ve gerçek modelle yeniden üretir.

Pencere ekranda gösterilmeden çizilir; kullanıcının sohbet geçmişine dokunmamak için geçici bir veri
klasörü kullanılır. Cevaplar düzenlenmez: görüntüde ne varsa modelin o anda ürettiği cevaptır.

Kullanım (Windows):
    python tools/screenshots.py            # docs/ekran-goruntuleri/ altına yazar
"""

from __future__ import annotations

import os
import sys
import tempfile
import time
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
OUT = ROOT / "docs" / "ekran-goruntuleri"

# Ekran ölçeğinden bağımsız, her bilgisayarda aynı boyutta görüntü (1770×1170).
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
os.environ["QT_SCALE_FACTOR"] = "1.5"

SHOTS = [
    # (dosya, tema, sorular) — soru yoksa karşılama ekranı çekilir
    ("1_karsilama.png", "light", []),
    ("2_cevap.png", "light", ["Bebeğim 5 aylık. Ek gıdaya başlayabilir miyim?"]),
    ("3_acil_durum.png", "dark", ["Hamileyim, 30 haftalığım. Başım çok ağrıyor ve bulanık görüyorum."]),
    ("4_doz_ve_konu_disi.png", "dark", ["Bebeğime kaç ml ateş düşürücü şurup vermeliyim?",
                                        "Python'da bir listeyi nasıl sıralarım?"]),
]


def main() -> int:
    data_dir = Path(tempfile.mkdtemp(prefix="ilk-goz-agrim-goruntu-"))
    os.environ["ILK_GOZ_AGRIM_DATA_DIR"] = str(data_dir)

    from PySide6.QtCore import Qt
    from PySide6.QtGui import QFont
    from PySide6.QtWidgets import QApplication

    from config.settings import APP_NAME, ModelSettings, model_file
    from inference.engine import LocalModel
    from storage.history import ConversationStore
    from ui.main_window import MainWindow

    app = QApplication([sys.argv[0]])
    app.setApplicationName(APP_NAME)
    app.setFont(QFont("Segoe UI", 10))
    app.setStyle("Fusion")
    window = MainWindow(
        settings=ModelSettings(theme="light"),
        model=LocalModel(),
        initial_model_path=model_file(),
        store=ConversationStore(data_dir / "history"),
        settings_path=data_dir / "settings.json",
    )
    window.setAttribute(Qt.WA_DontShowOnScreen, True)
    window.resize(1180, 780)
    window.show()

    def settle(rounds: int = 15) -> None:
        for _ in range(rounds):
            app.processEvents()
            time.sleep(0.02)

    def wait_ready(timeout_s: float = 600) -> None:
        deadline = time.monotonic() + timeout_s
        while window.state != "ready":
            if window.state == "error" or time.monotonic() > deadline:
                raise RuntimeError(f"Model hazır değil: {window.notice_label.text() or window.state}")
            settle(1)
        settle()

    wait_ready()
    OUT.mkdir(parents=True, exist_ok=True)
    for name, theme, questions in SHOTS:
        window.new_conversation()
        window.settings = replace(window.settings, theme=theme)
        window.apply_appearance()
        for question in questions:
            window.input.setPlainText(question)
            window.send_message()
            settle()
            wait_ready()
        settle()
        window.grab().save(str(OUT / name))
        print(f"{name}: {' / '.join(questions) or 'karşılama ekranı'}")
    window.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
