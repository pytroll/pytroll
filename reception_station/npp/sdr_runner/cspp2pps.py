"""Scanning the CSPP working directory and cleaning up after CSPP processing
and move the SDR granules into the PPS directory structure"""

import os, shutil
from glob import glob


# Harcoded path to PPS files! FIXME!
PPS_SOURCE = "/san1/pps/import/PPS_data/source"


def cleanup_cspp_workdir(workdir):
    """Clean up the CSPP working dir after processing"""
    import os
    import glob
    filelist = glob.glob('%s/*' % workdir)
    this = [ os.remove(s) for s in filelist if os.path.isfile(s) ]
    print "Number of files left after cleaning working dir = ", len(this)
    #shutil.rmtree(workdir)
    #os.mkdir(workdir)
    return

def get_datetime(filename):
    """Get start observation time from the filename. Example:
    'GMODO_npp_d20120405_t0037099_e0038341_b00001_c20120405124731856767_cspp_dev.h5'
    """
    from datetime import datetime

    bname = os.path.basename(filename)
    sll = bname.split('_')
    return datetime.strptime(sll[2] + sll[3][:-1], 
                             "d%Y%m%dt%H%M%S")

def get_files4pps(sdr_dir):
    """Get the sdr filenames (all M bands plus geolocation for the direct
    readout swath"""

    # VIIRS M-bands + geolocation:
    mband_files = (glob(os.path.join(sdr_dir, 'SVM??_npp_*.h5')) + 
                   glob(os.path.join(sdr_dir, 'GM??O_npp_*.h5')))
    ## VIIRS I-bands + geolocation:
    #iband_files = (glob(os.path.join(sdr_dir, 'SVI??_npp_*.h5')) + 
    #               glob(os.path.join(sdr_dir, 'GI??O_npp_*.h5')))

    return sorted(mband_files)

def create_pps_subdirname(obstime):
    """Generate the pps subdirectory name from the start observation time, ex.:
    'npp_20120405_0037_02270'"""
    from pre_cspp import get_npp_orbit_number

    orbnum = get_npp_orbit_number(obstime)
    return obstime.strftime('npp_%Y%m%d_%H%M_') + '%.5d' % orbnum

def make_okay_files(subdir_name):
    """Make okay files to signal that PPS TM can start"""
    import subprocess
    okfile = os.path.join(PPS_SOURCE, subdir_name + ".okay")
    subprocess.call(['touch', okfile])

def pack_sdr_files4pps(sdrfiles, subdir):
    """Correct the SDR files for orbit number and copy the files to the
    sub-directory under the pps directory structure"""
    import pre_cspp

    path = os.path.join(PPS_SOURCE, subdir)
    if not os.path.exists(path):
        os.mkdir(path)

    print "SDR files: ", sdrfiles
    for sdrfile in sdrfiles:
	newfilename = os.path.join(path, os.path.basename(sdrfile))
	print "Copy sdrfile for PPS: ", newfilename
	shutil.copy(sdrfile, newfilename)

    return

# --------------------------------
if __name__ == "__main__":    
    import sys
    if len(sys.argv) < 2:
        print "Usage %s <cspp work dir>" % sys.argv[0]
        sys.exit()
    else:
        # SDR DIR:
        CSPP_WRKDIR = sys.argv[1]

    FILES = get_files4pps(CSPP_WRKDIR)
    start_time = get_datetime(FILES[0])

    subd = create_pps_subdirname(start_time)
    pack_sdr_files4pps(FILES, subd)
    make_okay_files(subd)
