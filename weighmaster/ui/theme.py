"""Master QSS stylesheet — modern cargo-dashboard inspired design."""

# ─── Colour tokens ────────────────────────────────────────────────────────────
BG_PAGE       = "#F3F4F6"
BG_SIDEBAR    = "#FFFFFF"
BG_CARD       = "#FFFFFF"
BG_INPUT      = "#F9FAFB"
BG_TABLE_ALT  = "#FAFBFC"
BG_HOVER      = "#F3F4F6"

BRAND         = "#4F46E5"   # Indigo
BRAND_DARK    = "#4338CA"
BRAND_LIGHT   = "#EEF2FF"
BRAND_MID     = "#6366F1"

TEAL          = "#14B8A6"
TEAL_LIGHT    = "#CCFBF1"

GREEN         = "#10B981"
GREEN_LIGHT   = "#D1FAE5"
GREEN_TEXT    = "#047857"
GREEN_PILL    = "#84CC16"   # Lime for status pills

AMBER         = "#F59E0B"
AMBER_LIGHT   = "#FEF3C7"
AMBER_TEXT    = "#92400E"
AMBER_PILL    = "#EAB308"   # Yellow for pills

RED           = "#EF4444"
RED_LIGHT     = "#FEE2E2"
RED_DARK      = "#B91C1C"
RED_PILL      = "#F87171"

PURPLE        = "#8B5CF6"
PURPLE_LIGHT  = "#EDE9FE"

TEXT_PRIMARY  = "#111827"
TEXT_BODY     = "#374151"
TEXT_SECONDARY= "#6B7280"
TEXT_MUTED    = "#9CA3AF"
TEXT_DISABLED = "#D1D5DB"

BORDER        = "#E5E7EB"
BORDER_MEDIUM = "#D1D5DB"
BORDER_FOCUS  = "#4F46E5"

SHADOW        = "rgba(0, 0, 0, 0.04)"
SHADOW_CARD   = "rgba(0, 0, 0, 0.06)"
SHADOW_HOVER  = "rgba(0, 0, 0, 0.08)"

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

/* ── Sidebar ── */
QWidget#Sidebar {{
    background-color: {BG_SIDEBAR};
    border-right: 1px solid {BORDER};
}}

QPushButton#NavItem {{
    background: transparent;
    border: none;
    border-radius: 10px;
    color: {TEXT_SECONDARY};
    font-size: 12px;
    font-weight: 500;
    font-family: "Inter", "DM Sans", "Segoe UI", sans-serif;
    text-align: left;
    padding: 10px 14px;
    min-height: 40px;
    margin: 2px 8px;
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
    border-radius: 10px;
    color: {TEXT_MUTED};
    font-size: 18px;
    padding: 8px;
    min-width: 40px;
    min-height: 40px;
    max-width: 40px;
    max-height: 40px;
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
    border: none;
    border-radius: 16px;
}}

QFrame#CardHeader {{
    background-color: {BG_CARD};
    border-bottom: 1px solid {BORDER};
    border-radius: 0px;
    padding: 0px 20px;
    min-height: 52px;
    max-height: 52px;
}}

/* ── KPI Cards ── */
QFrame#KpiCard {{
    background-color: {BG_CARD};
    border: none;
    border-radius: 16px;
    padding: 20px;
}}

QLabel#KpiValue {{
    font-family: "Inter", "DM Sans", sans-serif;
    font-size: 28px;
    font-weight: 700;
    color: {TEXT_PRIMARY};
    background: transparent;
}}

QLabel#KpiLabel {{
    font-size: 12px;
    color: {TEXT_MUTED};
    background: transparent;
    font-weight: 500;
}}

QLabel#KpiIcon {{
    font-size: 22px;
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
    font-size: 14px;
    color: {TEXT_BODY};
    background: transparent;
}}

/* ── Status chips / Pills ── */
QLabel#ChipStable {{
    background-color: {GREEN_LIGHT};
    color: {GREEN_TEXT};
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 10px;
    font-weight: 700;
    font-family: "Inter", "DM Sans", sans-serif;
}}

QLabel#ChipUnstable {{
    background-color: {AMBER_LIGHT};
    color: {AMBER_TEXT};
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 10px;
    font-weight: 700;
    font-family: "Inter", "DM Sans", sans-serif;
}}

QLabel#ChipOverload {{
    background-color: {RED_LIGHT};
    color: {RED_DARK};
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 10px;
    font-weight: 700;
    font-family: "Inter", "DM Sans", sans-serif;
}}

