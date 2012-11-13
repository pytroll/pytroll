"""Scanning the CSPP working directory and cleaning up after CSPP processing
and move the SDR granules to a destination directory"""

import os, shutil
from glob import glob
from sdr_runner.orbitno import TBUS_STYLE

import logging
LOG = logging.getLogger(__name__)

def cleanup_cspp_workdir(workdir):
    """Clean up the CSPP working dir after processing"""

    filelist = glob('%s/*' % workdir)
    this = [ os.remove(s) for s in filelist if os.path.isfile(s) ]
    LOG.info("Number of files left after cleaning working dir = " + str(len(this)))
    shutil.rmtree(workdir)
    #os.mkdir(workdir)
    return


def get_sdr_files(sdr_dir):
    """Get the sdr filenames (all M- and I-bands plus geolocation for the
    direct readout swath"""

    # VIIRS M-bands + geolocation:
    mband_files = (glob(os.path.join(sdr_dir, 'SVM??_npp_*.h5')) + 
                   glob(os.path.join(sdr_dir, 'GM??O_npp_*.h5')))
    # VIIRS I-bands + geolocation:
    iband_files = (glob(os.path.join(sdr_dir, 'SVI??_npp_*.h5')) + 
                   glob(os.path.join(sdr_dir, 'GI??O_npp_*.h5')))
    # VIIRS DNB band + geolocation:
    dnb_files = (glob(os.path.join(sdr_dir, 'SVDNB_npp_*.h5')) + 
                 glob(os.path.join(sdr_dir, 'GDNBO_npp_*.h5')))

    return sorted(mband_files) + sorted(iband_files) + sorted(dnb_files)

def create_subdirname(obstime, with_seconds=False):
    """Generate the pps subdirectory name from the start observation time, ex.:
    'npp_20120405_0037_02270'"""
    from pyorbital.orbital import Orbital
    from sdr_runner import orbitno

    tle = orbitno.get_tle('npp', obstime)
    orbital_ = Orbital(tle.platform, line1=tle.line1, line2=tle.line2)
    orbnum = orbital_.get_orbit_number(obstime, tbus_style=TBUS_STYLE)

    if with_seconds:
        return obstime.strftime('npp_%Y%m%d_%H%M%S_') + '%.5d' % orbnum
    else:
        return obstime.strftime('npp_%Y%m%d_%H%M_') + '%.5d' % orbnum


def make_okay_files(base_dir, subdir_name):
    """Make okay file to signal that all SDR files have been placed in
    destination directory"""
    import subprocess
    okfile = os.path.join(base_dir, subdir_name + ".okay")
    subprocess.call(['touch', okfile])
    return

def pack_sdr_files(sdrfiles, base_dir, subdir):
    """Copy the SDR files to the sub-directory under the pps directory
    structure"""

    path = os.path.join(base_dir, subdir)
    if not os.path.exists(path):
        os.mkdir(path)

    LOG.info("Number of SDR files: " + str(len(sdrfiles)))
    for sdrfile in sdrfiles:
        newfilename = os.path.join(path, os.path.basename(sdrfile))
        LOG.info("Copy sdrfile to destination: " + newfilename)
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

    rootdir = "/san1/pps/import/PPS_data/source"
    from sdr_runner import get_datetime_from_filename
    FILES = get_sdr_files(CSPP_WRKDIR)
    start_time = get_datetime_from_filename(FILES[0])

    subd = create_subdirname(start_time)
    pack_sdr_files(FILES, rootdir, subd)
    make_okay_files(rootdir, subd)
