#
# Read:
#   [server]
#   host = "host"
#   rpc_port = port
#   publish_port = port
#
# Remember lock on config writing/reading
#
import os
from datetime import datetime, timedelta
from ConfigParser import ConfigParser, NoOptionError
import fcntl

from datex import logger, datetime_format

class _LockedConfigFile(object):
    def __init__(self, filename):
        self.filename = filename
        self.cfg = ConfigParser()

    def _read(self):
        cfg = ConfigParser()
        fp = open(self.filename, 'r')
        fcntl.flock(fp.fileno(), fcntl.LOCK_EX)
        try:
            cfg.readfp(fp)    
        finally:
            fcntl.flock(fp.fileno(), fcntl.LOCK_UN)
            fp.close()
        self.cfg = cfg
    
    def _write(self):
        fp = open(self.filename, 'w')
        fcntl.flock(fp.fileno(), fcntl.LOCK_EX)
        try:
            self.cfg.write(fp)
        finally:
            fcntl.flock(fp.fileno(), fcntl.LOCK_UN)
            fp.close()

class DatexLastStamp(_LockedConfigFile):
    section = 'root'

    def __init__(self, datatype=None, filename=None):
        if not filename:
            filename = os.path.join(os.environ['DATEX_CONFIG_DIR'], 'stamp_%s.cfg'%datatype)        
        _LockedConfigFile.__init__(self, filename)
        print "FILENAME", filename
        if not os.path.isfile(filename):
            self.update_last_stamp(datetime.utcnow() - timedelta(hours=3))

    def get_last_stamp(self):
        self._read()
        return datetime.strptime(str(self.cfg.get(self.section, 'last_stamp')), datetime_format)

    def update_last_stamp(self, last_stamp):
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

    datatype_prefix = 'datatype-'

    def __init__(self, filename=None):
        if not filename:
            filename = os.path.join(os.environ['DATEX_CONFIG_DIR'], 'datex.cfg')
        _LockedConfigFile.__init__(self, filename)

    def get_server(self):
        self._read()
        host = _eval(self.cfg.get('server', 'host'))
        rpc_port = _eval(self.cfg.get('server', 'rpc_port'))
        publish_port = _eval(self.cfg.get('server', 'publish_port'))
        return host, rpc_port, publish_port

    def get_client(self):
        self._read()
        host = _eval(self.cfg.get('client', 'host'))
        rpc_port = _eval(self.cfg.get('client', 'rpc_port'))
        publish_port = _eval(self.cfg.get('client', 'publish_port'))
        return host, rpc_port, publish_port        

    def distribute(self, datatype):
        self._read()
        try:
            return bool(_eval(self.cfg.get(self.datatype_prefix + datatype, 'distribute')))
        except NoOptionError:
            return True

    def get_path(self, datatype):
        self._read()
        section = self.datatype_prefix + datatype
        fdir = str(self.cfg.get(section, 'dir'))
        fglob = str(self.cfg.get(section, 'glob'))
        return fdir, fglob

    def get_metadata(self, datatype):
        self._read()
        section = self.datatype_prefix + datatype
        format = str(self.cfg.get(section, 'format'))
        try:
            compressed = str(self.cfg.get(section, 'compressed'))
        except NoOptionError:
            compressed = 'no'
        return format, compressed

    def get_datatypes(self):
        self._read()
        ss = []
        for s in self.cfg.sections():
            if s.startswith(self.datatype_prefix):
                ss.append(s[len(self.datatype_prefix):])
        return ss

def _eval(s):
    try:
        s = eval(s)
    except NameError:
        s = str(s)
    return s
