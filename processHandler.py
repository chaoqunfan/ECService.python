#coding = utf-8

import sys
import Queue
from EventBase import *
from time import sleep

from threading import *

def defaultHandler(evtData):
    event = string2struct(evtData, EVENT_HEADER_TYPE)
    print("handle event %d" % event.code)

class processHandler(Thread):
    def __init__(self, evtQueue):
        super(processHandler, self).__init__(name = 'processHandler')

        self.evtQueue = evtQueue
        self.waitEvt = Event()
        self.thread_stop = True
        self.thread_exit = False
        self.evtProcFun = {}
        super(processHandler, self).start()

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
                #print string2struct(evtData, EVENT_HEADER_TYPE)
                if evtData is not None:
                    self.processEvent(evtData)
            except:
                #info = sys.exc_info()
                #print str(info[0]) + ";" + str(info[1])
                continue

    def processEvent(self, evtData):
        try:
            event = string2struct(evtData, EVENT_HEADER_TYPE)
        except:
            info = sys.exc_info()
            print str(info[0]) + ";" + str(info[1])
        if self.evtProcFun.has_key(event.code):
            fun = self.evtProcFun[event.code]
            fun(evtData)
        else:
            defaultHandler(evtData)

if __name__ == "__main__":
    q = Queue.Queue()
    p = processHandler(q)

    p.start()

    ev = EV_SS_START()
    ev2 = EV_SS_INIT_DONE()
    p.evtProcFun[ev.header.code] = defaultHandler

    q.put(struct2string(ev))
    q.put(struct2string(ev2))

    sleep(1)
    p.stop()

    sleep(3)
    p.start()

    q.put(struct2string(ev))
    sleep(1)
    p.stop()
    sleep(3)
    p.exit()


