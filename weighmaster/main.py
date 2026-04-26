"""WeighMaster Pro — entry point."""
import os
import sys
import logging
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase, QFont
from PyQt6.QtCore import Qt

from weighmaster.config import (
    APP_NAME, DATA_DIR, PDF_OUTPUT_DIR, LOG_FILE, LOG_LEVEL, SCALE_SIMULATOR
)


def setup_logging() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL, logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def load_fonts(app: QApplication) -> None:
    from weighmaster.utils.resource_path import resource_path
    fonts_dir = resource_path("weighmaster", "assets", "fonts")
    if fonts_dir.exists():
        for font_file in fonts_dir.glob("*.ttf"):
            QFontDatabase.addApplicationFont(str(font_file))
    app.setFont(QFont("DM Sans", 12))


def bootstrap() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PDF_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    from weighmaster.database.connection import init_db
    init_db()

    from weighmaster.database.connection import get_session
    from weighmaster.database.models import Company
    with get_session() as session:
        company = session.query(Company).first()

    return company


def main() -> None:
    setup_logging()
    log = logging.getLogger(__name__)
    log.info("Starting %s", APP_NAME)

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion("1.0.0")
    # AA_UseHighDpiPixmaps is removed in PyQt6 / Qt6 (enabled by default)
    if hasattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'):
        app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    load_fonts(app)

    from weighmaster.ui.theme import STYLESHEET
    app.setStyleSheet(STYLESHEET)

    company = bootstrap()

    if company is None:
        from weighmaster.ui.windows.setup_wizard import SetupWizard
        wizard = SetupWizard()
        if wizard.exec() != wizard.DialogCode.Accepted:
            sys.exit(0)
        company = bootstrap()

    from weighmaster.ui.windows.login_window import LoginWindow
    login = LoginWindow()
    if login.exec() != login.DialogCode.Accepted:
        sys.exit(0)

    user = login.authenticated_user

    from weighmaster.ui.windows.main_window import MainWindow
    window = MainWindow(user=user)
    window.show()

    if SCALE_SIMULATOR:
        log.info("Scale simulator mode active")
        from weighmaster.hardware.simulator import ScaleSimulator
        scale = ScaleSimulator()
    else:
        from weighmaster.hardware.scale_reader import ScaleReader
        from weighmaster.database.connection import get_session
        from weighmaster.database.models import Company
        # COM_PORT env var overrides the database setting (useful for one-off tests)
        port_override = os.getenv("COM_PORT", "")
        with get_session() as session:
            co = session.query(Company).first()
            scale = ScaleReader(
                port=port_override or (co.com_port if co else "COM3") or "COM3",
                baud_rate=(co.baud_rate if co else 9600) or 9600,
                data_bits=(co.data_bits if co else 8) or 8,
                parity=(co.parity if co else "E") or "E",
                stop_bits=(co.stop_bits if co else 1) or 1,
                protocol=(co.scale_protocol if co else "xk3190") or "xk3190",
            )

    scale.weight_updated.connect(window.on_weight_updated)
    scale.connection_ok.connect(window.on_scale_connected)
    scale.connection_lost.connect(window.on_scale_disconnected)
    scale.start()

    window._scale_thread = scale

    exit_code = app.exec()
    scale.stop()
    log.info("Application exiting with code %d", exit_code)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
