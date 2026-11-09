"""İlk Göz Ağrım – masaüstü uygulamasının giriş noktası."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from config.settings import APP_ID, APP_NAME, app_data_dir, load_settings, resolve_model_path, settings_file
from inference.engine import LocalModel
from storage.history import ConversationStore
from ui.main_window import MainWindow


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=APP_NAME)
    parser.add_argument("--model", type=Path, help="Kullanılacak .gguf model dosyası")
    args, qt_args = parser.parse_known_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    app = QApplication([sys.argv[0], *qt_args])
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(APP_ID)
    app.setFont(QFont("Segoe UI", 10))
    # Fusion, uygulamanın renk paletini her parçada tutarlı uygular (Windows 11 stili bazılarını yok sayar).
    app.setStyle("Fusion")

    settings = load_settings()
    model_path = args.model or resolve_model_path(settings)
    window = MainWindow(
        settings=settings,
        model=LocalModel(),
        initial_model_path=model_path,
        store=ConversationStore(app_data_dir() / "history"),
        settings_path=settings_file(),
    )
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
