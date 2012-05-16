import os
from datetime import datetime, timedelta
import re
import ConfigParser

import logging
LOG = logging.getLogger('polar-preproc')

_RE_NPP_STAMP = re.compile('.*?(([A-Za-z0-9]+)_d(\d+)_t(\d+)_e(\d+)_b(\d+)).*')

try:
    config_dir = os.environ['POLAR_PREPROC_CONFIG_DIR']
except KeyError:
    LOG.error('POLAR_PREPROC_CONFIG is not defined')
    raise

#
# Read config file (SITE and DOMAIN)
#
_conf = ConfigParser.ConfigParser()
_conf.read(os.path.join(config_dir, 'polar_preproc.cfg'))
SITE = eval(_conf.get('general', 'site'))
DOMAIN = eval(_conf.get('general', 'domain'))
TLE_DIRS = eval(_conf.get('general', 'tle_dirs'))
TLE_FILE_FORMAT = eval(_conf.get('general', 'tle_file_format'))

# NPP stuff:
RT_STPS_BATCH = eval(_conf.get('npp', 'rt_stps_batch'))
RT_STPS_NPP_TEMPLATE_CONFIG_FILE = eval(_conf.get('npp', 'rt_stps_npp_template_config_file'))


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
