import ctypes
from CapsuleSDK.Error import *
from CapsuleSDK.PPGTimedData import PPGTimedData
from CapsuleSDK.EEGTimedData import EEGTimedData
from CapsuleSDK.EEGArtifacts import EEGArtifacts
from CapsuleSDK.DeviceInfo import DeviceInfo
from CapsuleSDK.Resistances import Resistances
from CapsuleSDK.PSDData import PSDData
from typing import Callable
from CapsuleSDK.CapsulePointersImpl import capsule_pointers

class Device_Mode(ctypes.c_int):
    Device_Mode_Resistance = 0
    Device_Mode_Signal = 1
    Device_Mode_StartMEMS = 3
    Device_Mode_StopMEMS = 4
    Device_Mode_StartPPG = 5
    Device_Mode_StopPPG = 6
    Device_Mode_SignalAndResist = 2

class Device_Connection_Status(ctypes.c_int):
    Device_ConnectionState_Disconnected = 0
    Device_ConnectionState_Connected = 1
    Device_ConnectionState_UnsupportedConnection = 2

class Device_Status(ctypes.c_int):
    clCDevice_Status_Invalid = 0
    clCDevice_Status_PowerDown = 1
    clCDevice_Status_Idle = 2
    clCDevice_Status_Signal = 3
    clCDevice_Status_Resist = 4
    clCDevice_Status_SignalResist = 5
    clCDevice_Status_Envelope = 6

class ChannelNames:
    def __init__(self, pointer, lib):
        self._lib = lib
        self._pointer = pointer

    def __len__(self):
        self._lib.clCDevice_ChannelNames_GetChannelsCount.restype = ctypes.c_int
        self._lib.clCDevice_ChannelNames_GetChannelsCount.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(Error)]
        error = Error()
        count = self._lib.clCDevice_ChannelNames_GetChannelsCount(self._pointer, ctypes.byref(error))
        if error.code is not Error_Code.OK:
            raise CapsuleException(error)
        return count 

    def get_index_by_name(self, name):
        self._lib.clCDevice_ChannelNames_GetChannelIndexByName.restype = ctypes.c_int
        self._lib.clCDevice_ChannelNames_GetChannelIndexByName.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_char_p, ctypes.POINTER(Error)]
        error = Error()
        idx = self._lib.clCDevice_ChannelNames_GetChannelIndexByName(self._pointer, name, ctypes.byref(error))
        if error.code is not Error_Code.OK:
            raise CapsuleException(error)
        return idx
    
    def get_name_by_index(self, idx):
        self._lib.clCDevice_ChannelNames_GetChannelNameByIndex.restype = ctypes.c_char_p
        self._lib.clCDevice_ChannelNames_GetChannelNameByIndex.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.POINTER(Error)]
        error = Error()
        name = self._lib.clCDevice_ChannelNames_GetChannelNameByIndex(self._pointer, idx, ctypes.byref(error))
        if error.code is not Error_Code.OK:
            raise CapsuleException(error)
        return name.decode('utf-8')

