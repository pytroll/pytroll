"""
Script to run CSPP in real time
"""

import os
import sys
from datetime import datetime
import glob
from subprocess import call
import re

from polar_preproc import get_npp_stamp, LOG

def do_prod(filename, logfile=None):
    """
    Run CSPP on VIIRS RDR filename, via the CSPP VIIRS main script viirs_sdr.sh
    """
    cspp_batch = "time viirs_sdr.sh %s" % filename
    if logfile:
        stderr = open(logfile, 'w')
    else:
        stderr = sys.stderr
    try:
        LOG.info("Running '%s'" % cspp_batch)
        retcode = call(cspp_batch, stdout=stderr, stderr=stderr, shell=True)
        if retcode != 0:
            if retcode < 0:
                text = "cspp was terminated by signal %d" % -retcode
                raise OSError(text)
            else:
                text = "cspp returned %d" % retcode
    finally:
        if stderr.name == logfile:
            stderr.close()

    files = glob.glob('./*h5')
    if len(files) > 0:
        LOG.warning("OOPS h5 leftovers: %s"%str(files))
    
if __name__ == '__main__':
    import sys
    do_prod(sys.argv[1])
