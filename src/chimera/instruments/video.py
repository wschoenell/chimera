#TODO HEADER
import threading
from chimera.core.lock import lock
from chimera.core.chimeraobject import ChimeraObject
from chimera.interfaces.video import VideoInformation


class VideoBase(ChimeraObject, VideoInformation):

    def __init__(self):
        ChimeraObject.__init__(self)

        self.abort = threading.Event()
        self.abort.clear()

    def __stop__(self):
        self.abortExposure(readout=False)

    def _saveFrame(self, imageRequest, frameData, extra):
        # TODO: Save image
        raise NotImplementedError()

    def _getReadoutModeInfo(self, binning, window):
        """
        Check if the given binning and window could be used on the given CCD.

        Returns a tuple (modeId, binning, top, left, width, height)
        """
        # TODO: getReadOutModeInfo
        raise NotImplementedError()

    def getLastVideoFrame(self):
        raise NotImplementedError()


    def getFrameRate(self):
        raise NotImplementedError()

    def getBinnings(self):
        raise NotImplementedError()

    def getPhysicalSize(self):
        raise NotImplementedError()

    def getPixelSize(self):
        raise NotImplementedError()

    def getReadoutModes(self):
        """Get readout modes supported by this camera.
        The return value would have the following format:
         {ccd1: {mode1: ReadoutMode(), mode2: ReadoutMode2()},
          ccd2: {mode1: ReadoutMode(), mode2: ReadoutMode2()}}
        """
        raise NotImplementedError()

    def supports(self, feature=None):
        raise NotImplementedError()


    def getGammas(self):
        pass

    def getGains(self):
        pass

    # Video camera thermal control #

    @lock
    def startCooling(self, tempC):
        raise NotImplementedError()

    @lock
    def stopCooling(self):
        raise NotImplementedError()

    def isCooling(self):
        raise NotImplementedError()

    @lock
    def getTemperature(self):
        raise NotImplementedError()

    @lock
    def getSetPoint(self):
        raise NotImplementedError()

    @lock
    def startFan(self, rate=None):
        raise NotImplementedError()

    @lock
    def stopFan(self):
        raise NotImplementedError()

    def isFanning(self):
        raise NotImplementedError()

