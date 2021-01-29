# Copyright 2020 Charles Henry
from PyQt5.QtCore import QTimer
import time


class RuzuSchedule:

    def __init__(self, alarm_func, cancel_func):
        self.alarm_func = alarm_func
        self.cancel_func = cancel_func
        self.schedule_interval = 1000
        self.timer = QTimer()
        self.timer.timeout.connect(self.exec_schedule)
        self.enabled = False

    def set_schedule(self, interval):
        print("set_schedule ", time.ctime())
        self.schedule_interval = interval

    def exec_schedule(self):
        print("exec_schedule ", time.ctime())
        self.alarm_func()

    def start_schedule(self):
        print("start_schedule ", time.ctime())
        self.timer.start(self.schedule_interval*1000)
        self.enabled = True

    def stop_schedule(self):
        print("stop_schedule ", time.ctime())
        self.timer.stop()
        self.cancel_func()
        self.enabled = False

    def update_state(self, config):
        if self.schedule_interval != config['frequency'] * 60:
            print('Existing freq: [%s], new freq: [%s]' % (self.schedule_interval, config['frequency'] * 60))
            self.schedule_interval = config['frequency'] * 60
            # Must restart schedule if it's already running
            if self.enabled:
                self.start_schedule()

        # Restart schedule if flag has changed
        if self.enabled != config['enabled']:
            print('Enabled flag changed from [%s] to [%s]' % (self.enabled, config['enabled']))
            if config['enabled']:
                self.start_schedule()
            else:
                self.stop_schedule()
