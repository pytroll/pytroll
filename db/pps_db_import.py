import sys
import os
import glob
from datetime import datetime, timedelta

import shapely

import pytroll_db
from pyorbital import orbital

TIMESTEP = 10 # Time step in seconds used to define the resloution of the ground track
TLE_LOCATION = "/data/24/saf/polar_in/tle"

sat_lookup = {'metop02' : 'Metop-A'}

def get_latest_tle():
    """Get the latest tle file from disk"""
    files = glob.glob("%s/tle-*.txt" % TLE_LOCATION)
    tlefile = files[-1] # Take the latest
    return tlefile

def add_product(dcm, filename):
    info = filename.split('_')
    satname = info[0]
    orbit = int(info[3])
    time_start = datetime.strptime(info[1] + info[2], '%Y%m%d%H%M')
    time_end = time_start + timedelta(minutes=3)

    ft = dcm.get_file_type('PPS_cloud_type_granule')
    ff = dcm.get_file_format('HDF5')

    nf = dcm.create_file(filename, file_type=ft, file_format=ff)
   
    p = dcm.get_parameter('time_start')
    pv = dcm.create_parameter_value(time_start.isoformat(), file_obj=nf, parameter=p)
    p = dcm.get_parameter('time_end')
    pv = dcm.create_parameter_value(time_end.isoformat(), file_obj=nf, parameter=p)
    p = dcm.get_parameter('orbit_number')
    pv = dcm.create_parameter_value(orbit, file_obj=nf, parameter=p)
    p = dcm.get_parameter('satellite_name')
    pv = dcm.create_parameter_value(satname, file_obj=nf, parameter=p)

    sat = orbital.Orbital(sat_lookup.get(satname, satname), tle_file=get_latest_tle())

    dt = timedelta(seconds=10)
    print time_start
    current_time = time_start
    lonlat_list = []
    while current_time <= time_end:
        pos = sat.get_lonlatalt(current_time)
        lonlat_list.append(pos[:2])
        current_time += dt

    value = 'LINESTRING ('
    for i, item in enumerate(lonlat_list):
        if i == 0:
            value += '%s %s' % (item[0], item[1])
        else:
            value += ' ,%s %s' % (item[0], item[1])
    value += ')'

    wkt_o = shapely.wkt.loads(value)
    p_track = dcm.get_parameter('sub_satellite_track')
    pls = dcm.create_parameter_linestring(wkt_o, file_obj=nf, parameter=p_track)

    dcm.save()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: %s <path> <glob-string>" % sys.argv[0]
        sys.exit(0)
    dcm = pytroll_db.DCManager('postgresql://polar:polar@safe:5432/sat_db') 
    dirname, file_filter = sys.argv[1:3]
    tmp = '%s/%s' % (dirname, file_filter)
    print tmp
    files = glob.glob('%s/%s' % (dirname, file_filter))
    #print 'files: ', files
    for file_path in files:
        try:
            add_product(dcm, os.path.basename(file_path))
        except Exception, e:
            print 'Failed to add file %s to database: %s' % (os.path.basename(file_path), e)
            dcm.rollback()

        break
