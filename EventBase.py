# coding=utf-8

from ctypes import *

# implement the event header class

def string2struct(string, stype):
    # convert python string to c/c++ structure type
    if not issubclass(stype, Structure):
        raise ValueError('The type of the struct is not a ctypes.Structure')
    p = cast(string, POINTER(stype))
    return p.contents

def struct2string(s):
    length = sizeof(s)
    p = cast(pointer(s), POINTER(c_char * length))
    #print int(p.contents.raw,16)
    return p.contents.raw

class EVENT_HEADER_TYPE(Structure):
    _fields_ = [
        ('code', c_uint32),
        ('length', c_uint32),
        ('sid', c_uint32),
        ('rid', c_uint32),
        ('checksum', c_uint32),
        ('not_log', c_uint32),
        ('send_time', c_int64),
        ('received_time', c_int64),
        ('complete_time', c_int64)
    ]

class EventBase(Structure):
    def __init__(self, code):
        Structure.__init__(self)
        self.header.code = code

    _fields_ = [('header', EVENT_HEADER_TYPE)]

    def code(self):
        return self.header.code

    def sender(self):
        return self.header.sid

    def receiver(self):
        return self.header.rid

    def sum(self):
        return self.header.code + self.header.length + self.header.sid + self.header.rid

    def length(self):
        return self.header.length

class EV_ECL_CONNECT(EventBase):
    def __init__(self, code=1):
        EventBase.__init__(self, code)

    _fields_ = [
        ('type', c_int32),
        ('conn_status', c_int32),
        ('en_connected_probe', c_int32),
        ('from', c_int32),
        ('to', c_int32),
        ('fd', c_int32)
    ]

class EV_ECL_CONNECTED(EventBase):
    def __init__(self, code = 3):
        EventBase.__init__(self, code)

    _fields_ = [
        ('from', c_int32),
        ('to', c_int32)
    ]

class EV_ECL_DISCONNECT(EventBase):
    def __init__(self, code=2):
        EventBase.__init__(self, code)

class EV_ECL_DISCONNECTED(EventBase):
    def __init__(self, code=4):
        EventBase.__init__(self, code)

    _fields_ = [
        ('from', c_int32),
        ('to', c_int32)
    ]

class EV_SS_START(EventBase):
    def __init__(self, code=1001):
        EventBase.__init__(self, code)

class EV_SS_INIT_DONE(EventBase):
    def __init__(self, code=1003):
        EventBase.__init__(self, code)

class EV_FPGA_CONF_REGISTER_DEV(EventBase):
    def __init__(self, code=0x70009):
        EventBase.__init__(self, code)