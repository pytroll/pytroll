# -*- coding: utf-8 -*-
"""
mp3_filematch.py

Created on Fri Sep  6 07:23:30 2013

@author: ras
"""
import sys
import os
import re
from datetime import datetime, timedelta
import socket

BASE_URI = 'ssh://%s' % socket.gethostname()

_FILENAME_MATCH = {

    'FENGYUN-HRPT-0':
        {'_filematch': re.compile("^(fy3.)_(\d{8}_\d{4})_(\d{6})_(\d{6})_(\d{1,6})_(.{3})\.hrp(|_last)$"), 
         '_timematch': ("%Y%m%d_%H%M", "%H%M%S", "%H%M%S"),
         '_md_type': 'noaa-raw',
         'format': "HRPT",
         'type': "binary",
         'instrument': "HRP",
         'level': '0',
         'source': 'MEOS Polar'},
    
    'FENGYUN-MPT-0':
        {'_filematch': re.compile("^(fy3.)_(\d{8}_\d{4})_(\d{6})_(\d{6})_(\d{1,6})_(.{3})\.mpt(|_last)$"), 
         '_timematch': ("%Y%m%d_%H%M", "%H%M%S", "%H%M%S"),
         '_md_type': 'noaa-raw',
         'format': "MPT",
         'type': "binary",
         'instrument': "MPT",
         'level': '0',
         'source': 'MEOS Polar'},

    'METOP-HRPT-0':
        {'_filematch': re.compile("(^.{4})_HRP_.._(M..)_(\d{14})Z_(\d{14})Z_.*_(.{3})(|_last)$"),
         '_timematch': ("%Y%m%d%H%M%S", "%Y%m%d%H%M%S"),
         '_md_type': 'metop-raw',
         'format': "EPS",
         'type': "binary",
         'instrument': "",
         'level': '0',
         'source': 'MEOS Polar'},
    
    'NOAA-HRPT-0':
        {'_filematch': re.compile("^(noaa\d{2})_(\d{8}_\d{4})_(\d{6})_(\d{6})_(\d{1,6})_(.{3})\.hrp(|_last)$"),
         '_timematch': ("%Y%m%d_%H%M", "%H%M%S", "%H%M%S"),
         '_md_type': 'noaa-raw',
         'format': "HRPT",
         'type': "binary",
         'instrument': "HRP",
         'level': '0',
         'source': 'MEOS Polar'},

    'NPP-CADU-0':
        {'_filematch': re.compile("^(npp)_(\d{8}_\d{4})_(\d{6})_(\d{6})_(\d{1,6})_(.{3})\.hrd(|_last)$"), 
         '_timematch': ("%Y%m%d_%H%M", "%H%M%S", "%H%M%S"),
         '_md_type': 'noaa-raw',
         'format': "CADU",
         'type': "binary",
         'instrument': "HRD",
         'level': '0',
         'source': 'MEOS Polar'},

    'AQUA-EOS-1B':
        {'_filematch': re.compile("^MYD02.KM_(AQUA)_(\d{5})_(\d{8}_\d{6}).hdf$"),
         '_timematch': ("%Y%m%d_%H%M%S",),
         '_md_type': 'modis-1b',
         'format': "EOS",
         'type': "HDF4",
         'instrument': "MODIS",
         'level': '1b',
         'source': 'MEOS Polar'},

    'TERRA-EOS-1B':
        {'_filematch': re.compile("^MOD02.KM_(TERRA)_(\d{5})_(\d{8}_\d{6}).hdf$"),
         '_timematch': ("%Y%m%d_%H%M%S",),
         '_md_type': 'modis-1b',
         'format': "EOS",
         'type': "HDF4",
         'instrument': "MODIS",
         'level': '1b',
         'source': 'MEOS Polar'},

    'SCHEDULE-CONFIRMATION':
        {'_filematch': re.compile("^(\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})-acquisition-" + 
                                 "schedule-confirmation-(.{3})-(.{3})\.xml$"), 
         '_timematch': ("%Y-%m-%d-%H-%M-%S",),        
         '_md_type': 'schedule',
         'format': "SCHEDULE-CONFIRMATION",
         'type': "xml",
         'source': 'MEOS Polar'},

    'PYTROLL-MESSAGE':
        {'_filematch': re.compile(".*\.message$"),
         '_md_type': 'message',
         'format': 'PYTROLL-MESSAGE',
         'type': "text"},

    'STATUS-FILES':
        {'_filematch': re.compile("(.*)-(\d{5})\.(\d)\.level-(.*)_(.*)$"),
         '_md_type': 'status_file',
         'format': 'STATUS-FILES',
         'type': "text",
         'source': 'MEOS Polar'},

    }

_ANTENNA_LONG_NAMES = {'orb': 'orbital',
                       'dat': 'datron',
                       'yan': 'yantai'}

