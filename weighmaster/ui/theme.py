"""Master QSS stylesheet — cargo-dashboard inspired design."""

# ─── Colour tokens ────────────────────────────────────────────────────────────
BG_PAGE       = "#F1F3F6"
BG_SIDEBAR    = "#FFFFFF"
BG_CARD       = "#FFFFFF"
BG_INPUT      = "#F8FAFC"
BG_TABLE_ALT  = "#F8FAFC"
BG_HOVER      = "#F1F5F9"
BG_TOPNAV     = "#FFFFFF"

BRAND         = "#4F46E5"   # Indigo
BRAND_DARK    = "#3730A3"
BRAND_LIGHT   = "#EEF2FF"
BRAND_MID     = "#6366F1"

TEAL          = "#0D9488"
TEAL_LIGHT    = "#CCFBF1"

GREEN         = "#16A34A"
GREEN_LIGHT   = "#DCFCE7"
GREEN_TEXT    = "#14532D"
GREEN_PILL    = "#22C55E"

AMBER         = "#D97706"
AMBER_LIGHT   = "#FEF3C7"
AMBER_TEXT    = "#78350F"
AMBER_PILL    = "#F59E0B"

RED           = "#DC2626"
RED_LIGHT     = "#FEE2E2"
RED_DARK      = "#991B1B"
RED_PILL      = "#EF4444"

PURPLE        = "#7C3AED"
PURPLE_LIGHT  = "#EDE9FE"
PURPLE_TEXT   = "#4C1D95"

BLUE          = "#2563EB"
BLUE_LIGHT    = "#DBEAFE"

TEXT_PRIMARY  = "#0F172A"
TEXT_BODY     = "#1E293B"
TEXT_SECONDARY= "#475569"
TEXT_MUTED    = "#94A3B8"
TEXT_DISABLED = "#CBD5E1"

BORDER        = "#E2E8F0"
BORDER_MEDIUM = "#CBD5E1"
BORDER_FOCUS  = "#4F46E5"

SHADOW        = "rgba(15, 23, 42, 0.04)"
SHADOW_CARD   = "rgba(15, 23, 42, 0.06)"

