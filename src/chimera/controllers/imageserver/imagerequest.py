import logging
from chimera.interfaces.camera import Shutter, Bitpix
from chimera.core.exceptions import ChimeraValueError, ObjectNotFoundException

log = logging.getLogger(__name__)


class ImageRequest(dict):
    valid_keys = ['exptime', 'frames',
                  'interval', 'shutter',
                  'binning', 'window',
                  'bitpix', 'filename',
                  'compress_format',
                  'type', 'wait_dome',
                  'object_name']

    def __init__(self, **kwargs):

        defaults = {'exptime': 1.0,
                    'frames': 1,
                    'interval': 0.0,
                    'shutter': Shutter.OPEN,
                    'binning': "1x1",
                    'window': None,
                    'bitpix': Bitpix.uint16,
                    'filename': '$DATE-$TIME',
                    'compress_format': "NO",
                    'type': 'object',
                    'wait_dome': True,
                    'object_name': ''}

        # Automatically call getMetadata on all instruments + site as long
        # as only one instance of each is listed by the manager.
        self.auto_collect_metadata = True

        # URLs of proxies from which to get metadata before taking each image
        self.metadataPre = []

        # URLs of proxies from which to get metadata after taking each image
        self.metadataPost = []

        # Headers accumulated during processing of each frame
        # (=headers+metadatapre+metadatapost)
        self.headers = []

        self._proxies = {}

        self.update(defaults)

        # validate keywords passed
        not_valid = [k for k in kwargs.keys() if k not in defaults.keys()]

        if any(not_valid):
            if len(not_valid) > 1:
                msg = "Invalid keywords: "
                for k in not_valid:
                    msg += "'%s', " % str(k)
                msg = msg[:-2]

            else:
                msg = "Invalid keyword '%s'" % str(not_valid[0])

            raise TypeError(msg)

        self.update(kwargs)

        # do some checkings
        if self['exptime'] < 0.0:
            raise ChimeraValueError('Invalid exposure length (<0 seconds).')

        # FIXME: magic number here! But we shouldn't allow arbitrary maximum
        # for safety reasons.
        if self['exptime'] > 12 * 60 * 60:
            raise ChimeraValueError(
                'Invalid exposure. Must be lower them 12 hours.')

        if self['frames'] < 1:
            raise ChimeraValueError('Invalid number of frames (<1 frame).')

        if self['interval'] < 0.0:
            raise ChimeraValueError(
                'Invalid interval between exposures (<0 seconds)')

        if str(self['shutter']) not in Shutter:
            raise ChimeraValueError(
                'Invalid shutter value: ' + str(self['shutter']))
        else:
            self["shutter"] = Shutter.fromStr(str(self["shutter"]))

        if self["object_name"]:
            self.headers.append((
                "OBJECT", str(self["object_name"]), "name of observed object"))

    def __setitem__(self, key, value):

        if not key in ImageRequest.valid_keys:
            raise KeyError("%s is not a valid key for ImageRequest" % key)

        self.update({key: value})

    def __str__(self):
        return (
            'exptime: %f, frames: %i, shutter: %s, type: %s' %
            (self['exptime'], self['frames'], self['shutter'], self['type']))

    def beginExposure(self, manager):

        self._fetchPreHeaders(manager)

        if self["wait_dome"]:
            try:
                dome = manager.getProxy(manager.getResourcesByClass("Dome")[0])
                dome.syncWithTel()
                log.debug(
                    "Dome slit position synchronized with telescope position.")

            except ObjectNotFoundException:
                log.info("No dome present, taking exposure without dome sync.")

    def endExposure(self, manager):
        self._fetchPostHeaders(manager)

    def _fetchPreHeaders(self, manager):
        auto_main = []
        auto_secondary = dict()
        if self.auto_collect_metadata:
            for cls in ('Site', 'Camera', 'Dome', 'FilterWheel', 'Focuser', 'Telescope', 'WeatherStation'):
                locations = manager.getResourcesByClass(cls)
                if len(locations) == 1:
                    auto_main.append(str(locations[0]))
                elif len(locations) == 0:
                    log.warning(
                        "No %s available, header would be incomplete." % cls)
                else:
                    log.warning(
                        "More than one %s available. Will append an integer at end of the ramaining %s headers." % (
                        cls, cls))
                    auto_main.append(str(locations[0]))
                    auto_secondary.update({str(locations[i]): i for i in range(1, len(locations))})

            self._getHeaders(manager, auto_main + self.metadataPre)
            self._getSecondaryHeaders(manager, auto_secondary)

    def _fetchPostHeaders(self, manager):
        self._getHeaders(manager, self.metadataPost)

    def _getHeaders(self, manager, locations):

        for location in locations:

            if not location in self._proxies:
                try:
                    self._proxies[location] = manager.getProxy(location)
                except Exception:
                    log.exception('Unable to get metadata from %s' % (location))

            self.headers += self._proxies[location].getMetadata(self)

    def _getSecondaryHeaders(self, manager, locations):
        """
        Fixes metadata of instruments that are not unique by appending an integer to all keywords
        :param manager: Manager
        :param locations: dict
        """

        for location in locations:

            if not location in self._proxies:
                try:
                    self._proxies[location] = manager.getProxy(location)
                except Exception:
                    log.exception('Unable to get metadata from %s' % location)

            md = self._proxies[location].getMetadata(self)
            md_fixed = list()

            for keyword in md:
                # Python tuples does not support item assignment, so I do this ugly trick converting to list then
                # back to tuple
                keyword = list(keyword)
                keyword[0] += str(locations[location])
                md_fixed.append(tuple(keyword))

            self.headers += md_fixed
