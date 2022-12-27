# Copyright 2020 Charles Henry
import time
import sys
import logging
from aqt import mw
from aqt.qt import *
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
    ruzu_popup.show_popup()


def hide_card():
    logger.info('hide_card: %s' % time.ctime())
    ruzu_popup.hide_card()


def show_options():
    ruzu_options = RuzuOptions(mw, ruzu_schedule)
    return ruzu_options.exec()


# Init Ruzu Schedule
ruzu_schedule = RuzuSchedule(show_next_card, hide_card)
ruzu_schedule.set_schedule(anki_utils.get_config()['frequency'] * 60)
if anki_utils.get_config()['enabled']:
    logger.info('Starting Ruzu Pop-ups...')
    ruzu_schedule.start_schedule()

mw.addonManager.setConfigAction(__name__, show_options)

options_action = QAction("Ruzu Pop-ups Options", mw)
options_action.triggered.connect(lambda _: show_options())
mw.form.menuTools.addAction(options_action)
