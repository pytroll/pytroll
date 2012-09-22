"""Level-1 processing for VIIRS NPP Direct Readout data.  Using the CSPP
level-1 processor from the SSEC, Wisconsin based on the ADL from the NASA DRL.
Listen for pytroll messages from nimbus (NPP file dispatch) and trigger
processing on direct readout data
"""

# Does'nt handle the execution of several instances of CSPP at the same time
# So, it assumes CSPP is finished before the next pass arrives, which will also
# normally (hopefully!) always be the case.
# FIXME!

import os

CSPP_HOME = os.environ.get("CSPP_HOME", '')
CSPP_WORKDIR = os.environ.get("CSPP_WORKDIR", '')
APPL_HOME = os.environ.get('NPP_SDRPROC', '')
ETC_DIR = os.environ.get('NPP_SDRPROC_CONFIG_DIR', '')


import ConfigParser
#CONFIG_PATH = "%s/etc" % os.environ.get('CSPP_HOME', '')
CONFIG_PATH = "%s" % ETC_DIR
print "CONFIG_PATH: ", CONFIG_PATH 

CONF = ConfigParser.ConfigParser()
CONF.read(os.path.join(CONFIG_PATH, "npp_sdr_config.cfg"))

MODE = os.getenv("SMHI_MODE")
if MODE is None:
    MODE = "offline"

OPTIONS = {}
for option, value in CONF.items(MODE, raw = True):
    OPTIONS[option] = value
 

# Safe:
addr_npp = "tcp://safe.smhi.se:9002"

LEVEL1_PUBLISH_PORT = 9020

SERVERNAME = OPTIONS['servername']

from urlparse import urlparse
import posttroll.subscriber
from posttroll.publisher import Publish
from posttroll.message import Message

from sdr_runner import get_datetime_from_filename
from sdr_runner.post_cspp import (get_sdr_files, 
                                  create_subdirname, 
                                  pack_sdr_files, make_okay_files,
                                  cleanup_cspp_workdir)

from sdr_runner.pre_cspp import fix_rdrfile

from sdr_runner import LOG

#: Default time format
_DEFAULT_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

#: Default log format
_DEFAULT_LOG_FORMAT = '[%(levelname)s: %(asctime)s : %(name)s] %(message)s'

import os, sys
_NPP_SDRPROC_LOG_FILE = os.environ.get('NPP_SDRPROC_LOG_FILE', None)
import logging

if _NPP_SDRPROC_LOG_FILE:
    handler = logging.FileHandler(_NPP_SDRPROC_LOG_FILE)
else:
    handler = logging.StreamHandler(sys.stderr)

formatter = logging.Formatter(fmt=_DEFAULT_LOG_FORMAT,
                              datefmt=_DEFAULT_TIME_FORMAT)
handler.setFormatter(formatter)

handler.setLevel(10)
LOG.setLevel(10)
LOG.addHandler(handler)


CSPP_ENVS = {"CSPP_HOME": CSPP_HOME,
             "CSPP_REV": "20120215",
             "CSPP_ANC_CACHE_DIR " : os.path.join(CSPP_HOME,'cache'),
             "CSPP_ANC_HOME" : os.path.join(CSPP_HOME,'static'),
             "CSPP_ANC_TILE_PATH" : "%s/static/ADL/data/tiles/Terrain-Eco-ANC-Tile/withMetadata" % (CSPP_HOME),
             "PATH" : '%s/atms/sdr:%s/atms/sdr:%s/viirs/edr:%s/viirs/sdr' % (CSPP_HOME, 
                                                                             CSPP_HOME,
                                                                             CSPP_HOME,
                                                                             CSPP_HOME),
             "ADL_HOME" : "%s/ADL" % (CSPP_HOME),
             "NPP_GRANULE_ID_BASETIME" : "1698019234000000",
             "DSTATICDATA" : '%s/ADL/CMN/Utilities/INF/util/time/src' % CSPP_HOME,
             "DPE_SITE_ID" : "cspp",
             "DPE_DOMAIN" : "dev",
             "INFTK_DM_ROOT" : "JUST_NEED_TO_HAVE_AN_ENV_VARIABLE"
             }

# ---------------------------------------------------------------------------
def run_cspp(viirs_rdr_file):
    """Run CSPP on VIIRS RDR files"""
    import subprocess
    #from subprocess import Popen
    import time
    import tempfile

    try:
        working_dir = tempfile.mkdtemp(dir=CSPP_WORKDIR)
    except OSError:
        working_dir = tempfile.mkdtemp()

    # Change working directory:
    fdwork = os.open(working_dir, os.O_RDONLY)
    os.fchdir(fdwork)

    print "Envs: ", CSPP_ENVS

    os.system("echo $PATH > ~/cspp_path.log")
    # Run the command:
    #retv = Popen(["viirs_sdr.sh", viirs_rdr_file], 
    #             env=CSPP_ENVS)
    #tup = retv.communicate()
    #print tup
    t0_clock = time.clock()
    t0_wall = time.time()
    subprocess.call(["viirs_sdr.sh", viirs_rdr_file])
    print time.clock() - t0_clock, "seconds process time"
    print time.time() - t0_wall, "seconds wall clock time"

    # Close working directory:
    os.close(fdwork)

    return working_dir

