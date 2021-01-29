# Copyright 2020 Charles Henry
from aqt import QLabel, QGridLayout, QPushButton, QDialog, QCheckBox, QComboBox
from ..anki_utils import AnkiUtils


class RuzuOptions(QDialog):

    def __init__(self, parent, ruzu_schedule):
        super().__init__(parent=parent)
        self.anki_utils = AnkiUtils()
        self.ruzu_schedule = ruzu_schedule
        self.config = self.anki_utils.get_config()
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
            'Every 5 seconds': 5/60,
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
            print('Default frequency to Every 5 Minutes')
            freq_select_idx = 2
        finally:
            self.freq_select.setCurrentIndex(freq_select_idx)

        # Enable Disable
        self.enabled_check_text = QLabel(text='Enable pop-ups')
        self.enabled_check = QCheckBox()
        self.enabled_check.setChecked(self.config['enabled'])

        # OK
        self.ok_btn = QPushButton(text='OK')
        self.ok_btn.clicked.connect(self.save_and_close)
        # Cancel
        self.close_btn = QPushButton(text='Cancel')
        self.close_btn.clicked.connect(self.hide)

        ###
        # Layout management - Add objects to main pop-up window
        ###
        self.grid = QGridLayout()
        self.grid.addWidget(self.deck_select, 0, 1)
        self.grid.addWidget(self.deck_select_text, 0, 0)
        self.grid.addWidget(self.freq_select, 1, 1)
        self.grid.addWidget(self.freq_select_text, 1, 0)
        self.grid.addWidget(self.enabled_check, 2, 1)
        self.grid.addWidget(self.enabled_check_text, 2, 0)
        self.grid.addWidget(self.ok_btn, 3, 0)
        self.grid.addWidget(self.close_btn, 3, 1)
        self.setLayout(self.grid)

    def save_and_close(self):
        self.update_config()
        self.hide()

    def update_config(self):
        print('Update config...')
        self.config = {
            "deck": self.deck_select.currentText(),
            "frequency": self.freq_select_map[self.freq_select.currentText()],
            "enabled": self.enabled_check.checkState() == 2,
            "window_location": "bottom_right",
            "show_marked_card_flag": False
        }
        self.anki_utils.set_config(self.config)
        self.ruzu_schedule.update_state(self.config)

        # TODO - Remove debug
        print(self.anki_utils.get_config())
