# Copyright 2020 Charles Henry
from aqt.webview import AnkiWebView
from PyQt5 import QtCore
from aqt import Qt, QWidget, QGridLayout, QPushButton, QDialog, QHBoxLayout
from ..anki_utils import AnkiUtils


class RuzuPopup(QDialog):

    def __init__(self, parent):
        self.parent = parent
        self.anki_utils = AnkiUtils()
        self.current_card_id = None
        self.cur_button_count = 0

        # popup_window (QWidget)
        # -grid (QGridLayout)
        # --card_view (QWebEngineView)
        # --bottom_grid (QGridLayout)
        # ---buttons self.btn[0~3] (QPushButton)

        ###
        # Top level Pop-up Window
        ###
        parent.popup_window = self.popup_window = QWidget()
        self.popup_window.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.popup_window.setWindowFlag(Qt.FramelessWindowHint)  # Hide the title bar
        self.popup_window.setWindowTitle("Anki Review")  # Set the title (visible in windows taskbar)
        self.popup_window.setGeometry(0, 0, 400, 300)  # Set window geometry

        ###
        # Card View
        ###
        parent.card_view = self.card_view = AnkiWebView()

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
        self.grid.addWidget(self.card_view)
        self.grid.addLayout(self.bottom_grid, 1, 0)
        self.popup_window.setLayout(self.grid)

    def set_card_position(self):
        # Move to bottom right of screen
        # https://stackoverflow.com/questions/28322073/move-qmessagebox-to-bottom-right-corner-of-the-screen
        screen_geometry = self.parent.app.desktop().availableGeometry()
        screen_geo = screen_geometry.bottomRight()
        msg_geo = self.popup_window.frameGeometry()
        msg_geo.moveBottomRight(screen_geo)
        self.popup_window.move(msg_geo.topLeft())

    def show_question_button(self):
        for i in range(5):
            self.bottom_grid_2.addWidget(self.btn[i])  # Remove all buttons
        self.bottom_grid.addWidget(self.btn[4])

    def show_answer_buttons(self):
        # TODO - Take in actual buttons tuple?
        for i in range(5):
            self.bottom_grid_2.addWidget(self.btn[i])  # Remove all buttons
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

    def reset_card(self):
        self.card_view.setHtml(None)

    def update_card(self, card):
        # TODO - Look into using existing AnkiWebView object to render duplicate card with full compatibility
        self.card_view.setHtml("""
                    <!doctype html>
                    <html class=" webkit chrome win js">
                        <head>
                            <title>main webview</title>
                            <style>
                                body { zoom: 1; background: #f0f0f0; direction: ltr; font-size:12px;font-family:"Segoe UI"; }
                                button { font-family:"Segoe UI"; }
                                :focus { outline: 1px solid #0078d7; }
                            </style>
                        </head>

                        <body class="card card2 isWin">
                            <div id="qa" style="opacity: 1;">
                                """ + card + """
                            </div>
                        </body>
                    </html>
                """)

    def pre_popup_validate(self):
        print('pre_popup_validate...')
        # Get current deck from config
        current_deck = self.anki_utils.get_config()['deck']

        # Check that review is active and current deck is as expected (if not then start review)
        if not self.anki_utils.review_is_active() or current_deck != self.anki_utils.selected_deck():
            print('Start review...')
            review_started = self.anki_utils.move_to_review_state(current_deck)
            print('review_started: %s' % review_started)
            if not review_started:
                print('Failed to start review...')
            if review_started and not self.anki_utils.review_is_active():
                print('No cards left to review')
                # TODO - Show popup saying no cards left, state that schedule is now off
                # TODO - Turn off schedule automatically

    def show_answer_popup(self):
        print('show_answer_popup...')
        self.popup_window.hide()
        self.pre_popup_validate()
        show_ans_result = self.anki_utils.show_answer()
        print('Show Answer Result: %s' % show_ans_result)

        # Collect card details (html, css, buttons)
        current_card = self.anki_utils.get_current_card()
        if self.current_card_id != current_card['card_id']:
            # TODO - Inform user of this action?
            print('Card has changed, show new card...')
            self.show_question_popup()
        else:
            self.cur_button_count = len(current_card['button_list'])
            self.show_answer_buttons()
            self.update_card(current_card['answer'])

            # Show pop-up
            self.set_card_position()
            self.popup_window.show()

    def show_question_popup(self):
        print('display_popup...')
        self.popup_window.hide()
        self.pre_popup_validate()
        show_q_result = self.anki_utils.show_question()
        print('Show Question Result: %s' % show_q_result)

        # Collect card details (html, css, buttons)
        current_card = self.anki_utils.get_current_card()
        self.current_card_id = current_card['card_id']
        print('Setting current card to %s' % current_card['card_id'])
        self.update_card(current_card['question'])
        self.show_question_button()

        # Show pop-up
        self.set_card_position()
        self.popup_window.show()

    def send_answer(self, ease_name):
        # TODO - Clean this up, not elegant at all
        if self.cur_button_count == 2:
            if ease_name == "Again":
                ease = 1
            elif ease_name == "Good":
                ease = 2
            else:
                # TODO - Handle this error better, notify user?
                print('Invalid ease used, expected [Again] or [Good] but got [%s]' % ease_name)
                ease = 0
        elif self.cur_button_count == 3:
            if ease_name == "Again":
                ease = 1
            elif ease_name == "Good":
                ease = 2
            elif ease_name == "Easy":
                ease = 3
            else:
                # TODO - Handle this error better, notify user?
                print('Invalid ease used, expected [Again], [Good] or [Easy] but got [%s]' % ease_name)
                ease = 0
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
                # TODO - Handle this error better, notify user?
                print('Invalid ease used, expected [Again], [Hard], [Good] or [Easy] but got [%s]' % ease_name)
                ease = 0

        # Only attempt to answer card if ease is valid
        if ease != 0:
            print('send_answer with ease_name [%s]' % ease_name)
            print('send_answer with ease [%s]' % ease)

            # Get current card and check it's the expected card
            current_card = self.anki_utils.get_current_card()
            current_card = self.anki_utils.get_current_card()
            if current_card['card_id'] == self.current_card_id:
                # Send the answer
                answer_result = self.anki_utils.answer_card(ease)
                print('answer_result: %s' % answer_result)
            else:
                # TODO - Handle this error better, notify user?
                print('The card you tried to answer is no longer the card being reviewed...')

        self.hide_card()

    def hide_card(self):
        self.reset_card()
        self.popup_window.hide()
