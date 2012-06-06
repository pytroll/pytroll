#
#
import os
from datetime import datetime
import glob
import re

from polar_preproc import LOG, get_npp_stamp
from polar_preproc.npp_granule import NPPGranule

_lv1_outdir = './.outdir.lv1'
_lv1_signaldir = './.signaldir.lv1'

# Removing creation time in filenames
_re_filename_replace = re.compile('_c\d+_')

def site_notify(work_dir, product_times, outdir=None, signaldir=None):
    """ Get list of product files for a given granule (any h5 file is a product).
    Move files to outdir and write a json metadata to signaldir.

    In the operational environment 'outdir' and 'signaldir' can be defined by
    symbolic links in the working directory'
    """
    # anything overwrite workdir symlinks.
    signaldir = signaldir or outdir

    if not isinstance(product_times, (list, tuple)):
        product_times = [product_times]

    if outdir == None and os.path.isdir(_lv1_outdir):
        outdir = _lv1_outdir
    else:
        outdir = '.'
    outdir = os.path.realpath(outdir)
    if signaldir == None and os.path.isdir(_lv1_signaldir):
        signaldir = _lv1_signaldir
    else:
        signaldir = '.'
    signaldir = os.path.realpath(signaldir)

    for time in sorted(product_times):
        time = time.strftime('d%Y%m%d_t%H%M%S')
        files = glob.glob(os.path.join(work_dir, "*_%s*.h5" % time))
        if len(files) < 1:
            LOG.error('Found no H5 files for %r ' % time)
            continue

        lv1_files = []
        for fin in files:
            fout = os.path.join(outdir, 
                                _re_filename_replace.sub('_', os.path.basename(fin)))
            LOG.info("Moving %s to %s" % (fin, fout))
            correct_georef(fin)
            os.rename(fin, fout)
            lv1_files.append('file://' + fout)

        if lv1_files and os.path.isdir(signaldir):
            stamp = get_npp_stamp(lv1_files[0])
            grn = NPPGranule(stamp.platform,
                             stamp.start_time,
                             end_time=stamp.end_time,
                             orbit_number=stamp.orbit_number,
                             items=lv1_files)
            jsfile = os.path.join(signaldir, 
                                  "SDR_%s_%s_%s.json" % (grn.stamp,
                                                         grn.site,
                                                         grn.domain))
            LOG.info("Writing %s", jsfile)
            grn.dump(jsfile)

def correct_georef(filename):
    """ Creation data are removed from all file names. This is also needed for 
    the GEO_Ref file attribute.
    """
    import h5py
    georef_key = 'N_GEO_Ref'
    fp = h5py.File(filename, 'r+')
    try:
        if georef_key in fp.attrs.keys():
            fdir, fname = os.path.split(fp.attrs[georef_key][0][0])
            fname = _re_filename_replace.sub('_', fname)
            LOG.info("Replacing GEO_Ref with '%s'" % fname)
            fp.attrs.modify(georef_key, [[os.path.join(fdir, fname)]])
    finally:
        fp.close()

if __name__ == '__main__':
    import sys
    try:
        _datadir = sys.argv[1]
        _time_stamp = sys.argv[2]
    except IndexError:
        print >> sys.stderr, \
            'usage: python site_utils.py <data-dir> <time-stamp> [<out-dir>]'
    try:
        _outdir = sys.argv[3]
    except IndexError:
        _outdir = '.'

    if _time_stamp[0] == 'd':
        _time_fmt = 'd%Y%m%d_t%H%M%S'
    else:
        _time_fmt = '%Y%m%d_%H%M%S'
    _time_stamp = datetime.strptime(_time_stamp, _time_fmt)
    notify(_datadir, _time_stamp, outdir=_outdir)
