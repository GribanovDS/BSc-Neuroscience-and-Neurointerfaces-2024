import ctypes

from CapsuleSDK.Calibrator import IndividualNFBData
from CapsuleSDK.Error import *
from typing import Callable
from CapsuleSDK.CapsulePointersImpl import capsule_pointers


class Productivity_FatigueGrowthRate(ctypes.c_int):
    None_ = 0
    Low = 1
    Medium = 2
    High = 3

class Productivity_Metrics(ctypes.Structure):
    _fields_ = [
        ("timestampMilli", ctypes.c_int64),
        ("fatigueScore", ctypes.c_float),
        ("reverseFatigueScore", ctypes.c_float),
        ("gravityScore", ctypes.c_float),
        ("relaxationScore", ctypes.c_float),
        ("concentrationScore", ctypes.c_float),
        ("productivityScore", ctypes.c_float),
        ("currentValue", ctypes.c_float),
        ("alpha", ctypes.c_float),
        ("productivityBaseline", ctypes.c_float),
        ("accumulatedFatigue", ctypes.c_float),
        ("fatigueGrowthRate", Productivity_FatigueGrowthRate),
        ("artifactsData", ctypes.POINTER(ctypes.c_uint8)),
        ("artifactsSize", ctypes.c_uint64)
    ]

class Productivity_RecommendationValue(ctypes.c_int):
    NoRecommendation = 0
    Involvement = 1
    Relaxation = 2
    SlightFatigue = 3
    SevereFatigue = 4
    ChronicFatigue = 5

class Productivity_StressValue(ctypes.c_int):
    NoStress = 0
    Anxiety = 1
    Stress = 2

class Productivity_Indexes(ctypes.Structure):
    _fields_ = [
        ("timestampMilli", ctypes.c_int64),
        ("relaxation", Productivity_RecommendationValue),
        ("stress", Productivity_StressValue),
        ("gravityBaseline", ctypes.c_float),
        ("productivityBaseline", ctypes.c_float),
        ("fatigueBaseline", ctypes.c_float),
        ("reverseFatigueBaseline", ctypes.c_float),
        ("relaxationBaseline", ctypes.c_float),
        ("concentrationBaseline", ctypes.c_float),
        ("hasArtifacts", ctypes.c_bool)
    ]

class Productivity_Baselines(ctypes.Structure):
    _fields_ = [
        ("timestampMilli", ctypes.c_int64),
        ("gravity", ctypes.c_float),
        ("productivity", ctypes.c_float),
        ("fatigue", ctypes.c_float),
        ("reverseFatigue", ctypes.c_float),
        ("relaxation", ctypes.c_float),
        ("concentration", ctypes.c_float)
    ]

    def __init__(self, concentration=-1, fatigue=-1, gravity=-1,
                  productivity=-1, relax=-1, reverse_fatigue=-1, timestamp=-1):
        self.concentration = concentration
        self.fatigue = fatigue
        self.gravity = gravity
        self.productivity = productivity
        self.relax = relax
        self.reverseFatigue = reverse_fatigue
        self.timestamp = timestamp