QLabel#ChipComplete {{
    background-color: {GREEN_LIGHT};
    color: {GREEN_TEXT};
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 10px;
    font-weight: 600;
}}

QLabel#ChipVoid {{
    background-color: {RED_LIGHT};
    color: {RED_DARK};
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 10px;
    font-weight: 600;
}}

QLabel#ChipPending {{
    background-color: {AMBER_LIGHT};
    color: {AMBER_TEXT};
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 10px;
    font-weight: 600;
}}

/* ── Status Pills (bright) ── */
QLabel#PillGreen {{
    background-color: {GREEN_PILL};
    color: white;
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 10px;
    font-weight: 700;
}}

QLabel#PillPurple {{
    background-color: {PURPLE};
    color: white;
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 10px;
    font-weight: 700;
}}

QLabel#PillYellow {{
    background-color: {AMBER_PILL};
    color: white;
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 10px;
    font-weight: 700;
}}

QLabel#PillRed {{
    background-color: {RED_PILL};
    color: white;
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 10px;
    font-weight: 700;
}}

/* ── Buttons ── */
QPushButton#BtnPrimary {{
    background-color: {BRAND};
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0 20px;
    font-size: 13px;
    font-weight: 600;
    font-family: "Inter", "DM Sans", sans-serif;
    min-height: 40px;
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
    border-radius: 12px;
    padding: 0 32px;
    font-size: 14px;
    font-weight: 700;
    font-family: "Inter", "DM Sans", sans-serif;
    min-height: 50px;
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
    color: {BRAND};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 0 20px;
    font-size: 13px;
    font-weight: 600;
    font-family: "Inter", "DM Sans", sans-serif;
    min-height: 40px;
}}

QPushButton#BtnSecondary:hover {{
    background-color: {BRAND_LIGHT};
    border-color: {BRAND};
    color: {BRAND};
}}

QPushButton#BtnSecondary:pressed {{
    background-color: #C7D2FE;
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
    border-radius: 10px;
    padding: 0 20px;
    font-size: 13px;
    font-weight: 600;
    min-height: 40px;
}}

QPushButton#BtnDanger:hover {{
    background-color: {RED_LIGHT};
}}

QPushButton#BtnSmall {{
    background-color: transparent;
    color: {BRAND};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 0 12px;
    font-size: 12px;
    min-height: 32px;
}}

QPushButton#BtnSmall:hover {{
    background-color: {BRAND_LIGHT};
    border-color: {BRAND};
}}

/* ── Inputs ── */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {{
    background-color: {BG_INPUT};
    border: 1.5px solid {BORDER};
    border-radius: 10px;
    padding: 0 14px;
    min-height: 40px;
    color: {TEXT_PRIMARY};
    font-size: 13px;
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
    font-size: 14px;
    font-weight: 700;
    background-color: {BRAND_LIGHT};
    border-color: {BRAND};
    letter-spacing: 1px;
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
    border-radius: 10px;
    selection-background-color: {BRAND_LIGHT};
    color: {TEXT_BODY};
    padding: 4px;
}}

/* ── Tables ── */
QTableWidget#TableWidget {{
    background: white;
    border: none;
    border-radius: 16px;
    gridline-color: transparent;
    selection-background-color: {BRAND_LIGHT};
    alternate-background-color: {BG_TABLE_ALT};
}}

QTableWidget#TableWidget::item {{
    padding: 10px 14px;
    color: {TEXT_BODY};
    border: none;
    min-height: 48px;
}}

QTableWidget#TableWidget::item:selected {{
    background-color: {BRAND_LIGHT};
    color: {TEXT_PRIMARY};
}}

QHeaderView::section {{
    background-color: {BG_CARD};
    color: {TEXT_SECONDARY};
    font-weight: 600;
    font-size: 11px;
    padding: 10px 14px;
    border: none;
    border-bottom: 1px solid {BORDER};
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* ── Status bar ── */
QWidget#StatusBar {{
    background-color: {BG_SIDEBAR};
    border-top: 1px solid {BORDER};
    min-height: 36px;
    max-height: 36px;
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
    color: {TEXT_SECONDARY};
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
    color: {RED};
    background: transparent;
    font-weight: 600;
}}

/* ── Page titles ── */
QLabel#PageTitle {{
    font-family: "Inter", "DM Sans", sans-serif;
    font-size: 20px;
    font-weight: 700;
    color: {TEXT_PRIMARY};
    background: transparent;
}}

QLabel#SectionTitle {{
    font-family: "Inter", "DM Sans", sans-serif;
    font-size: 14px;
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
    border-radius: 20px;
    padding: 4px 16px;
    font-size: 11px;
    font-weight: 700;
}}

