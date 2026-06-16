# Copyright 2020 Charles Henry
from aqt.webview import AnkiWebView
from PyQt6 import QtCore, QtGui
from aqt import Qt, QWidget, QGridLayout, QPushButton, QDialog, QHBoxLayout, QVBoxLayout, QLineEdit, QLabel, QMenu
from ..anki_utils import AnkiUtils
import logging
import re
import html
import time
import math


# Visual themes for the pop-up. Each theme defines colours for the card surface
# (where the flash-card text is shown), the surrounding window chrome, the answer
# buttons, the top icons and the self-typing feedback. Readability is the top
# priority, so every theme pairs a card background with a strongly contrasting
# default text colour. THEME_ORDER controls how themes appear in the options
# drop-down; DEFAULT_THEME is used when the config has no (or an unknown) theme.
#
# NO_THEME is a special entry: it applies *no* custom styling at all, so the
# pop-up falls back to the native Qt look (standard widget colours), exactly as
# it behaved before themes were introduced. It is the default.
NO_THEME = "No Theme"
DEFAULT_THEME = NO_THEME
THEME_ORDER = [NO_THEME, "Classic", "Dark", "Sepia", "Solarized Light", "Nord",
               "High Contrast", "macOS", "Windows 11", "Ubuntu"]
THEMES = {
    # Classic: former "Light" look.
    "Classic": {
        "card_bg": "#ffffff",
        "card_fg": "#202020",
        "window_bg": "#ffffff",
        "btn_bg": "#ffffff",
        "btn_fg": "#202020",
        "btn_border": "#d9d9d9",
        "btn_border_width": "1px",
        "btn_hover": "#f2f2f2",
        "icon": "#464646",
        "icon_off_tint": "rgba(0, 0, 0, 0.05)",
        "icon_off_hover": "rgba(0, 0, 0, 0.15)",
        "input_bg": "#ffffff",
        "input_fg": "#202020",
        "input_border": "#d9d9d9",
        "feedback_correct": "#1c7c35",
        "feedback_partial": "#9a3412",
        "feedback_incorrect": "#b42318",
    },
    "Dark": {
        "card_bg": "#252526",
        "card_fg": "#e6e6e6",
        "window_bg": "#1e1e1e",
        "btn_bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4c4c52, stop:1 #2f2f33)",
        "btn_fg": "#e6e6e6",
        "btn_border": "#5a5a62",
        "btn_hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5c5c64, stop:1 #3a3a40)",
        "btn_radius": "8px",
        "window_radius": 10,
        "icon": "#d0d0d0",
        "icon_off_tint": "rgba(255, 255, 255, 0.08)",
        "icon_off_hover": "rgba(255, 255, 255, 0.18)",
        "input_bg": "#2d2d2d",
        "input_fg": "#e6e6e6",
        "input_border": "#4a4a4a",
        "input_radius": "8px",
        "feedback_correct": "#4ec06a",
        "feedback_partial": "#e0a458",
        "feedback_incorrect": "#f1707a",
    },
    "Sepia": {
        "card_bg": "#f4ecd8",
        "card_fg": "#4b3a26",
        "window_bg": "#efe6d4",
        "btn_bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f1e6cd, stop:1 #e0cfa9)",
        "btn_fg": "#4b3a26",
        "btn_border": "#cbb994",
        "btn_hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f7eed8, stop:1 #e8d8b4)",
        "btn_radius": "8px",
        "window_radius": 10,
        "icon": "#6b573c",
        "icon_off_tint": "rgba(75, 58, 38, 0.08)",
        "icon_off_hover": "rgba(75, 58, 38, 0.18)",
        "input_bg": "#f4ecd8",
        "input_fg": "#4b3a26",
        "input_border": "#cbb994",
        "input_radius": "8px",
        "feedback_correct": "#3f7d34",
        "feedback_partial": "#9a5a12",
        "feedback_incorrect": "#a33027",
    },
    "Solarized Light": {
        "card_bg": "#fdf6e3",
        "card_fg": "#586e75",
        "window_bg": "#eee8d5",
        "btn_bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f5efda, stop:1 #e4ddc1)",
        "btn_fg": "#586e75",
        "btn_border": "#d8cfb0",
        "btn_hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #fbf6e6, stop:1 #ece4ca)",
        "btn_radius": "8px",
        "window_radius": 10,
        "icon": "#657b83",
        "icon_off_tint": "rgba(88, 110, 117, 0.08)",
        "icon_off_hover": "rgba(88, 110, 117, 0.18)",
        "input_bg": "#fdf6e3",
        "input_fg": "#586e75",
        "input_border": "#d8cfb0",
        "input_radius": "8px",
        "feedback_correct": "#718c00",
        "feedback_partial": "#b58900",
        "feedback_incorrect": "#dc322f",
    },
    "Nord": {
        "card_bg": "#3b4252",
        "card_fg": "#eceff4",
        "window_bg": "#2e3440",
        "btn_bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6a8db5, stop:1 #5e81ac)",
        "btn_fg": "#eceff4",
        "btn_border": "#3b5378",
        "btn_hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #7b9cc2, stop:1 #6a8db5)",
        "btn_radius": "8px",
        "window_radius": 10,
        "icon": "#d8dee9",
        "icon_off_tint": "rgba(236, 239, 244, 0.08)",
        "icon_off_hover": "rgba(236, 239, 244, 0.18)",
        "input_bg": "#3b4252",
        "input_fg": "#eceff4",
        "input_border": "#4c566a",
        "input_radius": "8px",
        "feedback_correct": "#a3be8c",
        "feedback_partial": "#ebcb8b",
        "feedback_incorrect": "#bf616a",
    },
    "High Contrast": {
        "card_bg": "#000000",
        "card_fg": "#ffffff",
        "window_bg": "#000000",
        "btn_bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2a2a2a, stop:1 #000000)",
        "btn_fg": "#ffffff",
        "btn_border": "#ffffff",
        "btn_hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3d3d3d, stop:1 #1a1a1a)",
        "btn_radius": "8px",
        "window_radius": 8,
        "icon": "#ffffff",
        "icon_off_tint": "rgba(255, 255, 255, 0.12)",
        "icon_off_hover": "rgba(255, 255, 255, 0.28)",
        "input_bg": "#000000",
        "input_fg": "#ffffff",
        "input_border": "#ffffff",
        "input_radius": "8px",
        "feedback_correct": "#00ff66",
        "feedback_partial": "#ffd400",
        "feedback_incorrect": "#ff5b5b",
    },
    # macOS-style: light graphite chrome, very light "frosted" card, glossy
    # Apple-blue buttons with strongly rounded (pill-like) corners and rounded
    # window corners, like Big Sur / Sonoma.
    "macOS": {
        "card_bg": "#ffffff",
        "card_fg": "#1d1d1f",
        "window_bg": "#e8e8ea",
        "btn_bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3a93ff, stop:1 #007aff)",
        "btn_fg": "#ffffff",
        "btn_border": "#0a64d6",
        "btn_hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5aa6ff, stop:1 #1f8bff)",
        "btn_radius": "14px",
        "window_radius": 14,
        "icon": "#3c3c43",
        "icon_off_tint": "rgba(0, 0, 0, 0.06)",
        "icon_off_hover": "rgba(0, 0, 0, 0.14)",
        "input_bg": "#ffffff",
        "input_fg": "#1d1d1f",
        "input_border": "#c4c4c8",
        "input_radius": "10px",
        "feedback_correct": "#1c7c35",
        "feedback_partial": "#b25000",
        "feedback_incorrect": "#d70015",
    },
    # Windows 11-style: cool Mica-like grey surface, flatter Fluent "accent"
    # buttons in the signature Windows blue, with the small 4px Fluent corner
    # radius on buttons and window.
    "Windows 11": {
        "card_bg": "#fbfbfb",
        "card_fg": "#1b1b1b",
        "window_bg": "#f0f3f9",
        "btn_bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1a86e8, stop:1 #005fb8)",
        "btn_fg": "#ffffff",
        "btn_border": "#005299",
        "btn_hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2b93f0, stop:1 #0a6cc4)",
        "btn_radius": "4px",
        "window_radius": 8,
        "icon": "#2b2b2b",
        "icon_off_tint": "rgba(0, 0, 0, 0.05)",
        "icon_off_hover": "rgba(0, 0, 0, 0.12)",
        "input_bg": "#ffffff",
        "input_fg": "#1b1b1b",
        "input_border": "#c2c2c2",
        "input_radius": "4px",
        "feedback_correct": "#0f7b0f",
        "feedback_partial": "#9d5d00",
        "feedback_incorrect": "#c42b1c",
    },
    # Ubuntu-style: warm "Yaru" aubergine chrome with glossy Ubuntu-orange
    # buttons and light card surface for maximum text readability.
    "Ubuntu": {
        "card_bg": "#fbfaf9",
        "card_fg": "#2c2c2c",
        "window_bg": "#3c2c34",
        "btn_bg": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f47b42, stop:1 #e2571a)",
        "btn_fg": "#ffffff",
        "btn_border": "#c64a14",
        "btn_hover": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff8c52, stop:1 #f0682b)",
        "btn_radius": "8px",
        "window_radius": 10,
        "icon": "#772953",
        "icon_off_tint": "rgba(0, 0, 0, 0.06)",
        "icon_off_hover": "rgba(0, 0, 0, 0.14)",
        "input_bg": "#ffffff",
        "input_fg": "#2c2c2c",
        "input_border": "#d8c9c1",
        "input_radius": "8px",
        "feedback_label_fg": "#e8e8e8",
        "feedback_correct": "#6fdc80",
        "feedback_partial": "#ffd089",
        "feedback_incorrect": "#ff9aa6",
    },
}


