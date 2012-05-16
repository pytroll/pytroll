import os
import sys
from datetime import datetime, timedelta
import re

from pyorbital.orbital import Orbital
from pyorbital.tlefile import Tle
from polar_preproc import TLE_DIRS, TLE_FILE_FORMAT, LOG
import polar_preproc as ppp

class NoTleFile(Exception):
    pass

TLE_SATNAME = {'npp' : 'SUOMI NPP',}
TBUS_STYLE = False

TLE_BUFFER = {}

def _get_tle_file(timestamp):
    # Find a not to old TLE file
    for path in TLE_DIRS:
        if os.path.isdir(path):
            for i in range(5):
                tobj = timestamp - timedelta(days=i)
                fname = os.path.join(path, tobj.strftime(TLE_FILE_FORMAT))
                if os.path.isfile(fname):
                    LOG.info("Found TLE file: '%s'" % fname)
                    return fname
    raise NoTleFile("Found no TLE file close in time to " + 
                    str(tobj.strftime(TLE_FILE_FORMAT)))

def get_tle(platform, timestamp=None):
    stamp = platform + timestamp.strftime('-%Y%m%d')
    try:
        tle = TLE_BUFFER[stamp]
    except KeyError:
        tle = Tle(TLE_SATNAME[platform], _get_tle_file(timestamp))
        TLE_BUFFER[stamp] = tle
    return tle

_re_replace_orbitno = re.compile("_b(\d{5})")
def replace_orbitno(filename):
    stamp = ppp.get_npp_stamp(filename)

    # Correct h5 attributes
    no_date = datetime(1958, 1, 1)
    epsilon_time = timedelta(days=2)
    import h5py

    def _get_a_good_date(name, obj):
        if isinstance(obj, h5py.Dataset):
            date_key, time_key = ('Ending_Date', 'Ending_Time')
            if date_key in obj.attrs.keys():
                time_val = datetime.strptime(
                    obj.attrs[date_key][0][0] + 
                    obj.attrs[time_key][0][0],
                        '%Y%m%d%H%M%S.%fZ')
                if not good_time_val__[0] and abs(time_val - no_date) > epsilon_time:
                    good_time_val__[0] = time_val
                
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

                    # Check for no date (1958) problem:
                    if abs(time_val - no_date) < epsilon_time:
                        LOG.info("Start time wrong: %s" % time_val.strftime('%Y%m%d'))
                        LOG.info("Will use the first good end time encounter " + 
                                 "in file to determine orbit number")
                        time_val = good_time_val__[0]

                    orbit_val = orbital.get_orbit_number(time_val,
                                                         tbus_style=TBUS_STYLE)
                    obj.attrs.modify(orbit_key, [[orbit_val]])
                    counter__[0] += 1

    # Correct h5 attributes
    tle = get_tle(stamp.platform, stamp.start_time)
    orbital = Orbital(tle.platform, line1=tle.line1, line2=tle.line2)
    orbit = orbital.get_orbit_number(stamp.start_time, tbus_style=TBUS_STYLE)
    LOG.info("Replacing orbit number %05d with %05d" % (stamp.orbit_number, orbit))
    fp = h5py.File(filename, 'r+')
    good_time_val__ = [None]
    fp.visititems(_get_a_good_date)
    counter__ = [0]
    fp.visititems(_check_orbitno)    
    if counter__[0] == 0:
        raise IOError("Failed replacing orbit number in hdf5 attributes '%s'" % fname)
    LOG.info("Replaced orbit number in %d attributes" % counter__[0])
    fp.close()

    # Correct filename
    dname, fname = os.path.split(filename)
    fname, n = _re_replace_orbitno.subn('_b%05d' % orbit, fname)
    if n != 1:
        raise IOError("Failed replacing orbit number in filename '%s'" % fname)
    return os.path.join(dname, fname)

if __name__ == '__main__':
    import sys
    print replace_orbitno(sys.argv[1])