QLabel#StepDone {{
    background-color: {GREEN_LIGHT};
    color: {GREEN};
    border-radius: 20px;
    padding: 4px 16px;
    font-size: 11px;
    font-weight: 600;
}}

QLabel#StepPending {{
    background-color: {BG_PAGE};
    color: {TEXT_MUTED};
    border-radius: 20px;
    padding: 4px 16px;
    font-size: 11px;
    border: 1px solid {BORDER};
}}

/* ── Ticket summary ── */
QFrame#TicketSummaryBox {{
    background-color: {GREEN_LIGHT};
    border: 1px solid {GREEN};
    border-radius: 12px;
    padding: 16px;
}}

QFrame#TicketSummaryBox QLabel {{
    background: transparent;
    color: {GREEN_TEXT};
}}

QLabel#NetHero {{
    font-family: "JetBrains Mono", "Courier New", monospace;
    font-size: 32px;
    font-weight: 700;
    color: {BRAND};
    background: transparent;
}}

/* ── Tab widget ── */
QTabWidget::pane {{
    border: none;
    border-radius: 16px;
    background: white;
}}

QTabBar::tab {{
    background: transparent;
    color: {TEXT_SECONDARY};
    padding: 10px 24px;
    border: none;
    border-bottom: 2px solid transparent;
    font-size: 13px;
    font-weight: 500;
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
    background: transparent;
    width: 6px;
    margin: 0;
    border-radius: 3px;
}}

QScrollBar::handle:vertical {{
    background: {BORDER_MEDIUM};
    border-radius: 3px;
    min-height: 24px;
}}

QScrollBar::handle:vertical:hover {{
    background: {TEXT_MUTED};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 6px;
    border-radius: 3px;
}}

QScrollBar::handle:horizontal {{
    background: {BORDER_MEDIUM};
    border-radius: 3px;
    min-width: 24px;
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
    border-radius: 4px;
    height: 6px;
    text-align: center;
}}

QProgressBar::chunk {{
    background: {BRAND};
    border-radius: 4px;
}}

/* ── Checkbox ── */
QCheckBox {{
    color: {TEXT_BODY};
    font-size: 13px;
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 1.5px solid {BORDER_MEDIUM};
    border-radius: 5px;
    background: white;
}}

QCheckBox::indicator:checked {{
    background-color: {BRAND};
    border-color: {BRAND};
}}

/* ── Login card ── */
QFrame#LoginCard {{
    background-color: white;
    border: none;
    border-radius: 20px;
    padding: 40px;
}}

/* ── Setup card ── */
QFrame#SetupCard {{
    background-color: white;
    border: none;
    border-radius: 16px;
    padding: 28px;
}}

/* ── Error message ── */
QLabel#ErrorLabel {{
    background-color: {RED_LIGHT};
    color: {RED_DARK};
    border: 1px solid #FCA5A5;
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 13px;
    font-weight: 500;
}}

/* ── Success message ── */
QLabel#SuccessLabel {{
    background-color: {GREEN_LIGHT};
    color: {GREEN_TEXT};
    border: 1px solid #86EFAC;
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 13px;
    font-weight: 500;
}}

/* ── Info message ── */
QLabel#InfoLabel {{
    background-color: {BRAND_LIGHT};
    color: {BRAND_DARK};
    border: 1px solid #93C5FD;
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 13px;
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
    border-radius: 10px;
    padding: 10px;
}}

/* ── Sidebar section label ── */
QLabel#SidebarSection {{
    font-size: 9px;
    font-weight: 700;
    color: {TEXT_MUTED};
    letter-spacing: 1px;
    background: transparent;
    padding: 10px 16px 4px 16px;
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
    padding: 20px 28px;
    min-height: 80px;
    max-height: 80px;
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
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 14px;
    font-weight: 700;
    text-align: center;
}}

/* ── Top nav bar ── */
QFrame#TopNav {{
    background-color: {BG_SIDEBAR};
    border-bottom: 1px solid {BORDER};
    min-height: 56px;
    max-height: 56px;
}}

QPushButton#TopNavBtn {{
    background: transparent;
    border: none;
    border-radius: 8px;
    color: {TEXT_SECONDARY};
    font-size: 13px;
    font-weight: 500;
    padding: 6px 14px;
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
    border: 1.5px solid {BORDER};
    border-radius: 20px;
    padding: 0 16px;
    min-height: 36px;
    color: {TEXT_PRIMARY};
    font-size: 13px;
}}

QLineEdit#SearchInput:focus {{
    border-color: {BRAND};
    background-color: white;
}}
"""
