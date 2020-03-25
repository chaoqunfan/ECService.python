#coding = utf-8

import sys
import Queue

from threading import *

def defaultHandler(evtData):
    event = string2struct(evtData, EVENT_HEADER_TYPE)
    print "handle event %" event.code

class processHandler(Thread):
    def __init__(self, evtQueue):
        super(processHandler, self).__init__(name = 'processHandler')

        self.evtQueue = evtQueue
        self.waitEvt = Event()
        self.thread_stop = False
        self.thread_exit = False
        self.evtProcFun = {}

    def start(self):
        self.thread_stop = False
        self.waitEvt.set()

    def stop(self):
        self.thread_stop = True
        self.waitEvt.clear()

    def exit(self):
        self.waitEvt.set()
        self.thread_exit = True

    def run(self):
        while True:
            if self.thread_exit is True:
                print 'thread exit'
                return

            if self.thread_stop is True:
                self.waitEvt.wait()

            if self.evtQueue is None:
                print 'processHandle evtQueue is Null'
                return

            try:
                evtData = self.evtQueue.get(timeout = 2)
                if evtData is not None:
                    self.processEvent(evtData)
            except:
                info = sys.exec_info()
                print info[0] + ";" + info[1]
                continue

    def processEvent(self, evtData):
        try:
            event = string2struct(evtData, EVENT_HEADER_TYPE)
        except:
            info = sys.exec_info()
            print info[0] + ";" + info[1]
        if self.evtProcFun.has_key(event.code):
            fun = self.evtProcFun[event.code]
            fun(evtData)
        else:
            defaultHandler(evtData)

