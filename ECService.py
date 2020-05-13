#coding=utf-8

import time
import Queue

from processHandler import *
from Connection import *
from socketHandler import *
from EventBase import *
from SysmapConfig import *

class ECService:
    def __init__(self, svcId):
        self.svcId = svcId
        self.evtQueue = Queue.Queue()
        self.sockHandler = socketHandler(svcId, self.evtQueue)
        ip, port = findSVCIpPort(svcId)
        if ip is not None:
            self.sockHandler.tcpListen(ip, port)
            print("service [%d] is listen on [%s:%d]" % (self.svcId, ip, port))
        else:
            print ("get service [%d] ip error" % self.svcId)
        self.procHandler = processHandler(self.evtQueue)
        self.sockHandler.start()

    # start callback handle
    def startProc(self):
        if self.procHandler is not None:
            self.procHandler.start()

    # stop callback handle
    def stopProc(self):
        if self.procHandler is not None:
            self.procHandler.stop()

    # exit socket communication
    def exit(self):
        if self.sockHandler is not None:
            self.sockHandler.exit()
        if self.procHandler is not None:
            self.procHandler.exit()

    # send event to connected service(business connect service list, not socket connect)
    def sendTo(self, toSvc, ev):
        ev.header.sid = self.svcId
        ev.header.rid = toSvc

        conn = self.sockHandler.connectTo(toSvc)

        if conn is not None:
            conn.sendEv(ev)

    # establish business connect service(include socket connect)
    def connectTo(self, toSvc):
        conn = self.sockHandler.connectTo(toSvc)
        if conn is not None:
            time.sleep(1)
            if conn.status == 'connected':
                return 'connected'

        return None

    # register event and it's callback for processing
    def registerEvent(self, evtCode, func = None):
        self.procHandler.evtProcFun[evtCode] = func

    # wait event and others
    def waitEvent(self, evtCode, timeoutSec):
        st = time.time()
        try:
            while (time.time()-st) <= timeoutSec:
                evtData = self.evtQueue.get(timeout=timeoutSec)
                if evtData is not None:
                    event = string2struct(evtData, EVENT_HEADER_TYPE)
                    if event.code == evtCode:
                        return evtCode
        except:
            info = sys.exc_info()
            print info[0]+";"+info[1]
            return None

if __name__ == "__main__":
    parseSysmap()
    test1 = serviceID["test1"]
    test2 = serviceID["test2"]

    service = ECService(test1)
    service.registerEvent(1001, defaultHandler)
    # ...