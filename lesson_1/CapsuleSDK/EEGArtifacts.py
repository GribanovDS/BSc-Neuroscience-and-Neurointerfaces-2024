import ctypes
from CapsuleSDK.Error import *

class EEGArtifacts:
    def __init__(self, pointer, lib):
        self._lib = lib
        self._pointer = pointer

        self._lib.clCEEGArtifacts_GetTimestampMilli.restype = ctypes.c_uint64
        self._lib.clCEEGArtifacts_GetTimestampMilli.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(Error)]

        self._lib.clCEEGArtifacts_GetChannelsCount.restype = ctypes.c_int
        self._lib.clCEEGArtifacts_GetChannelsCount.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(Error)]

        self._lib.clCEEGArtifacts_GetArtifactByChannel.restype = ctypes.c_uint8
        self._lib.clCEEGArtifacts_GetArtifactByChannel.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.POINTER(Error)]

        self._lib.clCEEGArtifacts_GetEEGQuality.restype = ctypes.c_uint8
        self._lib.clCEEGArtifacts_GetEEGQuality.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.POINTER(Error)]

    def get_timestamp(self):
        error = Error()
        ts = self._lib.clCEEGArtifacts_GetTimestampMilli(self._pointer, error)
        if error.code is not Error_Code.OK:
            raise CapsuleException(error)

        return ts

    def get_channels_count(self):
        error = Error()
        ts = self._lib.clCEEGArtifacts_GetChannelsCount(self._pointer, error)
        if error.code is not Error_Code.OK:
            raise CapsuleException(error)

        return ts

    def get_artifacts_by_channel(self, channelIdx):
        error = Error()
        artifacts = self._lib.clCEEGArtifacts_GetArtifactByChannel(self._pointer, channelIdx, ctypes.byref(error))
        if error.code is not Error_Code.OK:
            raise CapsuleException(error)
        
        return artifacts

    def get_eeg_quality(self, channelIdx):
        error = Error()
        artifacts = self._lib.clCEEGArtifacts_GetEEGQuality(self._pointer, channelIdx, ctypes.byref(error))
        if error.code is not Error_Code.OK:
            raise CapsuleException(error)
        
        return artifacts