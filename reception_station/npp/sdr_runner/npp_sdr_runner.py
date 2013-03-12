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

import sdr_runner
_PACKAGEDIR = sdr_runner.__path__[0]
_CONFIG_PATH = os.path.join(os.path.dirname(_PACKAGEDIR), 'etc')

CSPP_SDR_HOME = os.environ.get("CSPP_SDR_HOME", '')
CSPP_RT_SDR_LUTS = os.path.join(CSPP_SDR_HOME, 'anc/cache/luts')
CSPP_WORKDIR = os.environ.get("CSPP_WORKDIR", '')
APPL_HOME = os.environ.get('NPP_SDRPROC', '')

import ConfigParser
CONFIG_PATH = os.environ.get('NPP_SDRPROC_CONFIG_DIR', _CONFIG_PATH)
print "CONFIG_PATH: ", CONFIG_PATH 

CONF = ConfigParser.ConfigParser()
CONF.read(os.path.join(CONFIG_PATH, "npp_sdr_config.cfg"))

MODE = os.getenv("SMHI_MODE")
if MODE is None:
    MODE = "offline"

OPTIONS = {}
for option, value in CONF.items(MODE, raw = True):
    OPTIONS[option] = value

LEVEL1_PUBLISH_PORT = 9020
SERVERNAME = OPTIONS['servername']

THR_LUT_FILES_AGE_DAYS = OPTIONS.get('threshold_lut_files_age_days', 14)
URL_JPSS_REMOTE_ANC_DIR = OPTIONS['url_jpss_remote_anc_dir']
LUT_DIR = OPTIONS.get('lut_dir', CSPP_RT_SDR_LUTS)
LUT_UPDATE_STAMPFILE_RPEFIX = OPTIONS['lut_update_stampfile_prefix']
URL_DOWNLOAD_TRIAL_FREQUENCY_HOURS = OPTIONS['url_download_trial_frequency_hours']

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

#: Default time format
_DEFAULT_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

#: Default log format
_DEFAULT_LOG_FORMAT = '[%(levelname)s: %(asctime)s : %(name)s] %(message)s'

import os, sys
_NPP_SDRPROC_LOG_FILE = os.environ.get('NPP_SDRPROC_LOG_FILE', None)
import logging
from logging import handlers

LOG = logging.getLogger('npp_sdr_runner')

if _NPP_SDRPROC_LOG_FILE:
    #handler = logging.FileHandler(_NPP_SDRPROC_LOG_FILE)
    ndays = int(OPTIONS["log_rotation_days"])
    ncount = int(OPTIONS["log_rotation_backup"])
    handler = handlers.TimedRotatingFileHandler(_NPP_SDRPROC_LOG_FILE,
                                                when='midnight', 
                                                interval=ndays, 
                                                backupCount=ncount, 
                                                encoding=None, 
                                                delay=False, 
                                                utc=True)
else:
    handler = logging.StreamHandler(sys.stderr)

formatter = logging.Formatter(fmt=_DEFAULT_LOG_FORMAT,
                              datefmt=_DEFAULT_TIME_FORMAT)
handler.setFormatter(formatter)

handler.setLevel(logging.DEBUG)
LOG.setLevel(logging.DEBUG)
LOG.addHandler(handler)


CSPP_ENVS = {"CSPP_SDR_HOME": CSPP_SDR_HOME,
             "CSPP_REV": "20120215",
             "CSPP_ANC_CACHE_DIR " : os.path.join(CSPP_SDR_HOME,'cache'),
             "CSPP_ANC_HOME" : os.path.join(CSPP_SDR_HOME,'static'),
             "CSPP_ANC_TILE_PATH" : "%s/static/ADL/data/tiles/Terrain-Eco-ANC-Tile/withMetadata" % (CSPP_SDR_HOME),
             "PATH" : '%s/atms/sdr:%s/atms/sdr:%s/viirs/edr:%s/viirs/sdr' % (CSPP_SDR_HOME, 
                                                                             CSPP_SDR_HOME,
                                                                             CSPP_SDR_HOME,
                                                                             CSPP_SDR_HOME),
             "ADL_HOME" : "%s/ADL" % (CSPP_SDR_HOME),
             "NPP_GRANULE_ID_BASETIME" : "1698019234000000",
             "DSTATICDATA" : '%s/ADL/CMN/Utilities/INF/util/time/src' % CSPP_SDR_HOME,
             "DPE_SITE_ID" : "cspp",
             "DPE_DOMAIN" : "dev",
             "INFTK_DM_ROOT" : "JUST_NEED_TO_HAVE_AN_ENV_VARIABLE"
             }

