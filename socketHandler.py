#coding=utf-8

import socket
import select
import Queue
import sys
from Connection import *
from EventBase import *
from SysmapConfig import *
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

    # thread stop
    def stop(self):
        self.thread_stop = True

    # close socket communication
    def exit(self):
        for s in self.rlists:
            if s is not self.sock:
                s.shutdown(socket.SHUT_RDWR)
            s.close()
            removeConn(s)

    # is thread active
    def getStatus(self):
        pass

    # thread call back function
    def run(self):
        code = 0
        connEv = EV_ECL_CONNECT()
        while True:
            if self.thread_stop:
                self.exit()
                return

            rs,ws,es = select.select(self.rlists, self.wlists, self.rlists, 2)
            if not(rs or ws or es):
                continue
            for s in rs:
                # server socket accept
                if s is self.sock:
                    ns, addr = self.sock.accept()
                    print 'connect by ', addr

                    ns.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    ns.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                    ns.setblocking(False)

                    # update connection management
                    newConn(0, self.svcId, ns)

                    # update read socket list
                    self.rlists.append(ns)

                # client socket
                else:
                    try:
                        data, code = self.recv(s)
                    except:
                        info = sys.exc_info()
                        print info[0], ";", info[1]
                        self.rlists.remove(s)
                        removeConn(s)
                        s.shutdown(socket.SHUT_RDWR)
                        s.close()
                        continue

                    if data is None:
                        continue

                    # connect manager, connect probe and probeRes
                    if code == connEv.code():
                        ev = string2struct(data, EV_ECL_CONNECT)
                        processConnEv(ev, s)
                    # put evnt to queue to handle
                    else:
                        self.evtQueue.put(data)
                        #print 'queue size = ' + str(self.evtQueue.qsize())

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
                removeConn(s)


    # socket recv send shutdown
    def recv(self, sock):
        header = sock.recv(48)
        if header is not None:
            d = string2struct(header, EVENT_HEADER_TYPE)
            # print 'code = ' + str(d.code) + ' length = ' + str(d.length)

            if d.length + d.code + d.sid + d.rid != d.checksum:
                print 'invalid event header, the checksum check failed'
                raise Exception("checksum error")
            else:
                if d.length > 48:
                    if d.length > 2048:
                        sleep(0.5) # to large ?!
                    payload = sock.recv(d.length-48)
                    return (''.join([header, payload]), d.code)
                else:
                    return (header, d.code)
        else:
            raise Exception("recive error")

    def send(self):
        pass

    # create socket client to connect server
    def connectTo(self, toId):
        # get conn from connection management
        conn = findConnById(self.svcId, toId)
        if conn is None:
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
                info = sys.exc_info()
                print info[0], ":", info[1]
                return None

            # create new connection mangement
            conn = newConn(self.svcId, toId, sock)
            sock.setblocking(False)
            self.rlists.append(sock)
            # wait the select call timeout and then can process the new socket
            # do not understanding
            sleep(2)
            # connection probe
            conn.sendProbe()
        return conn

    # create socket server and listen
    def tcpListen(self, ip=None, port=65534):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setblocking(False)
        self.sock.bind((ip, port))
        self.sock.listen(5)
        self.rlists.append(self.sock)


