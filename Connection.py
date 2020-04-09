#coding=utf-8

import socket
import EventBase
from time import sleep
# import EventLibs

connList = []

connEvTypeProbe = 4
connEvTypeProbeRes = 8

class Connection:
    def __init__(self, fid, tid, sock, status):
        self.fid = fid
        self.tid = tid
        self.sock = sock
        self.status = status

    def updateStatus(self, status):
        self.status = status

    def sendEv(self, ev):
        ev.header.length = sizeof(ev)
        ev.header.checksum = ev.sum()
        print 'sending event %d to %d' % (ev.header.code, ev.header.sid)
        if self.sock is not None:
            self.sock.send(struct2string(ev))
        else:
            print "connection from %d to %d's socket is None" % (self.fid, self.tid)

    def sendProbe(self):
        ev = EV_ECL_CONNECT()

        ev.to = self.tid
        setattr(ev, "from", self.fid)
        ev.fd = 0
        ev.type = connEvTypeProbe
        ev.en_connected_probe = 0
        ev.conn_status = 4
        ev.header.rid = self.tid
        ev.header.sid = self.fid
        self.sendEv(ev)

    def sendProbeRes(self):
        ev = EV_ECL_CONNECT()

        ev.to = self.tid
        setattr(ev, "from", self.fid)
        ev.fd = 0
        ev.type = connEvTypeProbeRes
        ev.en_connected_probe = 0
        ev.conn_status = 2
        ev.header.rid = self.tid
        ev.header.sid = self.fid
        self.sendEv(ev)

def newConn(fid, tid, sock):
    conn = Connection(fid, tid, sock, 'inited')
    connList.append(conn)
    return conn

def removeConn(sock):
    conn = findConn(sock)
    if None != conn:
        connList.remove(conn)

def findConnById(fid, tid):
    for c in connList:
        if fid == c.fid and tid == c.tid:
            return c
        if fid == c.tid and tid == c.fid:
            return c
    return None

def findConn(sock):
    for c in connList:
        if sock is c.sock:
            return c
    return None

def processConnEv(ev, sock):
    conn = findConn(sock)
    if None == conn:
        return
    if ev.type == connEvTypeProbe:
        conn.fid = ev.header.sid
        conn.updateStatus('connected')
        conn.sendProbeRes()
    if ev.type == connEvTypeProbeRes:
        conn.updateStatus('connected')

def displayConn():
    for c in connList:
        print str(c.fid) + ' ' + str(c.tid)

if __name__ == "__main__":
    newConn(100, 200, None)
    conn = findConnById(100, 200)
    if conn is not None:
        print ("conn: from %d to %d" %(conn.fid, conn.tid))
    else:
        print ("conn: not found")

    conn = findConnById(200, 100)
    if conn is not None:
        print ("conn: from %d to %d" %(conn.fid, conn.tid))
    else:
        print ("conn: not found")