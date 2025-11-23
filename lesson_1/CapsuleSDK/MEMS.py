import ctypes
from CapsuleSDK.Error import *
from CapsuleSDK.MEMSTimedData import MEMSTimedData
from typing import Callable
from CapsuleSDK.CapsulePointersImpl import capsule_pointers

class MEMS:
    _name_in_pointers_map = "MEMS"
    def __init__(self, device, lib):
        self._lib = lib
        self._lib.clCMEMS_Create.restype = ctypes.POINTER(ctypes.c_int)
        self._lib.clCMEMS_Create.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(Error)]
        error = Error()
        self._pointer = self._lib.clCMEMS_Create(device.get_c_pointer(), ctypes.byref(error))
        if error.code is not Error_Code.OK:
            raise CapsuleException(error)

    def set_on_update(self, callback: Callable[['MEMS', MEMSTimedData], None]):
        global _mems_lib_impl, _mems_update_callback
        _mems_lib_impl = self._lib
        _mems_update_callback = callback
        self.__save_obj()
        error = Error()
        self._lib.clCMEMS_SetOnMEMSTimedDataUpdateEvent(self._pointer, update_impl, ctypes.byref(error))
        if error.code is not Error_Code.OK:
            raise CapsuleException(error)

    def __save_obj(self):
        global capsule_pointers
        capsule_pointers[self._name_in_pointers_map] = self


# impl details
_mems_lib_impl = None

_mems_update_callback = None
@ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
def update_impl(_mems, data):
    global _mems_lib_impl, _mems_update_callback, capsule_pointers
    _mems_update_callback(capsule_pointers['MEMS'], MEMSTimedData(data, _mems_lib_impl))