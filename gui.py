"""
gui.py
------
Phishing Email Analyzer — futuristic minimal UI
"""

import os
import time
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QPushButton, QFileDialog,
    QMessageBox, QStackedWidget, QFrame,
    QSizePolicy, QInputDialog, QLineEdit, QScrollArea
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QRectF
from PyQt5.QtGui import QFont, QPainter, QPen, QColor


# ── Theme definitions ──────────────────────────────────────────────────────────
_THEMES = {
    "light": {
        "BG": "#F2F4F8", "SURFACE": "#FFFFFF", "BORDER": "#E2E6EA",
        "ACCENT": "#5BB8D4", "PURPLE": "#0D9BAC",
        "TEXT": "#1A2028", "SUBTEXT": "#6B7A8C", "DIM": "#C8D4DC",
        "RISK": {"Low": "#22C55E", "Medium": "#F59E0B", "High": "#F97316", "Critical": "#EF4444"},
        "BTN_HOVER": "#EBF6FA",
        "ANALYZE_HOVER": "#45A8C4", "ANALYZE_PRESSED": "#3898B4",
        "EXPORT_BG": "#EBF9FB", "EXPORT_BORDER": "#B2E0E8", "EXPORT_HOVER": "#D4F2F8",
        "LOG_BG": "#F8FAFB", "LOG_FG": "#475569", "LOG_TS": "#94A3B8",
        "TABBAR_BG": "#E8ECF0",
        "AI_BG": "#EBF9FB", "AI_BORDER": "#B2E0E8",
        "AI_PH_BG": "#F8FAFB",
        "KW_BG": "#FFFBEB", "KW_FG": "#D97706", "KW_BORDER": "#FDE68A",
        "TAG_BG": "#EBF6FA", "TAG_BORDER": "#B2DCF0",
        "ENG_BORDER": "#FEE2E2", "ENG_FG": "#DC2626",
    },
    "dark": {
        "BG": "#1E2428", "SURFACE": "#252D33", "BORDER": "#3A4E5A",
        "ACCENT": "#5BB8D4", "PURPLE": "#0D9BAC",
        "TEXT": "#E8F0F4", "SUBTEXT": "#8AAFC0", "DIM": "#3E5A6A",
        "RISK": {"Low": "#3DD68C", "Medium": "#E0A030", "High": "#F07830", "Critical": "#F05050"},
        "BTN_HOVER": "#1E3A4A",
        "ANALYZE_HOVER": "#3AA8C8", "ANALYZE_PRESSED": "#2A90B0",
        "EXPORT_BG": "#0A2830", "EXPORT_BORDER": "#1A5060", "EXPORT_HOVER": "#0E3040",
        "LOG_BG": "#141C22", "LOG_FG": "#8AAFC0", "LOG_TS": "#4A6A80",
        "TABBAR_BG": "#141C22",
        "AI_BG": "#0A2028", "AI_BORDER": "#1A5060",
        "AI_PH_BG": "#141C22",
        "KW_BG": "#2A2010", "KW_FG": "#E09030", "KW_BORDER": "#604010",
        "TAG_BG": "#0A2030", "TAG_BORDER": "#1A4060",
        "ENG_BORDER": "#3A1A1A", "ENG_FG": "#FF6060",
    },
}

# Active theme name — toggled at runtime
_ACTIVE_THEME = "light"

# Module-level colour variables — updated by _set_theme()
BG      = _THEMES["light"]["BG"]
SURFACE = _THEMES["light"]["SURFACE"]
BORDER  = _THEMES["light"]["BORDER"]
ACCENT  = _THEMES["light"]["ACCENT"]
PURPLE  = _THEMES["light"]["PURPLE"]
TEXT    = _THEMES["light"]["TEXT"]
SUBTEXT = _THEMES["light"]["SUBTEXT"]
DIM     = _THEMES["light"]["DIM"]
RISK_COLORS = dict(_THEMES["light"]["RISK"])
# Inline-only extras
BTN_HOVER       = _THEMES["light"]["BTN_HOVER"]
ANALYZE_HOVER   = _THEMES["light"]["ANALYZE_HOVER"]
ANALYZE_PRESSED = _THEMES["light"]["ANALYZE_PRESSED"]
EXPORT_BG       = _THEMES["light"]["EXPORT_BG"]
EXPORT_BORDER   = _THEMES["light"]["EXPORT_BORDER"]
EXPORT_HOVER    = _THEMES["light"]["EXPORT_HOVER"]
LOG_BG          = _THEMES["light"]["LOG_BG"]
LOG_FG          = _THEMES["light"]["LOG_FG"]
LOG_TS          = _THEMES["light"]["LOG_TS"]
TABBAR_BG       = _THEMES["light"]["TABBAR_BG"]
AI_BG           = _THEMES["light"]["AI_BG"]
AI_BORDER       = _THEMES["light"]["AI_BORDER"]
AI_PH_BG        = _THEMES["light"]["AI_PH_BG"]
KW_BG           = _THEMES["light"]["KW_BG"]
KW_FG           = _THEMES["light"]["KW_FG"]
KW_BORDER       = _THEMES["light"]["KW_BORDER"]
TAG_BG          = _THEMES["light"]["TAG_BG"]
TAG_BORDER      = _THEMES["light"]["TAG_BORDER"]
ENG_BORDER      = _THEMES["light"]["ENG_BORDER"]
ENG_FG          = _THEMES["light"]["ENG_FG"]


def _set_theme(name: str):
    """Update all module-level colour globals to the given theme."""
    global _ACTIVE_THEME
    global BG, SURFACE, BORDER, ACCENT, PURPLE, TEXT, SUBTEXT, DIM, RISK_COLORS
    global BTN_HOVER, ANALYZE_HOVER, ANALYZE_PRESSED
    global EXPORT_BG, EXPORT_BORDER, EXPORT_HOVER
    global LOG_BG, LOG_FG, LOG_TS, TABBAR_BG
    global AI_BG, AI_BORDER, AI_PH_BG
    global KW_BG, KW_FG, KW_BORDER, TAG_BG, TAG_BORDER, ENG_BORDER, ENG_FG
    t = _THEMES[name]
    _ACTIVE_THEME   = name
    BG              = t["BG"];      SURFACE = t["SURFACE"]; BORDER  = t["BORDER"]
    ACCENT          = t["ACCENT"];  PURPLE  = t["PURPLE"]
    TEXT            = t["TEXT"];    SUBTEXT = t["SUBTEXT"]; DIM     = t["DIM"]
    RISK_COLORS     = dict(t["RISK"])
    BTN_HOVER       = t["BTN_HOVER"]
    ANALYZE_HOVER   = t["ANALYZE_HOVER"];  ANALYZE_PRESSED = t["ANALYZE_PRESSED"]
    EXPORT_BG       = t["EXPORT_BG"];      EXPORT_BORDER   = t["EXPORT_BORDER"]
    EXPORT_HOVER    = t["EXPORT_HOVER"]
    LOG_BG          = t["LOG_BG"];  LOG_FG = t["LOG_FG"];  LOG_TS = t["LOG_TS"]
    TABBAR_BG       = t["TABBAR_BG"]
    AI_BG           = t["AI_BG"];   AI_BORDER = t["AI_BORDER"]; AI_PH_BG = t["AI_PH_BG"]
    KW_BG           = t["KW_BG"];   KW_FG  = t["KW_FG"];   KW_BORDER = t["KW_BORDER"]
    TAG_BG          = t["TAG_BG"];  TAG_BORDER = t["TAG_BORDER"]
    ENG_BORDER      = t["ENG_BORDER"]; ENG_FG = t["ENG_FG"]


FONT_FAMILY = "'Inter', 'Segoe UI', 'SF Pro Display', sans-serif"
FONT_BASE   = 16
FONT_INPUT  = 16
FONT_RESULT = 15
FONT_SMALL  = 14
FONT_TITLE  = 20