# ─── Master stylesheet ────────────────────────────────────────────────────────
STYLESHEET = f"""

/* ── Global ── */
QMainWindow, QDialog, QWidget {{
    background-color: {BG_PAGE};
    color: {TEXT_BODY};
    font-family: "Inter", "DM Sans", "Segoe UI", sans-serif;
    font-size: 13px;
}}

QLabel {{
    color: {TEXT_BODY};
    background: transparent;
}}

/* ── Top navigation bar ── */
QWidget#TopNavBar {{
    background-color: {BG_TOPNAV};
    border-bottom: 1px solid {BORDER};
    min-height: 52px;
    max-height: 52px;
}}

QLabel#TopNavAppName {{
    font-size: 14px;
    font-weight: 700;
    color: {TEXT_PRIMARY};
    background: transparent;
    font-family: "Inter", "DM Sans", sans-serif;
}}

QLabel#TopNavLogo {{
    font-size: 20px;
    color: {BRAND};
    background: transparent;
}}

QLabel#TopNavDivider {{
    color: {BORDER};
    background: {BORDER};
    max-width: 1px;
    min-width: 1px;
    min-height: 22px;
    max-height: 22px;
}}

QLabel#TopNavScaleOnline {{
    font-size: 11px;
    color: {GREEN};
    background: transparent;
    font-weight: 600;
}}

QLabel#TopNavScaleOffline {{
    font-size: 11px;
    color: {RED};
    background: transparent;
    font-weight: 600;
}}

QLabel#TopNavUser {{
    font-size: 12px;
    color: {TEXT_SECONDARY};
    background: transparent;
    font-weight: 500;
}}

QLabel#TopNavClock {{
    font-family: "JetBrains Mono", "Courier New", monospace;
    font-size: 11px;
    color: {TEXT_MUTED};
    background: transparent;
}}

QWidget#TopNavUserPill {{
    background-color: {BG_HOVER};
    border-radius: 8px;
    border: 1px solid {BORDER};
}}

/* ── Sidebar ── */
QWidget#Sidebar {{
    background-color: {BG_SIDEBAR};
    border-right: 1px solid {BORDER};
}}

QPushButton#NavItem {{
    background: transparent;
    border: none;
    border-radius: 8px;
    color: {TEXT_SECONDARY};
    font-size: 12px;
    font-weight: 500;
    font-family: "Inter", "DM Sans", "Segoe UI", sans-serif;
    text-align: left;
    padding: 9px 12px;
    min-height: 36px;
    margin: 1px 8px;
}}

QPushButton#NavItem:hover {{
    background-color: {BG_HOVER};
    color: {TEXT_PRIMARY};
}}

QPushButton#NavItem:checked {{
    background-color: {BRAND_LIGHT};
    color: {BRAND};
    font-weight: 600;
}}

QPushButton#NavIcon {{
    background: transparent;
    border: none;
    border-radius: 8px;
    color: {TEXT_MUTED};
    font-size: 16px;
    padding: 8px;
    min-width: 36px;
    min-height: 36px;
    max-width: 36px;
    max-height: 36px;
}}

QPushButton#NavIcon:hover {{
    background-color: {BG_HOVER};
    color: {TEXT_PRIMARY};
}}

QPushButton#NavIcon:checked {{
    background-color: {BRAND_LIGHT};
    color: {BRAND};
}}

/* ── Cards ── */
QFrame#Card {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 12px;
}}

QFrame#CardHeader {{
    background-color: {BG_CARD};
    border-bottom: 1px solid {BORDER};
    border-radius: 0px;
    padding: 0px 20px;
    min-height: 48px;
    max-height: 48px;
}}

/* ── KPI Cards ── */
QFrame#KpiCard {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 16px;
}}

QLabel#KpiValue {{
    font-family: "Inter", "DM Sans", sans-serif;
    font-size: 24px;
    font-weight: 700;
    color: {TEXT_PRIMARY};
    background: transparent;
}}

QLabel#KpiLabel {{
    font-size: 11px;
    color: {TEXT_MUTED};
    background: transparent;
    font-weight: 500;
    letter-spacing: 0.2px;
}}

QLabel#KpiIcon {{
    font-size: 20px;
    background: transparent;
}}

QLabel#KpiTrend {{
    font-size: 11px;
    font-weight: 600;
    background: transparent;
}}

/* ── Weight display ── */
QLabel#WeightHero {{
    font-family: "JetBrains Mono", "Courier New", monospace;
    font-size: 52px;
    font-weight: 700;
    color: {AMBER};
    background: transparent;
    letter-spacing: -2px;
}}

QLabel#WeightHero[stable="true"] {{
    color: {GREEN};
}}

QLabel#WeightHero[stable="false"] {{
    color: {AMBER};
}}

QLabel#WeightHero[overload="true"] {{
    color: {RED};
}}

QLabel#WeightUnit {{
    font-family: "JetBrains Mono", "Courier New", monospace;
    font-size: 16px;
    color: {TEXT_MUTED};
    background: transparent;
}}

QLabel#SubWeight {{
    font-family: "JetBrains Mono", "Courier New", monospace;
    font-size: 13px;
    color: {TEXT_BODY};
    background: transparent;
}}

/* ── Status chips / Pills ── */
QLabel#ChipStable {{
    background-color: {GREEN_LIGHT};
    color: {GREEN_TEXT};
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 10px;
    font-weight: 700;
    font-family: "Inter", "DM Sans", sans-serif;
    letter-spacing: 0.3px;
}}

QLabel#ChipUnstable {{
    background-color: {AMBER_LIGHT};
    color: {AMBER_TEXT};
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 10px;
    font-weight: 700;
    font-family: "Inter", "DM Sans", sans-serif;
    letter-spacing: 0.3px;
}}

QLabel#ChipOverload {{
    background-color: {RED_LIGHT};
    color: {RED_DARK};
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 10px;
    font-weight: 700;
    font-family: "Inter", "DM Sans", sans-serif;
    letter-spacing: 0.3px;
}}

QLabel#ChipComplete {{
    background-color: {GREEN_LIGHT};
    color: {GREEN_TEXT};
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.3px;
}}

QLabel#ChipVoid {{
    background-color: {RED_LIGHT};
    color: {RED_DARK};
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.3px;
}}

QLabel#ChipPending {{
    background-color: {AMBER_LIGHT};
    color: {AMBER_TEXT};
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.3px;
}}

/* ── Status Pills (bright, cargo-style) ── */
QLabel#PillGreen {{
    background-color: {GREEN_PILL};
    color: white;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.5px;
}}

QLabel#PillPurple {{
    background-color: {PURPLE};
    color: white;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.5px;
}}

QLabel#PillYellow {{
    background-color: {AMBER_PILL};
    color: white;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.5px;
}}

QLabel#PillRed {{
    background-color: {RED_PILL};
    color: white;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.5px;
}}

QLabel#PillBlue {{
    background-color: {BLUE};
    color: white;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.5px;
}}

QLabel#PillTeal {{
    background-color: {TEAL};
    color: white;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.5px;
}}

/* ── Buttons ── */
QPushButton#BtnPrimary {{
    background-color: {BRAND};
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0 18px;
    font-size: 13px;
    font-weight: 600;
    font-family: "Inter", "DM Sans", sans-serif;
    min-height: 36px;
}}

QPushButton#BtnPrimary:hover {{
    background-color: {BRAND_DARK};
}}

QPushButton#BtnPrimary:pressed {{
    background-color: {BRAND_MID};
}}

QPushButton#BtnPrimary:disabled {{
    background-color: {BORDER_MEDIUM};
    color: {TEXT_DISABLED};
}}

QPushButton#BtnCapture {{
    background-color: {BRAND};
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0 28px;
    font-size: 14px;
    font-weight: 700;
    font-family: "Inter", "DM Sans", sans-serif;
    min-height: 46px;
    letter-spacing: 0.3px;
}}

QPushButton#BtnCapture:hover {{
    background-color: {BRAND_DARK};
}}

QPushButton#BtnCapture:disabled {{
    background-color: {BORDER_MEDIUM};
    color: {TEXT_DISABLED};
}}

QPushButton#BtnSecondary {{
    background-color: white;
    color: {TEXT_BODY};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 0 18px;
    font-size: 13px;
    font-weight: 500;
    font-family: "Inter", "DM Sans", sans-serif;
    min-height: 36px;
}}

QPushButton#BtnSecondary:hover {{
    background-color: {BG_HOVER};
    border-color: {BORDER_MEDIUM};
    color: {TEXT_PRIMARY};
}}

QPushButton#BtnSecondary:pressed {{
    background-color: #E2E8F0;
}}

QPushButton#BtnSecondary:disabled {{
    border-color: {BORDER};
    color: {TEXT_DISABLED};
    background-color: {BG_PAGE};
}}

QPushButton#BtnDanger {{
    background-color: transparent;
    color: {RED};
    border: 1px solid {RED_LIGHT};
    border-radius: 8px;
    padding: 0 18px;
    font-size: 13px;
    font-weight: 600;
    min-height: 36px;
}}

QPushButton#BtnDanger:hover {{
    background-color: {RED_LIGHT};
    border-color: {RED};
}}

QPushButton#BtnSmall {{
    background-color: transparent;
    color: {BRAND};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 0 10px;
    font-size: 11px;
    font-weight: 600;
    min-height: 28px;
}}

QPushButton#BtnSmall:hover {{
    background-color: {BRAND_LIGHT};
    border-color: {BRAND};
}}

QPushButton#BtnMiniPrimary {{
    background-color: {BRAND_LIGHT};
    color: {BRAND};
    border: none;
    border-radius: 6px;
    padding: 0 10px;
    font-size: 11px;
    font-weight: 600;
    min-height: 26px;
}}

QPushButton#BtnMiniPrimary:hover {{
    background-color: {BRAND};
    color: white;
}}

QPushButton#BtnMiniDanger {{
    background-color: {RED_LIGHT};
    color: {RED_DARK};
    border: none;
    border-radius: 6px;
    padding: 0 10px;
    font-size: 11px;
    font-weight: 600;
    min-height: 26px;
}}

QPushButton#BtnMiniDanger:hover {{
    background-color: {RED};
    color: white;
}}

/* ── Inputs ── */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {{
    background-color: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 0 12px;
    min-height: 36px;
    color: {TEXT_PRIMARY};
    font-size: 13px;
    selection-background-color: {BRAND_LIGHT};
}}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus,
QDoubleSpinBox:focus, QDateEdit:focus {{
    border: 1.5px solid {BRAND};
    background-color: white;
}}

QLineEdit:hover, QComboBox:hover, QSpinBox:hover,
QDoubleSpinBox:hover, QDateEdit:hover {{
    border-color: {BORDER_MEDIUM};
    background-color: white;
}}

QLineEdit:disabled, QComboBox:disabled {{
    background-color: {BG_PAGE};
    color: {TEXT_MUTED};
    border-color: {BORDER};
}}

QLineEdit#PlateInput {{
    font-family: "JetBrains Mono", "Courier New", monospace;
    font-size: 14px;
    font-weight: 700;
    background-color: {BRAND_LIGHT};
    border-color: {BRAND};
    letter-spacing: 1.5px;
    color: {BRAND_DARK};
}}

QComboBox::drop-down {{
    border: none;
    padding-right: 8px;
    width: 24px;
}}

QComboBox QAbstractItemView {{
    background: white;
    border: 1px solid {BORDER};
    border-radius: 8px;
    selection-background-color: {BRAND_LIGHT};
    color: {TEXT_BODY};
    padding: 4px;
}}

/* ── Tables ── */
QTableWidget#TableWidget {{
    background: white;
    border: none;
    border-radius: 0px;
    gridline-color: {BORDER};
    selection-background-color: {BRAND_LIGHT};
    alternate-background-color: {BG_TABLE_ALT};
}}

QTableWidget#TableWidget::item {{
    padding: 6px 12px;
    color: {TEXT_BODY};
    border: none;
    min-height: 36px;
    font-size: 12px;
}}

QTableWidget#TableWidget::item:selected {{
    background-color: {BRAND_LIGHT};
    color: {TEXT_PRIMARY};
}}

QHeaderView::section {{
    background-color: {BG_TABLE_ALT};
    color: {TEXT_MUTED};
    font-weight: 600;
    font-size: 10px;
    padding: 8px 12px;
    border: none;
    border-bottom: 1px solid {BORDER};
    text-transform: uppercase;
    letter-spacing: 0.6px;
}}

/* ── Status bar ── */
QWidget#StatusBar {{
    background-color: {BG_SIDEBAR};
    border-top: 1px solid {BORDER};
    min-height: 30px;
    max-height: 30px;
}}

QLabel#StatusBarLabel {{
    font-size: 11px;
    color: {TEXT_SECONDARY};
    background: transparent;
    font-family: "Inter", "DM Sans", sans-serif;
    font-weight: 500;
}}

QLabel#StatusBarClock {{
    font-family: "JetBrains Mono", "Courier New", monospace;
    font-size: 11px;
    color: {TEXT_MUTED};
    background: transparent;
}}

QLabel#ScaleOnline {{
    font-size: 11px;
    color: {GREEN};
    background: transparent;
    font-weight: 600;
}}

QLabel#ScaleOffline {{
    font-size: 11px;
    color: {TEXT_MUTED};
    background: transparent;
    font-weight: 500;
}}

/* ── Page titles ── */
QLabel#PageTitle {{
    font-family: "Inter", "DM Sans", sans-serif;
    font-size: 18px;
    font-weight: 700;
    color: {TEXT_PRIMARY};
    background: transparent;
}}

QLabel#PageSubtitle {{
    font-size: 12px;
    color: {TEXT_MUTED};
    background: transparent;
    font-weight: 400;
}}

QLabel#SectionTitle {{
    font-family: "Inter", "DM Sans", sans-serif;
    font-size: 13px;
    font-weight: 600;
    color: {TEXT_PRIMARY};
    background: transparent;
}}

QLabel#TicketNumber {{
    font-family: "JetBrains Mono", "Courier New", monospace;
    font-size: 11px;
    font-weight: 700;
    color: {BRAND};
    background: transparent;
    letter-spacing: 0.5px;
}}

/* ── Step pills ── */
QLabel#StepActive {{
    background-color: {BRAND};
    color: white;
    border-radius: 6px;
    padding: 3px 14px;
    font-size: 11px;
    font-weight: 700;
}}

QLabel#StepDone {{
    background-color: {GREEN_LIGHT};
    color: {GREEN};
    border-radius: 6px;
    padding: 3px 14px;
    font-size: 11px;
    font-weight: 600;
}}

QLabel#StepPending {{
    background-color: {BG_PAGE};
    color: {TEXT_MUTED};
    border-radius: 6px;
    padding: 3px 14px;
    font-size: 11px;
    border: 1px solid {BORDER};
}}

/* ── Ticket summary ── */
QFrame#TicketSummaryBox {{
    background-color: {GREEN_LIGHT};
    border: 1px solid #86EFAC;
    border-radius: 10px;
    padding: 16px;
}}

QFrame#TicketSummaryBox QLabel {{
    background: transparent;
    color: {GREEN_TEXT};
}}

QLabel#NetHero {{
    font-family: "JetBrains Mono", "Courier New", monospace;
    font-size: 30px;
    font-weight: 700;
    color: {BRAND};
    background: transparent;
}}

/* ── Tab widget ── */
QTabWidget::pane {{
    border: none;
    border-top: 1px solid {BORDER};
    background: white;
}}

QTabBar::tab {{
    background: transparent;
    color: {TEXT_SECONDARY};
    padding: 9px 20px;
    border: none;
    border-bottom: 2px solid transparent;
    font-size: 12px;
    font-weight: 500;
    margin-right: 2px;
}}

QTabBar::tab:selected {{
    color: {BRAND};
    border-bottom: 2px solid {BRAND};
    font-weight: 600;
}}

QTabBar::tab:hover {{
    color: {TEXT_PRIMARY};
    background-color: {BG_HOVER};
}}

/* ── Scrollbars ── */
QScrollBar:vertical {{
    background: transparent;
    width: 5px;
    margin: 0;
    border-radius: 3px;
}}

QScrollBar::handle:vertical {{
    background: {BORDER_MEDIUM};
    border-radius: 3px;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background: {TEXT_MUTED};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 5px;
    border-radius: 3px;
}}

QScrollBar::handle:horizontal {{
    background: {BORDER_MEDIUM};
    border-radius: 3px;
    min-width: 20px;
}}

/* ── Message boxes ── */
QMessageBox {{
    background: white;
}}

QMessageBox QLabel {{
    color: {TEXT_BODY};
    font-size: 13px;
}}

/* ── Progress bar ── */
QProgressBar {{
    background: {BG_PAGE};
    border: none;
    border-radius: 3px;
    height: 4px;
    text-align: center;
}}

QProgressBar::chunk {{
    background: {BRAND};
    border-radius: 3px;
}}

/* ── Checkbox ── */
QCheckBox {{
    color: {TEXT_BODY};
    font-size: 13px;
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {BORDER_MEDIUM};
    border-radius: 4px;
    background: white;
}}

QCheckBox::indicator:checked {{
    background-color: {BRAND};
    border-color: {BRAND};
}}

/* ── Login card ── */
QFrame#LoginCard {{
    background-color: white;
    border: 1px solid {BORDER};
    border-radius: 16px;
    padding: 40px;
}}

/* ── Setup card ── */
QFrame#SetupCard {{
    background-color: white;
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 24px;
}}

/* ── Error message ── */
QLabel#ErrorLabel {{
    background-color: {RED_LIGHT};
    color: {RED_DARK};
    border: 1px solid #FCA5A5;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 12px;
    font-weight: 500;
}}

/* ── Success message ── */
QLabel#SuccessLabel {{
    background-color: {GREEN_LIGHT};
    color: {GREEN_TEXT};
    border: 1px solid #86EFAC;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 12px;
    font-weight: 500;
}}

/* ── Info message ── */
QLabel#InfoLabel {{
    background-color: {BRAND_LIGHT};
    color: {BRAND_DARK};
    border: 1px solid #93C5FD;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 12px;
    font-weight: 500;
}}

/* ── Divider ── */
QFrame#HLine {{
    color: {BORDER};
    max-height: 1px;
    background: {BORDER};
}}

/* ── Void row styling in tables ── */
QTableWidget#TableWidget QTableWidgetItem[void="true"] {{
    color: {TEXT_MUTED};
    text-decoration: line-through;
}}

/* ── Manual weight unlock area ── */
QFrame#ManualWeightBox {{
    background-color: {AMBER_LIGHT};
    border: 1px solid #FDE68A;
    border-radius: 8px;
    padding: 10px;
}}

/* ── Sidebar section label ── */
QLabel#SidebarSection {{
    font-size: 9px;
    font-weight: 700;
    color: {TEXT_MUTED};
    letter-spacing: 1.2px;
    background: transparent;
    padding: 10px 16px 2px 16px;
    text-transform: uppercase;
}}

/* ── Company badge in sidebar ── */
QLabel#CompanyBadge {{
    font-size: 11px;
    color: {TEXT_SECONDARY};
    background: transparent;
    padding: 0 16px;
    font-weight: 500;
}}

/* ── Wizard header ── */
QFrame#WizardHeader {{
    background-color: {BRAND};
    border-radius: 0px;
    padding: 16px 24px;
    min-height: 68px;
    max-height: 68px;
}}

QFrame#WizardHeader QLabel {{
    color: white;
    background: transparent;
}}

/* ── Overload warning banner ── */
QLabel#OverloadBanner {{
    background-color: {RED_LIGHT};
    color: {RED_DARK};
    border: 1px solid #FCA5A5;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
    font-weight: 700;
    text-align: center;
}}

/* ── Top nav bar (page-level) ── */
QFrame#TopNav {{
    background-color: {BG_SIDEBAR};
    border-bottom: 1px solid {BORDER};
    min-height: 48px;
    max-height: 48px;
}}

QPushButton#TopNavBtn {{
    background: transparent;
    border: none;
    border-radius: 6px;
    color: {TEXT_SECONDARY};
    font-size: 12px;
    font-weight: 500;
    padding: 5px 12px;
    margin: 0 2px;
}}

QPushButton#TopNavBtn:hover {{
    background-color: {BG_HOVER};
    color: {TEXT_PRIMARY};
}}

QPushButton#TopNavBtn:checked {{
    background-color: {BRAND_LIGHT};
    color: {BRAND};
    font-weight: 600;
}}

/* ── Search input ── */
QLineEdit#SearchInput {{
    background-color: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 0 12px;
    min-height: 32px;
    color: {TEXT_PRIMARY};
    font-size: 12px;
}}

QLineEdit#SearchInput:focus {{
    border-color: {BRAND};
    background-color: white;
}}

/* ── Filter chip buttons ── */
QPushButton#FilterChip {{
    background-color: white;
    color: {TEXT_SECONDARY};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 0 12px;
    font-size: 11px;
    font-weight: 500;
    min-height: 30px;
}}

QPushButton#FilterChip:hover {{
    border-color: {BRAND};
    color: {BRAND};
    background-color: {BRAND_LIGHT};
}}

QPushButton#FilterChip:checked {{
    background-color: {BRAND};
    color: white;
    border-color: {BRAND};
    font-weight: 600;
}}

/* ── Page header band ── */
QWidget#PageHeaderBand {{
    background-color: {BG_CARD};
    border-bottom: 1px solid {BORDER};
    min-height: 52px;
    max-height: 52px;
}}

/* ── Quick actions toolbar ── */
QFrame#ActionBar {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 10px;
}}

/* ── Stat strip (colored left border KPI variant) ── */
QFrame#StatStrip {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
}}
"""