class Device:
    _name_in_pointers_map = "Device"
    def __init__(self, locator, device_id, lib):
        self._lib = lib
        self._lib.clCDeviceLocator_CreateDevice.restype = ctypes.POINTER(ctypes.c_int)
        self._lib.clCDeviceLocator_CreateDevice.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_char_p, ctypes.POINTER(Error)]
        error = Error()
        self._pointer = self._lib.clCDeviceLocator_CreateDevice(locator.get_c_pointer(), device_id.encode('utf-8'), ctypes.byref(error))
        if error.code is not Error_Code.OK:
            raise CapsuleException(error)


    def __del__(self):
        self._lib.clCDevice_Release(self._pointer)

    def set_on_connection_status_changed(self, callback: Callable[['Device', Device_Connection_Status], None]):
        global _device_lib_impl, _device_connection_callback
        _device_lib_impl = self._lib
        _device_connection_callback = callback
        self.__save_obj()
        self._lib.clCDevice_SetOnConnectionStatusChangedEvent(self._pointer, connection_status_changed_impl)

    def set_on_resistances(self, callback: Callable[['Device', Resistances], None]):
        global _device_lib_impl, _device_resistances_callback
        _device_lib_impl = self._lib
        _device_resistances_callback = callback
        self.__save_obj()
        self._lib.clCDevice_SetOnResistanceUpdateEvent(self._pointer, resistances_impl)

    def set_on_battery_charge_changed(self, callback: Callable[['Device', int], None]):
        global _device_lib_impl, _device_battery_charged_callback
        _device_lib_impl = self._lib
        _device_battery_charged_callback = callback
        self.__save_obj()
        self._lib.clCDevice_SetOnBatteryChargeUpdateEvent(self._pointer, battery_charge_changed_impl)
    
    def set_on_mode_changed(self, callback: Callable[['Device', Device_Mode], None]):
        global _device_lib_impl, _device_mode_changed_callback
        _device_lib_impl = self._lib
        _device_mode_changed_callback = callback
        self.__save_obj()
        self._lib.clCDevice_SetOnModeSwitchedEvent(self._pointer, mode_changed_impl)

    def set_on_eeg(self, callback: Callable[['Device', EEGTimedData], None]):
        global _device_lib_impl, _device_eeg_callback
        _device_lib_impl = self._lib
        _device_eeg_callback = callback
        self.__save_obj()
        self._lib.clCDevice_SetOnEEGDataEvent(self._pointer, eeg_impl)

    def set_on_psd(self, callback: Callable[['Device', PSDData], None]):
        global _device_lib_impl, _device_psd_callback
        _device_lib_impl = self._lib
        _device_psd_callback = callback
        self.__save_obj()
        self._lib.clCDevice_SetOnPSDDataEvent(self._pointer, psd_impl)

    def set_on_error(self, callback: Callable[['Device', str], None]):
        global _device_lib_impl, _device_error_callback
        _device_lib_impl = self._lib
        _device_error_callback = callback
        self.__save_obj()
        self._lib.clCDevice_SetOnErrorEvent(self._pointer, error_impl)
    
    def set_on_eeg_artifacts(self, callback: Callable[['Device', EEGArtifacts], None]):
        global _device_lib_impl, _device_eeg_artifacts_callback
        _device_lib_impl = self._lib
        _device_eeg_artifacts_callback = callback
        self.__save_obj()
        self._lib.clCDevice_SetOnEEGArtifactsEvent(self._pointer, eeg_artifacts_impl)

    def connect(self, bipolarChannels: bool):
        self._lib.clCDevice_Connect.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_bool, ctypes.POINTER(Error)]
        error = Error()
        self._lib.clCDevice_Connect(self._pointer, bipolarChannels, ctypes.byref(error))
        print(str(error.message.decode('utf-8')))
        if error.code != Error_Code.OK:
            raise CapsuleException(error)

    def disconnect(self):
        error = Error()
        self._lib.clCDevice_Disconnect(self._pointer, error)
        if error.code is not Error_Code.OK:
            raise CapsuleException(error)

    def get_battery_charge(self):
        error = Error()
        self._lib.clCDevice_GetBatteryCharge.restype = ctypes.c_int
        self._lib.clCDevice_GetBatteryCharge.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(Error)]
        charge = self._lib.clCDevice_GetBatteryCharge(self._pointer, ctypes.byref(error))
        if error.code is not Error_Code.OK:
            raise CapsuleException(error)
        return charge

    def get_mode(self) -> Device_Mode:
        self._lib.clCDevice_GetMode.restype = Device_Mode
        self._lib.clCDevice_GetMode.argtypes = [ctypes.POINTER(ctypes.c_int)]
        return self._lib.clCDevice_GetMode(self._pointer)

    def start(self):
        self._lib.clCDevice_Start.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(Error)]
        error = Error()
        self._lib.clCDevice_Start(self._pointer, ctypes.byref(error))
        if error.code is not Error_Code.OK:
            raise CapsuleException(error)
 
    def stop(self):
        self._lib.clCDevice_Start.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(Error)]
        error = Error()
        self._lib.clCDevice_Stop(self._pointer, ctypes.byref(error))
        if error.code is not Error_Code.OK:
            raise CapsuleException(error)

    def is_connected(self):
        self._lib.clCDevice_IsConnected.restype = ctypes.c_bool
        self._lib.clCDevice_IsConnected.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(Error)]
        error = Error()
        res = self._lib.clCDevice_IsConnected(self._pointer, ctypes.byref(error))
        if error.code is not Error_Code.OK:
            raise CapsuleException(error)

        return res

    def get_info(self) -> DeviceInfo:
        self._lib.clCDevice_GetInfo.restype = ctypes.POINTER(ctypes.c_int)
        self._lib.clCDevice_GetInfo.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(Error)]
        error = Error()
        info = self._lib.clCDevice_GetInfo(self._pointer, ctypes.byref(error))
        if error.code is not Error_Code.OK:
            raise CapsuleException(error)
        return DeviceInfo(info, self._lib)

    def get_eeg_sample_rate(self):
        self._lib.clCDevice_GetEEGSampleRate.restype = ctypes.c_float
        self._lib.clCDevice_GetEEGSampleRate.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(Error)]
        error = Error()
        rate = self._lib.clCDevice_GetEEGSampleRate(self._pointer, ctypes.byref(error))
        if error.code is not Error_Code.OK:
            raise CapsuleException(error)

        return rate
    
    def get_mems_sample_rate(self):
        self._lib.clCDevice_GetMEMSSampleRate.restype = ctypes.c_float
        self._lib.clCDevice_GetMEMSSampleRate.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(Error)]
        error = Error()
        rate = self._lib.clCDevice_GetMEMSSampleRate(self._pointer, ctypes.byref(error))
        if error.code is not Error_Code.OK:
            raise CapsuleException(error)

        return rate


    def get_ppg_sample_rate(self):
        self._lib.clCDevice_GetPPGSampleRate.restype = ctypes.c_float
        self._lib.clCDevice_GetPPGSampleRate.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(Error)]
        error = Error()
        rate = self._lib.clCDevice_GetPPGSampleRate(self._pointer, ctypes.byref(error))
        if error.code is not Error_Code.OK:
            raise CapsuleException(error)

        return rate

    def get_ppg_ir_amplitude(self):
        self._lib.clCDevice_GetPPGIrAmplitude.restype = ctypes.c_int
        self._lib.clCDevice_GetPPGIrAmplitude.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(Error)]
        error = Error()
        amp = self._lib.clCDevice_GetPPGIrAmplitude(self._pointer, ctypes.byref(error))
        if error.code is not Error_Code.OK:
            raise CapsuleException(error)

        return amp

    def get_ppg_red_amplitude(self):
        self._lib.clCDevice_GetPPGRedAmplitude.restype = ctypes.c_int
        self._lib.clCDevice_GetPPGRedAmplitude.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(Error)]
        error = Error()
        amp = self._lib.clCDevice_GetPPGRedAmplitude(self._pointer, ctypes.byref(error))
        if error.code is not Error_Code.OK:
            raise CapsuleException(error)

        return amp

    def get_channel_names(self):
        self._lib.clCDevice_GetChannelNames.restype = ctypes.POINTER(ctypes.c_int)
        self._lib.clCDevice_GetChannelNames.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(Error)]
        error = Error()
        channel_names = self._lib.clCDevice_GetChannelNames(self._pointer, ctypes.byref(error))
        if error.code is not Error_Code.OK:
            raise CapsuleException(error)
        return ChannelNames(channel_names, self._lib)

    def get_c_pointer(self):
        return self._pointer
    
    def __save_obj(self):
        global capsule_pointers
        capsule_pointers[self._name_in_pointers_map] = self


