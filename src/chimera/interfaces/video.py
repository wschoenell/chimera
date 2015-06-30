from chimera.core.interface import Interface


class Video(Interface):

    """
    Base camera interface.
    """

    # config
    __config__ = {"device": "USB",
                  "camera_model": None,
                  "ccd_model": None,
                  "telescope_focal_length": None  # milimeter
                  }




class VideoInformation(Video):

    # for getCCDs, getBinnings and the instrument should return a
    # hash with keys as Human readable strings, which could be later passed as a
    # ImageRequest and be recognized by the instrument. Those strings can
    # be use as key to an internal hashmap.
    # example:
    # ADCs = {'12 bits': SomeInternalValueWhichMapsTo12BitsADC,
    #         '16 bits': SomeInternalValueWhichMapsTo16BitsADC}

    def getFrameRate(self):
        pass

    def getBinnings(self):
        pass

    def getPhysicalSize(self):
        pass

    def getPixelSize(self):
        pass

    def getReadoutModes(self):
        """Get readout modes supported by this camera.
        The return value would have the following format:
         {ccd1: {mode1: ReadoutMode(), mode2: ReadoutMode2()},
          ccd2: {mode1: ReadoutMode(), mode2: ReadoutMode2()}}
        """
        pass

    def getGammas(self):
        pass

    def getGains(self):
        pass

    #
    # special features support
    #

    def supports(self, feature=None):
        pass
