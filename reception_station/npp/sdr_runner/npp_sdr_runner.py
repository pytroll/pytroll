#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2013 Adam.Dybbroe

# Author(s):

#   Adam.Dybbroe <a000680@c14526.ad.smhi.se>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Level-1 processing for VIIRS Suomi NPP Direct Readout data. Using the CSPP
level-1 processor from the SSEC, Wisconsin, based on the ADL from the NASA DRL.
Listen for pytroll messages from Nimbus (NPP file dispatch) and trigger
processing on direct readout RDR data (granules or full swaths)
"""


import os
from glob import glob
from datetime import datetime, timedelta

import sdr_runner
import sdr_runner.orbitno
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
    import stat

    now = datetime.utcnow()

    tdelta = timedelta(seconds=float(URL_DOWNLOAD_TRIAL_FREQUENCY_HOURS)*3600.)
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
        return True

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
        return
    else:
        fpt.close()

    LOG.info("LUTs downloaded. LUT-update timestamp file = " + filename)

    return

# ---------------------------------------------------------------------------
def run_cspp(*viirs_rdr_files):
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
    cmdlist = [viirs_sdr_call]
    cmdlist.extend(viirs_rdr_files)
    t0_clock = time.clock()
    t0_wall = time.time()
    LOG.info("Popen call arguments: " + str(cmdlist))
    viirs_sdr_proc = Popen(cmdlist,
                           cwd=working_dir,
                           stderr=PIPE, stdout=PIPE)
    while True:
        line = viirs_sdr_proc.stdout.readline()
        if not line:
            break
        LOG.info(line.strip('\n'))

    while True:
        errline = viirs_sdr_proc.stderr.readline()
        if not errline:
            break
        LOG.info(errline.strip('\n'))
    LOG.info("Seconds process time: " + str(time.clock() - t0_clock))
    LOG.info("Seconds wall clock time: " + str(time.time() - t0_wall))

    viirs_sdr_proc.poll()
    return working_dir

def get_sdr_times(filename):
    """Get the start and end times from the SDR file name
    """
    bname = os.path.basename(filename)
    sll = bname.split('_')
    start_time = datetime.strptime(sll[2] + sll[3][:-1], 
                                   "d%Y%m%dt%H%M%S")
    end_time = datetime.strptime(sll[2] + sll[4][:-1], 
                                 "d%Y%m%de%H%M%S")
    if end_time < start_time:
        end_time += timedelta(days=1)
    
    return start_time, end_time

def publish_sdr(publisher, result_files):
    """Publish the messages that SDR files are ready
    """
    # Now publish:
    for result_file in result_files:
        filename = os.path.split(result_file)[1]
        to_send = {}
        to_send['uri'] = ('ssh://%s/%s' % (SERVERNAME, result_file))
        to_send['filename'] = filename
        to_send['instrument'] = 'viirs'
        to_send['satellite'] = 'NPP'
        to_send['format'] = 'HDF5'
        to_send['type'] = 'SDR'
        
        to_send['start_time'], to_send['end_time'] = get_sdr_times(filename)
        msg = Message('/oper/polar/direct_readout/norrkoping',
                      "file", to_send).encode()
        LOG.debug("sending: " + str(msg))
        publisher.send(msg)

def spawn_cspp(current_granule, *glist):
    """Spawn a CSPP run on the set of RDR files given"""

    LOG.info("Start CSPP: RDR files = " + str(glist))
    working_dir = run_cspp(*glist)
    LOG.info("CSPP SDR processing finished...")
    # Assume everything has gone well!
    new_result_files = get_sdr_files(working_dir)
    if len(new_result_files) == 0:
        LOG.warning("No SDR files available. CSPP probably failed!")
        return working_dir, []

    LOG.info("current_granule = " + str(current_granule))
    LOG.info("glist = " + str(glist))
    if current_granule in glist and len(glist) == 1:
        LOG.info("Current granule is identical to the 'list of granules'" + 
                 " No sdr result files will be skipped")
        return working_dir, new_result_files
        
    # Only bother about the "current granule" - skip the rest
    start_time = get_datetime_from_filename(current_granule)
    start_str = start_time.strftime("d%Y%m%d_t%H%M%S")
    result_files = [new_file
                    for new_file in new_result_files
                    if start_str in new_file]
    
    return working_dir, result_files


class ViirsSdrProcessor(object):
    """
    Container for the VIIRS SDR processing based on CSPP

    """

    def __init__(self, ncpus):
        from multiprocessing.pool import ThreadPool
        self.pool = ThreadPool(ncpus)
        self.ncpus = ncpus

        self.orbit = 1 # Initialised orbit number
        self.fullswath = False
        self.cspp_results = []
        self.working_dirs = []
        self.glist = []
        self.pass_start_time = None
        self.result_files = []
        self.sdr_home = OPTIONS['level1_home']

    def initialise(self):
        """Initialise the processor"""
        self.fullswath = False
        self.cspp_results = []
        self.working_dirs = []
        self.glist = []
        self.pass_start_time = None
        self.result_files = []

    def pack_sdr_files(self, subd):
        return pack_sdr_files(self.result_files, self.sdr_home, subd)


    def run(self, msg):
        """Start the VIIRS SDR processing using CSPP on one rdr granule"""
        
        LOG.debug("Received message: " + str(msg))
        if self.glist and len(self.glist) > 0:
            LOG.debug("glist: " + str(self.glist))

        if msg is None and self.glist and len(self.glist) > 2:
            # The swath is assumed to be finished now
            del self.glist[0]
            keeper = self.glist[1]
            LOG.info("Start CSPP: RDR files = " + str(self.glist))
            self.cspp_results.append(self.pool.apply_async(spawn_cspp, 
                                                           [keeper] + self.glist))
            return False
        elif msg and not (msg.data['satellite'] == "NPP" and 
                          msg.data['instrument'] == 'viirs'):
            LOG.info("Not a Suomi NPP VIIRS scene. Continue...")
            return True
        elif msg is None:
            return True

        LOG.debug("")
        LOG.debug("\tMessage:")
        LOG.debug(str(msg))
        urlobj = urlparse(msg.data['uri'])
        LOG.debug("Server = " + str(urlobj.netloc))
        if urlobj.netloc != SERVERNAME:
            LOG.warning("Server %s not the current one: %s" %(str(urlobj.netloc), 
                                                              SERVERNAME))
            return True
        LOG.info("Ok... " + str(urlobj.netloc))
        LOG.info("Sat and Instrument: " + str(msg.data['satellite']) 
                 + " " + str(msg.data['instrument']))
                    
        start_time = msg.data['start_time']
        try:
            end_time = msg.data['end_time']
        except KeyError:
            LOG.warning("No end_time in message! Guessing start_time + 86 seconds...")
            end_time = msg.data['start_time'] + timedelta(seconds=86)
        try:
            orbnum = int(msg.data['orbit_number'])
        except KeyError:
            LOG.warning("No orbit_number on message! Set to none...")
            orbnum = None

        rdr_filename = urlobj.path
        path, fname =  os.path.split(rdr_filename)
        if not fname.endswith('.h5'):
            LOG.warning("Not an rdr file! Continue")
            return True

        # Check if the file exists:
        if not os.path.exists(rdr_filename):
            raise IOError("File is reported to be dispatched " + 
                          "but is not there! File = " + 
                          rdr_filename)

        # Do processing:
        LOG.info("RDR to SDR processing on npp/viirs with CSPP start!" + 
                 " Start time = " + str(start_time))
        if orbnum:
            LOG.info("Orb = %d" % orbnum)
            self.orbit = orbnum

        LOG.info("File = %s" % str(rdr_filename))

        # Fix orbit number in RDR file:
        LOG.info("Fix orbit number in rdr file...")
        try:
            rdr_filename = fix_rdrfile(rdr_filename)
        except IOError:
            LOG.error('Failed to fix orbit number in RDR file = ' + 
                      str(urlobj.path))
            import traceback
            traceback.print_exc(file=sys.stderr)
        except sdr_runner.orbitno.NoTleFile:
            LOG.error('Failed to fix orbit number in RDR file = ' + 
                      str(urlobj.path))
            LOG.error('No TLE file...')
            import traceback
            traceback.print_exc(file=sys.stderr)

        self.glist.append(rdr_filename)

        if len(self.glist) > 4:
            raise RuntimeError("Invalid number of granules to "
                               "process!!!")
        if len(self.glist) == 4:
            del self.glist[0]
        if len(self.glist) == 3:
            keeper = self.glist[1]
        if len(self.glist) == 2:
            keeper = self.glist[0]
        if len(self.glist) == 1:
            # Check start and end time and check if the RDR file
            # contains several granules (a full local swath):
            tdiff = end_time - start_time
            if tdiff.seconds > 4*60:
                LOG.info("RDR file contains 3 or more granules. " + 
                         "We assume it is a full local swath!")
                keeper = self.glist[0]
                self.fullswath = True
            else:
                LOG.info("Only one granule. This is not enough for CSPP" + 
                         " Continue")
                return True

        start_time = get_datetime_from_filename(keeper)
        if self.pass_start_time is None:
            self.pass_start_time = start_time

        LOG.info("Before call to spawn_cspp. Argument list = " + 
                 str([keeper] + self.glist))
        self.cspp_results.append(self.pool.apply_async(spawn_cspp, 
                                                       [keeper] + self.glist))
        if self.fullswath:
            LOG.info("Full swath. Break granules loop")
            return False

        return True

# ---------------------------------------------------------------------------
def npp_rolling_runner():
    """The NPP/VIIRS runner. Listens and triggers processing on RDR granules."""
    from multiprocessing import cpu_count

    # Roll over log files at application start:
    try:
        LOG.handlers[0].doRollover()
    except AttributeError:
        LOG.warning("No log rotation supported for this handler...")
    LOG.info("*** Start the Suomi NPP SDR runner:")
    LOG.info("THR_LUT_FILES_AGE_DAYS = " + str(THR_LUT_FILES_AGE_DAYS))

    fresh = check_lut_files(THR_LUT_FILES_AGE_DAYS)
    if fresh:
        LOG.info("Files in the LUT dir are fresh...")
        LOG.info("...or download has been attempted recently! " + 
                 "No url downloading....")
    else:
        LOG.warning("Files in the LUT dir are non existent or old. " +
                    "Start url fetch...")
        update_lut_files()


    ncpus_available = cpu_count()
    LOG.info("Number of CPUs available = " + str(ncpus_available))
    ncpus = int(OPTIONS.get('ncpus', 1))
    LOG.info("Will use %d CPUs when running CSPP instances" % ncpus)
    viirs_proc = ViirsSdrProcessor(ncpus)

    with posttroll.subscriber.Subscribe('RDR') as subscr:
        with Publish('npp_dr_runner', 'SDR', 
                     LEVEL1_PUBLISH_PORT) as publisher:
            while True:
                viirs_proc.initialise()
                for msg in subscr.recv(timeout=90):
                    status = viirs_proc.run(msg)
                    if not status:
                        break # end the loop and reinitialize !
                        
                LOG.info("Get the results from the multiptocessing pool-run")
                for res in viirs_proc.cspp_results:
                    working_dir, tmp_result_files = res.get()
                    viirs_proc.working_dirs.append(working_dir)
                    viirs_proc.result_files.extend(tmp_result_files)

                tobj = viirs_proc.pass_start_time
                LOG.info("Time used in sub-dir name: " + 
                         str(tobj.strftime("%Y-%m-%d %H:%M")))
                subd = create_subdirname(tobj, orbit=viirs_proc.orbit)
                LOG.info("Create sub-directory for sdr files: %s" % str(subd))
                sdr_files = viirs_proc.pack_sdr_files(subd)
                make_okay_files(viirs_proc.sdr_home, subd)

                publish_sdr(publisher, sdr_files)
                
                for working_dir in viirs_proc.working_dirs:
                    LOG.info("Cleaning up directory %s" % working_dir)
                    cleanup_cspp_workdir(working_dir)

                LOG.info("Now that SDR processing has completed, " + 
                         "check for new LUT files...")
                fresh = check_lut_files(THR_LUT_FILES_AGE_DAYS)
                if fresh:
                    LOG.info("Files in the LUT dir are fresh...")
                    LOG.info("...or download has been attempted recently! " + 
                             "No url downloading....")
                else:
                    LOG.warning("Files in the LUT dir are " + 
                                "non existent or old. " +
                                "Start url fetch...")
                    update_lut_files()

    return

# ---------------------------------------------------------------------------
if __name__ == "__main__":

    npp_rolling_runner()
