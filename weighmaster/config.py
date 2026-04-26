from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

APP_NAME = "WeighMaster Pro"
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

TICKET_PREFIX = "WM"
TICKET_ZERO_PAD = 4

DEFAULT_BAUD_RATE = 9600
STABLE_THRESHOLD_KG = 0.5
STABLE_DURATION_SEC = 2.0
SCALE_READ_TIMEOUT = 2.0
MAX_WEIGHT_KG = 80_000.0
OVERLOAD_KG = 80_900.0

# Multi-deck / multi-axle defaults
MAX_AXLES = 8
DEFAULT_AXLE_COUNT = 1

SESSION_TIMEOUT_MIN = 60
LOGIN_LOCKOUT_ATTEMPTS = 5
LOGIN_LOCKOUT_SEC = 30

WINDOW_MIN_WIDTH = 1024
WINDOW_MIN_HEIGHT = 680
TABLE_PAGE_SIZE = 50

DATA_DIR = Path(os.getenv("DB_PATH", "./data/weighmaster.db")).parent
DB_PATH = Path(os.getenv("DB_PATH", "./data/weighmaster.db"))
PDF_OUTPUT_DIR = DATA_DIR / "certificates"
LOG_FILE = DATA_DIR / "weighmaster.log"

SCALE_SIMULATOR = os.getenv("SCALE_SIMULATOR", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