# ---------------------------------------------------------------------------
def start_npp_sdr_processing(level1_home, mypublisher, message):
    """From a posttroll message start the npp processing"""

    LOG.info("")
    LOG.info("\tMessage:")
    LOG.info(str(message))
    urlobj = urlparse(message.data['uri'])
    LOG.info("Server = " + str(urlobj.netloc))
    if urlobj.netloc != SERVERNAME:
        return
    LOG.info("Ok... " + str(urlobj.netloc))
    LOG.info("Sat and Instrument: " + str(message.data['satellite']) 
             + " " + str(message.data['instrument']))

    if (message.data['satellite'] == "NPP" and 
        message.data['instrument'] == 'viirs'):
        start_time = message.data['start_time']
        try:
            orbnum = int(message.data['orbit_number'])            
        except KeyError:
            orbnum = None
        path, fname =  os.path.split(urlobj.path)
        if fname.endswith('.h5'):
            # Check if the file exists:
            if not os.path.exists(urlobj.path):
                raise IOError("File is reported to be dispatched " + 
                              "but is not there! File = " + 
                              urlobj.path)

            # Do processing:
            LOG.info("RDR to SDR processing on npp/viirs with CSPP start!" + 
                     " Start time = ", start_time)
            if orbnum:
                LOG.info("Orb = %d" % orbnum)
            LOG.info("File = %s" % str(urlobj.path))
            # Fix orbit number in RDR file:
            try:
                rdr_filename = fix_rdrfile(urlobj.path)
            except IOError:
                LOG.error('Failed to fix orbit number in RDR file = ' + str(urlobj.path))
                import traceback
                traceback.print_exc(file=sys.stderr)

            LOG.info("Start CSPP: RDR file = " + str(rdr_filename))
            working_dir = run_cspp(rdr_filename)
            LOG.info("CSPP SDR processing finished...")
            # Assume everything has gone well! 
            # Move the files from working dir:
            result_files = get_sdr_files(working_dir)
            if len(result_files) == 0:
                LOG.warning("No SDR files available. CSPP probably failed!")
                return

            # Use the start time from the RDR message!:
            tobj = start_time
            LOG.info("Time used in sub-dir name: " + str(tobj.strftime("%Y-%m-%d %H:%M")))
            subd = create_subdirname(tobj)
            LOG.info("Create sub-directory for sdr files: %s" % str(subd))
            pack_sdr_files(result_files, level1_home, subd)
            make_okay_files(level1_home, subd)

            cleanup_cspp_workdir(working_dir)

            # Now publish:
            filename = result_files[0]
            LOG.info("Filename = %s" % filename)
            to_send = {}
            to_send['uri'] = ('ssh://safe.smhi.se/' +  
                              os.path.join(level1_home, 
                                           filename))
            to_send['filename'] = filename
            to_send['instrument'] = 'viirs'
            to_send['satellite'] = 'NPP'
            to_send['format'] = 'HDF5'
            to_send['type'] = 'SDR'
            to_send['start_time'] = start_time #start_time.isoformat()
            message = Message('/oper/polar/direct_readout/norrkoping',
                          "file", to_send).encode()
            mypublisher.send(message)

    return


# ---------------------------------------------------------------------------
def npp_runner():
    """The NPP/VIIRS runner. Listens and triggers processing"""

    sdr_home = OPTIONS['level1_home']

    with posttroll.subscriber.Subscribe('RDR') as subscr:
        with Publish('npp_dr_runner', 'SDR', 
                     LEVEL1_PUBLISH_PORT) as publisher:        
            for msg in subscr.recv():
                start_npp_sdr_processing(sdr_home, publisher, msg)

    return

# ---------------------------------------------------------------------------
if __name__ == "__main__":

    #npp_runner()

    rdr_home_dir = OPTIONS['level0_home']
    sdr_home_dir = OPTIONS['level1_home']

    from glob import glob
    rdrlist = glob('%s/RNSCA-RVIRS_*' % rdr_home_dir)
    rdr_filename = rdrlist[0]
    rdr_filename = fix_rdrfile(rdr_filename)
    wrkdir = run_cspp(rdr_filename)
    #wrkdir = "/san1/wrk_cspp/tmpujTkcm"
    result_files = get_sdr_files(wrkdir)
    tobj = get_datetime_from_filename(rdr_filename)
    subd = create_subdirname(tobj)
    pack_sdr_files(result_files, sdr_home_dir, subd)
    make_okay_files(sdr_home_dir, subd)
    cleanup_cspp_workdir(wrkdir)
