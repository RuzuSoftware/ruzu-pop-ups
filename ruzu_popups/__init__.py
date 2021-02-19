# Copyright 2020 Charles Henry
import time
import logging
from aqt import mw
from aqt.qt import *
from aqt import QMainWindow, QPushButton
from .gui.popup import RuzuPopup
from .anki_utils import AnkiUtils
from .gui.options import RuzuOptions
from .ruzu_schedule import RuzuSchedule

logger = logging.getLogger(__name__.split('.')[0])
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", "%H:%M:%S")
sh = logging.StreamHandler(sys.stdout)
sh.setFormatter(formatter)
logger.addHandler(sh)
logger.setLevel(logging.WARNING)


ruzu_popup = RuzuPopup(mw)
anki_utils = AnkiUtils()


def show_next_card():
    logger.info('show_next_card: %s' % time.ctime())
    ruzu_popup.show_question_popup()


def hide_card():
    logger.info('hide_card: %s' % time.ctime())
    ruzu_popup.hide_card()


def show_debug(rschedule):
    logger.info("start_app %s" % time.ctime())
    win = QMainWindow(parent=mw)
    win.setGeometry(0, 0, 400, 300)
    win.setWindowTitle("Window Title")

    btn_width = 100
    btn_height = 50
    btn_padding = 20
    start_btn = QPushButton(parent=win, text="Start")
    start_btn.setGeometry(btn_padding * 1 + btn_width * 0, btn_padding, btn_width, btn_height)
    stop_btn = QPushButton(parent=win, text="Stop")
    stop_btn.setGeometry(btn_padding * 2 + btn_width * 1, btn_padding, btn_width, btn_height)
    show_next_btn = QPushButton(parent=win, text="Show next card")
    show_next_btn.setGeometry(btn_padding * 3 + btn_width * 2, btn_padding, btn_width, btn_height)

    start_btn.clicked.connect(rschedule.start_schedule)
    stop_btn.clicked.connect(rschedule.stop_schedule)
    show_next_btn.clicked.connect(rschedule.exec_schedule)

    start_btn.show()
    stop_btn.show()
    show_next_btn.show()
    win.show()


def show_options():
    ruzu_options = RuzuOptions(mw, ruzu_schedule)
    return ruzu_options.exec_()


# Init Ruzu Schedule
ruzu_schedule = RuzuSchedule(show_next_card, hide_card)
ruzu_schedule.set_schedule(anki_utils.get_config()['frequency'] * 60)
if anki_utils.get_config()['enabled']:
    logger.info('Starting Ruzu Pop-ups...')
    ruzu_schedule.start_schedule()

mw.addonManager.setConfigAction(__name__, show_options)

# Add debug options, to be removed in future version
options_action = QAction("Ruzu Pop-ups Debug", mw)
options_action.triggered.connect(lambda _: show_debug(ruzu_schedule))
mw.form.menuTools.addAction(options_action)

options_action = QAction("Ruzu Pop-ups Options", mw)
options_action.triggered.connect(lambda _: show_options())
mw.form.menuTools.addAction(options_action)

