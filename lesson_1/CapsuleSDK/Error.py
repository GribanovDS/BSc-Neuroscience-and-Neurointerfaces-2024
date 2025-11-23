from enum import Enum
import ctypes

class Error_Code(ctypes.c_int):
    OK = 0
    FailedToConnect = 1
    FailedToInitConnection = 2
    FailedToInitialize = 3
    DeviceError = 4
    IndividualNFBNotCalibrated = 5
    NotReceived = 6
    DeviceIsNull = 7
    ModuleAlreadyExists = 8
    ModuleIsNotSupported = 9
    FailedToSendData = 10
    Unknown = 255

class Error(ctypes.Structure):
    _fields_ = [
        ("message", ctypes.c_char * 256),
        ("success", ctypes.c_bool),
        ("code", ctypes.c_int)
    ]

class CapsuleException(Exception):
    def __init__(self, capsule_error : Error):
        self.message = capsule_error.message
        self.code = capsule_error.code
        super().__init__(self.message)