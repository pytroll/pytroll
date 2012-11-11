import os
from datetime import datetime, timedelta
import re
import ConfigParser

import logging
LOG = logging.getLogger('npp-sdr-processing')

_RE_NPP_STAMP = re.compile('.*?(([A-Za-z0-9]+)_d(\d+)_t(\d+)_e(\d+)_b(\d+)).*')

import sdr_runner
_PACKAGEDIR = sdr_runner.__path__[0]
CONFIG_PATH = os.path.join(os.path.dirname(_PACKAGEDIR), 'etc')

#try:
#    CONFIG_PATH = os.environ['NPP_SDRPROC_CONFIG_DIR']
#except KeyError:
#    LOG.error('NPP_SDRPROC_CONFIG_DIR is not defined')
#    raise

#
# Read config file (SITE and DOMAIN)
#
CONF = ConfigParser.ConfigParser()
CONF.read(os.path.join(CONFIG_PATH, "npp_sdr_config.cfg"))

MODE = os.getenv("SMHI_MODE")
if MODE is None:
    MODE = "offline"

OPTIONS = {}
for option, value in CONF.items(MODE, raw = True):
    OPTIONS[option] = value


SITE = eval(CONF.get(MODE, 'site'))
DOMAIN = eval(CONF.get(MODE, 'domain'))
TLE_DIRS = eval(CONF.get(MODE, 'tle_dirs'))
TLE_FILE_FORMAT = eval(CONF.get(MODE, 'tle_file_format'))



class NPPStamp(object):
    """ A NPP stamp is:
    <platform>_d<start_date>_t<start_time>_e<end_time>_b<orbit_number>
    """
    def __init__(self, platform, start_time, end_time, orbit_number):
        self.platform = platform
        self.start_time = start_time
        self.end_time = end_time
        self.orbit_number = orbit_number

    def __str__(self):
        date = self.start_time.strftime('%Y%m%d')
        start = (self.start_time.strftime('%H%M%S') + 
                 str(self.start_time.microsecond/100000)[0])
        end = (self.end_time.strftime('%H%M%S') +
               str(self.end_time.microsecond/100000)[0])
        return "%s_d%s_t%s_e%s_b%05d" % (self.platform, date, start, end,
                                         self.orbit_number)

    def __cmp__(self, other):
        return cmp(str(self), str(other))

def get_npp_stamp(filename):
    """A unique stamp for a granule.
    <name>_d<date>_t<start-time>_e<end-time>_b<orbit_number>
    """
    match = _RE_NPP_STAMP.match(os.path.basename(filename))                 
    if not match:
        return
    start_time, end_time = _dte2time(match.group(3), match.group(4),
                                     match.group(5))
    return NPPStamp(match.group(2), start_time, end_time, 
                    int(match.group(6)))

def _dte2time(date, start_time, end_time):
    start_time = (datetime.strptime(date + start_time[:6], '%Y%m%d%H%M%S') +
                  timedelta(microseconds=int(start_time[6])*100000))
    end_time = (datetime.strptime(date + end_time[:6], '%Y%m%d%H%M%S') +
                timedelta(microseconds=int(end_time[6])*100000))
    if start_time > end_time:
        end_time += timedelta(days=1)
    return start_time, end_time


def get_datetime_from_filename(filename):
    """Get start observation time from the filename. Example:
    'GMODO_npp_d20120405_t0037099_e0038341_b00001_c20120405124731856767_cspp_dev.h5'
    """

    bname = os.path.basename(filename)
    sll = bname.split('_')
    return datetime.strptime(sll[2] + sll[3][:-1], 
                             "d%Y%m%dt%H%M%S")