class _MoveHandle(QPushButton):
    """Button that drags its target window while the left mouse button is held."""

    def __init__(self, window, on_moved=None, clamp=None):
        super().__init__()
        self._window = window
        self._on_moved = on_moved
        self._clamp = clamp
        self._drag_offset = None

    def _move_window(self, point):
        if self._clamp is not None:
            point = self._clamp(point)
        self._window.move(point)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._drag_offset = event.globalPosition().toPoint() - self._window.pos()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_offset is not None and (
            event.buttons() & QtCore.Qt.MouseButton.LeftButton
        ):
            self._move_window(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if (
            event.button() == QtCore.Qt.MouseButton.LeftButton
            and self._drag_offset is not None
        ):
            self._drag_offset = None
            if self._on_moved is not None:
                self._on_moved()
            event.accept()
            return
        super().mouseReleaseEvent(event)


class RuzuPopup(QDialog):

    def __init__(self, parent):
        self.parent = parent
        self.anki_utils = AnkiUtils()
        self.current_card_id = None
        self.cur_button_count = 0
        config = self.anki_utils.get_config()
        self.enable_self_typing = config.get('enable_self_typing', False)
        self.typing_mode = False  # Always start with typing mode OFF
        self.pre_reveal_mode = False
        # Which set of bottom controls is currently shown ('pre_reveal',
        # 'question' or 'answer'). Lets us re-render the live pop-up when a
        # setting changes while it is on screen.
        self._display_state = None
        # Last card content rendered into the web view, so we can repaint it with
        # the new theme colours when the theme is switched while the pop-up is up.
        # _last_card_kind is 'prep' (the reveal bell), 'card' (question/answer
        # html) or None (nothing rendered yet).
        self._last_card_kind = None
        self._last_card_html = None
        self.last_typed_answer = ''
        self.skip_until = 0  # Epoch time until which pop-ups are skipped (in-memory only)
        # Restore the saved pop-up position from config (persists across Anki
        # restarts). Stored as {"x": int, "y": int}; None/invalid -> default spot.
        self.window_position = self._position_from_config(config.get('window_position'))
        self.infinity_mode = False  # Session only; immediately load next card after answering.
        self.skip_options = [1, 2, 3, 5, 10, 15, 30, 60, 120, 180]
        self.logger = logging.getLogger(__name__.split('.')[0])
        # Active visual theme (resolved from config; refreshed on every render).
        # This is a safe placeholder until _apply_theme() runs at the end of
        # __init__ (which resolves the real theme, including the dynamic
        # "No Theme" palette that needs the already-created popup_window).
        self._theme = THEMES.get(config.get('theme', DEFAULT_THEME), THEMES["Classic"])
        # Base button stylesheet for the current theme. Set properly in
        # _apply_theme(); initialised here because _apply_typing_toggle_ui()
        # (called during widget setup below) reads it before the first render.
        self._btn_style = ''

        # popup_window (QWidget)
        # -grid (QGridLayout)
        # --card_view (QWebEngineView)
        # --bottom_grid (QGridLayout)
        # ---buttons self.btn[0~3] (QPushButton)

        ###
        # Top level Pop-up Window
        ###
        parent.popup_window = self.popup_window = QWidget()
        self.popup_window.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.popup_window.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)  # Hide the title bar
        self.popup_window.setWindowTitle("Anki Review")  # Set the title (visible in windows taskbar)
        self.popup_window.setGeometry(0, 0, 400, 300)  # Set window geometry
        # Translucent top-level window so a styled container can paint smooth,
        # anti-aliased rounded corners. (A QRegion setMask gives jagged corners;
        # Qt stylesheet border-radius is anti-aliased.) The container below is
        # the actual visible, themed surface.
        self.popup_window.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        parent.container = self.container = QWidget()
        self.container.setObjectName('ruzuContainer')

        ###
        # Card View
        ###
        parent.card_view = self.card_view = AnkiWebView()
        # The web view is made translucent so the rounded backing widget below
        # (card_bg_widget) shows through at the corners. That backing widget
        # paints the themed card background with anti-aliased rounded top corners
        # and also prevents any grey flash during the async setHtml load.
        self.card_view.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.card_view.setStyleSheet("background: transparent;")
        parent.card_bg_widget = self.card_bg_widget = QWidget()
        self.card_bg_widget.setObjectName('ruzuCardBg')
        card_bg_layout = QVBoxLayout(self.card_bg_widget)
        card_bg_layout.setContentsMargins(0, 0, 0, 0)
        card_bg_layout.addWidget(self.card_view)
        self._apply_card_view_bg()

        ###
        # Buttons
        ###
        btn_width = 100
        btn_height = 20
        btn_padding = 20
        self.btn = []
        self.btn.append(QPushButton(text="Again"))
        self.btn[0].clicked.connect(lambda _: self.send_answer("Again"))
        self.btn[0].setGeometry(btn_padding, btn_padding, btn_width, btn_height)
        self.btn.append(QPushButton(text="Hard"))
        self.btn[1].clicked.connect(lambda _: self.send_answer("Hard"))
        self.btn[1].setGeometry(btn_padding, btn_padding, btn_width, btn_height)
        self.btn.append(QPushButton(text="Good"))
        self.btn[2].clicked.connect(lambda _: self.send_answer("Good"))
        self.btn[2].setGeometry(btn_padding, btn_padding, btn_width, btn_height)
        self.btn.append(QPushButton(text="Easy"))
        self.btn[3].clicked.connect(lambda _: self.send_answer("Easy"))
        self.btn[3].setGeometry(btn_padding, btn_padding, btn_width, btn_height)
        self.btn.append(QPushButton(text="Show Answer"))
        self.btn[4].setGeometry(btn_padding, btn_padding, btn_width, btn_height)
        self.btn[4].clicked.connect(lambda _: self.show_answer_popup())
        self.btn.append(QPushButton(text="Reveal Question"))
        self.btn[5].setGeometry(btn_padding, btn_padding, btn_width, btn_height)
        self.btn[5].clicked.connect(lambda _: self.show_question_popup())
        self.typing_toggle_btn = None
        self.enable_self_typing = config.get('enable_self_typing', False)
        if self.enable_self_typing:
            self.typing_toggle_btn = QPushButton(text="Type Answer: Off")
            self.typing_toggle_btn.setMinimumWidth(140)
            self.typing_toggle_btn.setToolTip("Type Answer: Off")
            self.typing_toggle_btn.clicked.connect(lambda _: self.toggle_typing_mode())
        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("Type your answer...")
        self.answer_input.returnPressed.connect(self.show_answer_popup)
        self.feedback_label = QLabel()
        self.feedback_label.setObjectName('ruzuFeedback')
        self.feedback_label.setWordWrap(True)
        self.feedback_label.setStyleSheet("font-size: 12px; font-weight: bold;")
        # Hidden until a self-typing answer is evaluated, so it does not add an
        # empty gap below the buttons (a hidden widget takes no layout space).
        self.feedback_label.setVisible(False)
        self._apply_typing_toggle_ui()

        ###
        # Settings icon (top right corner of the card view)
        ###
        self.settings_btn = QPushButton()
        self.settings_btn.setFixedSize(26, 26)
        self.settings_btn.setToolTip("Skip pop-ups for a while")
        self.settings_btn.setIcon(self._build_sleep_icon())
        self.settings_btn.setIconSize(QtCore.QSize(18, 18))
        self.settings_btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.settings_btn.setStyleSheet(
            "QPushButton { border: none; background: rgba(0, 0, 0, 0.05);"
            " border-radius: 6px; }"
            " QPushButton:hover { background: rgba(0, 0, 0, 0.15); }"
        )
        self.settings_btn.clicked.connect(lambda _: self._show_settings_menu())

        ###
        # Move handle (drag the pop-up while left mouse button is held)
        ###
        self.move_btn = _MoveHandle(
            self.popup_window,
            on_moved=self._save_window_position,
            clamp=self._clamp_to_screens,
        )
        self.move_btn.setFixedSize(26, 26)
        self.move_btn.setToolTip("Move")
        self.move_btn.setIcon(self._build_move_icon())
        self.move_btn.setIconSize(QtCore.QSize(18, 18))
        self.move_btn.setCursor(QtCore.Qt.CursorShape.SizeAllCursor)
        self.move_btn.setStyleSheet(
            "QPushButton { border: none; background: rgba(0, 0, 0, 0.05);"
            " border-radius: 6px; }"
            " QPushButton:hover { background: rgba(0, 0, 0, 0.15); }"
        )

        ###
        # Infinity Mode icon (instantly load the next card after answering)
        ###
        self.infinity_btn = QPushButton()
        self.infinity_btn.setFixedSize(26, 26)
        self.infinity_btn.setIconSize(QtCore.QSize(18, 18))
        self.infinity_btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.infinity_btn.clicked.connect(lambda _: self.toggle_infinity_mode())
        self._apply_infinity_toggle_ui()

        ###
        # Layout management - Add objects to main pop-up window
        ###
        parent.grid = self.grid = QGridLayout()
        parent.bottom_grid = self.bottom_grid = QHBoxLayout()
        # self.bottom_grid.setVerticalSpacing(10)
        self.bottom_grid.setContentsMargins(10, 5, 10, 10)
        for i in range(4):
            self.bottom_grid.addWidget(self.btn[i])
        parent.bottom_grid_2 = self.bottom_grid_2 = QHBoxLayout()  # Used to hide buttons when needed
        parent.bottom_wid_2 = self.bottom_wid_2 = QWidget()  # Used to hide buttons when needed
        self.bottom_wid_2.setLayout(self.bottom_grid_2)  # Used to hide buttons when needed
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.addWidget(self.card_bg_widget)
        parent.top_btn_grid = self.top_btn_grid = QHBoxLayout()
        self.top_btn_grid.setContentsMargins(0, 4, 4, 0)
        self.top_btn_grid.setSpacing(4)
        self.top_btn_grid.addWidget(self.move_btn)
        self.top_btn_grid.addWidget(self.infinity_btn)
        self.top_btn_grid.addWidget(self.settings_btn)
        self.grid.addLayout(
            self.top_btn_grid, 0, 0,
            QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignRight
        )
        self.grid.addLayout(self.bottom_grid, 1, 0)
        self.grid.addWidget(self.feedback_label, 2, 0)
        self.container.setLayout(self.grid)
        # Outer layout simply hosts the rounded container inside the (now
        # translucent) top-level window, with no extra margins.
        outer_layout = QVBoxLayout(self.popup_window)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(self.container)

        # Timer used to defer the Infinity Mode reload by one event-loop turn.
        # Right after answering, Anki has not yet advanced to the next card, so
        # we must yield to the event loop before re-rendering. The timer is
        # parented to popup_window (a real QObject) so it fires reliably.
        #
        # IMPORTANT: the timeout is connected via a lambda, NOT directly to
        # self._infinity_reload. RuzuPopup derives from QDialog but never calls
        # super().__init__(), so it is not an initialised QObject. If a bound
        # method of such an object is used as a slot, PyQt treats it as a slot on
        # an (invalid) QObject receiver and Qt silently never delivers the
        # signal. A lambda's __self__ is a plain Python object, so the call goes
        # through normally (this is why the answer buttons, which also use
        # lambdas, work).
        self._infinity_timer = QtCore.QTimer(self.popup_window)
        self._infinity_timer.setSingleShot(True)
        self._infinity_timer.timeout.connect(lambda: self._infinity_reload())
        # Counts how many times _infinity_reload has waited for Anki to advance
        # to the next card (used to cap the polling so it can never loop forever).
        self._infinity_retries = 0

        # Apply the configured theme to the window chrome, buttons and icons.
        self._apply_theme()

    def _current_theme(self):
        # Resolve the theme from config every time so changes made in the options
        # dialog take effect on the next pop-up without restarting Anki.
        name = self.anki_utils.get_config().get('theme', DEFAULT_THEME)
        if name in THEMES:
            return THEMES[name]
        # NO_THEME (or any unknown value): build a palette from Qt's standard
        # colours so feedback/card rendering still has valid values to read.
        return self._no_theme_palette()

    def _is_no_theme(self):
        # True when the configured theme is "No Theme" (native Qt look) or an
        # unknown value that should fall back to no styling.
        name = self.anki_utils.get_config().get('theme', DEFAULT_THEME)
        return name not in THEMES

    def _no_theme_palette(self):
        # Derive a theme-shaped dict from the application's current Qt palette so
        # the pop-up uses the native standard colours (and adapts to a light or
        # dark Qt theme). Used as the colour source while "No Theme" is active.
        palette = self.popup_window.palette()
        role = QtGui.QPalette.ColorRole

        def colour(which):
            return palette.color(which).name()

        window = colour(role.Window)
        base = colour(role.Base)
        text = colour(role.WindowText)
        button = colour(role.Button)
        button_text = colour(role.ButtonText)
        mid = colour(role.Mid)
        return {
            "card_bg": base,
            "card_fg": text,
            "window_bg": window,
            "btn_bg": button,
            "btn_fg": button_text,
            "btn_border": mid,
            "btn_hover": button,
            "icon": text,
            "icon_off_tint": "transparent",
            "icon_off_hover": "rgba(127, 127, 127, 0.20)",
            "input_bg": base,
            "input_fg": text,
            "input_border": mid,
            "feedback_correct": "#1c7c35",
            "feedback_partial": "#9a3412",
            "feedback_incorrect": "#b42318",
            "window_radius": 0,
        }

    def _apply_theme(self):
        if self._is_no_theme():
            self._apply_no_theme()
            return

        theme = self._theme = self._current_theme()

        # Rounded radii for the window corners (anti-aliased via stylesheet).
        radius = int(theme.get('window_radius', 0) or 0)
        # Container: paints the themed window background with smooth rounded
        # corners. The QLabel rule sets the default text colour for child labels.
        self.container.setStyleSheet(
            "#ruzuContainer { background: %s; border-radius: %dpx; }"
            " QLabel { color: %s; background: transparent; }"
            % (theme['window_bg'], radius, theme['card_fg'])
        )
        # Card backing: themed card surface with rounded *top* corners only
        # (the bottom of the card meets the button strip).
        self.card_bg_widget.setStyleSheet(
            "#ruzuCardBg { background: %s;"
            " border-top-left-radius: %dpx; border-top-right-radius: %dpx; }"
            % (theme['card_bg'], radius, radius)
        )

        # Answer / action buttons.
        btn_style = (
            "QPushButton { background: %(bg)s; color: %(fg)s;"
            " border: %(border_width)s solid %(border)s; border-radius: %(radius)s; padding: 6px 12px;"
            " font-weight: 500; }"
            " QPushButton:hover { background: %(hover)s; }"
            " QPushButton:pressed { background: %(border)s; }"
            " QPushButton:disabled { color: %(border)s; }"
        ) % {
            'bg': theme['btn_bg'],
            'fg': theme['btn_fg'],
            'border': theme['btn_border'],
            'border_width': theme.get('btn_border_width', '1px'),
            'hover': theme['btn_hover'],
            'radius': theme.get('btn_radius', '6px'),
        }
        self._btn_style = btn_style
        for b in self.btn:
            b.setStyleSheet(btn_style)
        if self.typing_toggle_btn:
            self._apply_typing_toggle_ui()

        # Self-typing answer input.
        self.answer_input.setStyleSheet(
            "QLineEdit { background: %s; color: %s; border: 1px solid %s;"
            " border-radius: %s; padding: 5px 8px; }"
            % (theme['input_bg'], theme['input_fg'], theme['input_border'],
               theme.get('input_radius', '6px'))
        )

        # Top icons (move + gear) re-rendered in the theme's icon colour.
        icon_colour = QtGui.QColor(theme['icon'])
        icon_btn_style = (
            "QPushButton { border: none; background: %s; border-radius: 6px; }"
            " QPushButton:hover { background: %s; }"
            % (theme['icon_off_tint'], theme['icon_off_hover'])
        )
        self.settings_btn.setIcon(self._build_sleep_icon(icon_colour))
        self.settings_btn.setStyleSheet(icon_btn_style)
        self.move_btn.setIcon(self._build_move_icon(icon_colour))
        self.move_btn.setStyleSheet(icon_btn_style)

        # Infinity icon depends on its on/off state, so delegate to its helper.
        self._apply_infinity_toggle_ui()

        # Card surface background (web page paint colour) follows the theme.
        self._apply_card_view_bg()

        # Feedback label base colour (overridden per result in _set_feedback).
        self.feedback_label.setStyleSheet(
            "font-size: 12px; font-weight: bold; color: %s; padding: 0 12px;" % theme['card_fg']
        )

    def _apply_no_theme(self):
        # "No Theme": strip all custom widget styling so the pop-up renders in the
        # native Qt look (default widget colours, square corners), exactly as it
        # did before themes were added. self._theme still holds a palette-derived
        # dict so card/feedback rendering has valid colours to read.
        theme = self._theme = self._no_theme_palette()
        palette = self.popup_window.palette()
        role = QtGui.QPalette.ColorRole
        window = palette.color(role.Window).name()
        base = palette.color(role.Base).name()
        text = palette.color(role.WindowText).name()

        # Opaque native window background with square corners (no rounding), and
        # the standard text colour for child labels.
        self.container.setStyleSheet(
            "#ruzuContainer { background: %s; }"
            " QLabel { color: %s; background: transparent; }"
            % (window, text)
        )
        # Card surface uses the default text-entry background (usually white).
        self.card_bg_widget.setStyleSheet("#ruzuCardBg { background: %s; }" % base)

        # Native buttons and input: clear stylesheets so Qt/the OS draws them.
        self._btn_style = ""
        for b in self.btn:
            b.setStyleSheet("")
        if self.typing_toggle_btn:
            self._apply_typing_toggle_ui()
        self.answer_input.setStyleSheet("")

        # Top icons in the default text colour on native (transparent) buttons.
        icon_colour = QtGui.QColor(text)
        self.settings_btn.setIcon(self._build_sleep_icon(icon_colour))
        self.settings_btn.setStyleSheet("")
        self.move_btn.setIcon(self._build_move_icon(icon_colour))
        self.move_btn.setStyleSheet("")

        # Infinity icon depends on its on/off state, so delegate to its helper.
        self._apply_infinity_toggle_ui()

        # Card surface background (web page paint colour).
        self._apply_card_view_bg()

        # Feedback label base style (overridden per result in _set_feedback).
        self.feedback_label.setStyleSheet("font-size: 12px; font-weight: bold;")

    def _apply_card_view_bg(self):
        # The web view is translucent: its background is painted by the rounded
        # card_bg_widget behind it (which also avoids the grey flash during the
        # async setHtml load). So paint the web page itself transparent.
        transparent = QtGui.QColor(QtCore.Qt.GlobalColor.transparent)
        try:
            self.card_view.page().setBackgroundColor(transparent)
        except Exception:
            pass
        try:
            palette = self.card_view.palette()
            palette.setColor(self.card_view.backgroundRole(), transparent)
            self.card_view.setPalette(palette)
        except Exception:
            pass

    def set_card_position(self):
        # If the user has dragged the pop-up before in this session, restore it.
        if isinstance(self.window_position, QtCore.QPoint):
            point = self._clamp_to_screens(self.window_position)
            self.popup_window.move(point)
            return

        # Default: move to bottom right of screen
        # https://stackoverflow.com/questions/28322073/move-qmessagebox-to-bottom-right-corner-of-the-screen
        # https://forum.qt.io/topic/134570/qapplication-desktop-screengeometry-not-work-in-qt6
        screen_geometry = self.parent.app.primaryScreen().availableGeometry()
        screen_geo = screen_geometry.bottomRight()
        msg_geo = self.popup_window.frameGeometry()
        msg_geo.moveBottomRight(screen_geo)
        self.popup_window.move(msg_geo.topLeft())

    def _clamp_to_screens(self, point):
        # Keep the whole window inside the visible desktop area so it can never
        # be dragged (or restored) off-screen and become unreachable.
        app = self.parent.app
        screen = app.screenAt(point)
        if screen is None:
            screen = (
                self.popup_window.screen()
                or app.primaryScreen()
            )
        area = screen.availableGeometry()
        win = self.popup_window.frameGeometry()

        max_x = area.right() - win.width() + 1
        max_y = area.bottom() - win.height() + 1
        # If the window is larger than the screen, prefer showing the top-left.
        x = min(max(point.x(), area.left()), max(max_x, area.left()))
        y = min(max(point.y(), area.top()), max(max_y, area.top()))
        return QtCore.QPoint(x, y)

    def _save_window_position(self):
        pos = self.popup_window.pos()
        self.window_position = QtCore.QPoint(pos.x(), pos.y())
        self.logger.info('Saved pop-up position to (%s, %s)' % (pos.x(), pos.y()))
        # Persist to config so the position survives an Anki restart.
        try:
            config = self.anki_utils.get_config()
            config['window_position'] = {'x': pos.x(), 'y': pos.y()}
            self.anki_utils.set_config(config)
        except Exception:
            self.logger.warning('Could not persist pop-up position to config', exc_info=True)

    def _position_from_config(self, value):
        # Convert a stored {"x": int, "y": int} mapping into a QPoint. Returns
        # None for missing/invalid values so the default placement is used.
        if isinstance(value, dict) and 'x' in value and 'y' in value:
            try:
                return QtCore.QPoint(int(value['x']), int(value['y']))
            except (TypeError, ValueError):
                return None
        return None

    def _build_move_icon(self, color=None):
        size = 36
        pixmap = QtGui.QPixmap(size, size)
        pixmap.fill(QtCore.Qt.GlobalColor.transparent)

        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
        icon_colour = color if color is not None else QtGui.QColor(70, 70, 70)
        pen = QtGui.QPen(icon_colour)
        pen.setWidth(2)
        pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(QtCore.Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(QtGui.QBrush(icon_colour))

        c = size / 2.0
        arm = size * 0.30   # length of each arm from the centre
        head = size * 0.10  # half-width / depth of each arrowhead

        # Cross strokes.
        painter.drawLine(QtCore.QPointF(c, c - arm), QtCore.QPointF(c, c + arm))
        painter.drawLine(QtCore.QPointF(c - arm, c), QtCore.QPointF(c + arm, c))

        def triangle(tip, left, right):
            path = QtGui.QPainterPath()
            path.moveTo(tip)
            path.lineTo(left)
            path.lineTo(right)
            path.closeSubpath()
            painter.drawPath(path)

        # Up / down / left / right arrowheads.
        triangle(QtCore.QPointF(c, c - arm - head),
                 QtCore.QPointF(c - head, c - arm),
                 QtCore.QPointF(c + head, c - arm))
        triangle(QtCore.QPointF(c, c + arm + head),
                 QtCore.QPointF(c - head, c + arm),
                 QtCore.QPointF(c + head, c + arm))
        triangle(QtCore.QPointF(c - arm - head, c),
                 QtCore.QPointF(c - arm, c - head),
                 QtCore.QPointF(c - arm, c + head))
        triangle(QtCore.QPointF(c + arm + head, c),
                 QtCore.QPointF(c + arm, c - head),
                 QtCore.QPointF(c + arm, c + head))
        painter.end()

        return QtGui.QIcon(pixmap)

    def _build_infinity_icon(self, active, color=None):
        size = 36
        pixmap = QtGui.QPixmap(size, size)
        pixmap.fill(QtCore.Qt.GlobalColor.transparent)

        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
        if active:
            colour = QtGui.QColor(245, 158, 11)
        else:
            colour = color if color is not None else QtGui.QColor(70, 70, 70)
        pen = QtGui.QPen(colour)
        pen.setWidthF(3.4)
        pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(QtCore.Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)

        # Infinity symbol (lemniscate / horizontal figure-eight) as a stroked
        # path: two lobes crossing in the centre of the 36x36 canvas.
        path = QtGui.QPainterPath()
        path.moveTo(18, 18)
        path.cubicTo(14, 10, 6, 10, 6, 18)    # centre -> up -> left side
        path.cubicTo(6, 26, 14, 26, 18, 18)   # left side -> down -> centre
        path.cubicTo(22, 10, 30, 10, 30, 18)  # centre -> up -> right side
        path.cubicTo(30, 26, 22, 26, 18, 18)  # right side -> down -> centre
        painter.drawPath(path)
        painter.end()

        return QtGui.QIcon(pixmap)

    def _build_sleep_icon(self, color=None):
        # "Zzz" sleep glyph: three Z letters of increasing size along a diagonal,
        # matching the "put pop-ups to sleep for X minutes" function.
        size = 36
        pixmap = QtGui.QPixmap(size, size)
        pixmap.fill(QtCore.Qt.GlobalColor.transparent)

        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QtGui.QPainter.RenderHint.TextAntialiasing, True)
        icon_colour = color if color is not None else QtGui.QColor(70, 70, 70)
        painter.setPen(QtGui.QPen(icon_colour))

        # (font point size, centre x, centre y) for each Z, smallest first.
        letters = [
            (8, size * 0.30, size * 0.66),
            (11, size * 0.50, size * 0.48),
            (15, size * 0.72, size * 0.28),
        ]
        for point_size, cx, cy in letters:
            font = QtGui.QFont("Segoe UI", point_size)
            font.setBold(True)
            painter.setFont(font)
            metrics = QtGui.QFontMetricsF(font)
            rect = metrics.boundingRect("Z")
            x = cx - rect.width() / 2.0 - rect.left()
            y = cy + rect.height() / 2.0 - rect.bottom()
            painter.drawText(QtCore.QPointF(x, y), "Z")
        painter.end()

        return QtGui.QIcon(pixmap)

    def _format_skip_label(self, minutes):
        if minutes < 60:
            return "%d minute%s" % (minutes, "" if minutes == 1 else "s")
        hours = minutes // 60
        return "%d hour%s" % (hours, "" if hours == 1 else "s")

    def _show_settings_menu(self):
        menu = QMenu(self.popup_window)
        skip_menu = menu.addMenu("Skip pop-ups for...")
        for minutes in self.skip_options:
            action = skip_menu.addAction(self._format_skip_label(minutes))
            action.triggered.connect(
                lambda checked=False, mins=minutes: self.skip_popups_for(mins)
            )
        if time.time() < self.skip_until:
            remaining = int((self.skip_until - time.time()) / 60) + 1
            resume = menu.addAction("Resume pop-ups now (~%d min left)" % remaining)
            resume.triggered.connect(lambda checked=False: self.resume_popups())
        menu.exec(self.settings_btn.mapToGlobal(self.settings_btn.rect().bottomLeft()))

    def skip_popups_for(self, minutes):
        self.skip_until = time.time() + minutes * 60
        self.logger.info(
            'Skipping pop-ups for %d minutes (until %s)' % (minutes, time.ctime(self.skip_until))
        )
        # Dismiss the current pop-up if it is showing.
        self.hide_popup()

    def resume_popups(self):
        self.skip_until = 0
        self.logger.info('Skip cancelled, pop-ups resumed')

    def show_show_button(self):
        self.pre_reveal_mode = True
        self._display_state = 'pre_reveal'
        self._clear_bottom_controls()
        if self.typing_mode:
            self.bottom_grid.addWidget(self.answer_input)
            self.answer_input.setFocus()
        self.bottom_grid.addWidget(self.btn[5])
        if self.typing_toggle_btn:
            self.bottom_grid.addWidget(self.typing_toggle_btn)

    def show_question_button(self):
        self.pre_reveal_mode = False
        self._display_state = 'question'
        self._clear_bottom_controls()
        if self.typing_mode:
            self.btn[4].setText("Check")
            self.bottom_grid.addWidget(self.answer_input)
            self.bottom_grid.addWidget(self.btn[4])
        else:
            self.btn[4].setText("Show Answer")
            self.bottom_grid.addWidget(self.btn[4])
        if self.typing_toggle_btn:
            self.bottom_grid.addWidget(self.typing_toggle_btn)

    def show_answer_buttons(self):
        # TODO - Take in actual buttons tuple?
        self.pre_reveal_mode = False
        self._display_state = 'answer'
        self._clear_bottom_controls()
        if self.cur_button_count == 2:
            self.bottom_grid.addWidget(self.btn[0])  # Again
            self.bottom_grid.addWidget(self.btn[2])  # Good
        elif self.cur_button_count == 3:
            self.bottom_grid.addWidget(self.btn[0])  # Again
            self.bottom_grid.addWidget(self.btn[2])  # Good
            self.bottom_grid.addWidget(self.btn[3])  # Easy
        else:
            for i in range(4):
                self.bottom_grid.addWidget(self.btn[i])  # Again, Hard, Good, Easy

    def _clear_bottom_controls(self):
        for i in range(6):
            self.bottom_grid_2.addWidget(self.btn[i])  # Remove all buttons
        if self.typing_toggle_btn:
            self.bottom_grid_2.addWidget(self.typing_toggle_btn)
        self.bottom_grid_2.addWidget(self.answer_input)

    def _apply_infinity_toggle_ui(self):
        active = self.infinity_mode
        theme = self._theme
        icon_colour = QtGui.QColor(theme['icon'])
        self.infinity_btn.setIcon(self._build_infinity_icon(active, icon_colour))
        if active:
            self.infinity_btn.setToolTip("Infinity Mode: ON")
            self.infinity_btn.setStyleSheet(
                "QPushButton { border: none; background: rgba(245, 158, 11, 0.25);"
                " border-radius: 6px; }"
                " QPushButton:hover { background: rgba(245, 158, 11, 0.40); }"
            )
        else:
            self.infinity_btn.setToolTip("Infinity Mode: OFF")
            self.infinity_btn.setStyleSheet(
                "QPushButton { border: none; background: %s;"
                " border-radius: 6px; }"
                " QPushButton:hover { background: %s; }"
                % (theme['icon_off_tint'], theme['icon_off_hover'])
            )

    def toggle_infinity_mode(self):
        self.infinity_mode = not self.infinity_mode
        self._apply_infinity_toggle_ui()
        self.logger.debug('infinity_mode toggled to %s' % self.infinity_mode)

    def _apply_typing_toggle_ui(self):
        if not self.typing_toggle_btn:
            return
        base_style = self._btn_style
        if self.typing_mode:
            self.typing_toggle_btn.setText("Type Answer: On")
            self.typing_toggle_btn.setToolTip("Type Answer: On")
            self.typing_toggle_btn.setStyleSheet(
                base_style + " QPushButton { font-weight: bold; }")
        else:
            self.typing_toggle_btn.setText("Type Answer: Off")
            self.typing_toggle_btn.setToolTip("Type Answer: Off")
            self.typing_toggle_btn.setStyleSheet(base_style)

    def _set_feedback(self, evaluation):
        theme = self._theme
        self.feedback_label.setVisible(True)
        # The feedback is shown inside a block painted with the card background
        # colour (see _feedback_label_style), so it always matches the card above
        # and stays readable. The text colour signals the result: green when
        # correct, orange when almost correct, red when incorrect.
        if evaluation['is_correct'] and not evaluation['accepted_with_one_error']:
            label_colour = self._feedback_line_colour(theme['feedback_correct'])
            self.feedback_label.setText(
                '<span style="color:%s;">Correct:</span> "%s"' % (
                    label_colour, html.escape(evaluation['typed']))
            )
            self.feedback_label.setStyleSheet(self._feedback_label_style(label_colour))
            return

        if evaluation['accepted_with_one_error']:
            label_colour = self._feedback_line_colour(theme['feedback_partial'])
            self.feedback_label.setText(
                '<span style="color:%s;">Almost correct (1 character tolerated).</span><br>'
                '<span style="color:%s;">Your answer:</span> %s<br>'
                '<span style="color:%s;">Correct answer:</span> %s' % (
                    label_colour, label_colour, evaluation['typed_markup'],
                    label_colour, evaluation['expected_markup'])
            )
            self.feedback_label.setStyleSheet(self._feedback_label_style(label_colour))
            return

        label_colour = self._feedback_line_colour(theme['feedback_incorrect'])
        self.feedback_label.setText(
            '<span style="color:%s;">Incorrect.</span><br>'
            '<span style="color:%s;">Your answer:</span> %s<br>'
            '<span style="color:%s;">Correct answer:</span> %s' % (
                label_colour, label_colour, evaluation['typed_markup'],
                label_colour, evaluation['expected_markup'])
        )
        self.feedback_label.setStyleSheet(self._feedback_label_style(label_colour))
        self.logger.debug(
            'feedback box set: card_bg=%s text=%s sheet=%s'
            % (theme['card_bg'], label_colour, self.feedback_label.styleSheet()))

    def _feedback_label_style(self, text_colour):
        # Style for the feedback block: it uses the theme's *card* background
        # colour (matching the card surface shown above it) with comfortable
        # padding and a small inset margin, so it reads as a tidy block. The
        # corners are rounded when the theme itself is rounded (and square for
        # "No Theme"), capped so a short block never looks pill-shaped.
        #
        # The selector targets the label by objectName (QLabel#ruzuFeedback) so
        # it beats the container's generic "QLabel { background: transparent; }"
        # rule (an id selector has higher specificity than a type selector);
        # otherwise the transparent ancestor rule would hide the block.
        theme = self._theme
        radius = min(int(theme.get('window_radius', 0) or 0), 10)
        return (
            "QLabel#ruzuFeedback { font-size: 12px; font-weight: bold; color: %s;"
            " background: %s; border-radius: %dpx;"
            " padding: 8px 12px; margin: 0 8px 8px 8px; }"
            % (text_colour, theme['card_bg'], radius)
        )

    def _feedback_line_colour(self, semantic_colour):
        # Keep the semantic colour's hue but nudge its lightness until it has
        # enough contrast against the card background it now sits on.
        return self._readable_feedback_colour(semantic_colour)

    def _readable_feedback_colour(self, hexcolour):
        # The feedback text sits inside a block painted with the theme's card
        # background colour. To guarantee the green/orange/red feedback stays
        # legible in *every* theme, we keep the colour's hue but nudge its
        # lightness until it has enough WCAG contrast against that card
        # background.
        bg = QtGui.QColor(self._theme['card_bg'])
        fg = QtGui.QColor(hexcolour)
        if not fg.isValid() or not bg.isValid():
            return hexcolour

        def _luminance(colour):
            def _channel(value):
                value /= 255.0
                return value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4
            return (0.2126 * _channel(colour.red())
                    + 0.7152 * _channel(colour.green())
                    + 0.0722 * _channel(colour.blue()))

        def _contrast(a, b):
            la, lb = _luminance(a), _luminance(b)
            high, low = max(la, lb), min(la, lb)
            return (high + 0.05) / (low + 0.05)

        bg_is_dark = _luminance(bg) < 0.4
        hue, sat, light, alpha = fg.getHslF()
        if hue < 0:  # achromatic; keep hue at 0 so setHslF stays valid
            hue = 0.0
        # Push lightness toward white (on dark backgrounds) or black (on light
        # backgrounds) until the AA contrast ratio of 4.5 is reached.
        for _ in range(20):
            if _contrast(fg, bg) >= 4.5:
                break
            light = min(1.0, light + 0.05) if bg_is_dark else max(0.0, light - 0.05)
            fg.setHslF(hue, sat, light, alpha)
        return fg.name()

    def _clear_feedback(self):
        self.feedback_label.setText('')
        # Collapse the label so no empty space remains below the buttons.
        self.feedback_label.setVisible(False)
        self.feedback_label.setStyleSheet(
            "font-size: 12px; font-weight: bold; padding: 0 12px; color: %s;" % self._theme['card_fg'])

    def _extract_text(self, value):
        value = self._extract_backside_html(value)
        # Convert answer HTML to plain text for basic comparison.
        # Strip style/script content first so CSS does not leak into feedback.
        cleaned = re.sub(r'<style[^>]*>.*?</style>', ' ', value or '', flags=re.IGNORECASE | re.DOTALL)
        cleaned = re.sub(r'<script[^>]*>.*?</script>', ' ', cleaned, flags=re.IGNORECASE | re.DOTALL)
        no_tags = re.sub(r'<[^>]+>', ' ', cleaned)
        plain_text = html.unescape(no_tags)
        return ' '.join(plain_text.split())

    def _extract_backside_html(self, value):
        html_value = value or ''
        # Anki separator can be id="answer", id='answer', or id=answer.
        answer_sep = re.search(r'<hr[^>]*\bid\s*=\s*(["\']?)answer\1[^>]*>', html_value, flags=re.IGNORECASE)
        if answer_sep:
            return html_value[answer_sep.end():]

        # Fallback for templates that use plain <hr> without id.
        generic_sep = re.search(r'<hr\b[^>]*>', html_value, flags=re.IGNORECASE)
        if generic_sep:
            return html_value[generic_sep.end():]

        return html_value

    def _normalize_text(self, value):
        normalized = (value or '').strip().lower()
        normalized = re.sub(r'\s+', ' ', normalized)
        return normalized

    def _levenshtein_distance_max_one(self, left, right):
        # Fast distance check with early exit, only cares about 0/1/>1 edits.
        if abs(len(left) - len(right)) > 1:
            return 2

        i = 0
        j = 0
        edits = 0
        while i < len(left) and j < len(right):
            if left[i] == right[j]:
                i += 1
                j += 1
                continue

            edits += 1
            if edits > 1:
                return edits

            if len(left) == len(right):
                i += 1
                j += 1
            elif len(left) > len(right):
                i += 1
            else:
                j += 1

        if i < len(left) or j < len(right):
            edits += 1

        return edits

    def _highlight_diff(self, typed_word, expected_word):
        typed_html = []
        expected_html = []
        max_len = max(len(typed_word), len(expected_word))

        for idx in range(max_len):
            typed_char = typed_word[idx] if idx < len(typed_word) else ''
            expected_char = expected_word[idx] if idx < len(expected_word) else ''

            if typed_char == expected_char:
                if typed_char:
                    escaped = html.escape(typed_char)
                    typed_html.append(escaped)
                    expected_html.append(escaped)
            else:
                # Highlighted diff characters carry BOTH their own light pastel
                # background AND an explicit dark text colour. This makes them
                # self-contained and readable in every theme, regardless of the
                # surrounding feedback line colour (which on dark themes is light
                # and would otherwise be invisible on these light backgrounds).
                if typed_char:
                    typed_html.append(
                        '<span style="background:#ffd6d6; color:#7f1d1d;'
                        ' border-radius:2px;">%s</span>' % html.escape(typed_char))
                if expected_char:
                    expected_html.append(
                        '<span style="background:#d9fbe1; color:#14532d;'
                        ' border-radius:2px;">%s</span>' % html.escape(expected_char))

        return ''.join(typed_html) or '-', ''.join(expected_html) or '-'

    def _evaluate_typed_answer(self, typed_answer, answer_html):
        typed_norm = self._normalize_text(typed_answer)
        answer_text = self._extract_text(answer_html)
        answer_norm = self._normalize_text(answer_text)

        result = {
            'is_correct': False,
            'accepted_with_one_error': False,
            'typed': typed_answer,
            'typed_markup': html.escape(typed_answer or '-'),
            'expected_markup': html.escape(answer_text[:120] or '-')
        }

        if not typed_norm or not answer_norm:
            return result

        if typed_norm == answer_norm:
            result['is_correct'] = True
            result['expected_markup'] = html.escape(answer_text)
            return result

        best_word = answer_norm
        best_distance = self._levenshtein_distance_max_one(typed_norm, answer_norm)

        # For single-word input, compare against individual answer words as well.
        if ' ' not in typed_norm:
            answer_words = re.findall(r'\w+', answer_norm)
            for answer_word in answer_words:
                distance = self._levenshtein_distance_max_one(typed_norm, answer_word)
                if distance < best_distance:
                    best_distance = distance
                    best_word = answer_word

        if best_distance == 0:
            result['is_correct'] = True
            typed_markup, expected_markup = self._highlight_diff(typed_norm, best_word)
            result['typed_markup'] = typed_markup
            result['expected_markup'] = expected_markup
            return result

        if best_distance == 1:
            result['is_correct'] = True
            result['accepted_with_one_error'] = True
            typed_markup, expected_markup = self._highlight_diff(typed_norm, best_word)
            result['typed_markup'] = typed_markup
            result['expected_markup'] = expected_markup
            return result

        typed_markup, expected_markup = self._highlight_diff(typed_norm, best_word)
        result['typed_markup'] = typed_markup
        result['expected_markup'] = expected_markup
        return result

    def toggle_typing_mode(self):
        self.typing_mode = not self.typing_mode
        self._apply_typing_toggle_ui()
        self.answer_input.clear()
        self.logger.debug('typing_mode toggled to %s' % self.typing_mode)

        # Refresh controls in whichever mode is currently displayed.
        if self.popup_window.isVisible():
            if self.pre_reveal_mode:
                self.show_show_button()
            else:
                self.show_question_button()
                if self.typing_mode:
                    self.answer_input.setFocus()

    def apply_config(self):
        # Apply the currently saved config to this already-running pop-up so that
        # option changes take effect immediately, without an Anki restart. The
        # pop-up is created once at add-on load, so values cached in __init__
        # (e.g. enable_self_typing) would otherwise stay stale until restart.
        config = self.anki_utils.get_config()
        self._set_self_typing_enabled(config.get('enable_self_typing', False))

        # Refresh chrome (theme + button styling) for the (possibly new) theme.
        self._apply_theme()

        # If a pop-up is currently on screen, re-render its controls so a newly
        # toggled option (e.g. self-typing) shows up right away.
        if self.popup_window.isVisible():
            try:
                self._render_current_controls()
            except Exception:
                self.logger.warning('Could not refresh live pop-up controls', exc_info=True)
            # Repaint the card itself so the new theme's text colour applies
            # immediately, instead of only on the next pop-up. Kept in its own
            # try/except so a controls failure can't block the card re-render.
            try:
                self._rerender_current_card()
            except Exception:
                self.logger.warning('Could not re-render live card', exc_info=True)

    def _rerender_current_card(self):
        # Re-render the card content currently shown in the web view using the
        # active theme (its colours are read from self._theme during render).
        if self._last_card_kind == 'prep':
            self.prep_card()
        elif self._last_card_kind == 'card':
            self.update_card(self._last_card_html)

    def _set_self_typing_enabled(self, enabled):
        # Create or tear down the self-typing toggle button to match the setting,
        # keeping internal state consistent.
        if enabled and self.typing_toggle_btn is None:
            self.typing_toggle_btn = QPushButton(text="Type Answer: Off")
            self.typing_toggle_btn.setMinimumWidth(140)
            self.typing_toggle_btn.setToolTip("Type Answer: Off")
            self.typing_toggle_btn.clicked.connect(lambda _: self.toggle_typing_mode())
            self._apply_typing_toggle_ui()
        elif not enabled and self.typing_toggle_btn is not None:
            button = self.typing_toggle_btn
            self.typing_toggle_btn = None
            button.setParent(None)
            button.deleteLater()
        if not enabled:
            # Leaving typing mode behind when the feature is switched off.
            self.typing_mode = False
        self.enable_self_typing = enabled

    def _render_current_controls(self):
        # Re-render whichever set of bottom controls is currently displayed.
        if self._display_state == 'pre_reveal':
            self.show_show_button()
        elif self._display_state == 'question':
            self.show_question_button()
        elif self._display_state == 'answer':
            self.show_answer_buttons()

    def reset_card(self):
        self.card_view.setHtml(None)

    def prep_card(self):
        # Refresh chrome in case the theme changed since the last render.
        self._apply_theme()
        theme = self._theme
        self._last_card_kind = 'prep'
        self._last_card_html = None
        # Update card with 'Reveal card' html
        self.card_view.setHtml("""
                    <!doctype html>
                    <html>
                        <head>
                            <style>
                                html, body { height: 100%%; margin: 0;
                                    background: transparent; color: %(fg)s; }
                            </style>
                        </head>
                        <body>
                            <div style="margin: auto; text-align: center; line-height: 90vh; font-size: 60px;">🔔</div>
                        </body>
                    </html>
                """ % {'fg': theme['card_fg']})

    def update_card(self, card):
        # Refresh chrome in case the theme changed since the last render.
        self._apply_theme()
        theme = self._theme
        self._last_card_kind = 'card'
        self._last_card_html = card
        # TODO - Look into using existing AnkiWebView object to render duplicate card with full compatibility
        # Note: the card HTML is concatenated (not %-formatted) so that any '%'
        # characters inside the card content cannot break string formatting.
        head = """
                    <!doctype html>
                    <html class=" webkit chrome win js">
                        <head>
                            <title>main webview</title>
                            <style>
                                html, body { height: 100%%; margin: 0; padding: 0; }
                                body { zoom: 1; background: transparent; color: %(fg)s; direction: ltr; font-size:12px;font-family:"Segoe UI"; }
                                #qa { padding: 12px; box-sizing: border-box; min-height: 100%%; }
                                button { font-family:"Segoe UI"; }
                                :focus { outline: 1px solid #0078d7; }
                            </style>
                        </head>

                        <body class="card card2 isWin">
                            <div id="qa" style="opacity: 1;">
                                """ % {'fg': theme['card_fg']}
        # Anki note templates commonly hard-code their own ".card { background:
        # white; color: black }". Because our <body> carries the "card" class,
        # that rule would otherwise repaint the surface. We append an override
        # <style> AFTER the card content so, with equal specificity but later
        # document order, our ".card" rule wins for the base surface: we force it
        # transparent so the rounded card backing widget shows through (including
        # the rounded corners), and set the theme text colour. We deliberately do
        # NOT use !important, so any per-element colours set inside the card
        # (e.g. coloured words) are preserved.
        override = """
                            </div>
                            <style id="ruzu-theme-override">
                                html, body { background-color: transparent; }
                                .card { background-color: transparent; color: %(fg)s; }
                            </style>
                        """ % {'fg': theme['card_fg']}
        tail = """
                        </body>
                    </html>
                """
        self.card_view.setHtml(head + card + override + tail)

    def pre_popup_validate(self):
        self.logger.info('pre_popup_validate...')
        # Get current deck from config
        current_deck = self.anki_utils.get_config()['deck']

        # Check that review is active and current deck is as expected (if not then start review)
        if not self.anki_utils.review_is_active() or current_deck != self.anki_utils.selected_deck():
            self.logger.info('Start review...')
            review_started = self.anki_utils.move_to_review_state(current_deck)
            self.logger.info('review_started: %s' % review_started)
            if not review_started:
                # The deck could not be entered (e.g. it no longer exists or has
                # no cards to study right now). Inform the user with a tooltip
                # instead of crashing with an unhandled exception.
                self.logger.warning('Failed to start review for deck "%s"' % current_deck)
                self._notify(
                    'Ruzu Pop-ups: no cards available to review in deck "%s".' % current_deck
                )
                return False
            if review_started and not self.anki_utils.review_is_active():
                self.logger.info('No cards left to review')
                self._notify('Ruzu Pop-ups: no cards left to review in deck "%s".' % current_deck)
                return False
        return True

    def _notify(self, message):
        # Show a non-blocking Anki tooltip if available, otherwise just log.
        try:
            from aqt.utils import tooltip
            tooltip(message)
        except Exception:
            self.logger.info(message)

    def show_answer_popup(self):
        self.logger.info('show_answer_popup...')
        typed_answer = self.answer_input.text().strip()
        self.last_typed_answer = typed_answer
        self.popup_window.hide()
        if not self.pre_popup_validate():
            return
        self.answer_input.clear()

        # TODO - Extra if this fails for some reason
        show_ans_result = self.anki_utils.show_answer()
        self.logger.debug('Show Answer Result: %s' % show_ans_result)

        # Collect card details (html, css, buttons)
        current_card = self.anki_utils.get_current_card()
        if self.current_card_id != current_card['card_id']:
            self.logger.info('Card has changed, show new card...')
            self.show_question_popup()
        else:
            self.cur_button_count = len(current_card['button_list'])
            self.show_answer_buttons()
            self.update_card(current_card['answer'])
            # Feedback is set AFTER update_card: update_card() calls _apply_theme()
            # which rewrites the feedback label's stylesheet, so setting the
            # feedback block last makes sure its styling (the card-coloured box)
            # is the one that actually sticks.
            if self.typing_mode and typed_answer:
                evaluation = self._evaluate_typed_answer(typed_answer, current_card['answer'])
                self._set_feedback(evaluation)
            else:
                self._clear_feedback()

            # Show pop-up
            self.set_card_position()
            self.popup_window.show()
            self._focus_popup()

    def _focus_popup(self):
        # Keep the frameless, always-on-top popup visually on top. Button clicks
        # no longer depend on the window being active (see _PopupWindow), so we
        # only raise it here and avoid aggressively grabbing activation, which
        # could otherwise interfere with the click currently being processed.
        if self.popup_window.isVisible():
            self.popup_window.raise_()

    def _infinity_reload(self):
        # Load the next card for Infinity Mode. Right after answering, Anki may
        # not have advanced to the next card yet. If we re-rendered immediately
        # the "skip rerender" guard in show_question_popup() would still see the
        # old card and abort, leaving the pop-up stuck on the answered card. So
        # we poll: if Anki still reports the just-answered card, wait a moment and
        # try again (capped so it can never loop forever).
        if self.current_card_id is not None and self.anki_utils.review_is_active():
            try:
                current_card = self.anki_utils.get_current_card()
            except Exception:
                current_card = None
            if current_card is not None and current_card['card_id'] == self.current_card_id:
                if self._infinity_retries < 40:  # ~2s worth of 50ms polls
                    self._infinity_retries += 1
                    self._infinity_timer.start(50)
                    return
        self._infinity_retries = 0

        # Anki has advanced (or we gave up waiting). Render the next card. Unlike
        # show_popup() this deliberately ignores the skip window and the "user is
        # actively reviewing" guard, because right after answering a card Anki's
        # main window is focused and those guards would otherwise cancel reload.
        self._clear_feedback()
        if self.anki_utils.get_config()['click_to_reveal']:
            self.hide_card()
            self.prep_card()
            self.show_show_button()
            self.set_card_position()
            self.popup_window.show()
            self._focus_popup()
        else:
            self.show_question_popup()

    def show_popup(self):
        self.logger.info('show_popup...')
        # Honour one-off skip window (in-memory, resets on Anki restart).
        if time.time() < self.skip_until:
            self.logger.info('Pop-up skipped, skip active until %s' % time.ctime(self.skip_until))
            return
        # Don't interrupt while the user is actively studying a deck in Anki.
        if self.anki_utils.user_is_actively_reviewing():
            self.logger.info('Pop-up skipped, user is actively reviewing in Anki')
            return
        self._clear_feedback()
        # Enter pre reveal state based on user config
        if self.anki_utils.get_config()['click_to_reveal']:
            self.hide_card()
            self.prep_card()
            self.show_show_button()
            self.set_card_position()
            self.popup_window.show()
            self._focus_popup()
        else:
            self.show_question_popup()

    def show_question_popup(self):
        self.logger.info('show_question_popup...')

        # Skip re-render if popup is already visible with the same card.
        # Only safe to check when a review is actually active, otherwise
        # get_current_card() raises (e.g. after a click-to-reveal cycle).
        if (self.popup_window.isVisible() and self.current_card_id is not None
                and self.anki_utils.review_is_active()):
            current_card = self.anki_utils.get_current_card()
            if current_card['card_id'] == self.current_card_id:
                self.logger.debug('Card already displayed, skipping rerender')
                return

        self._clear_feedback()
        # Hide first so the subsequent show() re-activates the window. On Windows
        # re-showing a hidden top-level window makes it the foreground/active
        # window, which is what lets a single click hit the answer buttons.
        self.popup_window.hide()
        if not self.pre_popup_validate():
            return
        show_q_result = self.anki_utils.show_question()
        self.logger.debug('Show Question Result: %s' % show_q_result)

        # Collect card details (html, css, buttons)
        current_card = self.anki_utils.get_current_card()
        self.current_card_id = current_card['card_id']
        self.logger.debug('Setting current card to %s' % current_card['card_id'])
        self.update_card(current_card['question'])
        self.show_question_button()

        # Show pop-up
        self.set_card_position()
        self.popup_window.show()
        self._focus_popup()
        # Restore focus to answer input if typing mode is active. Typing needs
        # real keyboard focus, so activate the window explicitly here (button
        # clicks no longer rely on activation, but text input still does).
        if self.typing_mode:
            self.popup_window.activateWindow()
            self.answer_input.setFocus()

    def send_answer(self, ease_name):
        # TODO - Clean this up, not elegant at all
        if self.cur_button_count == 2:
            if ease_name == "Again":
                ease = 1
            elif ease_name == "Good":
                ease = 2
            else:
                raise Exception('Invalid ease used, expected [Again] or [Good] but got [%s]' % ease_name)
        elif self.cur_button_count == 3:
            if ease_name == "Again":
                ease = 1
            elif ease_name == "Good":
                ease = 2
            elif ease_name == "Easy":
                ease = 3
            else:
                raise Exception('Invalid ease used, expected [Again], [Good] or [Easy] but got [%s]' % ease_name)
        else:
            if ease_name == "Again":
                ease = 1
            elif ease_name == "Hard":
                ease = 2
            elif ease_name == "Good":
                ease = 3
            elif ease_name == "Easy":
                ease = 4
            else:
                raise Exception('Invalid ease used, expected '
                                '[Again], [Hard], [Good] or [Easy] but got [%s]' % ease_name)

        self.logger.debug('send_answer with ease_name [%s]' % ease_name)
        self.logger.debug('send_answer with ease [%s]' % ease)

        # Get current card and check it's the expected card
        current_card = self.anki_utils.get_current_card()
        if current_card['card_id'] == self.current_card_id:
            # Send the answer
            answer_result = self.anki_utils.answer_card(ease)
            self.logger.debug('answer_result: %s' % answer_result)
        else:
            # TODO - Handle this better, notify user?
            self.logger.warning('The card you tried to answer is no longer the card being reviewed...')

        # In Infinity Mode, load the next card automatically. The reload is
        # deferred via a timer so Anki has a chance to advance to the next card
        # first; _infinity_reload() then polls until the new card is available.
        if self.infinity_mode:
            self._infinity_retries = 0
            self._infinity_timer.start(50)
        else:
            self.hide_popup()

    def hide_popup(self):
        self.reset_card()
        self.popup_window.hide()

    def hide_card(self):
        self.hide_popup()
        current_deck = self.anki_utils.get_config()['deck']
        review_ended = self.anki_utils.move_to_overview_state(current_deck)
        self.logger.info('review_ended: %s' % review_ended)
