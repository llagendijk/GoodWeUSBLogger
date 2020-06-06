"""
from https://github.com/vpelletier/python-hidraw

 copied and renamed due to the existence of another 'hidraw' package on pypi which seems to conflict in some way.

"""
from __future__ import absolute_import
from __future__ import print_function
import ctypes
import struct
import collections
import fcntl
import ioctl_opt
import binascii

# input.h
import sys

BUS_USB = 0x03
BUS_HIL = 0x04
BUS_BLUETOOTH = 0x05
BUS_VIRTUAL = 0x06

# hid.h
_HID_MAX_DESCRIPTOR_SIZE = 4096

if sys.version[0] < '3':

    def b(x):
        return x
else:
    import codecs

    def b(x):
        return codecs.latin_1_encode(x)[0]


# hidraw.h
class _hidraw_report_descriptor(ctypes.Structure):
    _fields_ = [
        ('size', ctypes.c_uint),
        ('value', ctypes.c_ubyte * _HID_MAX_DESCRIPTOR_SIZE),
    ]


class _hidraw_devinfo(ctypes.Structure):
    _fields_ = [
        ('bustype', ctypes.c_uint),
        ('vendor', ctypes.c_short),
        ('product', ctypes.c_short),
    ]


_HIDIOCGRDESCSIZE = ioctl_opt.IOR(ord('H'), 0x01, ctypes.c_int)
_HIDIOCGRDESC = ioctl_opt.IOR(ord('H'), 0x02, _hidraw_report_descriptor)
_HIDIOCGRAWINFO = ioctl_opt.IOR(ord('H'), 0x03, _hidraw_devinfo)
_HIDIOCGRAWNAME = lambda len: ioctl_opt.IOC(ioctl_opt.IOC_READ, ord('H'), 0x04,
                                            len)
_HIDIOCGRAWPHYS = lambda len: ioctl_opt.IOC(ioctl_opt.IOC_READ, ord('H'), 0x05,
                                            len)
_HIDIOCSFEATURE = lambda len: ioctl_opt.IOC(
    ioctl_opt.IOC_WRITE | ioctl_opt.IOC_READ, ord('H'), 0x06, len)
_HIDIOCGFEATURE = lambda len: ioctl_opt.IOC(
    ioctl_opt.IOC_WRITE | ioctl_opt.IOC_READ, ord('H'), 0x07, len)
_HIDIOCSREPORT = lambda len: ioctl_opt.IOC(
    ioctl_opt.IOC_WRITE | ioctl_opt.IOC_READ, ord('H'), 0x08, len)

HIDRAW_FIRST_MINOR = 0
HIDRAW_MAX_DEVICES = 64
HIDRAW_BUFFER_SIZE = 64

DevInfo = collections.namedtuple('DevInfo', ['bustype', 'vendor', 'product'])


class HIDRaw(object):
    """
    Provides methods to access hidraw device's ioctls.
    """

    def __init__(self, device):
        """
        device (file, fileno)
            A file object or a fileno of an open hidraw device node.
        """
        self._device = device

    def _ioctl(self, func, arg, mutate_flag=False):
        result = fcntl.ioctl(self._device, func, arg, mutate_flag)
        if result < 0:
            raise IOError(result)

    def getRawReportDescriptor(self):
        """
        Return a binary string containing the raw HID report descriptor.
        """
        descriptor = _hidraw_report_descriptor()
        size = ctypes.c_uint()
        self._ioctl(_HIDIOCGRDESCSIZE, size, True)
        descriptor.size = size
        self._ioctl(_HIDIOCGRDESC, descriptor, True)
        return b''.join(chr(x) for x in descriptor.value[:size.value])

    # TODO: decode descriptor into a python object
    #def getReportDescriptor(self):

    def getInfo(self):
        """
        Returns a DevInfo instance, a named tuple with the following items:
        - bustype: one of BUS_USB, BUS_HIL, BUS_BLUETOOTH or BUS_VIRTUAL
        - vendor: device's vendor number
        - product: device's product number
        """
        devinfo = _hidraw_devinfo()
        self._ioctl(_HIDIOCGRAWINFO, devinfo, True)
        return DevInfo(devinfo.bustype, devinfo.vendor, devinfo.product)

    def getName(self, length=512):
        """
        Returns device name as an unicode object.
        """
        name = ctypes.create_string_buffer(length)
        self._ioctl(_HIDIOCGRAWNAME(length), name, True)
        return name.value.decode('UTF-8')

    def getPhysicalAddress(self, length=512):
        """
        Returns device physical address as a string.
        See hidraw documentation for value signification, as it depends on
        device's bus type.
        """
        name = ctypes.create_string_buffer(length)
        self._ioctl(_HIDIOCGRAWPHYS(length), name, True)
        return name.value

    def sendOutputReport(self, report, report_num=0):
        """
        Send an output report.
        """
        length = len(report) + 1
        buf = ctypes.create_string_buffer(
            struct.pack("B", report_num) + report, length)
        self._device.write(buf)


# sendFeatureReport seems to be unused, remove it?

    def sendFeatureReport(self, report, report_num=0):
        """
        Send a feature report.
        """
        length = len(report) + 1
        buf = ctypes.create_string_buffer(
            b(struct.pack("B", report_num) + report), length)
        self._ioctl(_HIDIOCSFEATURE(length), buf, True)
        print(_HIDIOCSFEATURE(length))

    def getFeatureReport(self, report_num=0, length=63):
        """
        Receive a feature report.
        Blocks, unless you configured provided file (descriptor) to be
        non-blocking.
        """
        length += 1
        buf = ctypes.create_string_buffer(length)
        buf[0] = chr(report_num)
        self._ioctl(_HIDIOCGFEATURE(length), buf, True)
        return buf.value
