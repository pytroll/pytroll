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
"""Reading datex configuration file. The file is locked during reading/writing.
"""
import os
from datetime import datetime, timedelta
from ConfigParser import ConfigParser, NoOptionError
import fcntl

from datex import logger, datetime_format

class _LockedConfigFile(object):
    """A ConfigParser where reading and writing is on a locked file.
    """
    def __init__(self, filename):
        self.filename = filename
        self.cfg = ConfigParser()

    def _read(self):
        """Read a config file while file is locked.
        """
        cfg = ConfigParser()
        fob = open(self.filename, 'r')
        fcntl.flock(fob.fileno(), fcntl.LOCK_EX)
        try:
            cfg.readfp(fob)    
        finally:
            fcntl.flock(fob.fileno(), fcntl.LOCK_UN)
            fob.close()
        self.cfg = cfg
    
    def _write(self):
        """Write a config file while file is locked.
        """
        fob = open(self.filename, 'w')
        fcntl.flock(fob.fileno(), fcntl.LOCK_EX)
        try:
            self.cfg.write(fob)
        finally:
            fcntl.flock(fob.fileno(), fcntl.LOCK_UN)
            fob.close()

class DatexLastStamp(_LockedConfigFile):
    """A class for reading and updating last time a file of a 
    specific datatype was seen.
    """
    section = 'root'

    def __init__(self, datatype=None, filename=None):
        if not filename:
            filename = os.path.join(os.environ['DATEX_CONFIG_DIR'],
                                    'stamp_%s.cfg'%datatype)        
        _LockedConfigFile.__init__(self, filename)
        if not os.path.isfile(filename):
            self.update_last_stamp(datetime.utcnow() - timedelta(hours=3))

    def get_last_stamp(self):
        """Return last time stamp.
        """
        self._read()
        return datetime.strptime(self.cfg.get(self.section, 'last_stamp'),
                                 datetime_format)

    def update_last_stamp(self, last_stamp):
        """Update last time stamp.
        """
        try:
            self._read()
        except IOError:
            logger.info("create last stamp file '%s'", self.filename)
            self.cfg.add_section(self.section)
        if not isinstance(last_stamp, str):
            last_stamp = last_stamp.strftime(datetime_format)
        self.cfg.set(self.section, 'last_stamp', last_stamp)
        self._write()


class DatexConfig(_LockedConfigFile):
    """Read a datex config file.
    """
    datatype_prefix = 'datatype-'

    def __init__(self, filename=None):
        if not filename:
            filename = os.path.join(os.environ['DATEX_CONFIG_DIR'], 'datex.cfg')
        _LockedConfigFile.__init__(self, filename)

    def get_server(self):
        """Return what a server want to read for rpc and publish addresses.
        """
        self._read()
        rpc_address = self.cfg.get('server', 'rpc_address')
        rpc_host, rpc_port = rpc_address.split(':')
        rpc_port = int(rpc_port)
        publish_destination = self.cfg.get('server', 'publish_destination')
        return (rpc_host, rpc_port), publish_destination

    def get_client(self):
        """Return what a client want to read for rpc and publish addresses.
        """
        self._read()
        rpc_address = self.cfg.get('client', 'rpc_address')
        rpc_host, rpc_port = rpc_address.split(':')
        rpc_port = int(rpc_port)
        publish_address = self.cfg.get('client', 'publish_address')
        return (rpc_host, rpc_port), publish_address

    def distribute(self, datatype):
        """Return if a given datatype should be distributed or not.
        """
        self._read()
        try:
            return bool(eval(self.cfg.get(self.datatype_prefix + datatype,
                                          'distribute')))
        except NoOptionError:
            return True

    def get_path(self, datatype):
        """Return data path for a given datatype.
        """
        self._read()
        section = self.datatype_prefix + datatype
        fdir = str(self.cfg.get(section, 'dir'))
        fglob = str(self.cfg.get(section, 'glob'))
        return fdir, fglob

    def get_metadata(self, datatype):
        """Return meta-data path for a given datatype.
        """
        self._read()
        section = self.datatype_prefix + datatype
        fmt = str(self.cfg.get(section, 'format'))
        try:
            cmpr = str(self.cfg.get(section, 'compressed'))
        except NoOptionError:
            cmpr = 'no'
        return fmt, cmpr

    def get_datatypes(self):
        """Return a list of published datatypes.
        """
        self._read()
        types = []
        for sec in self.cfg.sections():
            if sec.startswith(self.datatype_prefix):
                types.append(sec[len(self.datatype_prefix):])
        return types