# ---------------------------------------------------------------------------
def check_lut_files(thr_days=14):
    """Check if the LUT files under ${path_to_cspp_cersion}/anc/cache/luts are
    available and check if they are fresh. Return True if fresh/new files
    exists, otherwise False.
    It is files like these (with incredible user-unfriendly) names:
    510fc93d-8e4ed-6880946f-f2cdb929.asc
    510fc93d-8e4ed-6880946f-f2cdb929.VIIRS-SDR-GAIN-LUT_npp_20120217000000Z_20120220000001Z_ee00000000000000Z_PS-1-N-CCR-12-330-JPSS-DPA-002-PE-_noaa_all_all-_all.bin
    etc...

    We do not yet know if these files are always having the same name or if the
    number of files are expected to always be the same!?  Thus searching and
    checking is a bit difficult. We check if there any files at all, and then
    how old the latest file is, and hope that is sufficient.

    """

    from glob import glob
    from datetime import datetime, timedelta
    import stat
    import os.path

    now = datetime.utcnow()

    tdelta = timedelta(days=float(URL_DOWNLOAD_TRIAL_FREQUENCY_HOURS)/24.)
    # Get the time of the last update trial:
    files = glob(LUT_UPDATE_STAMPFILE_RPEFIX + '*')
    # Can we count on glob sorting the most recent file first. In case we can,
    # we don't need to check the full history of time stamp files. This will
    # save time! Currently we check all files...
    # FIXME!
    update_it = True
    for filename in files:
        tslot = datetime.strptime(os.path.basename(filename).split('.')[-1], '%Y%m%d%H%M')
        if now - tslot < tdelta:
            update_it = False
            break

    if not update_it:
        LOG.info('An URL update trial has been attempted recently. Continue')
        return

    LOG.info('No update trial seems to have been attempted recently')
    tdelta = timedelta(days=int(thr_days))

    files_ok = True
    LOG.info("Directory " + str(LUT_DIR) + "...")
    files = glob(os.path.join(LUT_DIR, '*'))
    if len(files) == 0:
        LOG.info("No LUT files available!")
        return False

    filename = files[0]
    tstamp = os.stat(filename)[stat.ST_MTIME]
    first_time = datetime.utcfromtimestamp(tstamp)
    #tstamp = os.stat(files[-1])[stat.ST_MTIME]
    #last_time = datetime.utcfromtimestamp(tstamp)

    if (now - first_time) > tdelta:
        LOG.info("File too old! File=%s " % filename)
        files_ok = False

    return files_ok

def update_lut_files():
    """
    Function to update the ancillary LUT files 

    These files need to be updated at least once every week, in order to
    achieve the best possible SDR processing.

    """
    import os, sys
    from datetime import datetime
    from subprocess import Popen, PIPE, STDOUT

    LOG.info("Start downloading....")

    # lftp -c "mirror --verbose --only-newer --parallel=2 $JPSS_REMOTE_ANC_DIR $CSPP_RT_SDR_LUTS"
    cmdstr = ('lftp -c "mirror --verbose --only-newer --parallel=2 ' + 
              URL_JPSS_REMOTE_ANC_DIR + ' ' + LUT_DIR + '"')

    lftp_proc = Popen(cmdstr, shell=True, 
                      stderr=PIPE, stdout=PIPE)
    
    while True:
        line = lftp_proc.stdout.readline()
        if not line:
            break
        LOG.info(line)

    while True:
        errline = lftp_proc.stderr.readline()
        if not errline:
            break
        LOG.info(errline)

    lftp_proc.poll()

    now = datetime.utcnow()
    timestamp = now.strftime('%Y%m%d%H%M')
    filename = LUT_UPDATE_STAMPFILE_RPEFIX + '.' + timestamp
    try:
        fpt = open(filename, "w")
        fpt.write(timestamp)
    except OSError:
        LOG.warning('Failed to write LUT-update time-stamp file')
    else:
        fpt.close()

    return