def get_metop_orbit(satellite, timestamp):
    from sat_schedules import fetch_tle
    from pyorbital import orbital
    satnames = {'M01': 'METOP-B',
                'M02': 'METOP-A',
                'M03': 'METOP-C'}
    try:
        satname = satnames[satellite]
    except KeyError:
        print >> sys.stderr, "ERROR, This 'get_metop_orbit' only work for METOP satellites"
        return 0        
    tles = fetch_tle.get_tle(timestamp)
    if not tles:
        return 0        
    l1, l2 = tles.get(satname)
    orb = orbital.Orbital(satname, line1=l1, line2=l2)
    return orb.get_orbit_number(timestamp, tbus_style=True)

def get_metop_orbit_from_file(filename):
    from eps_decode import get_mphr
    try:
        return get_mphr(filename, 'orbit_start')
    except AttributeError:        
        print >> sys.stderr, "ERROR: Could not read 'orbit_start' from EPS file '%s'" % \
            os.path.basename(filename)
        return 0

def filename_md(filename, filetype=None):
    """Match a filename from to MP3 system to a format and type.

    If filetype passed it will we will only try to match filename to
    that filetype.
    """
    md_ = {}
    basename = os.path.basename(filename)

    key = None
    if filetype:
        #
        # Match against a singe filetype.
        #
        try:
            key, val = filetype,  _FILENAME_MATCH[filetype]
        except KeyError:
            raise ValueError, "Unknow filetype '%s'" % filetype
        m__ = val['_filematch'].match(basename)
        if not m__:
            raise ValueError, "Filename '%s' do not match filetype '%s'" % (
                basename, filetype)
    else:
        #
        # Match against a all filetypes.
        #
        for k__, v__ in _FILENAME_MATCH.items():
            m__ = v__['_filematch'].match(basename)
            if m__:
                key, val = k__, v__
                break
    if not key:
        return

    for k__ in val:
        if k__[0] != '_':
            md_[k__] = val[k__]
    md_['filename'] = basename
    md_['uri'] = BASE_URI + filename
    
    try:
        md_['size'] =  os.path.getsize(filename)
    except OSError:
        print >> sys.stderr, "WARNING: Could not get size of '%s'" % \
            filename

    if key == 'PYTROLL-MESSAGE':
        pass
    elif key == 'SCHEDULE-CONFIRMATION':
        md_['creation-time'] = datetime.strptime(m__.groups()[0], 
                                                 val['_timematch'][0]).isoformat()
        md_['station'] = m__.groups()[1]
        antenna = m__.groups()[2]
        md_['antenna'] = _ANTENNA_LONG_NAMES.get(antenna, antenna)
    elif key == 'STATUS-FILES':
        md_['satellite'] = m__.groups()[0]
        md_['orbit'] = int(m__.groups()[1])
        md_['mp3_mode'] = int(m__.groups()[2])
        md_['level'] = m__.groups()[3]
        md_['content'] = m__.groups()[4]
    else:
        if val['_md_type'] == 'noaa-raw':
            md_['satellite'] = m__.groups()[0]

            # timestamp is up to minutes
            stamp = datetime.strptime(m__.groups()[1], val['_timematch'][0])
            t__ = datetime.strptime(m__.groups()[2], val['_timematch'][1])

            # start_time is hours:minutes
            start_time = datetime(stamp.year, stamp.month, stamp.day, 
                                      t__.hour, t__.minute, t__.second, t__.microsecond)
            if start_time < stamp:
                start_time += timedelta(hours=24)

            # end_time is hours:minutes
            t__ = datetime.strptime(m__.groups()[3], val['_timematch'][2])
            end_time = datetime(stamp.year, stamp.month, stamp.day, 
                                    t__.hour, t__.minute, t__.second, t__.microsecond)
            if end_time < stamp:
                end_time += timedelta(hours=24)

            md_['start_time'] = start_time.isoformat()
            md_['end_time'] = end_time.isoformat()
            md_['orbit_number'] = int(m__.groups()[4])
            md_['station'] = m__.groups()[5]

        elif val['_md_type'] == 'metop-raw':
            md_['instrument'] = m__.groups()[0].replace('x', '')
            md_['satellite'] = m__.groups()[1]
            stamp = datetime.strptime(m__.groups()[2], val['_timematch'][0])
            md_['start_time'] = stamp.isoformat()
            md_['end_time'] = datetime.strptime(m__.groups()[3], 
                                                val['_timematch'][1]).isoformat()
            md_['orbit_number'] = get_metop_orbit(md_['satellite'], stamp)
            md_['station'] = m__.groups()[4]

        elif val['_md_type'] == 'modis-1b':
            md_['satellite'] = m__.groups()[0]
            md_['orbit_number'] = int(m__.groups()[1])
            md_['station'] = os.environ.get('STATION', 'smb')
            print m__.groups()[2], val['_timematch'][0]
            md_['start_time'] = datetime.strptime(m__.groups()[2], 
                                                  val['_timematch'][0]).isoformat()

    return md_

if __name__ == '__main__':
    try:
        filetype = sys.argv[2]
    except IndexError:
        filetype = None
    md = filename_md(sys.argv[1], filetype)
    if md:
        for k, v in md.items():
            print '%-12s' % k, v, type(v)
