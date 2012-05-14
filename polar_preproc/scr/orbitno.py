import os
from datetime import datetime, timedelta
import re

from pyorbital.orbital import Orbital
from pyorbital.tlefile import Tle
from logger import LOG

import npp

class NoTleFile(Exception):
    pass

TLE_FILE_PATH=('/datadb/sat/orbit/tle',
               '/net/prodsat/datadb/sat/orbit/tle')
TLE_SATNAME = {'npp' : 'SUOMI NPP',}
TBUS_STYLE = False

TLE_BUFFER = {}

def get_tle_file(timestamp):
    # Find a not to old TLE file
    for path in TLE_FILE_PATH:
        if os.path.isdir(path):
            for i in range(5):
                t = timestamp - timedelta(days=i)
                f = path + t.strftime('/tle_%Y%m%d.txt')
                if os.path.isfile(f):
                    if path.startswith('/net'):
                        LOG.warning("Fetched TLE file over NFS '%s'" % f)
                    return f
    raise NoTleFile("Found no TLE file close in time to %s" % timestamp.strftime("%d/%m/%Y"))

def get_tle(satname, timestamp=None):
    stamp = satname + timestamp.strftime('-%Y%m%d')
    try:
        tle = TLE_BUFFER[stamp]
    except KeyError:
        tle = Tle(TLE_SATNAME[satname], get_tle_file(timestamp))
        TLE_BUFFER[stamp] = tle
    return tle

_re_replace_orbitno = re.compile("_b(\d{5})")
def check_and_replace_orbitno(filename):
    stamp = npp.get_npp_stamp(filename)
    if stamp.orbit > 123:
        return filename # orbit number looks healthy

    # Correct h5 attributes
    import h5py
    def _check_orbitno(name, obj):
        if isinstance(obj, h5py.Dataset):
            for date_key, time_key, orbit_key in (
                ('AggregateBeginningDate', 'AggregateBeginningTime', 
                 'AggregateBeginningOrbitNumber'),
                ('AggregateEndingDate', 'AggregateEndingTime',
                 'AggregateEndingOrbitNumber'),
                ('Beginning_Date', 'Beginning_Time',
                 'N_Beginning_Orbit_Number')):
                if orbit_key in obj.attrs.keys():
                    time_val = datetime.strptime(
                        obj.attrs[date_key][0][0] + 
                        obj.attrs[time_key][0][0],
                        '%Y%m%d%H%M%S.%fZ')
                    # FIXME, check for nodate = 1958
                    orbit_val = orbital.get_orbit_number(time_val,
                                                         tbus_style=TBUS_STYLE)
                    obj.attrs.modify(orbit_key, [[orbit_val]])
                    counter[0] += 1

    # Correct h5 attributes
    tle = get_tle(stamp.satname, stamp.start_time)
    orbital = Orbital(tle.satname, line1=tle.line1, line2=tle.line2)
    orbit = orbital.get_orbit_number(stamp.start_time, tbus_style=TBUS_STYLE)
    LOG.info("Replacing orbit number %05d with %05d" % (stamp.orbit, orbit))
    counter = [0]
    fp = h5py.File(filename, 'r+')
    fp.visititems(_check_orbitno)    
    if counter[0] == 0:
        raise NPPUtilsError("Failed replacing orbit number in hdf5 attributes '%s'" % fname)
    LOG.info("Replaced orbit number in %d attributes" % counter[0])
    fp.close()

    # Correct filename
    dname, fname = os.path.split(filename)
    fname, n = _re_replace_orbitno.subn('_b%05d' % orbit, fname)
    if n != 1:
        raise NPPUtilsError("Failed replacing orbit number in filename '%s'" % fname)
    return os.path.join(dname, fname)

if __name__ == '__main__':
    import sys
    print check_and_replace_orbitno(sys.argv[1])
