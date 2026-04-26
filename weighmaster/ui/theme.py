"""Master QSS stylesheet — ALL styles defined here, never inline."""

# ─── Colour tokens ────────────────────────────────────────────────────────────
BG_PAGE       = "#D9DEE3"
BG_SIDEBAR    = "#ECEFF3"
BG_CARD       = "#F6F8FB"
BG_INPUT      = "#FBFCFD"
BG_TABLE_ALT  = "#F2F5F8"

BRAND         = "#111418"
BRAND_DARK    = "#050709"
BRAND_LIGHT   = "#E4E8EF"
BRAND_MID     = "#5F6D80"
BRAND_GRAD_START = "#222A33"
BRAND_GRAD_END   = "#111418"

TEAL          = "#0D9488"
TEAL_LIGHT    = "#CCFBF1"

GREEN         = "#059669"
GREEN_LIGHT   = "#D1FAE5"
GREEN_TEXT    = "#047857"
AMBER         = "#B45309"
AMBER_LIGHT   = "#FEF3C7"
AMBER_TEXT    = "#92400E"
RED           = "#DC2626"
RED_LIGHT     = "#FEE2E2"
RED_DARK      = "#991B1B"

TEXT_PRIMARY  = "#0D1116"
TEXT_BODY     = "#2B3440"
TEXT_SECONDARY= "#4F5E6F"
TEXT_MUTED    = "#7F8B98"
TEXT_DISABLED = "#ADB6C1"

BORDER        = "#D4DAE1"
BORDER_MEDIUM = "#BFC8D2"
BORDER_FOCUS  = "#5F6D80"
SHADOW        = "rgba(10, 16, 24, 0.08)"

