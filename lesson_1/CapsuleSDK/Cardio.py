import ctypes
from CapsuleSDK.Error import *
from typing import Callable
from CapsuleSDK.PPGTimedData import PPGTimedData
from CapsuleSDK.CapsulePointersImpl import capsule_pointers

class Cardio_Data(ctypes.Structure):
    _fields_ = [
        ("timestampMilli", ctypes.c_int64),
        ("heartRate", ctypes.c_float),
        ("stressIndex", ctypes.c_float),
        ("kaplanIndex", ctypes.c_float),
        ("hasArtifacts", ctypes.c_bool),
        ("skinContact", ctypes.c_bool),
        ("motionArtifacts", ctypes.c_bool),
        ("metricsAvailable", ctypes.c_bool),
    ]

class Cardio:
    _name_in_pointers_map = "Cardio"
    def __init__(self, device, lib):
        self._lib = lib
        global capsule_pointers
        self._lib.clCCardio_Create.restype = ctypes.POINTER(ctypes.c_int)
        self._lib.clCCardio_Create.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(Error)]
        error = Error()
        self._pointer = self._lib.clCCardio_Create(device.get_c_pointer(), ctypes.byref(error))
        if error.code is not Error_Code.OK:
            raise CapsuleException(error)

    def set_on_indexes_update(self, callback: Callable[['Cardio', Cardio_Data], None]):
        global _cardio_lib_impl, _cardio_indexes_callback
        _cardio_lib_impl = self._lib
        _cardio_indexes_callback = callback
        self.__save_obj()
        error = Error()
        self._lib.clCCardio_SetOnIndexesUpdateEvent(self._pointer, indexes_update_impl, ctypes.byref(error))
        if error.code is not Error_Code.OK:
            raise CapsuleException(error)

    def set_on_ppg(self, callback: Callable[['Cardio', PPGTimedData], None]):
        global _cardio_lib_impl, _cardio_ppg_callback
        _cardio_lib_impl = self._lib
        _cardio_ppg_callback = callback
        self.__save_obj()
        error = Error()
        self._lib.clCCardio_SetOnPPGDataEvent(self._pointer, ppg_impl, ctypes.byref(error))
        if error.code is not Error_Code.OK:
            raise CapsuleException(error)

    def set_on_calibrated(self, callback: Callable[['Cardio'], None]):
        global _cardio_lib_impl, _cardio_calibrated_callback
        _cardio_lib_impl = self._lib
        _cardio_calibrated_callback = callback
        self.__save_obj()
        error = Error()
        self._lib.clCCardio_SetOnCalibratedEvent(self._pointer, calibrated_impl, ctypes.byref(error))
        if error.code is not Error_Code.OK:
            raise CapsuleException(error)

    def __save_obj(self):
        global capsule_pointers
        capsule_pointers[self._name_in_pointers_map] = self
        
        
# impl details
_cardio_lib_impl = None

_cardio_indexes_callback = None
@ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(Cardio_Data))
def indexes_update_impl(_cardio, data):
    global _cardio_lib_impl, _cardio_indexes_callback, capsule_pointers
    _cardio_indexes_callback(capsule_pointers['Cardio'], data.contents)

_cardio_calibrated_callback = None
@ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_int))
def calibrated_impl(_cardio):
    global _cardio_lib_impl, _cardio_calibrated_callback, capsule_pointers
    _cardio_calibrated_callback(capsule_pointers['Cardio'])

_cardio_ppg_callback = None
@ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
def ppg_impl(_cardio, ppg):
    global _cardio_lib_impl, _cardio_ppg_callback, capsule_pointers
    _cardio_ppg_callback(capsule_pointers['Cardio'], PPGTimedData(ppg, _cardio_lib_impl))