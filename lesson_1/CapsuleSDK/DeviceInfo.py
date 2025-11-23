import ctypes
from CapsuleSDK.Error import Error

class DeviceType(ctypes.c_int):
    DeviceType_Band = 0
    DeviceType_Buds = 1
    DeviceType_Headphones = 2
    DeviceType_Impulse = 3
    DeviceType_Any = 4
    DeviceType_BrainBit = 6
    DeviceType_SinWave = 100
    DeviceType_Noise = 101

class DeviceInfo:
    def __init__(self, pointer, lib):
        self._pointer = pointer
        self._lib = lib
        self._lib.clCDeviceInfo_GetName.restype = ctypes.c_char_p
        self._lib.clCDeviceInfo_GetFirmware.restype = ctypes.c_char_p
        self._lib.clCDeviceInfo_GetSerial.restype = ctypes.c_char_p
        self._lib.clCDeviceInfo_GetType.restype = ctypes.c_int
        self._lib.clCDeviceInfo_GetName.argtypes = [ctypes.POINTER(ctypes.c_int)]
        self._name = self._lib.clCDeviceInfo_GetName(self._pointer).decode('utf-8')
        self._firmware = self._lib.clCDeviceInfo_GetFirmware(self._pointer).decode('utf-8')
        self._serial = self._lib.clCDeviceInfo_GetSerial(self._pointer).decode('utf-8')
        self._type = DeviceType(self._lib.clCDeviceInfo_GetType(self._pointer))

    def get_name(self):
        return self._name
    
    def get_firmware(self):
        return self._firmware
    
    def get_serial(self):
        return self._serial
    
    def get_type(self):
        return self._type.value
