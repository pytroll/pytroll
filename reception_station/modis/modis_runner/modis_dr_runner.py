"""Level-1 processing for Terra/Aqua Modis Direct Readout data. Using the SPA
modis level-1 processor from the NASA Direct Readout Lab (DRL). Listens for
pytroll messages from the Nimbus server (PDS file dispatch) and triggers
processing on direct readout data
"""


import os, glob

SPA_HOME = os.environ.get("SPA_HOME", '')
APPL_HOME = os.environ.get('MODIS_LVL1PROC', '')
ETC_DIR = "%s/etc" % SPA_HOME

import ConfigParser
CONFIG_PATH = os.environ.get('MODIS_LVL1PROC_CONFIG_DIR', '')
print "CONFIG_PATH: ", CONFIG_PATH 

CONF = ConfigParser.ConfigParser()
CONF.read(os.path.join(CONFIG_PATH, "modis_dr_config.cfg"))

MODE = os.getenv("SMHI_MODE")
if MODE is None:
    MODE = "offline"

OPTIONS = {}
for option, value in CONF.items(MODE, raw = True):
    OPTIONS[option] = value
 
from datetime import datetime


LEVEL1_PUBLISH_PORT = 9010

packetfile_aqua_prfx = "P154095715409581540959"
modisfile_aqua_prfx = "P1540064AAAAAAAAAAAAAA"
modisfile_terra_prfx = "P0420064AAAAAAAAAAAAAA"

servername = "safe.smhi.se"

from urlparse import urlparse
import posttroll.subscriber
from posttroll.publisher import Publish
from posttroll.message import Message

# ---------------------------------------------------------------------------
def run_terra_l0l1(pdsfile):
    """Process Terra MODIS level 0 PDS data to level 1a/1b"""

    working_dir = OPTIONS['working_dir']
    # Change working directory:
    if not os.path.exists(working_dir):
        try:
            os.makedirs(working_dir)
        except OSError:
            print "Failed creating working directory %s" % working_dir
            working_dir = '/tmp'
            print "Will use /tmp"

    fdwork = os.open(working_dir, os.O_RDONLY)        
    os.fchdir(fdwork)

    level1b_home = OPTIONS['level1b_home']
    filetype_terra = OPTIONS['filetype_terra']
    geofile_terra = OPTIONS['geofile_terra']
    level1a_terra = OPTIONS['level1a_terra']
    level1b_terra = OPTIONS['level1b_terra']
    level1b_250m_terra = OPTIONS['level1b_250m_terra']
    level1b_500m_terra = OPTIONS['level1b_500m_terra']

    # Get the observation time from the filename as a datetime object:
    bname = os.path.basename(pdsfile)
    obstime = datetime.strptime(bname, filetype_terra)

    # level1_home
    proctime = datetime.now()
    lastpart = proctime.strftime("%Y%j%H%M%S.hdf")
    firstpart = obstime.strftime(level1b_terra)
    mod021km_file = "%s/%s_%s" % (level1b_home, firstpart, lastpart)
    firstpart = obstime.strftime(level1b_250m_terra)
    mod02qkm_file = "%s/%s_%s" % (level1b_home, firstpart, lastpart)
    firstpart = obstime.strftime(level1b_500m_terra)
    mod02hkm_file = "%s/%s_%s" % (level1b_home, firstpart, lastpart)

    retv = {'mod021km_file': mod021km_file,
            'mod02hkm_file': mod02hkm_file,
            'mod02qkm_file': mod02qkm_file,
            'level1a_file': level1a_terra}

    #proctime = datetime.now()
    lastpart = proctime.strftime("%Y%j%H%M%S.hdf")
    firstpart = obstime.strftime(level1a_terra)
    mod01files = glob.glob("%s/%s*hdf" % (level1b_home, firstpart))
    if len(mod01files) > 0:
        print("Level 1 file already exists: %s" % mod01files[0])
        return retv
        
    mod01_file = "%s/%s_%s" % (level1b_home, firstpart, lastpart)
    firstpart = obstime.strftime(geofile_terra)
    mod03_file = "%s/%s_%s" % (level1b_home, firstpart, lastpart)

    print "Level-1 filename: ",mod01_file
    satellite = "Terra"
    wrapper_home = os.path.join(SPA_HOME, "/modisl1db/wrapper/l0tol1")
    cmdstr = ("%s/run modis.pds %s sat %s modis.mxd01 %s modis.mxd03 %s" % 
              (wrapper_home, pdsfile, satellite, mod01_file, mod03_file))
    # Run the command:
    #subprocess.check_call(cmdstr)
    os.system(cmdstr)

    # Now do the level1a-1b processing:
    lut_home = os.path.join(SPA_HOME, "/modisl1db/algorithm/data/modist/cal")
    refl_lut = os.path.join(lut_home, "MOD02_Reflective_LUTs.V6.1.6.0_OC.hdf")
    emiss_lut = os.path.join(lut_home, "MOD02_Emissive_LUTs.V6.1.6.0_OC.hdf")
    qa_lut = os.path.join(lut_home, "MOD02_QA_LUTs.V6.1.6.0_OC.hdf")

    wrapper_home = os.path.join(SPA_HOME, "/modisl1db/wrapper/l1atob")
    cmdstr = ("%s/run modis.mxd01 %s modis.mxd03 %s modis_reflective_luts %s modis_emissive_luts %s modis_qa_luts %s modis.mxd021km %s modis.mxd02hkm %s modis.mxd02qkm %s" %
              (wrapper_home, mod01_file, mod03_file,
               refl_lut, emiss_lut, qa_lut, mod021km_file, mod02hkm_file, mod02qkm_file))
    # Run the command:
    os.system(cmdstr)

    # Close working directory:
    os.close(fdwork)

    return retv

