import os
from datetime import datetime, timedelta
import glob
import re

from polar_preproc import _dte2time
from polar_preproc.segment import Segment

_RE_GRANULE_FIELDS = re.compile('(?P<kind>[-A-Z]+)(?P<band>[0-9]*)_' +
                                '(?P<platform>[A-Za-z0-9]+)_'+
                                'd(?P<date>\d+)_t(?P<start_time>\d+)_' +
                                'e(?P<end_time>\d+)_b(?P<orbit>\d+)_' +
                                'c(?P<create_time>\d+)_(?P<site>[a-zA-Z0-9]+)_' +
                                '(?P<domain>[a-zA-Z0-9]+)\.h5')

class NPPGranule(Segment):

    description = "NPP Granule"

    def __init__(self, platform='npp', start_time=None, **kwargs):
        super(NPPGranule, self).__init__(platform=platform,
                                         start_time=start_time,
                                         **kwargs)
        self.items.sort()
        self.check_stamps()

    def check_stamps(self):
        stamp = self.stamp
        for fn in self.items:
            fn = os.path.basename(fn)
            if get_npp_stamp(fn) != stamp:
                raise IOError(
                    "Mismatch in npp stamp for '%s', expected '%s'" % 
                    (fn, stamp))

def get_granule_fields(filename, decode=True):
    """Extract the fields of an NPP CDFCB-format filename.
    PFE: adl_geo_ref.py
    """
    nfo = dict(_RE_GRANULE_FIELDS.match(os.path.basename(filename)
                                        ).groupdict())
    if decode:
        if nfo['band']:
            nfo['band'] = int(nfo['band'])
        nfo['orbit'] = int(nfo['orbit'])
        nfo['start_time'], nfo['end_time'] = (
            _dte2time(nfo['date'], nfo['start_time'], nfo['end_time']))
        nfo['create_time'] = datetime.strptime(nfo['create_time'],
                                               '%Y%m%d%H%M%S%f')
        del nfo['date']
    return nfo
