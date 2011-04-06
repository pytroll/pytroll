import sys
import os
from glob import glob
from datetime import datetime
import hashlib
import rpclite as rpc
from datex import logger, datetime_format, datex_config
from datex.config import DatexConfig

#-----------------------------------------------------------------------------
#
# Internal services
#
#-----------------------------------------------------------------------------
def _get_file_list(data_type, time_start=None, time_end=None):    
    if time_start is None:
        time_start = datetime.utcfromtimestamp(0)
    if time_end is None:
        time_end = datetime.utcnow()
        
    path, file_glob = datex_config.get_path(data_type)
    file_list = glob(os.path.join(path, file_glob))
    result = []
    for f in file_list:
        if not os.path.isfile(f):
            continue
        mtime = os.stat(f).st_mtime
        dt = datetime.utcfromtimestamp(mtime)        
        if time_start < dt < time_end:
            result.append((f, dt))

    result = sorted(result, lambda x,y: cmp(x[1], y[1]))
    return result

#-----------------------------------------------------------------------------
#
# Services
#
#-----------------------------------------------------------------------------
def get_file_list(data_type, time_start=None, time_end=None):    
    logger.info('... get_data_list(%s, %s, %s)'%(data_type, time_start, time_end))
    if time_start:
        time_start = datetime.strptime(time_start, datetime_format)
    if time_end:
        time_end = datetime.strptime(time_end, datetime_format)

    result = []
    for f, t in _get_file_list(data_type, time_start, time_end):
        f, t = os.path.basename(f), t.strftime(datetime_format)
        result.append((f, t))

    return result

def get_file(data_type, file_name):
    return get_file_chunk(data_type, file_name, 0, -1)

def get_file_chunk(data_type, file_name, offset, size):
    logger.info('... get_file_chunk(%s, %s, %d, %d)'%(data_type, file_name, offset, size))
    path = datex_config.get_path(data_type)[0]
    f = open(os.path.join(path, file_name))
    f.seek(offset)
    buf = f.read(size)
    f.close()
    return rpc.Binary(buf)

def get_file_md5(data_type, file_name):
    logger.info('... get_file_md5(%s, %s)', data_type, file_name)
    path = datex_config.get_path(data_type)[0]
    fp = open(os.path.join(path, file_name))
    m = hashlib.md5()
    while True:
        buf = fp.read(128)
        if not buf:
            break
        m.update(buf)
    fp.close()
    return m.hexdigest()    