# ---------------------------------------------------------------------------
def run_cspp(viirs_rdr_file):
    """Run CSPP on VIIRS RDR files"""
    from subprocess import Popen, PIPE, STDOUT
    import time
    import tempfile

    viirs_sdr_call = OPTIONS['viirs_sdr_call']

    try:
        working_dir = tempfile.mkdtemp(dir=CSPP_WORKDIR)
    except OSError:
        working_dir = tempfile.mkdtemp()

    # Run the command:
    cmdlist = [viirs_sdr_call, viirs_rdr_file]
    t0_clock = time.clock()
    t0_wall = time.time()
    viirs_sdr_proc = Popen(cmdlist,
                           cwd=working_dir,
                           stderr=PIPE, stdout=PIPE)
    while True:
        line = viirs_sdr_proc.stdout.readline()
        if not line:
            break
        LOG.info(line)

    while True:
        errline = viirs_sdr_proc.stderr.readline()
        if not errline:
            break
        LOG.info(errline)
    LOG.info("Seconds process time: " + str(time.clock() - t0_clock))
    LOG.info("Seconds wall clock time: " + str(time.time() - t0_wall))

    viirs_sdr_proc.poll()

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
        end_time = message.data['end_time']
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
            rdr_filename = urlobj.path
            try:
                rdr_filename = fix_rdrfile(urlobj.path)
            except IOError:
                LOG.error('Failed to fix orbit number in RDR file = ' + str(urlobj.path))
                import traceback
                traceback.print_exc(file=sys.stderr)
            except AttributeError:
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
            LOG.info("Time used in sub-dir name: " + 
                     str(tobj.strftime("%Y-%m-%d %H:%M")))
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
            to_send['format'] = 'SDR'
            to_send['type'] = 'HDF5'
            to_send['start_time'] = start_time #start_time.isoformat()
            to_send['end_time'] = end_time
            message = Message('/oper/polar/direct_readout/norrkoping',
                          "file", to_send).encode()
            mypublisher.send(message)

            LOG.info("Now that SDR processing has completed, " + 
                     "check for new LUT files...")
            fresh = check_lut_files(THR_LUT_FILES_AGE_DAYS)
            if fresh:
                LOG.info("Files in the LUT dir are fresh...")
                LOG.info("...or download has been attempted recently! " + 
                         "No url downloading....")
            else:
                LOG.warning("Files in the LUT dir are non existent or old. " +
                            "Start url fetch...")
                update_lut_files()

    return


# ---------------------------------------------------------------------------
def npp_runner():
    """The NPP/VIIRS runner. Listens and triggers processing"""

    sdr_home = OPTIONS['level1_home']
    # Roll over log files at application start:
    try:
        LOG.handlers[0].doRollover()
    except AttributeError:
        LOG.warning("No log rotation supported for this handler...")
    LOG.info("*** Start the Suomi NPP SDR runner:")

    fresh = check_lut_files(THR_LUT_FILES_AGE_DAYS)
    if fresh:
        LOG.info("Files in the LUT dir are fresh...")
        LOG.info("...or download has been attempted recently! " + 
                 "No url downloading....")
    else:
        LOG.warning("Files in the LUT dir are non existent or old. " +
                    "Start url fetch...")
        update_lut_files()

    with posttroll.subscriber.Subscribe('RDR') as subscr:
        with Publish('npp_dr_runner', 'SDR', 
                     LEVEL1_PUBLISH_PORT) as publisher:        
            for msg in subscr.recv():
                start_npp_sdr_processing(sdr_home, publisher, msg)

    return

# ---------------------------------------------------------------------------
if __name__ == "__main__":

    npp_runner()

    #rdr_filename = "/san1/polar_in/direct_readout/npp/RNSCA-RVIRS_npp_d20121111_t0825276_e0837086_b05391_c20121111084036199000_nfts_drl.h5"
    #LOG.info("Start CSPP: RDR file = " + str(rdr_filename))
    #working_dir = run_cspp(rdr_filename)
    #LOG.info("CSPP SDR processing finished...")


    """
    # Testing:
    rdr_home_dir = OPTIONS['level0_home']
    sdr_home_dir = OPTIONS['level1_home']

    from glob import glob
    rdrlist = glob('%s/RNSCA-RVIRS_*' % rdr_home_dir)
    #rdr_filename = rdrlist[0]
    for rdr_filename in rdrlist:
        try:
            rdr_filename = fix_rdrfile(rdr_filename)
        except IOError:
            import traceback
            traceback.print_exc()

        wrkdir = run_cspp(rdr_filename)
        result_files = get_sdr_files(wrkdir)
        tobj = get_datetime_from_filename(rdr_filename)
        subd = create_subdirname(tobj)
        pack_sdr_files(result_files, sdr_home_dir, subd)
        make_okay_files(sdr_home_dir, subd)
        cleanup_cspp_workdir(wrkdir)
    """
