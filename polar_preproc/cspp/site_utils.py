#
#
import os
from datetime import datetime
import glob
import re

from npp import LOG, get_npp_stamp
import npp.sdr_granule as npp_grn

"""
def start_passage(work_dir, satname, orbit):
    pass
    
def end_passage(work_dir, satname, orbit):
    pass
"""

# Removing creation time in filenames
_re_filename_replace = re.compile('_c\d+_')

def notify(work_dir, product_times, out_dir='.', signal=''):
    """ Get list of product files for a give granule (any h5 file is a product).
    Move files to out_dir.
    Write metadata to a json file.
    """
    signal = signal or out_dir

    if not isinstance(product_times, (list, tuple)):
        product_times = [product_times]

    for time in sorted(product_times):
        time = time.strftime('d%Y%m%d_t%H%M%S')
        files = glob.glob(os.path.join(work_dir, "*_%s*.h5" % time))
        if len(files) < 1:
            LOG.error('Found no H5 files for %r ' % time)
            continue

        lv1_files = []
        for fin in files:
            fout = os.path.join(out_dir, 
                                _re_filename_replace.sub('_', os.path.basename(fin)))
            LOG.info("Moving %s to %s" % (fin, fout))
            os.rename(fin, fout)
            lv1_files.append(os.path.basename(fout))

        stamp = get_npp_stamp(lv1_files[0])
        grn = npp_grn.SDRGranule(stamp.satname, stamp.start_time,
                                 end_time=stamp.end_time, orbit=stamp.orbit,
                                 path=out_dir, items=lv1_files)

        if os.path.isdir(signal):
            jsfile = os.path.join(signal, 
                                  "SDR_%s_%s_%s.json" % (grn.stamp,
                                                         grn.site,
                                                         grn.domain))
            LOG.info("Writing %s", jsfile)
            grn.dump(jsfile)

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
    notify(_datadir, _time_stamp, out_dir=_outdir)