# ─── Master stylesheet ────────────────────────────────────────────────────────
STYLESHEET = f"""

/* ── Global ── */
QMainWindow, QDialog, QWidget {{
    background-color: {BG_PAGE};
    color: {TEXT_BODY};
    font-family: "DM Sans", "Segoe UI", sans-serif;
    font-size: 12px;
}}

QLabel {{
    color: {TEXT_BODY};
    background: transparent;
}}

/* ── Sidebar ── */
QWidget#Sidebar {{
    background-color: {BG_SIDEBAR};
    border-right: 1px solid {BORDER};
}}

QPushButton#NavItem {{
    background: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
    color: {TEXT_SECONDARY};
    font-size: 12px;
    font-family: "DM Sans", "Segoe UI", sans-serif;
    text-align: left;
    padding: 8px 12px;
    min-height: 34px;
    margin: 1px 8px;
}}

QPushButton#NavItem:hover {{
    background-color: white;
    border-color: {BORDER};
    color: {TEXT_PRIMARY};
}}

QPushButton#NavItem:checked {{
    background-color: white;
    border: 1px solid {BORDER_MEDIUM};
    color: {TEXT_PRIMARY};
    font-weight: 600;
}}

/* ── Cards ── */
QFrame#Card {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
}}

QFrame#CardHeader {{
    background-color: {BG_CARD};
    border-bottom: 1px solid {BORDER};
    border-radius: 0px;
    padding: 0px 16px;
    min-height: 44px;
    max-height: 44px;
}}

/* ── Weight display ── */
QLabel#WeightHero {{
    font-family: "JetBrains Mono", "Courier New", monospace;
    font-size: 44px;
    font-weight: 700;
    color: {TEXT_PRIMARY};
    background: transparent;
    letter-spacing: 0px;
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
    font-size: 14px;
    color: {TEXT_BODY};
    background: transparent;
}}

/* ── Status chips ── */
QLabel#ChipStable {{
    background-color: #EAF8F1;
    color: {GREEN_TEXT};
    border: 1px solid #BDE7CD;
    border-radius: 8px;
    padding: 2px 10px;
    font-size: 9px;
    font-weight: 700;
    font-family: "DM Sans", sans-serif;
}}

QLabel#ChipUnstable {{
    background-color: #FFF5E8;
    color: {AMBER_TEXT};
    border: 1px solid #F9DEB2;
    border-radius: 8px;
    padding: 2px 10px;
    font-size: 9px;
    font-weight: 700;
    font-family: "DM Sans", sans-serif;
}}

QLabel#ChipOverload {{
    background-color: #FDECEC;
    color: {RED};
    border: 1px solid #F6C6C6;
    border-radius: 8px;
    padding: 2px 10px;
    font-size: 9px;
    font-weight: 700;
    font-family: "DM Sans", sans-serif;
}}

QLabel#ChipComplete {{
    background-color: {GREEN_LIGHT};
    color: {GREEN_TEXT};
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 9px;
    font-weight: 600;
}}

QLabel#ChipVoid {{
    background-color: {RED_LIGHT};
    color: {RED};
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 9px;
    font-weight: 600;
}}

QLabel#ChipPending {{
    background-color: {AMBER_LIGHT};
    color: {AMBER};
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 9px;
    font-weight: 600;
}}

/* ── Buttons ── */
QPushButton#BtnPrimary {{
    background-color: {BRAND};
    color: white;
    border: 1px solid {BRAND};
    border-radius: 8px;
    padding: 0 16px;
    font-size: 12px;
    font-weight: 600;
    font-family: "DM Sans", sans-serif;
    min-height: 34px;
}}

QPushButton#BtnPrimary:hover {{
    background-color: {BRAND_DARK};
}}

QPushButton#BtnPrimary:pressed {{
    background-color: {BRAND_GRAD_START};
}}

QPushButton#BtnPrimary:disabled {{
    background-color: {BORDER_MEDIUM};
    color: {TEXT_DISABLED};
}}

QPushButton#BtnCapture {{
    background-color: {BRAND};
    color: white;
    border: 1px solid {BRAND};
    border-radius: 8px;
    padding: 0 20px;
    font-size: 12px;
    font-weight: 700;
    font-family: "DM Sans", sans-serif;
    min-height: 40px;
    letter-spacing: 0px;
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
    color: {TEXT_PRIMARY};
    border: 1.5px solid {BORDER};
    border-radius: 8px;
    padding: 0 14px;
    font-size: 12px;
    font-weight: 600;
    font-family: "DM Sans", sans-serif;
    min-height: 34px;
}}

QPushButton#BtnSecondary:hover {{
    background-color: {BRAND_LIGHT};
    border-color: {BORDER_MEDIUM};
    color: {TEXT_PRIMARY};
}}

QPushButton#BtnSecondary:pressed {{
    background-color: #BFDBFE;
}}

QPushButton#BtnSecondary:disabled {{
    border-color: {BORDER_MEDIUM};
    color: {TEXT_DISABLED};
    background-color: {BG_PAGE};
}}

QPushButton#BtnDanger {{
    background-color: transparent;
    color: {RED};
    border: 1.5px solid {RED};
    border-radius: 8px;
    padding: 0 20px;
    font-size: 12px;
    font-weight: 600;
    min-height: 36px;
}}

QPushButton#BtnDanger:hover {{
    background-color: {RED_LIGHT};
}}

QPushButton#BtnSmall {{
    background-color: white;
    color: {TEXT_SECONDARY};
    border: 1px solid {BORDER};
    border-radius: 7px;
    padding: 0 10px;
    font-size: 11px;
    min-height: 26px;
}}

QPushButton#BtnSmall:hover {{
    background-color: {BG_TABLE_ALT};
    border-color: {BORDER_MEDIUM};
}}

QPushButton#BtnMiniPrimary {{
    background-color: {BRAND};
    color: white;
    border: 1px solid {BRAND};
    border-radius: 7px;
    padding: 0 10px;
    font-size: 10px;
    min-height: 26px;
}}

QPushButton#BtnMiniPrimary:hover {{
    background-color: {BRAND_DARK};
}}

QPushButton#BtnMiniDanger {{
    background-color: white;
    color: {RED};
    border: 1px solid #F2B6B6;
    border-radius: 7px;
    padding: 0 10px;
    font-size: 10px;
    min-height: 26px;
}}

QPushButton#BtnMiniDanger:hover {{
    background-color: {RED_LIGHT};
}}

/* ── Inputs ── */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {{
    background-color: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 0 10px;
    min-height: 34px;
    color: {TEXT_PRIMARY};
    font-size: 12px;
    selection-background-color: {BRAND_LIGHT};
}}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus,
QDoubleSpinBox:focus, QDateEdit:focus {{
    border: 2px solid {BRAND};
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
    font-size: 13px;
    font-weight: 700;
    background-color: white;
    border-color: {BORDER_MEDIUM};
    letter-spacing: 0px;
    color: {TEXT_PRIMARY};
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
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
    gridline-color: {BORDER};
    selection-background-color: {BRAND_LIGHT};
    alternate-background-color: {BG_TABLE_ALT};
}}

QTableWidget#TableWidget::item {{
    padding: 6px 10px;
    color: {TEXT_BODY};
    border: none;
    min-height: 36px;
}}

QTableWidget#TableWidget::item:selected {{
    background-color: {BRAND_LIGHT};
    color: {TEXT_PRIMARY};
}}

QHeaderView::section {{
    background-color: #EDF1F5;
    color: {TEXT_SECONDARY};
    font-weight: 600;
    font-size: 10px;
    padding: 6px 10px;
    border: none;
    border-bottom: 1px solid {BORDER};
    text-transform: none;
    letter-spacing: 0px;
}}

/* ── KPI Cards ── */
QLabel#KpiValue {{
    font-family: "Inter", "DM Sans", sans-serif;
    font-size: 20px;
    font-weight: 700;
    color: {TEXT_PRIMARY};
    background: transparent;
}}

QLabel#KpiLabel {{
    font-size: 10px;
    color: {TEXT_MUTED};
    background: transparent;
}}

QLabel#KpiIcon {{
    font-size: 9px;
    color: {TEXT_SECONDARY};
    background: #E9EDF2;
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 2px 6px;
    font-weight: 700;
    letter-spacing: 0px;
}}

QWidget#SidebarDivider {{
    background: {BORDER};
    min-height: 1px;
    max-height: 1px;
}}

/* ── Status bar ── */
QWidget#StatusBar {{
    background-color: {BG_SIDEBAR};
    border-top: 1px solid {BORDER};
    min-height: 32px;
    max-height: 32px;
}}

QLabel#StatusBarLabel {{
    font-size: 9px;
    color: {TEXT_SECONDARY};
    background: transparent;
    font-family: "DM Sans", sans-serif;
}}

QLabel#StatusBarClock {{
    font-family: "JetBrains Mono", "Courier New", monospace;
    font-size: 9px;
    color: {TEXT_SECONDARY};
    background: transparent;
}}

QLabel#ScaleOnline {{
    font-size: 9px;
    color: {GREEN};
    background: transparent;
    font-weight: 600;
}}

QLabel#ScaleOffline {{
    font-size: 9px;
    color: {RED};
    background: transparent;
    font-weight: 600;
}}

/* ── Page titles ── */
QLabel#PageTitle {{
    font-family: "Inter", "DM Sans", sans-serif;
    font-size: 15px;
    font-weight: 600;
    color: {TEXT_PRIMARY};
    background: transparent;
}}

QLabel#SectionTitle {{
    font-family: "Inter", "DM Sans", sans-serif;
    font-size: 12px;
    font-weight: 600;
    color: {TEXT_PRIMARY};
    background: transparent;
}}

QLabel#TicketNumber {{
    font-family: "JetBrains Mono", "Courier New", monospace;
    font-size: 11px;
    font-weight: 700;
    color: {TEXT_SECONDARY};
    background: transparent;
    letter-spacing: 0px;
}}

/* ── Step pills ── */
QLabel#StepActive {{
    background-color: {TEXT_PRIMARY};
    color: white;
    border-radius: 8px;
    padding: 2px 10px;
    font-size: 10px;
    font-weight: 700;
}}

QLabel#StepDone {{
    background-color: #EAF8F1;
    color: {GREEN};
    border: 1px solid #BDE7CD;
    border-radius: 8px;
    padding: 2px 10px;
    font-size: 10px;
    font-weight: 600;
}}

QLabel#StepPending {{
    background-color: #EDF1F5;
    color: {TEXT_MUTED};
    border-radius: 8px;
    padding: 2px 10px;
    font-size: 10px;
    border: 1px solid {BORDER};
}}

/* ── Ticket summary ── */
QFrame#TicketSummaryBox {{
    background-color: {GREEN_LIGHT};
    border: 1px solid {GREEN};
    border-radius: 8px;
    padding: 12px;
}}

QFrame#TicketSummaryBox QLabel {{
    background: transparent;
    color: {GREEN_TEXT};
}}

QLabel#NetHero {{
    font-family: "JetBrains Mono", "Courier New", monospace;
    font-size: 28px;
    font-weight: 700;
    color: {BRAND};
    background: transparent;
}}

/* ── Tab widget ── */
QTabWidget::pane {{
    border: 1px solid {BORDER};
    border-radius: 8px;
    background: white;
}}

QTabBar::tab {{
    background: transparent;
    color: {TEXT_SECONDARY};
    padding: 8px 20px;
    border: none;
    border-bottom: 2px solid transparent;
    font-size: 12px;
}}

QTabBar::tab:selected {{
    color: {BRAND};
    border-bottom: 2px solid {BRAND};
    font-weight: 600;
}}

QTabBar::tab:hover {{
    color: {TEXT_PRIMARY};
}}

/* ── Scrollbars ── */
QScrollBar:vertical {{
    background: {BG_PAGE};
    width: 8px;
    margin: 0;
    border-radius: 4px;
}}

QScrollBar::handle:vertical {{
    background: {BORDER_MEDIUM};
    border-radius: 4px;
    min-height: 24px;
}}

QScrollBar::handle:vertical:hover {{
    background: {TEXT_MUTED};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background: {BG_PAGE};
    height: 8px;
    border-radius: 4px;
}}

QScrollBar::handle:horizontal {{
    background: {BORDER_MEDIUM};
    border-radius: 4px;
    min-width: 24px;
}}

/* ── Message boxes ── */
QMessageBox {{
    background: white;
}}

QMessageBox QLabel {{
    color: {TEXT_BODY};
    font-size: 12px;
}}

/* ── Progress bar ── */
QProgressBar {{
    background: {BG_PAGE};
    border: 1px solid {BORDER};
    border-radius: 4px;
    height: 6px;
    text-align: center;
}}

QProgressBar::chunk {{
    background: {BRAND};
    border-radius: 4px;
}}

/* ── Stability progress bar ── */
QProgressBar#StabilityBar {{
    background: {BG_PAGE};
    border: none;
    border-radius: 2px;
    height: 4px;
    text-align: center;
}}

QProgressBar#StabilityBar::chunk {{
    background: {GREEN};
    border-radius: 2px;
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

/* ── Checkbox ── */
QCheckBox {{
    color: {TEXT_BODY};
    font-size: 12px;
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1.5px solid {BORDER_MEDIUM};
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
    padding: 32px;
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
    border: 1px solid {AMBER};
    border-radius: 8px;
    padding: 8px;
}}

/* ── Sidebar section label ── */
QLabel#SidebarSection {{
    font-size: 9px;
    font-weight: 700;
    color: {TEXT_MUTED};
    letter-spacing: 0px;
    background: transparent;
    padding: 8px 16px 4px 16px;
    text-transform: uppercase;
}}

/* ── Company badge in sidebar ── */
QLabel#CompanyBadge {{
    font-size: 10px;
    color: {TEXT_SECONDARY};
    background: transparent;
    padding: 0 16px;
}}

/* ── Wizard header ── */
QFrame#WizardHeader {{
    background-color: {BRAND};
    border-radius: 0px;
    padding: 16px 24px;
    min-height: 72px;
    max-height: 72px;
}}

QFrame#WizardHeader QLabel {{
    color: white;
    background: transparent;
}}

/* ── Wizard pages ── */
QWidget#WizardPage {{
    background-color: {BG_PAGE};
}}

/* ── Setup wizard form rows ── */
QFormLayout::item {{
    spacing: 8px;
}}

QLabel#FormLabel {{
    color: {TEXT_SECONDARY};
    font-size: 12px;
    font-weight: 500;
    background: transparent;
}}

QLabel#FormLabelRequired {{
    color: {TEXT_PRIMARY};
    font-size: 12px;
    font-weight: 600;
    background: transparent;
}}

/* ── Password strength ── */
QLabel#PwStrength {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
    background: transparent;
    padding: 4px 0px;
}}

/* ── Step indicator dots ── */
QFrame#StepDotActive {{
    background-color: {BRAND};
    border-radius: 6px;
    min-width: 12px;
    max-width: 12px;
    min-height: 12px;
    max-height: 12px;
}}

QFrame#StepDotDone {{
    background-color: {GREEN};
    border-radius: 6px;
    min-width: 12px;
    max-width: 12px;
    min-height: 12px;
    max-height: 12px;
}}

QFrame#StepDotPending {{
    background-color: {BORDER_MEDIUM};
    border-radius: 6px;
    min-width: 12px;
    max-width: 12px;
    min-height: 12px;
    max-height: 12px;
}}

QFrame#StepLine {{
    background-color: {BORDER};
    max-height: 2px;
}}

QFrame#StepLineDone {{
    background-color: {GREEN};
    max-height: 2px;
}}
"""
