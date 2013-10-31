#
#
import os
from datetime import datetime
import glob
import re

from polar_preproc import LOG, get_npp_stamp
from polar_preproc.npp_granule import NPPGranule
from polar_preproc.instrument import get_instrument

# Removing creation time in filenames
_re_filename_replace = re.compile('_c\d+_')

def site_notify(work_dir, product_times):
    """ Get list of product files for a given granule (any h5 file is a product).
    Move files to outdir and write a json metadata to signaldir.
    """
    if not isinstance(product_times, (list, tuple)):
        product_times = [product_times]

    lv1dir = os.path.realpath(os.environ.get('NPP_LV1_DIR', '.'))

    for time in sorted(product_times):
        time = time.strftime('d%Y%m%d_t%H%M%S')
        files = glob.glob(os.path.join(work_dir, "*_%s*.h5" % time))
        if len(files) < 1:
            LOG.error('Found no H5 files for %r ' % time)
            continue

        lv1_files = []
        instrument = set()
        for fin in files:
            stamp = get_npp_stamp(fin)
            outdir = os.path.join(lv1dir, "%s_%05d"%(stamp.platform,
                                                     stamp.orbit_number))
            inst = get_instrument(fin)
            if inst:
                if instrument and (inst not in instrument):
                    LOG.warning("Mixing instruments, reading '%s' but expected '%s'" % (
                            inst, ', '.join(instrument)))
                instrument.add(inst)
                outdir = os.path.join(outdir, inst)
            if not os.path.isdir(outdir):
                os.makedirs(outdir)
            fout = os.path.join(outdir, _re_filename_replace.sub(
                    '_', os.path.basename(fin)))

            LOG.info("Moving %s to %s" % (fin, fout))
            correct_georef(fin)
            os.rename(fin, fout)
            lv1_files.append('file://' + fout)

        if lv1_files:
            stamp = get_npp_stamp(lv1_files[0])
            if instrument:
                inst=', '.join(instrument)
            else:
                inst = None
            grn = NPPGranule(stamp.platform,
                             stamp.start_time,
                             end_time=stamp.end_time,
                             orbit_number=stamp.orbit_number,
                             instrument=inst,
                             items=lv1_files)

            head = 'SDR'
            if len(instrument) == 1:
                head += '-%s'%instrument.pop()
            jsfile = os.path.join(lv1dir, 
                                  "%s_%s_%s_%s.json" % (head,
                                                        grn.stamp,
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
            'usage: python site_utils.py <data-dir> <time-stamp>'
    if _time_stamp[0] == 'd':
        _time_fmt = 'd%Y%m%d_t%H%M%S'
    else:
        _time_fmt = '%Y%m%d_%H%M%S'
    _time_stamp = datetime.strptime(_time_stamp, _time_fmt)
    site_notify(_datadir, _time_stamp)