def _make_global_style() -> str:
    """Build the application stylesheet from current colour globals."""
    return f"""
    QMainWindow, QWidget {{
        background-color: {BG};
        color: {TEXT};
        font-family: {FONT_FAMILY};
        font-size: {FONT_BASE}px;
    }}
    QTextEdit {{
        background-color: {SURFACE};
        color: {TEXT};
        border: 1.5px solid {BORDER};
        border-radius: 10px;
        padding: 12px 14px;
        font-family: {FONT_FAMILY};
        font-size: {FONT_INPUT}px;
        line-height: 1.6;
        selection-background-color: #2563EB22;
    }}
    QTextEdit:focus {{
        border-color: {ACCENT};
    }}
    QTextEdit[readOnly="true"] {{
        color: {TEXT};
        background-color: {SURFACE};
    }}
    QPushButton {{
        background-color: {SURFACE};
        color: {TEXT};
        border: 1.5px solid {BORDER};
        border-radius: 8px;
        padding: 8px 20px;
        font-family: {FONT_FAMILY};
        font-size: {FONT_BASE}px;
    }}
    QPushButton:hover {{
        border-color: {ACCENT};
        color: {ACCENT};
        background-color: {BTN_HOVER};
    }}
    QPushButton:disabled {{
        color: {DIM};
        border-color: {BORDER};
        background-color: {BG};
    }}
    QPushButton#analyzeBtn {{
        background-color: {ACCENT};
        color: #FFFFFF;
        border: none;
        font-weight: 700;
        letter-spacing: 0.5px;
    }}
    QPushButton#analyzeBtn:hover {{
        background-color: {ANALYZE_HOVER};
    }}
    QPushButton#analyzeBtn:pressed {{
        background-color: {ANALYZE_PRESSED};
    }}
    QPushButton#analyzeBtn:disabled {{
        background-color: {BORDER};
        color: {SUBTEXT};
    }}
    QPushButton#exportBtn {{
        background-color: {EXPORT_BG};
        color: {PURPLE};
        border: 1.5px solid {EXPORT_BORDER};
    }}
    QPushButton#exportBtn:hover {{
        background-color: {EXPORT_HOVER};
        border-color: {PURPLE};
    }}
    QPushButton#explainBtn {{
        background-color: {EXPORT_BG};
        color: {PURPLE};
        border: 1.5px solid {EXPORT_BORDER};
    }}
    QPushButton#explainBtn:hover {{
        background-color: {EXPORT_HOVER};
        border-color: {PURPLE};
    }}
    QPushButton#explainBtn:disabled {{
        color: {DIM};
        border-color: {BORDER};
        background-color: {BG};
    }}
    QPushButton#settingsBtn {{
        background: {SURFACE};
        border: 1.5px solid {BORDER};
        border-radius: 8px;
        color: {SUBTEXT};
        font-size: 14px;
        padding: 5px 12px;
    }}
    QPushButton#settingsBtn:hover {{
        border-color: {ACCENT};
        color: {ACCENT};
        background-color: {BTN_HOVER};
    }}
    QPushButton#tabBtn {{
        background: transparent;
        border: none;
        border-top: 2px solid transparent;
        border-radius: 0;
        color: {SUBTEXT};
        font-family: {FONT_FAMILY};
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 1.2px;
        padding: 10px 24px 12px 24px;
    }}
    QPushButton#tabBtn[active="true"] {{
        color: {TEXT};
        background-color: {SURFACE};
        border-top: 2px solid {ACCENT};
    }}
    QPushButton#tabBtn:hover {{
        color: {TEXT};
        background-color: rgba(255,255,255,0.6);
    }}
    QProgressBar {{
        background-color: {BORDER};
        border: none;
        border-radius: 6px;
        height: 14px;
        text-align: center;
        color: {SURFACE};
        font-size: 11px;
        font-weight: 700;
        font-family: {FONT_FAMILY};
    }}
    QProgressBar::chunk {{
        background-color: {ACCENT};
        border-radius: 6px;
    }}
    QScrollBar:vertical {{
        background: {BG};
        width: 6px;
        border: none;
    }}
    QScrollBar::handle:vertical {{
        background: {BORDER};
        border-radius: 3px;
        min-height: 24px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {SUBTEXT};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    QScrollBar:horizontal {{
        background: {BG};
        height: 6px;
        border: none;
    }}
    QScrollBar::handle:horizontal {{
        background: {BORDER};
        border-radius: 3px;
        min-width: 24px;
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
    QMenu {{
        background-color: #FFFFFF;
        color: #1A2028;
        border: 1px solid #CCCCCC;
        padding: 4px;
        font-family: {FONT_FAMILY};
        font-size: 14px;
    }}
    QMenu::item {{
        padding: 6px 28px 6px 14px;
        color: #1A2028;
        background-color: #FFFFFF;
    }}
    QMenu::item:selected {{
        background-color: #D6E4F0;
        color: #1A2028;
    }}
    QMenu::item:disabled {{
        color: #AAAAAA;
    }}
    QMenu::separator {{
        height: 1px;
        background: #DDDDDD;
        margin: 4px 8px;
    }}
"""


# ── Circular progress widget ───────────────────────────────────────────────────

class CircularProgress(QWidget):
    """Tiny inline spinner for the footer status bar."""

    SIZE   = 18
    RING_W = 2

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(self.SIZE, self.SIZE)
        self._indeterminate = False
        self._value         = 0
        self._spin_angle    = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self.hide()

    def set_value(self, pct: int):
        self._indeterminate = False
        self._timer.stop()
        self._value = max(0, min(100, pct))
        self.show()
        self.update()

    def start_spin(self):
        self._indeterminate = True
        self._value = 0
        if not self._timer.isActive():
            self._timer.start(14)
        self.show()
        self.update()

    def stop(self):
        self._timer.stop()
        self._indeterminate = False
        self.hide()

    def _tick(self):
        self._spin_angle = (self._spin_angle - 5) % 360
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        pad  = self.RING_W + 1
        rect = QRectF(pad, pad, w - pad * 2, h - pad * 2)

        # Track
        pen = QPen(QColor(DIM))
        pen.setWidth(self.RING_W)
        pen.setCapStyle(Qt.FlatCap)
        p.setPen(pen)
        p.drawEllipse(rect)

        # Arc
        pen.setColor(QColor(ACCENT))
        pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)

        if self._indeterminate:
            start_angle = int((90 + self._spin_angle) * 16)
            span_angle  = -120 * 16
        else:
            start_angle = 90 * 16
            span_angle  = -int(self._value * 3.6) * 16

        p.drawArc(rect, start_angle, span_angle)
        p.end()


# ── Background worker threads ──────────────────────────────────────────────────

class ModelLoaderThread(QThread):
    progress = pyqtSignal(str, int)
    finished = pyqtSignal(bool)

    def run(self):
        def cb(msg, pct=-1):
            self.progress.emit(msg, pct)
        try:
            from analyzer import get_model
            model = get_model()
            model.load_or_train(progress_callback=cb)
            self.finished.emit(True)
        except Exception as e:
            self.progress.emit(f"Model error: {e}", -1)
            self.finished.emit(False)


class AnalyzerThread(QThread):
    progress = pyqtSignal(str, int)
    finished = pyqtSignal(dict)
    error    = pyqtSignal(str)

    def __init__(self, email_text, api_key=""):
        super().__init__()
        self.email_text = email_text
        self.api_key    = api_key

    def run(self):
        def cb(msg, pct=-1):
            self.progress.emit(msg, pct)
        try:
            import analyzer
            result = analyzer.analyze(
                self.email_text,
                api_key=self.api_key,
                progress_callback=cb
            )
            self.finished.emit(result)
        except (ValueError, RuntimeError) as e:
            self.error.emit(str(e))


class ImageReaderThread(QThread):
    finished = pyqtSignal(str)
    error    = pyqtSignal(str)
    chunk    = pyqtSignal(str)

    def __init__(self, image_path: str):
        super().__init__()
        self.image_path = image_path

    def run(self):
        try:
            import image_reader
            text = image_reader.extract_text_from_image(
                self.image_path, chunk_callback=self.chunk.emit
            )
            self.finished.emit(text)
        except Exception as e:
            self.error.emit(str(e))


class SummarizerThread(QThread):
    finished = pyqtSignal(str)
    error    = pyqtSignal(str)
    chunk    = pyqtSignal(str)

    def __init__(self, result: dict):
        super().__init__()
        self.result = result

    def run(self):
        try:
            import summarizer
            text = summarizer.generate_summary(
                self.result, chunk_callback=self.chunk.emit
            )
            self.finished.emit(text)
        except Exception as e:
            self.error.emit(str(e))


class VTURLCheckThread(QThread):
    """Checks a single URL/domain/IP against VirusTotal in the background."""
    finished = pyqtSignal(str, dict)   # (original_url, result_dict)
    error    = pyqtSignal(str, str)    # (original_url, error_message)

    def __init__(self, url: str, api_key: str):
        super().__init__()
        self.url     = url
        self.api_key = api_key

    def run(self):
        try:
            import re
            from virustotal import lookup_ip, lookup_domain, is_ip_address
            # Strip protocol and path to get the bare target
            stripped = re.sub(r'^https?://', '', self.url, flags=re.IGNORECASE)
            target   = re.split(r'[/?#]', stripped)[0]
            ip = is_ip_address(target)
            result = lookup_ip(ip, self.api_key) if ip else lookup_domain(target, self.api_key)
            self.finished.emit(self.url, result)
        except Exception as e:
            self.error.emit(self.url, str(e))


# ── Per-URL VirusTotal checker panel ──────────────────────────────────────────

