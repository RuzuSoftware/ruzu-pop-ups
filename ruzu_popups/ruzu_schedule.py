# Copyright 2020 Charles Henry
from PyQt5.QtCore import QTimer
import time
import logging


class RuzuSchedule:

    def __init__(self, alarm_func, cancel_func):
        self.alarm_func = alarm_func
        self.cancel_func = cancel_func
        self.schedule_interval = 1000
        self.timer = QTimer()
        self.timer.timeout.connect(self.exec_schedule)
        self.enabled = False
        self.logger = logging.getLogger(__name__.split('.')[0])

    def set_schedule(self, interval):
        self.logger.info("set_schedule %s" % time.ctime())
        self.schedule_interval = interval

    def exec_schedule(self):
        self.logger.info("exec_schedule %s" % time.ctime())
        self.alarm_func()

    def start_schedule(self):
        self.logger.info("start_schedule %s" % time.ctime())
        self.timer.start(self.schedule_interval*1000)
        self.enabled = True

    def stop_schedule(self):
        self.logger.info("stop_schedule %s" % time.ctime())
        self.timer.stop()
        self.cancel_func()
        self.enabled = False

    def update_state(self, config):
        if self.schedule_interval != config['frequency'] * 60:
            self.logger.debug('Existing freq: [%s], new freq: [%s]' % (self.schedule_interval, config['frequency'] * 60))
            self.schedule_interval = config['frequency'] * 60
            # Must restart schedule if it's already running
            if self.enabled:
                self.start_schedule()

        # Restart schedule if flag has changed
        if self.enabled != config['enabled']:
            self.logger.debug('Enabled flag changed from [%s] to [%s]' % (self.enabled, config['enabled']))
            if config['enabled']:
                self.start_schedule()
            else:
                self.stop_schedule()
