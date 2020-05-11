#coding=utf-8

import os
import sys
import codecs
from SVCIDLib import *
from xml.dom import minidom

isParseSysmap = 0
sysmapFile = "sysmap.xml"
services = {}

class Service:
    def __init__(self, name, svcId, ip, port, nodeName, procName):
        self.name = name
        self.svcId = svcId
        self.ip = ip
        self.port = port
        self.nodeName = nodeName
        self.procName = procName

def getAttrValue(node, attrName):
    return node.getAttribute(attrName) if node else ""

def getNodeValue(node, index=0):
    return node.childNodes[index].nodeValue if node else ""

def getXmlNode(node, name):
    return node.getElementsByTagName(name) if node else []

def encrypt(infile, key):
    p_len = len(key)
    f_len = len(infile)

    outfile = ""
    for i in range(f_len):
        # XOR
        ichr = (ord(infile[i])) ^ (ord(key[i%p_len]))
        if ichr == 0:
            outfile += infile[i]
        else:
            outfile += chr(ichr)

    return outfile

def parseEncrypt(filename):
    f = codecs.open(filename, 'r', 'utf-8')
    try:
        infile = f.read()
    finally:
        f.close()
    if infile[0] == "<":
        return minidom.parseString(infile)
    else:
        outfile = encrypt(infile, "Sinovision")
        return minidom.parseString(outfile)

# @implement: parse sysmap file
# @return: -1 -- parse failed
# @return:  0 -- parse success
def parseSysmap(filename = sysmapFile):
    global isParseSysmap

    if isParseSysmap == 1:
        return -1

    if os.path.exists(filename):
        pass
    else:
        print 'sysmap file [%s] not exist!' % filename
        return -1

    dom = parseEncrypt(filename)
    root = dom.documentElement

    if ("config" != root.nodeName):
        print "sysmap file [%s] root element is not config" % filename
        return -1

    nodeInfos = getXmlNode(root, "node_info")

    # traverse node info
    for nodeInfo in nodeInfos:
        nodeName = getAttrValue(nodeInfo, "name")
        nodeIp   = getAttrValue(nodeInfo, "ip")

        # traverse service info
        procInfos = getXmlNode(nodeInfo, "proc_info")
        for procInfo in procInfos:
            procName = getAttrValue(procInfo, "name")

            # traverse service info
            serviceInfos = getXmlNode(procInfo, "service_info")
            for serviceInfo in serviceInfos:
                serviceName = getAttrValue(serviceInfo, "name")
                port        = int(getAttrValue(serviceInfo, "port"))
                if serviceID.has_key(serviceName):
                    svcId = serviceID[serviceName]
                    svc = Service(serviceName, svcId, nodeIp, port, procName, nodeName)
                    services[serviceName] = svc
                else:
                    print "service [%s] is not in default table" % serviceName
    isParseSysmap = 1
    return 0

def findSVCIpPort(svcId):
    global isParseSysmap
    if isParseSysmap == 0:
        parseSysmap()

    for serviceName in services:
        if services[serviceName].svcId == svcId:
            return (services[serviceName].ip, services[serviceName].port)

    return (None, 0)

def displayServices():
    for serviceName in services:
        svc = services[serviceName]
        print "service name [%s] id [%d] ip [%s] port [%d] procName [%s] nodeName [%s] " % (svc.name, svc.svcId, svc.ip, svc.port, svc.procName, svc.nodeName)


if __name__ == "__main__":
    sys.path.append(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    print parseSysmap()
    #print services
    displayServices()

    print findSVCIpPort(300)