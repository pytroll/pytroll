#
#
import os
import sys
import re
import shutil
from subprocess import call
import glob

from npp import get_npp_stamp
from orbitno import check_and_replace_orbitno
from logger import LOG

RT_STPS_BATCH = "/usr/local/rt-stps/bin/batch.sh"
TEMPLATE_CONFIG_FILE = "/usr/local/rt-stps/config/npp.xml"

_NO_RENAMING = False

def _generate_stps_config_file(outdir='.'):
    _re_output_line = re.compile('\s*<rdr label="\w+" directory="[/a-z0-9]+" .*')
    _re_output_replace = re.compile(' directory="[/A-Za-z0-9]+" ')
    config_file = outdir + '/npp.xml'
    counter = 0
    with open(config_file, 'w') as fp_out:
        with open(TEMPLATE_CONFIG_FILE) as fp_in:
            for line in fp_in.readlines():
                if _re_output_line.match(line.lower()):
                    line, n =_re_output_replace.subn(' directory="%s" ' % 
                                                     outdir, line)
                    counter += n
                fp_out.write(line)
    if counter == 0:
        raise IOError("Generating config file '%s' failed" % config_file)
    LOG.info("Generated rt-stps config file '%s'" % config_file)
    return config_file

def _renaming(files, outdir='.'):
    # Renameing and moving
    _re_filename_replace = re.compile('_c\d+_')
    _files = []
    for f in files:
        fname = check_and_replace_orbitno(f)
        fname = _re_filename_replace.sub('_', os.path.basename(fname))
        fname = os.path.join(outdir, fname)
        LOG.info("Renaming %s to %s" % (f, fname))
        os.rename(f, fname) 
        _files.append(fname)
    return _files
    

def do_prod(filename, outdir='.', logfile=None):
    config_file = _generate_stps_config_file()
    if logfile:
        stderr = open(logfile, 'w')
    else:
        stderr = sys.stderr
    try:
        cmd = RT_STPS_BATCH + ' ' + config_file + ' ' + filename
        LOG.info("Running '%s'" % cmd)
        retcode = call(cmd, stdout=stderr, stderr=stderr, shell=True)
        if retcode != 0:
            if retcode < 0:
                text = "rt-stps was terminated by signal %d" % -retcode
            else:
                text = "rt-stps returned" % retcode
            raise OSError(text)
    finally:
        if stderr.name == logfile:
            stderr.close()

    files = sorted(glob.glob('./*.h5'))
    if _NO_RENAMING:
        return files
    return _renaming(files, outdir=outdir)

if __name__ == '__main__':
    import sys
    try:
        outdir = sys.argv[2]
    except:
        outdir = '.'
    do_prod(sys.argv[1], outdir=outdir)
