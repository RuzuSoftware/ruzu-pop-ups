# Copyright 2020 Charles Henry
from aqt import QLabel, QGridLayout, QPushButton, QWidget, QCheckBox, QComboBox, QDialog
from ..anki_utils import AnkiUtils
from .popup import THEME_ORDER, DEFAULT_THEME
import logging


class RuzuOptions(QDialog):

    def __init__(self, parent, ruzu_schedule):
        super().__init__(parent=parent)
        self.anki_utils = AnkiUtils()
        self.ruzu_schedule = ruzu_schedule
        self.config = self.anki_utils.get_config()
        self.logger = logging.getLogger(__name__.split('.')[0])
        # While True, widget change signals are ignored (set False once all
        # initial values are in place) so loading the dialog does not auto-save.
        self._loading = True
        ###
        # Top level Window
        ###
        self.setWindowTitle("Ruzu Pop-ups Options")
        self.setGeometry(0, 0, 400, 300)

        ###
        # Options
        ###
        # Deck
        self.deck_select_text = QLabel(text='Deck')
        self.deck_select = QComboBox()
        decks = self.anki_utils.get_decks()
        for deck in decks:
            self.deck_select.addItem(deck.name)
        self.deck_select.setCurrentIndex(max(self.deck_select.findText(self.config['deck']), 0))

        # Frequency
        self.freq_select_text = QLabel(text='Pop-up Frequency')
        self.freq_select_map = {
            'Every Minute': 1,
            'Every 3 Minutes': 3,
            'Every 5 Minutes': 5,
            'Every 10 Minutes': 10,
            'Every 15 Minutes': 15,
            'Every 20 Minutes': 20,
            'Every 25 Minutes': 25,
            'Every 30 Minutes': 30,
            'Every 45 Minutes': 45,
            'Every 60 Minutes': 60
        }
        self.freq_select = QComboBox()
        for frequency in self.freq_select_map.keys():
            self.freq_select.addItem(frequency)
        try:
            freq_select_idx = list(self.freq_select_map.values()).index(self.config['frequency'])
        except ValueError:
            self.logger.warning('Issue setting frequency dropdown based on config value, '
                                'setting frequency dropdown to default (Every 5 Minutes)')
            freq_select_idx = 2
        finally:
            self.freq_select.setCurrentIndex(freq_select_idx)

        # Enable Disable
        self.click_to_reveal_check_text = QLabel(text='Click to reveal')
        self.click_to_reveal_check = QCheckBox()
        self.click_to_reveal_check.setChecked(self.config['click_to_reveal'])

        # Enable Disable
        self.enabled_check_text = QLabel(text='Enable pop-ups')
        self.enabled_check = QCheckBox()
        self.enabled_check.setChecked(self.config['enabled'])

        # Self-typing mode
        self.enable_self_typing_check_text = QLabel(text='Enable Text Input Mode')
        self.enable_self_typing_check = QCheckBox()
        self.enable_self_typing_check.setChecked(self.config.get('enable_self_typing', False))

        # Theme
        self.theme_select_text = QLabel(text='Theme')
        self.theme_select = QComboBox()
        for theme_name in THEME_ORDER:
            self.theme_select.addItem(theme_name)
        self.theme_select.setCurrentIndex(
            max(self.theme_select.findText(self.config.get('theme', DEFAULT_THEME)), 0))

        # Close
        self.close_btn = QPushButton(text='Close')
        self.close_btn.clicked.connect(self.hide)

        # Show Next Card
        self.show_card_btn = QPushButton(text='Show Next Card')
        self.show_card_btn.clicked.connect(self.show_next_card_and_close)

        # Reset pop-up position (in case the window was dragged out of reach)
        self.reset_position_btn = QPushButton(text='Reset Pop-up Position')
        self.reset_position_btn.setToolTip(
            'Move the pop-up back to its default spot (bottom-right of the main screen).')
        self.reset_position_btn.clicked.connect(self.reset_window_position)

        ###
        # Layout management - Add objects to main pop-up window
        ###
        self.grid = QGridLayout()
        self.grid.addWidget(self.deck_select, 0, 1)
        self.grid.addWidget(self.deck_select_text, 0, 0)
        self.grid.addWidget(self.freq_select, 1, 1)
        self.grid.addWidget(self.freq_select_text, 1, 0)
        self.grid.addWidget(self.click_to_reveal_check, 2, 1)
        self.grid.addWidget(self.click_to_reveal_check_text, 2, 0)
        self.grid.addWidget(self.enabled_check, 3, 1)
        self.grid.addWidget(self.enabled_check_text, 3, 0)
        self.grid.addWidget(self.enable_self_typing_check, 4, 1)
        self.grid.addWidget(self.enable_self_typing_check_text, 4, 0)
        self.grid.addWidget(self.theme_select, 5, 1)
        self.grid.addWidget(self.theme_select_text, 5, 0)
        self.grid.addWidget(self.show_card_btn, 6, 1)
        self.grid.addWidget(self.reset_position_btn, 6, 0)
        self.grid.addWidget(self.close_btn, 7, 1)
        self.setLayout(self.grid)

        # Settings are saved and applied immediately on every change (no Save
        # button). Signals are connected only now, after all initial widget
        # values have been set above, so loading the dialog does not trigger a
        # save. The guard flag is belt-and-braces against any stray init signal.
        self._loading = False
        self.deck_select.currentIndexChanged.connect(self._on_setting_changed)
        self.freq_select.currentIndexChanged.connect(self._on_setting_changed)
        self.click_to_reveal_check.toggled.connect(self._on_setting_changed)
        self.enabled_check.toggled.connect(self._on_setting_changed)
        self.enable_self_typing_check.toggled.connect(self._on_setting_changed)
        self.theme_select.currentIndexChanged.connect(self._on_setting_changed)

    def _on_setting_changed(self, *_args):
        if getattr(self, '_loading', True):
            return
        self.save_config()

    def save_config(self):
        self.logger.info('Saving config...')
        # Preserve the persisted pop-up position; it is managed by dragging the
        # window, not by this dialog, so we must not wipe it when saving options.
        existing = self.anki_utils.get_config()
        self.config = {
            "deck": self.deck_select.currentText(),
            "frequency": self.freq_select_map[self.freq_select.currentText()],
            "enabled": self.enabled_check.isChecked(),
            "click_to_reveal": self.click_to_reveal_check.isChecked(),
            "enable_self_typing": self.enable_self_typing_check.isChecked(),
            "theme": self.theme_select.currentText(),
            "window_location": "bottom_right",
            "window_position": existing.get('window_position'),
            "show_marked_card_flag": False
        }
        self.anki_utils.set_config(self.config)
        # Apply schedule-related changes (frequency / enabled) right away...
        self.ruzu_schedule.update_state(self.config)
        # ...and apply the rest (theme, self-typing, etc.) to the live pop-up.
        self._apply_to_live_popup()
        self.logger.debug("New config value: %s" % self.anki_utils.get_config())

    def _apply_to_live_popup(self):
        # The pop-up instance is created once at add-on load (module level).
        # Reach it via a lazy import to avoid a circular import at module load.
        try:
            from .. import ruzu_popup
            ruzu_popup.apply_config()
        except Exception:
            self.logger.warning('Could not apply config to live pop-up', exc_info=True)

    def reset_window_position(self):
        # Clear the persisted position so the pop-up returns to its default spot.
        # Also reset (and reposition) the live pop-up if it already exists.
        self.logger.info('Reset pop-up position...')
        config = self.anki_utils.get_config()
        config['window_position'] = None
        self.anki_utils.set_config(config)
        # The pop-up instance is created once at add-on load (module level). Reach
        # it via a lazy import to avoid a circular import at module load time.
        try:
            from .. import ruzu_popup
            ruzu_popup.window_position = None
            if ruzu_popup.popup_window.isVisible():
                ruzu_popup.set_card_position()
        except Exception:
            self.logger.warning('Could not reset live pop-up position', exc_info=True)
        try:
            from aqt.utils import tooltip
            tooltip('Pop-up position reset to default.')
        except Exception:
            pass

    def show_next_card_and_close(self):
        self.ruzu_schedule.exec_schedule()
        self.close()