class Productivity:
    _name_in_pointers_map = "Productivity"
    def __init__(self, device, lib):
        self._lib = lib
        self._lib.clCProductivity_Create.restype = ctypes.POINTER(ctypes.c_int)
        self._lib.clCProductivity_Create.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(Error)]
        error = Error()
        self._pointer = self._lib.clCProductivity_Create(device.get_c_pointer(), ctypes.byref(error))
        if error.code is not Error_Code.OK:
            raise CapsuleException(error)

    def import_baselines(self, baselines : Productivity_Baselines):
        self._lib.clCProductivity_ImportBaselines.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(Productivity_Baselines), ctypes.POINTER(Error)]
        error = Error()
        self._lib.clCProductivity_ImportBaselines(self._pointer, ctypes.byref(baselines), ctypes.byref(error))
        if error.code is not Error_Code.OK:
            raise CapsuleException(error)
        
    def reset_accumulated_fatigue(self):
        self._lib.clCProductivity_ResetAccumulatedFatigue.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(Error)]
        error = Error()
        self._lib.clCProductivity_ResetAccumulatedFatigue(self._pointer, ctypes.byref(error))
        if error.code is not Error_Code.OK:
            raise CapsuleException(error)
        
    def calibrate_baselines(self):
        self._lib.clCProductivity_StartBaselineCalibration.argtypes = [ctypes.POINTER(ctypes.c_int)]
        self._lib.clCProductivity_StartBaselineCalibration(self._pointer)

    def set_on_baseline_update(self, callback: Callable[['Productivity', Productivity_Baselines], None]):
        global _productivity_lib_impl, _productivity_baseline_callback
        _productivity_lib_impl = self._lib
        _productivity_baseline_callback = callback
        self.__save_obj()
        self._lib.clCProductivity_SetOnBaselineUpdateEvent(self._pointer, baseline_impl)

    def set_on_metrics_update(self, callback: Callable[['Productivity', Productivity_Metrics], None]):
        global _productivity_lib_impl, _productivity_metrics_callback
        _productivity_lib_impl = self._lib
        _productivity_metrics_callback = callback
        self.__save_obj()
        self._lib.clCProductivity_SetOnMetricsUpdateEvent(self._pointer, metrics_impl)

    def set_on_indexes_update(self, callback: Callable[['Productivity', Productivity_Indexes], None]):
        global _productivity_lib_impl, _productivity_indexes_callback
        _productivity_lib_impl = self._lib
        _productivity_indexes_callback = callback
        self.__save_obj()
        self._lib.clCProductivity_SetOnIndexesUpdateEvent(self._pointer, indexes_impl)

    def set_on_calibration_progress(self, callback: Callable[['Productivity', float], None]):
        global _productivity_lib_impl, _productivity_calibration_progress_callback
        _productivity_lib_impl = self._lib
        _productivity_calibration_progress_callback = callback
        self.__save_obj()
        self._lib.clCProductivity_SetOnCalibrationProgressUpdateEvent(self._pointer, calibration_progress_impl)

    def set_on_individual_nfb(self, callback):
        global _productivity_lib_impl, _productivity_nfb_callback
        _productivity_lib_impl = self._lib
        _productivity_nfb_callback = callback
        self.__save_obj()
        self._lib.clCProductivity_SetOnIndividualNFBUpdateEvent(self._pointer, nfb_impl)

    def __save_obj(self):
        global capsule_pointers
        capsule_pointers[self._name_in_pointers_map] = self


# impl details
_productivity_lib_impl = None

_productivity_baseline_callback = None
@ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(Productivity_Baselines))
def baseline_impl(_prod, baselines):
    global _productivity_lib_impl, _productivity_baseline_callback, capsule_pointers
    _productivity_baseline_callback(capsule_pointers['Productivity'], baselines.contents)

_productivity_metrics_callback = None
@ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(Productivity_Metrics))
def metrics_impl(_prod, metrics):
    global _productivity_lib_impl, _productivity_metrics_callback, capsule_pointers
    _productivity_metrics_callback(capsule_pointers['Productivity'], metrics.contents)

_productivity_indexes_callback = None
@ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(Productivity_Indexes))
def indexes_impl(_prod, indexes):
    global _productivity_lib_impl, _productivity_indexes_callback, capsule_pointers
    _productivity_indexes_callback(capsule_pointers['Productivity'], indexes.contents)

_productivity_calibration_progress_callback = None
@ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_int), ctypes.c_float)
def calibration_progress_impl(_prod, progress):
    global _productivity_lib_impl, _productivity_calibration_progress_callback, capsule_pointers
    _productivity_calibration_progress_callback(capsule_pointers['Productivity'], progress)

_productivity_nfb_callback = None
@ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_int))
def nfb_impl(_prod):
    global _productivity_lib_impl, _productivity_nfb_callback, capsule_pointers
    _productivity_nfb_callback(capsule_pointers['Productivity'])