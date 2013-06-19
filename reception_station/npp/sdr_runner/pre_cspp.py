"""Fix the RDR files with respect to orbit number. There is a bug in the
RT-STPS software always giving the orbit number = 1"""

import os, sys
import h5py
from datetime import datetime, timedelta
import numpy as np
import pyorbital.orbital as orb

#import logging
#LOG = logging.getLogger(__name__)
from sdr_runner import LOG

TLEDIR = "/data/24/saf/polar_in/tle2"

# ---------------------------------------------------------------------------
def fix_rdrfile(filename):
    import os
    from sdr_runner.orbitno import replace_orbitno
    
    newname, orbnum = replace_orbitno(filename)
    os.rename(filename, newname)

    return newname, orbnum


# ---------------------------------------------------------------------------
def get_orbitnumbers_to_nppfile(npp_file):
    """Browse the RDR/SDR file and get granule start/end times, and determine
    the correct orbit numbers for those times, to be later corrected in the
    file."""
    deltat = timedelta(days=1)

    fobj = h5py.File(npp_file, 'r')

    # First get all start and end date/time of the granules:
    obstimes = {}
    start_obstime = None
    end_obstime = None
    for group in fobj['/Data_Products'].keys():
        for dset in fobj['/Data_Products'][group]:
            # Get begining and ending date/time:
            for begin_end in ['Beginning', 'Ending']:
                try:
                    time_key = 'Aggregate' + begin_end + 'Time'
                    date_key = 'Aggregate' + begin_end + 'Date'
                    x_date = fobj['/Data_Products'][group][dset].attrs[date_key]
                    x_time = fobj['/Data_Products'][group][dset].attrs[time_key]
                    if not start_obstime and begin_end == 'Beginning':
                        # Ex.: '20120405'+'021645'
                        datetime_str = (x_date[0][0] + 
                                        x_time[0][0].split('.')[0])
                        start_obstime = datetime.strptime(datetime_str, 
                                                          '%Y%m%d%H%M%S')
                    if not end_obstime and begin_end == 'Ending':
                        # Ex.: '20120405'+'021645'
                        datetime_str = (x_date[0][0] + 
                                        x_time[0][0].split('.')[0])
                        end_obstime = datetime.strptime(datetime_str, 
                                                        '%Y%m%d%H%M%S')
                except KeyError:
                    time_key = begin_end + '_Time'
                    date_key = begin_end + '_Date'
                    x_date = fobj['/Data_Products'][group][dset].attrs[date_key]
                    x_time = fobj['/Data_Products'][group][dset].attrs[time_key]
                
                datetime_str = (x_date[0][0] + 
                                x_time[0][0].split('.')[0])
                obstimes[group+dset+begin_end] = datetime.strptime(datetime_str, 
                                                                   '%Y%m%d%H%M%S')

            
    fobj.close()

    if not start_obstime and not end_obstime:
        raise IOError("Failed getting the granule start and end times")

    # Check for no date (1958) problem:
    dt1958 = datetime(1958, 1, 1)
    if abs(start_obstime - dt1958) < timedelta(days=2):
        print "Start time wrong: %s" % start_obstime.strftime('%Y%m%d')
        print "Will use the end time to determine orbit number"
        if abs(end_obstime - dt1958) < timedelta(days=2):
            raise IOError("Both start time and end time is far off in file!")
        obstime = end_obstime
    else:
        obstime = start_obstime
        
    datestr = obstime.strftime('%Y%m%d')
    try:
        sat = orb.Orbital('SUOMI NPP',  
                          tle_file=os.path.join(TLEDIR,
                                                'tle-%s.txt' % datestr)
                          )
    except IOError:
        datestr = (obstime - deltat).strftime('%Y%m%d')
        sat = orb.Orbital('SUOMI NPP', 
                          tle_file=os.path.join(TLEDIR,
                                                'tle-%s.txt' % datestr)
                          )

    # Get the start orbit number:
    orbits = {}
    start_orbnum = sat.get_orbit_number(obstime)
    orbits['start'] = start_orbnum

    # Get all orbit numbers for the swath.
    # Check for erroneous date-times (1958):
    prev_okay_obstime = obstime
    for key in obstimes:
        if abs(obstimes[key] - dt1958) < timedelta(days=2):
            obstime = prev_okay_obstime
        else:
            obstime = obstimes[key]

        orbits[key] = sat.get_orbit_number(obstime)
 
    print "Orbit numbers in swath:"
    for key in obstimes:
        print orbits[key], 
    print


    return orbits


def fix_nppfile4orbitnumber(orbits, npp_file, outdir):
    """Fix the NPP VIIRS RDR/SDR files with respect to oribit number. The
    RDR/SDR file is read and the correct orbit number is inserted, and the
    filename is fixed as well."""
    import shutil

    # Determine the new output filename:
    start_orbnum = orbits['start']
    npp_filename = os.path.basename(npp_file)
    new_filename = (npp_filename.split('_b')[0] +
                    '_b%.5d' % (start_orbnum) + 
                    npp_filename[npp_filename.find('_c')::])
    outfile = os.path.join(outdir, new_filename)

    if os.path.exists(outfile):
        print "File exists! %s" % os.path.basename(outfile)
        return outfile

    shutil.copy(npp_file, outfile)


    # Start browsing file and change the orbit number:
    out = h5py.File(outfile)

    for group in out['/Data_Products'].keys():
        for dset in out['/Data_Products'][group]:
            # Attributes:
            subsubg_attrs = out['/Data_Products'][group][dset].attrs
            for key, val in subsubg_attrs.items():
                if key in ['AggregateBeginningOrbitNumber',
                           'N_Beginning_Orbit_Number']:
                    start_orbnum = orbits[group+dset+'Beginning']
                    #print "Change orbit number from 1", start_orbnum
                    val =  np.array([[start_orbnum]]).astype('uint64')

                    out['/Data_Products'][group][dset].attrs[key] = val

                if key in ['AggregateEndingOrbitNumber']:
                    end_orbnum = orbits[group+dset+'Ending']
                    #print "Change orbit number from 1", end_orbnum
                    val =  np.array([[end_orbnum]]).astype('uint64')
                
                    out['/Data_Products'][group][dset].attrs[key] = val

    out.close()
    return outfile


def get_npp_orbit_number(obstime):
    """Get the orbit number for the Suomi NPP RDR/SDR file given the
    observation start time. The orbit number"""

    deltat = timedelta(days=1)
    datestr = obstime.strftime('%Y%m%d')
    try:
        sat = orb.Orbital('SUOMI NPP', 
                          tle_file=os.path.join(TLEDIR,
                                                'tle-%s.txt' % datestr)
                          )
    except IOError:
        datestr = (obstime - deltat).strftime('%Y%m%d')
        sat = orb.Orbital('SUOMI NPP', 
                          tle_file=os.path.join(TLEDIR,
                                                'tle-%s.txt' % datestr)
                          )
        
    orbit = sat.get_orbit_number(obstime)

    return orbit

# -------------------------
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "Usage: %s <rdr/sdr filename> <output dir>" % sys.argv[0]
        sys.exit()
    else:
        nppfile = sys.argv[1]
        output_dir = sys.argv[2]


    orbs = get_orbitnumbers_to_nppfile(nppfile)
    fix_nppfile4orbitnumber(orbs, nppfile, output_dir)
