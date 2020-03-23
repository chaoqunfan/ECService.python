#coding=utf-8

import socket
import select
import Queue
import sys

from threading import *

class socketHandler(Thread):
    def __init__(self, svcId, evtQueue):
        super(socketHandler, self).__init__(name = 'socketHandler')

        self.svcId = svcId
        self.evtQueue = evtQueue
        self.sock = None
        self.rlists = []
        self.wlists = []
        self.thread_stop = False

    # thread start
    def start(self):
        self.thread_stop = False
        super(socketHandler, self).start()

    # update thread stop flag
    # not stop thread
    def stop(self):
        self.thread_stop = True

    # exit socket communication
    # not thread exit
    def exit(self):
        pass

    # get thread isActive
    def getStatus(self):
        pass

    # thread call back function
    def run(self):
        while True:
            if self.thread_stop:
                self.exit()
                return

            rs,ws,es = select.select(self.rlists, self.wlists, self.rlists, timeout=2)
            if not(rs or ws or es):
                continue
            for s in rs:
                # server socket
                if s is self.sock:
                    ns, addr = self.sock.accept()
                    print 'connect by ', addr

                    ns.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    ns.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                    ns.setblocking(False)

                    # update connection management

                    # update read socket list
                    self.rlists.append(ns)

                    pass
                # client socket
                else:
                    try:
                        data = self.recv()
                    except:
                        pass
                    pass

            for s in es:
                print 'except ', s.getpeername()
                if s in self.rlists:
                    self.rlists.remove(s)
                if s in self.wlists:
                    self.wlists.remove(s)
                # close data transmission
                s.shutdown(2)
                # close this client socket
                s.close()

                # delete connction from connection management
                pass


    # socket recv send suhtdown
    def recv(self, sock):
        header = sock.recv(48)
        if header is not None:
            pass
        else:
            raise Exception("recive error")
        pass

    def send(self):
        pass

    # create socket client to connect server
    def connectTo(self, toId):
        # get conn from connection management
        if not None:
            print 'connect to service ' + str(toId)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                #todo: get the address and port
                ip, port = findSVCIpPort(toId)
                if ip is not None:
                    sock.connect((ip, port))
                else:
                    print "get service %d's ip error" % toId
                    return None
            except:
                info = sys.exec_info()
                print info[0], ":", info[1]
                return None

            # create new connection mangement
            sock.setblocking(False)
            self.rlists.append(sock)
            # wait the select call timeout and then can process the new socket
            sleep(2)
            # connection probe 

        pass

    # create socket server and listen
    def tcpListen(self, ip=None, port=65534):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setblocking(False)
        self.sock.bind((ip, port))
        self.sock.listen(5)
        self.rlists.append(self.sock)


