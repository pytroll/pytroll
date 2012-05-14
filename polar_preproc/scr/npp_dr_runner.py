"""Level-1 processing for VIIRS NPP Direct Readout data.  Using the CSPP
level-1 processor from the SSEC, Wisconsin based on the ADL from the NASA DRL.
Listen for pytroll messages from nimbus (NPP file dispatch) and trigger
processing on direct readout data
"""

# Doesn not handle the execution of several instances of CSPP at the same time
# So, it assumes CSPP is finished before the next pass arrives, which will also
# normally (hopefullye) always be the case.
# FIXME!

import os, glob

CSPP_HOME = os.environ.get("CSPP_HOME", '')
CSPP_WORKDIR = os.environ.get("CSPP_WORKDIR", '')
APPL_HOME = os.environ.get('NPP_LVL1PROC', '')
# Use config file from application dir: FIXME!
ETC_DIR = "%s/etc" % CSPP_HOME

import ConfigParser
CONFIG_PATH = "%s/etc" % os.environ.get('CSPP_HOME', '')
print "CONFIG_PATH: ", CONFIG_PATH 

CONF = ConfigParser.ConfigParser()
CONF.read(os.path.join(CONFIG_PATH, "npp_dr_config.cfg"))

MODE = os.getenv("SMHI_MODE")
if MODE is None:
    MODE = "offline"

OPTIONS = {}
for option, value in CONF.items(MODE, raw = True):
    OPTIONS[option] = value
 

from datetime import datetime

# Safe:
addr_npp = "tcp://safe.smhi.se:9002"

LEVEL1_PUBLISH_PORT = 9020

servername = "safe.smhi.se"

from urlparse import urlparse
import posttroll.subscriber
from posttroll.publisher import Publish
from posttroll.message import Message

from cspp2pps import (get_files4pps, get_datetime, 
                      create_pps_subdirname, 
                      pack_sdr_files4pps, make_okay_files,
                      cleanup_cspp_workdir)


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

    working_dir = OPTIONS['working_dir']
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
    print time.time() - t0_wall, "seconds wall time"

    # Close working directory:
    os.close(fdwork)

    return

# ---------------------------------------------------------------------------
def npp_runner():
    """The NPP/VIIRS runner. Listens and triggers processing"""
    print "Do something..."

    level1_home = OPTIONS['level1_home']
    working_dir = OPTIONS['working_dir']

    subscr = posttroll.subscriber.Subscriber([addr_npp])
    with Publish('npp_dr_runner', 'SDR', 
                 LEVEL1_PUBLISH_PORT) as publisher:        
        for msg in subscr.recv():
            print ""
            print "\tMessage:"
            print msg
            urlobj = urlparse(msg.data['uri'])
            print "Server = ", urlobj.netloc
            if urlobj.netloc != servername:
                continue
            print "Ok... ", urlobj.netloc
            print "Sat and Instrument: ", msg.data['satellite'], msg.data['instrument']

            if (msg.data['satellite'] == "NPP" and 
                msg.data['instrument'] == 'viirs'):
                start_time = msg.data['start_time']
                try:
                    orbnum = int(msg.data['orbit number'])            
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
                    print("RDR to SDR processing on npp/viirs with CSPP start!" + 
                          " Start time = ", start_time)
                    if orbnum:
                        print "Orb = %d" % orbnum
                    print "File = ", urlobj.path
                    print "Cleanup working dir before CSPP start..."
                    cleanup_cspp_workdir(working_dir)
                    print "Start CSPP:"
                    run_cspp(urlobj.path)
                    print("CSPP SDR processing finished...")
                    # Assume everything has gone well! 
                    # Move the files from working dir and fix orbit number:

                    result_files = get_files4pps(working_dir)
                    if len(result_files) == 0:
                        print "No SDR files available. CSPP probably failed!"
                        continue

                    #start_time = get_datetime(result_files[0])
                    # Use the start time from the RDR message!:
                    tobj = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
                    subd = create_pps_subdirname(tobj)
                    pack_sdr_files4pps(result_files, subd)
                    make_okay_files(subd)

                    # Now publish:
                    filename = result_files[0]
                    print filename
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
                    msg = Message('/oper/polar/direct_readout/norrkoping',
                                  "file", to_send).encode()
                    publisher.send(msg)


    return

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    npp_runner()
    #rdr_dir = "/san1/polar_in/direct_readout/npp"
    #run_cspp("%s/RNSCA-RVIRS_npp_d20120506_t1228116_e1242435_b00001_c20120506124759680000_nfts_drl.h5" % (rdr_dir))