# impl details
_device_lib_impl = None

_device_connection_callback = None
@ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_int), ctypes.c_int)
def connection_status_changed_impl(_device, device_connection_status):
    global _device_connection_callback
    global _device_lib_impl
    _device_connection_callback(capsule_pointers['Device'], device_connection_status)

_device_resistances_callback = None
@ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
def resistances_impl(_device, resistances):
    global _device_connection_callback
    global _device_lib_impl
    _device_resistances_callback(capsule_pointers['Device'], Resistances(resistances, _device_lib_impl))
    
_device_battery_charged_callback = None
@ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_int), ctypes.c_int)
def battery_charge_changed_impl(_device, charge):
    global _device_battery_charged_callback
    global _device_lib_impl
    _device_battery_charged_callback(capsule_pointers['Device'], charge)

_device_mode_changed_callback = None
@ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_int), Device_Mode)
def mode_changed_impl(_device, mode):
    global _device_mode_changed_callback
    global _device_lib_impl
    _device_mode_changed_callback(capsule_pointers['Device'], mode)

_device_eeg_callback = None
@ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
def eeg_impl(_device, eeg):
    global _device_eeg_callback, _device_lib_impl
    _device_eeg_callback(capsule_pointers['Device'], EEGTimedData(eeg, _device_lib_impl))

_device_psd_callback = None
@ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
def psd_impl(_device, psd):
    global _device_psd_callback, _device_lib_impl
    _device_psd_callback(capsule_pointers['Device'], PSDData(psd, _device_lib_impl))

_device_error_callback = None
@ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_int), ctypes.c_char_p)
def error_impl(_device, error):
    global _device_error_callback, _device_lib_impl
    _device_error_callback(capsule_pointers['Device'], str(error))

_device_eeg_artifacts_callback = None
@ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
def eeg_artifacts_impl(_device, artifacts):
    global _device_eeg_artifacts_callback, _device_lib_impl
    _device_eeg_artifacts_callback(capsule_pointers['Device'], EEGArtifacts(artifacts, _device_lib_impl))