# ---------------------------------------------------------------------------
def run_aqua_gbad(obs_time):
    """Run the gbad for aqua"""

    level0_home = OPTIONS['level0_home']
    packetfile = os.path.join(level0_home, 
                              obs_time.strftime(OPTIONS['packetfile_aqua']))

    att_dir = OPTIONS['attitude_home']
    eph_dir = OPTIONS['ephemeris_home']
    spa_config_file = OPTIONS['spa_config_file']
    att_file = os.path.basename(packetfile).split('.PDS')[0] + '.att'
    att_file = os.path.join(att_dir, att_file)
    eph_file = os.path.basename(packetfile).split('.PDS')[0] + '.eph'
    eph_file = os.path.join(eph_dir, eph_file)
    print "eph-file = ",eph_file

    wrapper_home = SPA_HOME + "/gbad/wrapper/gbad"
    cmdstr = ("%s/run aqua.gbad.pds %s aqua.gbad_att %s aqua.gbad_eph %s configurationfile %s" %
              (wrapper_home, packetfile, att_file, eph_file, spa_config_file))
    print "Command: ", cmdstr
    # Run the command:
    os.system(cmdstr)

    return att_file, eph_file

# ---------------------------------------------------------------------------
def run_aqua_l0l1(pdsfile):
    """Process Aqua MODIS level 0 PDS data to level 1a/1b"""
    import os

    working_dir = OPTIONS['working_dir']
    if not os.path.exists(working_dir):
        try:
            os.makedirs(working_dir)
        except OSError:
            print "Failed creating working directory %s" % working_dir
            working_dir = '/tmp'
            print "Will use /tmp"

    # Change working directory:
    fdwork = os.open(working_dir, os.O_RDONLY)
    os.fchdir(fdwork)

    #ephemeris_home = OPTIONS['ephemeris_home']
    #attitude_home = OPTIONS['attitude_home']
    level1b_home = OPTIONS['level1b_home']
    filetype_aqua = OPTIONS['filetype_aqua']
    geofile_aqua = OPTIONS['geofile_aqua']
    level1a_aqua = OPTIONS['level1a_aqua']
    level1b_aqua = OPTIONS['level1b_aqua']
    level1b_250m_aqua = OPTIONS['level1b_250m_aqua']
    level1b_500m_aqua = OPTIONS['level1b_500m_aqua']

    # Get the observation time from the filename as a datetime object:
    bname = os.path.basename(pdsfile)
    obstime = datetime.strptime(bname, filetype_aqua)

    # Get ephemeris and attitude names! FIXME!
    attitude, ephemeris = run_aqua_gbad(obstime)
    #ephemeris = "%s/P15409571540958154095911343000923001.eph" % ephemeris_home 
    #attitude  = "%s/P15409571540958154095911343000923001.att" % attitude_home
    
    leapsec_name = os.path.join(ETC_DIR, "leapsec.dat")
    utcpole_name = os.path.join(ETC_DIR, "utcpole.dat")
    geocheck_threshold = 50 # Hardcoded threshold!


    proctime = datetime.now()
    lastpart = proctime.strftime("%Y%j%H%M%S.hdf")
    firstpart = obstime.strftime(level1a_aqua)
    mod01files = glob.glob("%s/%s*hdf" % (level1b_home, firstpart))
    if len(mod01files) > 0:
        print("Level 1 file already exists: %s" % mod01files[0])
        return
        
    mod01_file = "%s/%s_%s" % (level1b_home, firstpart, lastpart)
    firstpart = obstime.strftime(geofile_aqua)
    mod03_file = "%s/%s_%s" % (level1b_home, firstpart, lastpart)

    print "Level-1 filename: ", mod01_file        
    satellite = "Aqua"
    wrapper_home = os.path.join(SPA_HOME, "modisl1db/wrapper/l0tol1")
    cmdstr = ("%s/run modis.pds %s sat %s modis.mxd01 %s modis.mxd03 %s gbad_eph %s gbad_att %s leapsec %s utcpole %s geocheck_threshold %s" % 
              (wrapper_home, pdsfile, satellite, mod01_file, mod03_file,
               ephemeris, attitude, leapsec_name, utcpole_name, geocheck_threshold))
    # Run the command:
    os.system(cmdstr)


    # Now do the level1a-1b processing:
    lut_home = os.path.join(SPA_HOME, "/modisl1db/algorithm/data/modisa/cal")
    refl_lut = os.path.join(lut_home, "MYD02_Reflective_LUTs.V6.1.7.1_OCb.hdf")
    emiss_lut = os.path.join(lut_home, "MYD02_Emissive_LUTs.V6.1.7.1_OCb.hdf")
    qa_lut = os.path.join(lut_home, "MYD02_QA_LUTs.V6.1.7.1_OCb.hdf")

    wrapper_home = SPA_HOME + "/modisl1db/wrapper/l1atob"
    # level1_home
    proctime = datetime.now()
    lastpart = proctime.strftime("%Y%j%H%M%S.hdf")
    firstpart = obstime.strftime(level1b_aqua)
    mod021km_file = "%s/%s_%s" % (level1b_home, firstpart, lastpart)
    firstpart = obstime.strftime(level1b_250m_aqua)
    mod02qkm_file = "%s/%s_%s" % (level1b_home, firstpart, lastpart)
    firstpart = obstime.strftime(level1b_500m_aqua)
    mod02hkm_file = "%s/%s_%s" % (level1b_home, firstpart, lastpart)
    cmdstr = ("%s/run modis.mxd01 %s modis.mxd03 %s modis_reflective_luts %s modis_emissive_luts %s modis_qa_luts %s modis.mxd021km %s modis.mxd02hkm %s modis.mxd02qkm %s" %
              (wrapper_home, mod01_file, mod03_file,
               refl_lut, emiss_lut, qa_lut, mod021km_file, mod02hkm_file, mod02qkm_file))
    # Run the command:
    os.system(cmdstr)

    # Close working directory:
    os.close(fdwork)

    return mod021km_file