class URLCheckerPanel(QFrame):
    """
    Shows a scrollable list of URLs extracted from an email.
    Each row has a 'Check VT' button that queries VirusTotal
    and shows the risk result inline below the URL.
    """

    def __init__(self, urls: list, api_key: str, parent=None):
        super().__init__(parent)
        self._api_key  = api_key
        self._threads  = {}        # url → VTURLCheckThread (keep alive)
        self._result_labels = {}   # url → QLabel
        self._buttons       = {}   # url → QPushButton
        self._setup(urls)

    def _setup(self, urls):
        self.setStyleSheet(
            f"URLCheckerPanel {{ background: {SURFACE}; border: 1.5px solid {BORDER};"
            f" border-radius: 12px; }}"
        )
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 10, 16, 12)
        outer.setSpacing(6)

        # Header row
        hdr_row = QHBoxLayout()
        hdr_lbl = QLabel(f"URLS FOUND ({len(urls)})")
        hdr_lbl.setStyleSheet(
            f"color: {SUBTEXT}; font-size: 11px; font-weight: 700;"
            f" letter-spacing: 1.5px; border: none; background: transparent;"
        )
        hdr_row.addWidget(hdr_lbl)
        hdr_row.addStretch()
        if not self._api_key:
            note = QLabel("Set a VT API key to enable per-URL checks")
            note.setStyleSheet(
                f"color: {SUBTEXT}; font-size: 11px; font-style: italic;"
                f" border: none; background: transparent;"
            )
            hdr_row.addWidget(note)
        outer.addLayout(hdr_row)

        # Scrollable rows — no fixed max, expands to fill available space
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(120)
        scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
            "QWidget { background: transparent; }"
        )

        container = QWidget()
        rows_layout = QVBoxLayout(container)
        rows_layout.setContentsMargins(0, 0, 4, 0)
        rows_layout.setSpacing(0)

        for url in urls:
            self._add_row(rows_layout, url)

        rows_layout.addStretch()
        scroll.setWidget(container)
        outer.addWidget(scroll)

    def _add_row(self, parent_layout, url):
        row_widget = QWidget()
        row_widget.setStyleSheet("background: transparent;")
        row_v = QVBoxLayout(row_widget)
        row_v.setContentsMargins(0, 0, 0, 0)
        row_v.setSpacing(0)

        # Thin separator
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {BORDER}; border: none;")
        row_v.addWidget(sep)

        # URL label + button on same row
        h = QHBoxLayout()
        h.setContentsMargins(0, 6, 0, 6)
        h.setSpacing(8)

        display = url if len(url) <= 64 else url[:62] + "…"
        url_lbl = QLabel(display)
        url_lbl.setToolTip(url)
        url_lbl.setStyleSheet(
            f"font-family: Consolas, 'Courier New', monospace; font-size: 13px;"
            f" color: {TEXT}; background: transparent; border: none;"
        )
        url_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        btn = QPushButton("Check VirusTotal")
        btn.setFixedHeight(30)
        btn.setMinimumWidth(140)
        btn.setStyleSheet(
            f"QPushButton {{ background: {ACCENT}; color: #FFFFFF; border: none;"
            f" border-radius: 6px; font-size: 13px; font-weight: 600; padding: 0 16px; }}"
            f"QPushButton:hover {{ background: {ANALYZE_HOVER}; }}"
            f"QPushButton:disabled {{ background: {BORDER}; color: {SUBTEXT}; }}"
        )
        if not self._api_key:
            btn.setEnabled(False)

        self._buttons[url] = btn
        h.addWidget(url_lbl)
        h.addWidget(btn)
        row_v.addLayout(h)

        # Result label — hidden until VT check completes
        result_lbl = QLabel()
        result_lbl.setWordWrap(True)
        result_lbl.setTextFormat(Qt.RichText)
        result_lbl.setStyleSheet(
            "padding: 0 0 6px 0; border: none; background: transparent;"
        )
        result_lbl.hide()
        self._result_labels[url] = result_lbl
        row_v.addWidget(result_lbl)

        parent_layout.addWidget(row_widget)

        # Capture url in default arg to avoid closure-over-loop bug
        btn.clicked.connect(lambda checked=False, u=url: self._check_url(u))

    def _check_url(self, url):
        btn = self._buttons.get(url)
        if btn:
            btn.setEnabled(False)
            btn.setText("…")

        thread = VTURLCheckThread(url, self._api_key)
        self._threads[url] = thread   # keep reference so it isn't GC'd
        thread.finished.connect(self._on_done)
        thread.error.connect(self._on_error)
        thread.start()

    def _on_done(self, url, result):
        lbl  = self._result_labels.get(url)
        btn  = self._buttons.get(url)
        risk = result.get("risk_level", "Unknown")
        rc   = RISK_COLORS.get(risk, TEXT)
        mal  = result.get("malicious",   0)
        sus  = result.get("suspicious",  0)
        harm = result.get("harmless",    0)
        undet= result.get("undetected",  0)
        total= result.get("total_engines", 0)
        engines = result.get("flagged_engines", [])

        def stat(label, val, color):
            return (
                f'<td style="text-align:center; padding:6px 18px 6px 0;">'
                f'<div style="font-size:20px; font-weight:700; color:{color}; line-height:1;">{val}</div>'
                f'<div style="font-size:10px; color:{SUBTEXT}; letter-spacing:1px; margin-top:2px;">{label}</div>'
                f'</td>'
            )

        stats_row = (
            f'<table cellspacing="0" cellpadding="0" style="margin:8px 0 6px 0;">'
            f'<tr>'
            f'{stat("MALICIOUS",  mal,   RISK_COLORS["Critical"])}'
            f'{stat("SUSPICIOUS", sus,   RISK_COLORS["High"])}'
            f'{stat("HARMLESS",   harm,  RISK_COLORS["Low"])}'
            f'{stat("UNDETECTED", undet, SUBTEXT)}'
            f'{stat("TOTAL",      total, TEXT)}'
            f'</tr></table>'
        )

        engine_html = ""
        if engines:
            # Render engines in a 3-column table so they sit side-by-side cleanly
            show = engines[:30]
            # Pad to a full multiple of 3
            while len(show) % 3 != 0:
                show.append(None)
            rows = ""
            for i in range(0, len(show), 3):
                cells = ""
                for e in show[i:i+3]:
                    if e:
                        cells += (
                            f'<td style="padding:4px 6px;">'
                            f'<span style="background:{ENG_BORDER}; color:{ENG_FG};'
                            f' border:1px solid {ENG_FG}44; border-radius:6px;'
                            f' padding:4px 10px; font-size:12px; font-weight:600;'
                            f' white-space:nowrap;">{_esc(e)}</span>'
                            f'</td>'
                        )
                    else:
                        cells += '<td></td>'
                rows += f'<tr>{cells}</tr>'
            extra = (
                f'<tr><td colspan="3" style="padding:4px 6px; color:{SUBTEXT}; font-size:11px;">'
                f'+{len(engines)-30} more engines…</td></tr>'
                if len(engines) > 30 else ""
            )
            engine_html = (
                f'<p style="margin:10px 0 6px 0; color:{SUBTEXT}; font-size:10px;'
                f' font-weight:700; letter-spacing:1.5px;">'
                f'FLAGGED BY {len(engines)} ENGINES</p>'
                f'<table cellspacing="0" cellpadding="0" style="border-collapse:collapse;">'
                f'{rows}{extra}'
                f'</table>'
            )
        else:
            engine_html = (
                f'<p style="margin:8px 0 4px 0; color:{RISK_COLORS["Low"]}; font-size:12px;">'
                f'✓ No engines flagged this domain.</p>'
            )

        html = (
            f'<div style="margin:4px 0 12px 0; padding:12px 16px;'
            f' background:{rc}11; border-left:3px solid {rc}; border-radius:6px;">'
            f'<span style="background:{rc}22; color:{rc}; border:1px solid {rc}55;'
            f' border-radius:10px; padding:2px 12px; font-size:12px; font-weight:700;">'
            f'{risk.upper()}</span>'
            f'{stats_row}'
            f'{engine_html}'
            f'</div>'
        )

        if lbl:
            lbl.setText(html)
            lbl.show()
        if btn:
            btn.setText("✓ Done")

    def _on_error(self, url, msg):
        lbl = self._result_labels.get(url)
        btn = self._buttons.get(url)
        if lbl:
            lbl.setText(
                f'<span style="color:{RISK_COLORS["Critical"]}; font-size:12px;">'
                f'Error: {_esc(msg[:70])}</span>'
            )
            lbl.show()
        if btn:
            btn.setText("Retry")
            btn.setEnabled(True)
            btn.clicked.disconnect()
            btn.clicked.connect(lambda checked=False, u=url: self._check_url(u))


