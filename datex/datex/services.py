#
# Copyright (c) 2009.
#
# DMI
# Lyngbyvej 100
# DK-2100 Copenhagen
# Denmark
#
# Author(s): 
#   Lars Orum Rasmussen
#   Martin Raspaud

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
"""services.py, used by datex_server.

   Implemented services.
"""
import os
from glob import glob
from datetime import datetime
import hashlib
import rpclite as rpc
from datex import logger, datetime_format, datex_config

#-----------------------------------------------------------------------------
#
# Internal services
#
#-----------------------------------------------------------------------------
def _get_file_list(data_type, time_start=None, time_end=None):    
    """Return a list of files for give datatype and time interval (internal).
    """
    if time_start is None:
        time_start = datetime.utcfromtimestamp(0)
    if time_end is None:
        time_end = datetime.utcnow()
        
    path, file_glob = datex_config.get_path(data_type)
    file_list = glob(os.path.join(path, file_glob))
    result = []
    for fname in file_list:
        if not os.path.isfile(fname):
            continue
        ftime = datetime.utcfromtimestamp(os.stat(fname).st_mtime)
        if time_start < ftime < time_end:
            result.append((fname, ftime))

    result = sorted(result, lambda x, y: cmp(x[1], y[1]))
    return result

#-----------------------------------------------------------------------------
#
# Exported services
#
#-----------------------------------------------------------------------------
def get_datatype_list():
    """Return a list of available data types.
    """
    logger.info('... get_datatype_list')
    return sorted(datex_config.get_datatypes())

def get_file_list(data_type, time_start=None, time_end=None):    
    """Return a list of files for give datatype and time interval.
    """
    logger.info('... get_file_list(%s, %s, %s)'%(data_type, time_start,
                                                 time_end))
    if time_start:
        time_start = datetime.strptime(time_start, datetime_format)
    if time_end:
        time_end = datetime.strptime(time_end, datetime_format)

    result = []
    for fname, ftime in _get_file_list(data_type, time_start, time_end):
        fname, ftime = os.path.basename(fname), ftime.strftime(datetime_format)
        result.append((fname, ftime))

    return result

def get_file(data_type, file_name):
    """Return given file.
    """
    return get_file_chunk(data_type, file_name, 0, -1)

def get_file_chunk(data_type, file_name, offset, size):
    """Return a chunk of given file.
    """
    logger.info('... get_file_chunk(%s, %s, %d, %d)'%(data_type, file_name,
                                                      offset, size))
    path = datex_config.get_path(data_type)[0]
    fob = open(os.path.join(path, file_name))
    fob.seek(offset)
    buf = fob.read(size)
    fob.close()
    return rpc.Binary(buf)

def get_file_md5(data_type, file_name):
    """Calculate md5 of a given file and return it.
    """
    logger.info('... get_file_md5(%s, %s)', data_type, file_name)
    path = datex_config.get_path(data_type)[0]
    fob = open(os.path.join(path, file_name))
    md5 = hashlib.md5()
    while True:
        buf = fob.read(128)
        if not buf:
            break
        md5.update(buf)
    fob.close()
    return md5.hexdigest()    