# ---------------------------------------------------------------------------
def start_modis_lvl1_processing(level1b_home, aqua_files,
                                mypublisher, message):
    """From a posttroll message start the modis lvl1 processing"""

    print ""
    print "Aqua files: ", aqua_files
    print "\tMessage:"
    print message
    urlobj = urlparse(message.data['uri'])
    print "Server = ", urlobj.netloc
    if urlobj.netloc != servername:
        return aqua_files
    print "Ok... ", urlobj.netloc
    print "Sat and Instrument: ", message.data['satellite'], message.data['instrument']

    to_send = {}

    if 'start_time' in message.data:
        start_time = message.data['start_time']
    else:
        start_time = None

    if (message.data['satellite'] == "TERRA" and 
        message.data['instrument'] == 'modis'):
        try:
            orbnum = int(message.data['orbit_number'])            
        except KeyError:
            orbnum = None

        path, fname =  os.path.split(urlobj.path)
        if fname.find(modisfile_terra_prfx) == 0 and fname.endswith('001.PDS'):
            # Check if the file exists:
            if not os.path.exists(urlobj.path):
                raise IOError("File is reported to be dispatched " + 
                              "but is not there! File = " + 
                              urlobj.path)

            # Do processing:
            print("Level-0 to lvl1 processing on terra start!" + 
                  " Start time = ", start_time)
            if orbnum:
                print "Orb = %d" % orbnum
            print "File = ", urlobj.path
            result_files = run_terra_l0l1(urlobj.path)
            # Assume everything has gone well! 
            # Add intelligence to run-function. FIXME!
            # Now publish:
            filename = result_files['level1a_file']
            to_send['uri'] = ('ssh://safe.smhi.se/' +  
                              os.path.join(level1b_home, 
                                               filename))
            to_send['filename'] = filename
            to_send['instrument'] = 'modis'
            to_send['satellite'] = 'TERRA'
            to_send['format'] = 'EOS'
            to_send['level'] = '1'
            to_send['type'] = 'HDF4'
            to_send['start_time'] = start_time


    elif (message.data['satellite'] == "AQUA" and 
          (message.data['instrument'] == 'modis' or 
           message.data['instrument'] == '0957')):
        try:
            orbnum = int(message.data['orbit_number'])            
        except KeyError:
            orbnum = None

        if orbnum:
            scene_id = orbnum
        else:
            if start_time:
                scene_id = start_time.strftime('%Y%m%d%H%M')
            else:
                print "No start time!!!"
                return aqua_files

        path, fname =  os.path.split(urlobj.path)
        if ((fname.find(modisfile_aqua_prfx) == 0 or 
             fname.find(packetfile_aqua_prfx) == 0) and 
            fname.endswith('001.PDS')):
            # Check if the file exists:
            if not os.path.exists(urlobj.path):
                raise IOError("File is reported to be dispatched " + 
                              "but is not there! File = " + 
                              urlobj.path)

            if not scene_id in aqua_files:
                aqua_files[scene_id] = []
            if len(aqua_files[scene_id]) == 0:
                aqua_files[scene_id] = [urlobj.path]
            else:
                if not urlobj.path in aqua_files[scene_id]:
                    aqua_files[scene_id].append(urlobj.path)

        if scene_id in aqua_files and len(aqua_files[scene_id]) == 2:
            print("aqua files with scene-id = %r :" % scene_id + 
                  str(aqua_files[scene_id]))
            aquanames = [ os.path.basename(s) for s in aqua_files[scene_id] ]

            lvl1filename = None
            if (aquanames[0].find(modisfile_aqua_prfx) == 0 and 
                aquanames[1].find(packetfile_aqua_prfx) == 0):
                # Do processing:
                print "Level-0 to lvl1 processing on aqua start! Scene = %r" % scene_id
                print "File = ", aqua_files[scene_id][0]
                lvl1filename = run_aqua_l0l1(aqua_files[scene_id][0])
                # Clean register: aqua_files dict
                aqua_files[scene_id] = []
            elif (aquanames[1].find(modisfile_aqua_prfx) == 0 and 
                  aquanames[0].find(packetfile_aqua_prfx) == 0):
                # Do processing:
                print "Level-0 to lvl1 processing on aqua start! Scene = %r" % scene_id
                print "File = ", aqua_files[scene_id][1]
                lvl1filename = run_aqua_l0l1(aqua_files[scene_id][1])
                # Clean register: aqua_files dict
                aqua_files[scene_id] = []
            else:
                print "Should not come here...???"

            # Now publish:
            filename = lvl1filename
            to_send = {}
            to_send['uri'] = ('ssh://safe.smhi.se/' +  
                              os.path.join(level1b_home, 
                                           filename))
            to_send['filename'] = filename
            to_send['instrument'] = 'modis'
            to_send['satellite'] = 'AQUA'
            to_send['format'] = 'EOS'
            to_send['level'] = '1'
            to_send['type'] = 'HDF4'
            to_send['start_time'] = start_time

    else:
        return aqua_files


    message = Message('/oper/polar/direct_readout/norrkoping',
                      "file", to_send).encode()
    mypublisher.send(message)

    return aqua_files

# ---------------------------------------------------------------------------
def modis_runner():
    """Listens and triggers processing"""

    lvl1b_home = OPTIONS['level1b_home']

    with posttroll.subscriber.Subscribe('PDS') as subscr:
        with Publish('modis_dr_runner', 'EOS 1', 
                     LEVEL1_PUBLISH_PORT) as publisher:        
            aquafiles = {}
            for msg in subscr.recv():
                aquafiles = start_modis_lvl1_processing(lvl1b_home, 
                                                        aquafiles,
                                                        publisher, msg)

    return

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    modis_runner()
