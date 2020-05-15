#coding:utf-8

from ECService import *

if __name__ == "__main__":
    parseSysmap()
    test1 = serviceID["test1"]
    test2 = serviceID["test2"]

    service = ECService(test1)
    service.registerEvent(1001, defaultHandler)
    service1 = ECService(test2)
    service1.registerEvent(0x70009, defaultHandler)

    service1.startProc()
    ev = EV_FPGA_CONF_REGISTER_DEV()
    service.sendTo(test2, ev)
    service1.stopProc()

    ev = EV_FPGA_CONF_REGISTER_DEV()
    service.sendTo(test2, ev)
    print type(service1.waitEvent(0x70009, 10))

    time.sleep(15)

    service.exit()
    service1.exit()