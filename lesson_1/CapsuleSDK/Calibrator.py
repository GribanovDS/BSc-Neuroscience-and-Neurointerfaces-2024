import ctypes
from CapsuleSDK.Error import *
from typing import Callable
from CapsuleSDK.CapsulePointersImpl import capsule_pointers

class IndividualNFBCalibrationStage(ctypes.c_int):
    IndividualNFBCalibrationStage_1 = 0
    IndividualNFBCalibrationStage_2 = 1
    IndividualNFBCalibrationStage_3 = 2
    IndividualNFBCalibrationStage_4 = 3

class IndividualNFBCalibrationFailReason(ctypes.c_int):
    IndividualNFBCalibrationFailReason_None = 0
    IndividualNFBCalibrationFailReason_TooManyArtifacts = 1
    IndividualNFBCalibrationFailReason_PeakIsABorder = 2

class IndividualNFBData(ctypes.Structure):
    _fields_ = [
        ("timestampMilli", ctypes.c_int64),
        ("failReason", IndividualNFBCalibrationFailReason),
        ("individualFrequency", ctypes.c_float),
        ("individualPeakFrequency", ctypes.c_float),
        ("individualPeakFrequencyPower", ctypes.c_float),
        ("individualPeakFrequencySuppression", ctypes.c_float),
        ("individualBandwidth", ctypes.c_float),
        ("individualNormalizedPower", ctypes.c_float),
        ("lowerFrequency", ctypes.c_float),
        ("upperFrequency", ctypes.c_float),
    ]

    def __init__(self, timestamp_milli=1,
                 fail_reason=IndividualNFBCalibrationFailReason.IndividualNFBCalibrationFailReason_None,
                 individual_frequency=10.0,
                 individual_peak_frequency=10.0,
                 individual_peak_frequency_power=10.0,
                 individual_peak_frequency_suppression=2.0,
                 individual_bandwidth=6.0,
                 individual_normalized_power=0.5,
                 lower_frequency=7.0,
                 upper_frequency=13.0):
        self.timestampMilli = timestamp_milli
        self.failReason = fail_reason
        self.individualFrequency = individual_frequency
        self.individualPeakFrequency = individual_peak_frequency
        self.individualPeakFrequencyPower = individual_peak_frequency_power
        self.individualPeakFrequencySuppression = individual_peak_frequency_suppression
        self.individualBandwidth = individual_bandwidth
        self.individualNormalizedPower = individual_normalized_power
        self.lowerFrequency = lower_frequency
        self.upperFrequency = upper_frequency

class Calibrator:
    _name_in_pointers_map = "Calibrator"
    def __init__(self, device, lib):
        self._lib = lib
        self._lib.clCNFBCalibrator_CreateOrGet.restype = ctypes.POINTER(ctypes.c_int)
        self._lib.clCNFBCalibrator_CreateOrGet.argtypes = [ctypes.POINTER(ctypes.c_int)]
        self._pointer = self._lib.clCNFBCalibrator_CreateOrGet(device.get_c_pointer())
    
    def import_alpha(self, individual_nfb_data):
        self._lib.clCNFBCalibrator_ImportIndividualNFBData.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(IndividualNFBData), ctypes.POINTER(Error)]
        error = Error()
        self._lib.clCNFBCalibrator_ImportIndividualNFBData(self._pointer, ctypes.byref(individual_nfb_data), ctypes.byref(error))
        if error.code is not Error_Code.OK:
            raise CapsuleException(error)

    def calibrate_quick(self):
        self._lib.clCNFBCalibrator_CalibrateIndividualNFBQuick.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(Error)]
        error = Error()
        self._lib.clCNFBCalibrator_CalibrateIndividualNFBQuick(self._pointer, ctypes.byref(error))
        if error.code is not Error_Code.OK:
            raise CapsuleException(error)

    def calibrate(self, individual_nfb_calibration_stage):
        self._lib.clCNFBCalibrator_CalibrateIndividualNFB.argtypes = [ctypes.POINTER(ctypes.c_int), IndividualNFBCalibrationStage, ctypes.POINTER(Error)]
        error = Error()
        self._lib.clCNFBCalibrator_CalibrateIndividualNFBQuick(self._pointer, individual_nfb_calibration_stage, ctypes.byref(error))
        if error.code is not Error_Code.OK:
            raise CapsuleException(error)


    def get_individual_nfb(self):
        self._lib.clCNFBCalibrator_GetIndividualNFB.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(IndividualNFBData), ctypes.POINTER(Error)]
        error = Error()
        individual_nfb_data = IndividualNFBData()
        self._lib.clCNFBCalibrator_GetIndividualNFB(self._pointer, ctypes.byref(individual_nfb_data), ctypes.byref(error))
        if error.code is not Error_Code.OK:
            raise CapsuleException(error)
        return individual_nfb_data

    def is_calibrated(self) -> bool:
        self._lib.clCNFBCalibrator_IsCalibrated.restype = ctypes.c_bool
        self._lib.clCNFBCalibrator_IsCalibrated.argtypes = [ctypes.POINTER(ctypes.c_int)]
        return self._lib.clCNFBCalibrator_IsCalibrated(self._pointer)

    def has_calibration_failed(self):
        self._lib.clCNFBCalibrator_HasCalibrationFailed.restype = ctypes.c_bool
        self._lib.clCNFBCalibrator_HasCalibrationFailed.argtypes = [ctypes.POINTER(ctypes.c_int)]
        return self._lib.clCNFBCalibrator_HasCalibrationFailed(self._pointer)

    def set_on_calibration_stage_finished(self, callback: Callable[['Calibrator'], None]):
        global _calibrator_lib_impl, _calibrator_stage_finished_callback
        _calibrator_lib_impl = self._lib
        _calibrator_stage_finished_callback = callback
        self.__save_obj()
        self._lib.clCNFBCalibrator_SetOnCalibrationStageFinishedEvent(self._pointer, calibration_stage_finished_impl)

    def set_on_calibration_finished(self, callback: Callable[['Calibrator', IndividualNFBData], None]):
        global _calibrator_lib_impl, _calibrator_finished_callback
        _calibrator_lib_impl = self._lib
        _calibrator_finished_callback = callback
        self.__save_obj()
        self._lib.clCNFBCalibrator_SetOnCalibratedEvent(self._pointer, calibration_finished_impl)

    def get_c_pointer(self):
        return self._pointer
    
    def __save_obj(self):
        global capsule_pointers
        capsule_pointers[self._name_in_pointers_map] = self
    


# impl details
_calibrator_lib_impl = None

_calibrator_stage_finished_callback = None
@ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_int))
def calibration_stage_finished_impl(_calibrator):
    global _calibrator_lib_impl, _calibrator_stage_finished_callback, capsule_pointers
    _calibrator_stage_finished_callback(capsule_pointers['Calibrator'])

_calibrator_finished_callback = None
@ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(IndividualNFBData))
def calibration_finished_impl(_calibrator, individual_data):
    global _calibrator_lib_impl, _calibrator_finished_callback, capsule_pointers
    _calibrator_finished_callback(capsule_pointers['Calibrator'], individual_data.contents)
