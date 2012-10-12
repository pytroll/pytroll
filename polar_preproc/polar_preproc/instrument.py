#
from polar_preproc import LOG

def get_instrument(filename, shortname=True):
    import h5py
    h5 = h5py.File(filename, 'r')
    try:
        try:
            inst = list(h5['Data_Products'])[0]
            if shortname:
                inst = inst.split('-')[0]
            return inst.upper()
        except (KeyError, IndexError):
            LOG.warning("Could not determine instrument using 'Data_Products' group")
    finally:
        h5.close()

if __name__ == '__main__':
    import sys
    print get_instrument(sys.argv[1])
