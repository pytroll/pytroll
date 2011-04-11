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
"""A datex RPC server proxy.

How a client is talking to a datex RPC server.
"""
import os
from datetime import datetime, timedelta
import hashlib

import rpclite as rpc
from datex import logger, datetime_format

#-----------------------------------------------------------------------------
#
# ServerProxy
#
#-----------------------------------------------------------------------------
class RPCProxy(object):
    """ How a client is talking to a datex RPC server
    """
    def __init__(self, url):
        self.url = url
        self.server = rpc.XMLRPCServerProxy(url)

    def get_file(self, datatype, filename, 
                 outdir='.', chunk_size=1000*5120, check_md5=False):
        """Fetch a file in chunks.
        """
        logger.info('getting %s', self.url + '/' + datatype + '/' + filename)
        if check_md5:
            md5 = hashlib.md5()        
        fob = open(os.path.join(outdir, filename), 'w+b')
        offset = 0
        while True: 
            buf = self.server.get_file_chunk(datatype, filename,
                                             offset, chunk_size, timeout=1800)
            buf = buf.data
            if not buf:
                break
            if check_md5:
                md5.update(buf)
            fob.write(buf)
            offset += len(buf)
        fob.close()
        logger.info('saved %s (%d bytes)', filename, offset)
        if check_md5:
            logger.info('md5 check on %s', filename)
            remote_md5 = self.server.get_file_md5(datatype, filename,
                                                  timeout=1800)
            if remote_md5 != md5.hexdigest():
                logger.error('md5 check failed on %s', filename)

    def get_file_md5(self, datatype, filename):
        """Get a files md5 sum.
        """
        logger.info('getting md5 %s',
                    self.url + '/' + datatype + '/' + filename)
        return self.server.get_file_md5(datatype, filename, timeout=1800)

    def info(self):
        """Get servers RPC info.
        """
        return [self.server.system.whoareyou()] + \
            self.server.system.listMethods()
            
    def list_files(self, datatype, latest=False):
        """Get list of files for given datatype.
        """
        if latest:
            time_start = (datetime.now() - 
                          timedelta(hours=2)).strftime(datetime_format)
            fnames = self.server.get_file_list(datatype, time_start)
        else:
            fnames = self.server.get_file_list(datatype)
        return fnames

    def list_files_latest(self, datatype):
        """Get list of files for given datatype ... just the latest.
        """
        return self.list_files(datatype, latest=True)

    def list_datatypes(self):
        """Get list of datatypes.
        """
        return self.server.get_datatype_list()