# ── Main window ────────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phishing Analyzer")
        self.setMinimumSize(1100, 820)
        self.resize(1280, 920)
        self._active_theme = "light"
        self.setStyleSheet(_make_global_style())
        self._last_result      = None
        self._step_start       = None
        self._model_ready      = False
        self._email_result_html = None   # stores template for AI slot injection
        self._build_ui()
        self._start_model_loader()

    # ── UI construction ────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── Header bar ────────────────────────────────────────────────────────
        header = QWidget()
        header.setObjectName("headerBar")
        header.setFixedHeight(66)
        header.setStyleSheet(
            f"#headerBar {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:0,"
            f" stop:0 #0E4F72, stop:1 {ACCENT}); border-bottom: none; }}"
        )
        hdr = QHBoxLayout(header)
        hdr.setContentsMargins(24, 0, 20, 0)
        hdr.setSpacing(14)

        # Icon in a translucent rounded box
        icon_wrap = QWidget()
        icon_wrap.setFixedSize(42, 42)
        icon_wrap.setStyleSheet(
            "background: rgba(255,255,255,0.15); border-radius: 10px;"
            " border: 1.5px solid rgba(255,255,255,0.28);"
        )
        icon_inner = QVBoxLayout(icon_wrap)
        icon_inner.setContentsMargins(0, 0, 0, 0)
        icon_inner.setAlignment(Qt.AlignCenter)
        icon_lbl = QLabel("◈")
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet("color: #FFFFFF; font-size: 20px; border: none;")
        icon_inner.addWidget(icon_lbl)
        hdr.addWidget(icon_wrap)

        # Title: two-tone using RichText label
        title_stack = QWidget()
        title_stack.setStyleSheet("background: transparent; border: none;")
        ts_layout = QVBoxLayout(title_stack)
        ts_layout.setContentsMargins(0, 0, 0, 0)
        ts_layout.setSpacing(2)

        title_lbl = QLabel("Phishing Analyzer")
        title_lbl.setStyleSheet(
            "color: #FFFFFF; font-size: 22px; font-weight: 800; border: none;"
        )

        ts_layout.addWidget(title_lbl)
        hdr.addWidget(title_stack)
        hdr.addStretch()

        self.settings_btn = QPushButton("VT Key")
        self.settings_btn.setObjectName("settingsBtn")
        self.settings_btn.setFixedHeight(28)
        self.settings_btn.setToolTip("Set your VirusTotal API key")
        self.settings_btn.clicked.connect(self._on_set_api_key)
        self.settings_btn.setStyleSheet(
            "QPushButton { background: rgba(255,255,255,0.18); color: #FFFFFF;"
            " border: 1px solid rgba(255,255,255,0.35); border-radius: 6px;"
            f" font-size: 13px; padding: 4px 12px; font-family: {FONT_FAMILY}; }}"
            "QPushButton:hover { background: rgba(255,255,255,0.30); }"
        )
        hdr.addWidget(self.settings_btn)

        # Theme toggle button
        self._theme_btn = QPushButton("🌙 Dark")
        self._theme_btn.setFixedHeight(28)
        self._theme_btn.setToolTip("Switch between light and dark theme")
        self._theme_btn.clicked.connect(self._toggle_theme)
        self._theme_btn.setStyleSheet(
            "QPushButton { background: rgba(255,255,255,0.18); color: #FFFFFF;"
            " border: 1px solid rgba(255,255,255,0.35); border-radius: 6px;"
            f" font-size: 13px; padding: 4px 12px; font-family: {FONT_FAMILY}; }}"
            "QPushButton:hover { background: rgba(255,255,255,0.30); }"
        )
        hdr.addWidget(self._theme_btn)

        self._header_widget = header   # saved for theme re-apply
        outer.addWidget(header)

        from virustotal import load_api_key
        if load_api_key():
            self.settings_btn.setText("VT Key ✓")

        # ── Body ──────────────────────────────────────────────────────────────
        body = QHBoxLayout()
        body.setContentsMargins(24, 18, 20, 16)
        body.setSpacing(16)

        # Left column
        left_col = QVBoxLayout()
        left_col.setSpacing(12)
        self._left_col = left_col   # keep reference for dynamic URL panel insertion

        # Input card
        card = QFrame()
        card.setStyleSheet(
            f"QFrame {{ background-color: {SURFACE}; border: 1.5px solid {BORDER};"
            f" border-radius: 12px; }}"
        )
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 16)
        card_layout.setSpacing(0)

        card_layout.addWidget(self._make_tab_bar())

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {BORDER}; border: none;")
        card_layout.addWidget(sep)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet("border: none;")
        self.stack.addWidget(self._make_paste_page())
        self.stack.addWidget(self._make_upload_page())
        card_layout.addWidget(self.stack)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(20, 10, 20, 0)
        btn_row.setSpacing(8)

        self.analyze_btn = QPushButton("Analyze")
        self.analyze_btn.setObjectName("analyzeBtn")
        self.analyze_btn.setFixedHeight(38)
        self.analyze_btn.setMinimumWidth(110)
        self.analyze_btn.setEnabled(False)
        self.analyze_btn.clicked.connect(self._on_analyze)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setFixedHeight(38)
        self.clear_btn.clicked.connect(self._on_clear)

        self.export_btn = QPushButton("Export PDF")
        self.export_btn.setObjectName("exportBtn")
        self.export_btn.setFixedHeight(38)
        self.export_btn.setEnabled(False)
        self.export_btn.clicked.connect(self._on_export_pdf)

        self.explain_btn = QPushButton("✦  Explain with AI")
        self.explain_btn.setObjectName("explainBtn")
        self.explain_btn.setFixedHeight(38)
        self.explain_btn.setEnabled(False)
        self.explain_btn.setToolTip("Ask Qwen to explain the results in plain English")
        self.explain_btn.clicked.connect(self._on_explain)

        btn_row.addWidget(self.analyze_btn)
        btn_row.addWidget(self.clear_btn)
        btn_row.addStretch()
        btn_row.addWidget(self.explain_btn)
        btn_row.addWidget(self.export_btn)
        card_layout.addLayout(btn_row)

        left_col.addWidget(card)

        # Results panel
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        self.results_display.setMinimumHeight(300)
        self.results_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.results_display.setPlaceholderText(
            "Results will appear here after analysis…"
        )
        left_col.addWidget(self.results_display, stretch=2)

        # URL checker panel — populated after email analysis, hidden otherwise
        self._url_panel = None   # holds the current URLCheckerPanel widget

        body.addLayout(left_col, stretch=1)

        # Right column — activity log
        right_widget = QWidget()
        right_widget.setFixedWidth(280)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        log_hdr = QHBoxLayout()
        log_title = QLabel("ACTIVITY LOG")
        log_title.setStyleSheet(
            f"color: {SUBTEXT}; font-size: 12px; font-weight: 700; letter-spacing: 2px;"
        )
        self.log_clear_btn = QPushButton("Clear")
        self.log_clear_btn.setFixedHeight(28)
        self.log_clear_btn.setFixedWidth(54)
        self.log_clear_btn.clicked.connect(self._clear_log)
        self.log_clear_btn.setStyleSheet(
            f"QPushButton {{ background: {SURFACE}; color: {SUBTEXT};"
            f" border: 1.5px solid {BORDER}; border-radius: 6px;"
            f" font-size: 12px; padding: 2px 8px; font-family: {FONT_FAMILY}; }}"
            f"QPushButton:hover {{ color: {ACCENT}; border-color: {ACCENT}; background: #EBF6FA; }}"
        )
        log_hdr.addWidget(log_title)
        log_hdr.addStretch()
        log_hdr.addWidget(self.log_clear_btn)
        right_layout.addLayout(log_hdr)

        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.log_display.setStyleSheet(
            f"QTextEdit {{"
            f"  background-color: #F8FAFB;"
            f"  color: #475569;"
            f"  border: 1.5px solid {BORDER};"
            f"  border-radius: 10px;"
            f"  padding: 10px 12px;"
            f"  font-family: Consolas, 'Courier New', monospace;"
            f"  font-size: 13px;"
            f"  line-height: 1.6;"
            f"}}"
        )
        right_layout.addWidget(self.log_display, stretch=1)

        body.addWidget(right_widget)
        outer.addLayout(body, stretch=1)

        # ── Footer ────────────────────────────────────────────────────────────
        footer = QWidget()
        footer.setObjectName("footerBar")
        footer.setFixedHeight(26)
        footer.setStyleSheet(
            f"#footerBar {{ background-color: {BG};"
            f" border-top: 1px solid {BORDER}; }}"
        )
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(28, 0, 20, 0)

        # Inline spinner + status label on the same row
        self._spinner = CircularProgress(footer)
        footer_layout.addWidget(self._spinner)

        self.status_lbl = QLabel("Loading ML model…")
        self.status_lbl.setStyleSheet(
            f"color: {SUBTEXT}; font-size: 13px; border: none; padding-left: 6px;"
        )
        footer_layout.addWidget(self.status_lbl)
        footer_layout.addStretch()
        outer.addWidget(footer)

    # ── Spinner helpers ────────────────────────────────────────────────────────

    def _show_spinner(self, msg: str = "", pct: int = -1):
        if pct < 0:
            self._spinner.start_spin()
            self.status_lbl.setText(msg)
        else:
            self._spinner.set_value(pct)
            self.status_lbl.setText(f"{msg}  {pct}%")

    def _hide_spinner(self):
        self._spinner.stop()

    # ── Tab bar + pages ────────────────────────────────────────────────────────

    def _make_tab_bar(self):
        bar = QWidget()
        bar.setObjectName("tabBarWidget")
        bar.setFixedHeight(46)
        bar.setStyleSheet(
            "#tabBarWidget { background-color: #E8ECF0;"
            " border-top-left-radius: 10px; border-top-right-radius: 10px; }"
        )
        row = QHBoxLayout(bar)
        row.setContentsMargins(8, 0, 8, 0)
        row.setSpacing(0)

        self.tab_paste  = QPushButton("PASTE")
        self.tab_upload = QPushButton("UPLOAD FILE")
        for btn in (self.tab_paste, self.tab_upload):
            btn.setObjectName("tabBtn")
            row.addWidget(btn)
        row.addStretch()

        self.tab_paste.setProperty("active", "true")
        self.tab_paste.setStyle(self.tab_paste.style())
        self.tab_paste.clicked.connect(lambda: self._switch_tab(0))
        self.tab_upload.clicked.connect(lambda: self._switch_tab(1))
        self._tab_bar_widget = bar   # saved for theme re-apply
        return bar

    def _make_paste_page(self):
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 14, 20, 0)

        self.email_input = QTextEdit()
        self.email_input.setPlaceholderText(
            "Paste the full email here (headers + body), or enter an IP address or domain…"
        )
        self.email_input.setMinimumHeight(240)
        self.email_input.setStyleSheet(
            f"QTextEdit {{"
            f"  background-color: {BG};"
            f"  border: 1.5px solid {BORDER};"
            f"  border-radius: 10px;"
            f"  color: {TEXT};"
            f"  font-size: {FONT_INPUT}px;"
            f"  padding: 14px 16px;"
            f"  line-height: 1.6;"
            f"}}"
            f"QTextEdit:focus {{"
            f"  border-color: {ACCENT};"
            f"}}"
        )
        layout.addWidget(self.email_input)
        return page

    def _make_upload_page(self):
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 14, 20, 0)
        layout.setAlignment(Qt.AlignCenter)

        drop_box = QFrame()
        drop_box.setFixedHeight(200)
        drop_box.setStyleSheet(
            f"QFrame {{ border: 2px dashed {BORDER}; border-radius: 12px;"
            f" background: {BG}; }}"
        )
        box_layout = QVBoxLayout(drop_box)
        box_layout.setAlignment(Qt.AlignCenter)
        box_layout.setSpacing(10)

        icon_lbl = QLabel("↑")
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(f"font-size: 36px; color: {ACCENT}; border: none;")
        box_layout.addWidget(icon_lbl)

        self.file_name_lbl = QLabel("No file selected")
        self.file_name_lbl.setAlignment(Qt.AlignCenter)
        self.file_name_lbl.setStyleSheet(
            f"color: {SUBTEXT}; font-size: {FONT_BASE}px; border: none;"
        )
        box_layout.addWidget(self.file_name_lbl)

        choose_btn = QPushButton("Choose File")
        choose_btn.setFixedWidth(130)
        choose_btn.setFixedHeight(34)
        choose_btn.clicked.connect(self._on_upload)
        box_layout.addWidget(choose_btn, alignment=Qt.AlignCenter)

        layout.addWidget(drop_box)

        hint = QLabel(".eml  ·  .txt  ·  .msg  ·  .png  ·  .jpg  ·  .webp")
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet(
            f"color: {SUBTEXT}; font-size: 11px; padding-top: 8px; letter-spacing: 1px;"
        )
        layout.addWidget(hint)

        self.image_status_lbl = QLabel("")
        self.image_status_lbl.setAlignment(Qt.AlignCenter)
        self.image_status_lbl.setStyleSheet(
            f"color: {ACCENT}; font-size: 12px; padding-top: 4px;"
        )
        layout.addWidget(self.image_status_lbl)

        return page

    # ── Activity log helpers ───────────────────────────────────────────────────

    def _log(self, msg: str, color: str = ""):
        ts    = time.strftime("%H:%M:%S")
        color = color or LOG_FG
        line  = (
            f'<span style="color:{LOG_TS};">[{ts}]</span> '
            f'<span style="color:{color};">{_esc(msg)}</span>'
        )
        self.log_display.append(line)
        self.log_display.verticalScrollBar().setValue(
            self.log_display.verticalScrollBar().maximum()
        )

    def _clear_log(self):
        self.log_display.clear()

    # ── Model loading ──────────────────────────────────────────────────────────

    def _start_model_loader(self):
        self._model_start = time.time()
        self._log("Starting ML model load…", ACCENT)
        self._show_spinner("Loading model…")
        self._loader = ModelLoaderThread()
        self._loader.progress.connect(self._on_model_progress)
        self._loader.finished.connect(self._on_model_ready)
        self._loader.start()

    def _on_model_progress(self, msg, pct):
        self.status_lbl.setText(msg)
        self._log(msg)
        if pct >= 0:
            self._show_spinner("Loading model", pct)
        # else: keep spinner going

    def _on_model_ready(self, success):
        elapsed = time.time() - self._model_start
        self._hide_spinner()
        self._model_ready = True
        if success:
            self.status_lbl.setText("Model ready — paste an email to begin.")
            self._log(f"✓ ML model ready  ({elapsed:.1f}s)", RISK_COLORS["Low"])
        else:
            self.status_lbl.setText("Model failed — rule-based checks only.")
            self._log("✗ ML model failed to load — rule-based checks only.", RISK_COLORS["Critical"])
        self.analyze_btn.setEnabled(True)

    # ── Analysis ───────────────────────────────────────────────────────────────

    def _on_analyze(self):
        from virustotal import load_api_key, is_ip_address, is_domain
        email_text = self.email_input.toPlainText().strip()
        if not email_text:
            self.results_display.setText("No content to analyze.")
            return

        api_key = load_api_key()
        if is_ip_address(email_text) or is_domain(email_text):
            if not api_key:
                QMessageBox.warning(
                    self, "API Key Required",
                    "A VirusTotal API key is needed to look up IPs and domains.\n\n"
                    "Click the VT Key button and paste your key.\n"
                    "(Free key available at virustotal.com)"
                )
                return

        self.analyze_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
        self.results_display.setHtml(
            f'<span style="color:{SUBTEXT}; font-family:{FONT_FAMILY}; font-size:{FONT_BASE}px;">Analyzing…</span>'
        )
        self._show_spinner("Analyzing…")
        self._step_start = time.time()
        self._log("── Analysis started ──", ACCENT)

        self._analyzer = AnalyzerThread(email_text, api_key=api_key)
        self._analyzer.progress.connect(self._on_analysis_progress)
        self._analyzer.finished.connect(self._on_analysis_done)
        self._analyzer.error.connect(self._on_analysis_error)
        self._analyzer.start()

    def _on_analysis_progress(self, msg, pct):
        self.status_lbl.setText(msg)
        self._log(msg)
        if pct >= 0:
            self._show_spinner("Analyzing", pct)
        # else: keep spinner

    def _on_analysis_done(self, result):
        elapsed = time.time() - self._step_start if self._step_start else 0
        self._last_result = result
        self._hide_spinner()
        self.analyze_btn.setEnabled(True)
        self.export_btn.setEnabled(True)
        self.explain_btn.setEnabled(True)

        rtype = result.get("type", "email")
        if rtype in ("ip", "domain"):
            subject = result.get("ip") or result.get("domain", "?")
            risk    = result.get("risk_level", "?")
            mal     = result.get("malicious", 0)
            total   = result.get("total_engines", 0)
            self._log(
                f"✓ {rtype.upper()} lookup: {subject}  |  Risk: {risk}  |  {mal}/{total} engines  ({elapsed:.1f}s)",
                RISK_COLORS.get(risk, TEXT)
            )
        else:
            score = result.get("score", 0)
            risk  = result.get("risk_level", "?")
            ml_c  = round(result.get("ml_confidence", 0) * 100, 1)
            kw    = int(result.get("keyword_score", 0))
            self._log(
                f"✓ Done  |  Score: {score}/100 ({risk})  |  ML: {ml_c}%  |  Keywords: {kw}/100  ({elapsed:.1f}s)",
                RISK_COLORS.get(risk, TEXT)
            )

        try:
            import report
            report.log_to_history(result)
        except Exception:
            pass

        if result.get("type") in ("ip", "domain"):
            self._display_vt_result(result)
        else:
            self._display_email_result(result)
        self.status_lbl.setText("Analysis complete.")

    def _on_analysis_error(self, msg):
        self._hide_spinner()
        self.analyze_btn.setEnabled(True)
        self.export_btn.setEnabled(False)
        self.results_display.setHtml(
            f'<p style="color:{RISK_COLORS["Critical"]}; font-family:{FONT_FAMILY}; padding:8px;">'
            f'<b>Error:</b> {_esc(msg)}</p>'
        )
        self.status_lbl.setText("Analysis failed.")
        self._log(f"✗ Error: {msg}", RISK_COLORS["Critical"])

    # ── Results rendering ──────────────────────────────────────────────────────

    def _display_vt_result(self, r):
        self._email_result_html = None   # VT results don't use the slot system
        kind       = r.get("type", "ip")
        risk       = r.get("risk_level", "Low")
        rc         = RISK_COLORS.get(risk, TEXT)
        malicious  = r.get("malicious", 0)
        suspicious = r.get("suspicious", 0)
        harmless   = r.get("harmless", 0)
        undetected = r.get("undetected", 0)
        total      = r.get("total_engines", 0)
        engines    = r.get("flagged_engines", [])
        reputation = r.get("reputation", 0)
        tags       = r.get("tags", [])

        if kind == "ip":
            subject    = r.get("ip", "")
            kind_label = "IP REPUTATION"
            meta_lines = [
                f'Country: <b style="color:{TEXT};">{_esc(r.get("country","?"))}</b>'
                f'&nbsp;·&nbsp; ASN: <b style="color:{TEXT};">{r.get("asn","?")}</b>',
                f'Network: <b style="color:{TEXT};">{_esc(r.get("network","?"))}</b>'
                f'&nbsp;·&nbsp; Owner: <b style="color:{TEXT};">{_esc(r.get("as_owner","?"))}</b>',
            ]
        else:
            subject    = r.get("domain", "")
            kind_label = "DOMAIN REPUTATION"
            cats       = r.get("categories", [])
            dns        = r.get("dns_records", [])
            meta_lines = [
                f'Registrar: <b style="color:{TEXT};">{_esc(r.get("registrar","?"))}</b>'
                f'&nbsp;·&nbsp; Created: <b style="color:{TEXT};">{r.get("creation_date","?")}</b>',
                f'Categories: <b style="color:{TEXT};">{_esc(", ".join(cats[:4]) or "—")}</b>',
                f'DNS: <span style="color:{TEXT};">{" &nbsp;·&nbsp; ".join(_esc(d) for d in dns[:3]) or "—"}</span>',
            ]

        # Score bar: malicious engines as % of total
        bar_pct = round(malicious / total * 100) if total > 0 else 0
        bar_empty = 100 - bar_pct

        rep_color = RISK_COLORS["Low"] if reputation >= 0 else RISK_COLORS["High"]

        def stat_card(label, val, color):
            return (
                f'<td width="110" style="text-align:center; padding:14px 8px;">'
                f'<div style="font-size:28px; font-weight:700; color:{color}; line-height:1;">{val}</div>'
                f'<div style="font-size:11px; color:{SUBTEXT}; letter-spacing:1px; margin-top:4px;">{label}</div>'
                f'</td>'
            )

        meta_html = "<br>".join(
            f'<span style="color:{SUBTEXT};">{m}</span>' for m in meta_lines
        )

        engine_html = ""
        if engines:
            rows = "".join(
                f'<div style="padding:4px 0; border-bottom:1px solid {ENG_BORDER}; font-size:13px;">'
                f'<span style="color:{SUBTEXT}; font-size:11px; margin-right:8px;">{i+1:02d}</span>'
                f'<span style="color:{ENG_FG};">{_esc(e)}</span>'
                f'</div>'
                for i, e in enumerate(engines[:24])
            )
            extra = (
                f'<div style="padding:4px 0; color:{SUBTEXT}; font-size:12px;">+{len(engines)-24} more…</div>'
                if len(engines) > 24 else ""
            )
            engine_html = (
                f'<p style="margin:14px 0 6px 0; color:{SUBTEXT}; font-size:12px; font-weight:600; letter-spacing:1.5px;">'
                f'FLAGGED ENGINES ({len(engines)})</p>'
                f'<div style="margin:0;">{rows}{extra}</div>'
            )

        tag_html = ""
        if tags:
            tag_pills = " ".join(
                f'<span style="background:{TAG_BG}; color:{ACCENT}; border:1px solid {TAG_BORDER};'
                f' border-radius:20px; padding:2px 10px; margin:2px; font-size:12px;">'
                f'{_esc(t)}</span>'
                for t in tags
            )
            tag_html = (
                f'<p style="margin:14px 0 6px 0; color:{SUBTEXT}; font-size:11px; font-weight:600; letter-spacing:1.5px;">TAGS</p>'
                f'<p style="margin:0 0 8px 0; line-height:2;">{tag_pills}</p>'
            )

        html = f"""
        <div style="font-family:{FONT_FAMILY}; font-size:{FONT_RESULT}px; color:{TEXT}; padding:12px 16px;">

          <p style="margin:0 0 2px 0; font-size:11px; font-weight:600; letter-spacing:1.5px; color:{SUBTEXT};">
            {kind_label}
          </p>

          <div style="margin:4px 0 0 0;">
            <span style="font-size:22px; font-weight:700; color:{rc};">{_esc(subject)}</span>
            <span style="margin-left:12px; background:{rc}22; color:{rc}; border:1px solid {rc}66;
                         border-radius:20px; padding:3px 14px; font-size:12px; font-weight:600;
                         letter-spacing:1px;">{risk.upper()}</span>
          </div>

          <table cellspacing="0" cellpadding="0"
                 style="width:100%; margin:10px 0 2px 0; border-collapse:collapse;">
            <tr>
              <td style="background:{rc}; height:3px; width:{bar_pct}%;"></td>
              <td style="background:{DIM}; height:3px;"></td>
            </tr>
          </table>

          <p style="margin:6px 0 14px 0; font-size:12px; line-height:1.7;">
            {meta_html}
            <br><span style="color:{SUBTEXT};">Reputation score:</span>
            <b style="color:{rep_color};">{reputation}</b>
            &nbsp;·&nbsp;
            <span style="color:{SUBTEXT};">Source: VirusTotal API v3</span>
          </p>

          <hr style="border:none; border-top:1px solid {BORDER}; margin:0 0 4px 0;">

          <table cellspacing="0" cellpadding="0" style="width:100%;">
            <tr>
              {stat_card("MALICIOUS",  malicious,  RISK_COLORS["Critical"])}
              {stat_card("SUSPICIOUS", suspicious, RISK_COLORS["High"])}
              {stat_card("HARMLESS",   harmless,   RISK_COLORS["Low"])}
              {stat_card("UNDETECTED", undetected, SUBTEXT)}
              {stat_card("TOTAL",      total,      TEXT)}
            </tr>
          </table>

          <hr style="border:none; border-top:1px solid {BORDER}; margin:4px 0 12px 0;">

          {tag_html}
          {engine_html}

        </div>
        """
        self.results_display.setHtml(html)

    def _display_email_result(self, result):
        score      = result.get("score", 0)
        risk       = result.get("risk_level", "Low")
        rc         = RISK_COLORS.get(risk, TEXT)
        ml_pct     = round(result.get("ml_confidence", 0) * 100, 1)
        ml_label   = result.get("ml_label", 0)
        ml_name    = result.get("ml_model_name", "Random Forest + TF-IDF")
        kw_score   = result.get("keyword_score", 0)
        url_score  = result.get("url_score", 0)
        bl_score   = result.get("blacklist_score", 0)
        kw_hits    = result.get("keyword_hits", [])
        urls_found = result.get("urls_found", [])
        findings   = result.get("findings", [])

        ml_contrib  = round(ml_pct * 0.40, 1) if ml_label == 1 else 0.0
        kw_contrib  = round(kw_score * 0.25, 1)
        url_contrib = round(url_score * 0.20, 1)
        bl_contrib  = round(bl_score * 0.15, 1)

        bar_pct   = min(100, max(0, score))
        bar_empty = 100 - bar_pct

        ml_verdict       = "Phishing" if ml_label == 1 else "Safe"
        ml_verdict_color = RISK_COLORS["High"] if ml_label == 1 else RISK_COLORS["Low"]

        def score_row(label, raw, weight, contrib, color):
            return (
                f'<tr>'
                f'<td width="190" style="padding:7px 16px 7px 0; color:{SUBTEXT}; white-space:nowrap;">{label}</td>'
                f'<td width="110" style="padding:7px 16px 7px 0; color:{color}; font-weight:600; white-space:nowrap;">{raw}</td>'
                f'<td width="80"  style="padding:7px 16px 7px 0; color:{SUBTEXT}; white-space:nowrap;">{weight}</td>'
                f'<td width="110" style="padding:7px 0; color:{color}; font-weight:600; white-space:nowrap;">+{contrib} pts</td>'
                f'</tr>'
            )

        # Keywords
        if kw_hits:
            pills = " ".join(
                f'<span style="background:{KW_BG}; color:{KW_FG}; border:1px solid {KW_BORDER};'
                f' border-radius:20px; padding:2px 10px; margin:2px; font-size:12px;">'
                f'{_esc(kw)}</span>'
                for kw in kw_hits
            )
            kw_section = (
                f'<p style="margin:14px 0 6px 0; color:{SUBTEXT}; font-size:11px;'
                f' font-weight:600; letter-spacing:1.5px;">FLAGGED KEYWORDS ({len(kw_hits)})</p>'
                f'<p style="margin:0 0 10px 0; line-height:2;">{pills}</p>'
            )
        else:
            kw_section = (
                f'<p style="margin:14px 0 4px 0; color:{SUBTEXT}; font-size:12px;">'
                f'No phishing keywords detected.</p>'
            )

        # URLs — rendered as interactive widget below results, not in HTML
        url_section = ""   # removed from HTML; see URLCheckerPanel below

        # Other findings
        other = [f for f in findings if "keyword" not in f.lower()]
        if other:
            finding_lines = "".join(
                f'<li style="margin:4px 0; color:{SUBTEXT}; font-size:12px;">{_esc(f)}</li>'
                for f in other
            )
            findings_section = (
                f'<p style="margin:14px 0 6px 0; color:{SUBTEXT}; font-size:11px;'
                f' font-weight:600; letter-spacing:1.5px;">OTHER FINDINGS</p>'
                f'<ul style="margin:0; padding-left:16px;">{finding_lines}</ul>'
            )
        else:
            findings_section = ""

        ai_placeholder = (
            f'<div style="padding:14px 16px; background:{AI_PH_BG};'
            f' border:1.5px dashed {BORDER}; border-radius:10px;'
            f' text-align:center;">'
            f'<p style="color:{SUBTEXT}; font-size:13px; margin:0; line-height:1.8;">'
            f'Click <b style="color:{PURPLE};">✦ Explain with AI</b><br>'
            f'for an AI-powered verdict</p>'
            f'</div>'
        )

        html = f"""
        <div style="font-family:{FONT_FAMILY}; font-size:{FONT_RESULT}px; color:{TEXT}; padding:12px 16px;">

          <!-- Score hero (full width, stays compact) -->
          <div style="margin:0 0 2px 0;">
            <span style="font-size:48px; font-weight:700; color:{rc}; line-height:1; letter-spacing:-2px;">{score}</span>
            <span style="font-size:18px; color:{SUBTEXT}; vertical-align:bottom; padding-bottom:6px;"> / 100</span>
            <span style="margin-left:14px; background:{rc}22; color:{rc}; border:1px solid {rc}66;
                         border-radius:20px; padding:4px 16px; font-size:13px; font-weight:600;
                         letter-spacing:1px; vertical-align:middle;">{risk.upper()}</span>
          </div>

          <!-- Score bar -->
          <table cellspacing="0" cellpadding="0"
                 style="width:100%; margin:8px 0 4px 0; border-collapse:collapse;">
            <tr>
              <td style="background:{rc}; height:3px; width:{bar_pct}%;"></td>
              <td style="background:{DIM}; height:3px;"></td>
            </tr>
          </table>

          <!-- Model line -->
          <p style="margin:6px 0 0 0; font-size:12px; color:{SUBTEXT}; line-height:1.6;">
            {_esc(ml_name)}&nbsp;&nbsp;·&nbsp;&nbsp;
            ML verdict: <b style="color:{ml_verdict_color};">{ml_verdict}</b>
            &nbsp;({ml_pct}% confidence)
          </p>

          <hr style="border:none; border-top:1px solid {BORDER}; margin:14px 0;">

          <!-- Two-column: Score breakdown LEFT | AI Verdict RIGHT (equal height, both tall) -->
          <table width="100%" cellspacing="0" cellpadding="0">
            <tr>
              <td width="55%" style="vertical-align:top; padding-right:20px;">
                <p style="margin:0 0 8px 0; color:{SUBTEXT}; font-size:11px;
                          font-weight:600; letter-spacing:1.5px;">SCORE BREAKDOWN</p>
                <table cellspacing="0" cellpadding="0" style="font-size:{FONT_SMALL}px; width:100%;">
                  <tr>
                    <td width="150" style="padding:6px 12px 6px 0; color:{SUBTEXT}; font-size:11px; font-weight:600; letter-spacing:1px; white-space:nowrap;">COMPONENT</td>
                    <td width="90"  style="padding:6px 12px 6px 0; color:{SUBTEXT}; font-size:11px; font-weight:600; letter-spacing:1px; white-space:nowrap;">SCORE</td>
                    <td width="70"  style="padding:6px 12px 6px 0; color:{SUBTEXT}; font-size:11px; font-weight:600; letter-spacing:1px; white-space:nowrap;">WEIGHT</td>
                    <td width="90"  style="padding:6px 0;           color:{SUBTEXT}; font-size:11px; font-weight:600; letter-spacing:1px; white-space:nowrap;">POINTS</td>
                  </tr>
                  {score_row("ML Classifier",    f"{ml_pct}%",          "× 0.40", ml_contrib,
                             RISK_COLORS["High"] if ml_label == 1 else RISK_COLORS["Low"])}
                  {score_row("Keyword Analysis", f"{kw_score:.0f}/100",  "× 0.25", kw_contrib,
                             RISK_COLORS["Medium"] if kw_contrib > 0 else SUBTEXT)}
                  {score_row("URL Heuristics",   f"{url_score:.0f}/100", "× 0.20", url_contrib,
                             RISK_COLORS["Medium"] if url_contrib > 0 else SUBTEXT)}
                  {score_row("Blacklist Check",  f"{bl_score:.0f}/100",  "× 0.15", bl_contrib,
                             RISK_COLORS["Critical"] if bl_contrib > 0 else SUBTEXT)}
                  <tr>
                    <td colspan="3" style="padding:10px 12px 4px 0; color:{TEXT}; font-weight:700;
                                           border-top:1px solid {BORDER}; white-space:nowrap;">TOTAL</td>
                    <td style="padding:10px 0 4px 0; color:{rc}; font-weight:700;
                               border-top:1px solid {BORDER}; white-space:nowrap;">= {score} pts</td>
                  </tr>
                </table>
              </td>
              <td width="45%" style="vertical-align:top;">
                __AI_SLOT__
              </td>
            </tr>
          </table>

          <hr style="border:none; border-top:1px solid {BORDER}; margin:14px 0;">

          {kw_section}
          {url_section}
          {findings_section}

        </div>
        """
        # Store template with __AI_SLOT__ sentinel for later injection
        self._email_result_html = html
        # Display with placeholder until AI runs
        self.results_display.setHtml(html.replace("__AI_SLOT__", ai_placeholder))

        # Build the URL checker panel below the results
        self._rebuild_url_panel(urls_found)

    def _rebuild_url_panel(self, urls):
        """Replace the URL checker panel widget with a fresh one."""
        from virustotal import load_api_key

        # Remove old panel if any
        if self._url_panel is not None:
            self._left_col.removeWidget(self._url_panel)
            self._url_panel.deleteLater()
            self._url_panel = None

        if not urls:
            return

        api_key = load_api_key()
        # Parent must be a QWidget — use the central widget
        panel = URLCheckerPanel(urls, api_key, parent=self.centralWidget())
        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._left_col.addWidget(panel, stretch=1)
        self._url_panel = panel

    # ── PDF export ─────────────────────────────────────────────────────────────

    def _on_export_pdf(self):
        if not self._last_result:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save PDF Report", "phishing_report.pdf", "PDF files (*.pdf)"
        )
        if not path:
            return
        try:
            import report
            saved = report.generate_pdf(self._last_result, output_path=path)
            QMessageBox.information(self, "Saved", f"Report saved to:\n{saved}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not generate PDF:\n{e}")

    # ── AI explanation ─────────────────────────────────────────────────────────

    def _on_explain(self):
        if not self._last_result:
            return

        self.explain_btn.setEnabled(False)
        self.explain_btn.setText("✦  Thinking…")
        self.status_lbl.setText("Asking Qwen to explain results…")
        self._show_spinner("AI thinking…")
        self._step_start = time.time()
        self._log("── Qwen (qwen2.5:3b) generating… ──", ACCENT)
        self.log_display.append(
            f'<span style="color:{LOG_FG}; font-size:13px;"></span>'
        )

        self._summarizer = SummarizerThread(self._last_result)
        self._summarizer.chunk.connect(self._on_summary_chunk)
        self._summarizer.finished.connect(self._on_summary_done)
        self._summarizer.error.connect(self._on_summary_error)
        self._summarizer.start()

    def _on_summary_chunk(self, text: str):
        cursor = self.log_display.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(text)
        self.log_display.setTextCursor(cursor)
        self.log_display.verticalScrollBar().setValue(
            self.log_display.verticalScrollBar().maximum()
        )

    def _on_summary_done(self, summary_text):
        elapsed = time.time() - self._step_start if self._step_start else 0
        self._hide_spinner()
        self.explain_btn.setEnabled(True)
        self.explain_btn.setText("✦  Explain with AI")
        self.status_lbl.setText("AI summary ready.")
        self._log(f"✓ Qwen summary ready  ({elapsed:.1f}s)", RISK_COLORS["Low"])

        brief = _extract_brief(summary_text)

        verdict_html = (
            f'<div style="padding:14px 16px; background:{AI_BG};'
            f' border:1.5px solid {AI_BORDER}; border-radius:10px;">'
            f'<p style="margin:0 0 8px 0; color:{PURPLE}; font-weight:700; font-size:13px;'
            f' letter-spacing:1px;">✦ AI VERDICT</p>'
            f'<p style="margin:0 0 10px 0; color:{TEXT}; font-size:{FONT_RESULT}px; line-height:1.7;">'
            f'{_esc(brief).replace(chr(10), "<br>")}</p>'
            f'<p style="margin:0; color:{SUBTEXT}; font-size:13px;">Full reasoning in Activity Log →</p>'
            f'</div>'
        )

        if self._email_result_html and "__AI_SLOT__" in self._email_result_html:
            # Inject verdict into the pre-allocated top-right slot
            self.results_display.setHtml(
                self._email_result_html.replace("__AI_SLOT__", verdict_html)
            )
        else:
            # Fallback for VT results — append at bottom
            current_html = self.results_display.toHtml()
            if "</body>" in current_html:
                updated = current_html.replace("</body>", verdict_html + "</body>")
            else:
                updated = current_html + verdict_html
            self.results_display.setHtml(updated)

    def _on_summary_error(self, msg):
        self._hide_spinner()
        self.explain_btn.setEnabled(True)
        self.explain_btn.setText("✦  Explain with AI")
        self.status_lbl.setText("AI summary failed.")
        self._log(f"✗ Qwen error: {msg}", RISK_COLORS["Critical"])
        QMessageBox.warning(self, "Qwen Error", f"Could not get AI summary:\n{msg}")

    # ── Theme toggle ───────────────────────────────────────────────────────────

    def _toggle_theme(self):
        new = "dark" if self._active_theme == "light" else "light"
        self._active_theme = new
        _set_theme(new)
        self.setStyleSheet(_make_global_style())
        self._reapply_inline_styles()
        self._theme_btn.setText("☀ Light" if new == "dark" else "🌙 Dark")
        # Re-render current results with new colours if available
        if self._last_result:
            if self._last_result.get("type") in ("ip", "domain"):
                self._display_vt_result(self._last_result)
            else:
                self._display_email_result(self._last_result)

    def _reapply_inline_styles(self):
        """Re-apply hardcoded inline styles that aren't covered by GLOBAL_STYLE."""
        # Header gradient
        self._header_widget.setStyleSheet(
            f"#headerBar {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:0,"
            f" stop:0 #0E4F72, stop:1 {ACCENT}); border-bottom: none; }}"
        )
        # Tab bar chrome
        self._tab_bar_widget.setStyleSheet(
            f"#tabBarWidget {{ background-color: {TABBAR_BG};"
            f" border-top-left-radius: 10px; border-top-right-radius: 10px; }}"
        )
        # Activity log
        self.log_display.setStyleSheet(
            f"QTextEdit {{"
            f"  background-color: {LOG_BG}; color: {LOG_FG};"
            f"  border: 1.5px solid {BORDER}; border-radius: 10px;"
            f"  padding: 10px 12px;"
            f"  font-family: Consolas, 'Courier New', monospace;"
            f"  font-size: 13px; line-height: 1.6;"
            f"}}"
        )
        # Log clear button
        self.log_clear_btn.setStyleSheet(
            f"QPushButton {{ background: {SURFACE}; color: {SUBTEXT};"
            f" border: 1.5px solid {BORDER}; border-radius: 6px;"
            f" font-size: 12px; padding: 2px 8px; font-family: {FONT_FAMILY}; }}"
            f"QPushButton:hover {{ color: {ACCENT}; border-color: {ACCENT}; background: {BTN_HOVER}; }}"
        )
        # Email input
        self.email_input.setStyleSheet(
            f"QTextEdit {{"
            f"  background-color: {BG}; border: 1.5px solid {BORDER};"
            f"  border-radius: 10px; color: {TEXT};"
            f"  font-size: {FONT_INPUT}px; padding: 14px 16px; line-height: 1.6;"
            f"}}"
            f"QTextEdit:focus {{ border-color: {ACCENT}; }}"
        )
        # Footer
        self.status_lbl.setStyleSheet(
            f"color: {SUBTEXT}; font-size: 13px; border: none; padding-left: 6px;"
        )

    # ── Settings ───────────────────────────────────────────────────────────────

    def _on_set_api_key(self):
        from virustotal import load_api_key, save_api_key
        current = load_api_key()
        key, ok = QInputDialog.getText(
            self, "VirusTotal API Key",
            "Paste your VirusTotal API key below.\n"
            "(Free key at virustotal.com — needed for IP / domain lookups)",
            QLineEdit.Password,
            current
        )
        if ok and key.strip():
            save_api_key(key.strip())
            self.settings_btn.setText("VT Key ✓")
            self.status_lbl.setText("VirusTotal API key saved.")
        elif ok and not key.strip():
            save_api_key("")
            self.settings_btn.setText("VT Key")
            self.status_lbl.setText("VirusTotal API key cleared.")

    # ── Tab / upload / clear ───────────────────────────────────────────────────

    def _switch_tab(self, index):
        self.stack.setCurrentIndex(index)
        self.tab_paste.setProperty("active",  "true" if index == 0 else "false")
        self.tab_upload.setProperty("active", "true" if index == 1 else "false")
        for btn in (self.tab_paste, self.tab_upload):
            btn.setStyle(btn.style())

    def _on_upload(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "",
            "All supported (*.eml *.txt *.msg *.png *.jpg *.jpeg *.webp *.bmp *.gif);;"
            "Email files (*.eml *.txt *.msg);;"
            "Image files (*.png *.jpg *.jpeg *.webp *.bmp *.gif);;"
            "All files (*)"
        )
        if not path:
            return

        from image_reader import is_image
        if is_image(path):
            self._start_image_extraction(path)
        else:
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                self.email_input.setPlainText(content)
                self.file_name_lbl.setText(os.path.basename(path))
                self._switch_tab(0)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not read file:\n{e}")

    # ── Image OCR flow ─────────────────────────────────────────────────────────

    def _start_image_extraction(self, path: str):
        fname = os.path.basename(path)
        self.file_name_lbl.setText(f"↑  {fname}")
        self.image_status_lbl.setText("Reading image with Gemma vision model…")
        self._switch_tab(1)
        self.email_input.setPlainText("")
        self.analyze_btn.setEnabled(False)
        self._show_spinner("Reading image…")

        self._step_start = time.time()
        self._log(f"── Image OCR: {fname} ──", ACCENT)
        self.log_display.append(
            f'<span style="color:{LOG_FG}; font-size:13px;"></span>'
        )

        self._img_reader = ImageReaderThread(path)
        self._img_reader.chunk.connect(self._on_image_chunk)
        self._img_reader.finished.connect(self._on_image_extracted)
        self._img_reader.error.connect(self._on_image_error)
        self._img_reader.start()

    def _on_image_chunk(self, text: str):
        cursor = self.log_display.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(text)
        self.log_display.setTextCursor(cursor)
        self.log_display.verticalScrollBar().setValue(
            self.log_display.verticalScrollBar().maximum()
        )

    def _on_image_extracted(self, text: str):
        elapsed = time.time() - self._step_start if self._step_start else 0
        self._hide_spinner()
        self._log(f"✓ Image text extracted  ({elapsed:.1f}s) — click Analyze", RISK_COLORS["Low"])
        self.image_status_lbl.setText("✓ Text extracted — click Analyze")
        self.email_input.setPlainText(text)
        self._switch_tab(0)
        if self._model_ready:
            self.analyze_btn.setEnabled(True)

    def _on_image_error(self, msg: str):
        self._hide_spinner()
        self._log(f"✗ Image OCR failed: {msg}", RISK_COLORS["Critical"])
        self.image_status_lbl.setText("✗ OCR failed — see log")
        if self._model_ready:
            self.analyze_btn.setEnabled(True)
        QMessageBox.warning(self, "Image OCR Error", f"Could not read text from image:\n\n{msg}")

    def _on_clear(self):
        self.email_input.clear()
        self.results_display.clear()
        self.file_name_lbl.setText("No file selected")
        self._last_result = None
        self._email_result_html = None
        self.export_btn.setEnabled(False)
        self.explain_btn.setEnabled(False)
        self._switch_tab(0)
        # Remove URL checker panel
        if self._url_panel is not None:
            self._left_col.removeWidget(self._url_panel)
            self._url_panel.deleteLater()
            self._url_panel = None


# ── Helpers ────────────────────────────────────────────────────────────────────

def _esc(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _extract_brief(full_text: str) -> str:
    import re
    match = re.search(r'Step\s*4[^\n]*\n(.*)', full_text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    paragraphs = [p.strip() for p in full_text.split('\n\n') if p.strip()]
    return paragraphs[-1] if paragraphs else full_text.strip()
