#
# Read:
#   [server]
#   host = "host"
#   rpc_port = port
#   publish_port = port
#
import os
from ConfigParser import ConfigParser

def read_config(filename=None):
    if not filename:
        filename = os.path.dirname(__file__) + '/datex_config.cfg' 
    cfg = ConfigParser()
    cfg.read(filename)
    host = _eval(cfg.get('server', 'host'))
    rpc_port = _eval(cfg.get('server', 'rpc_port'))
    publish_port = _eval(cfg.get('server', 'publish_port'))
    return host, rpc_port, publish_port

def _eval(s):
    try:
        s = eval(s)
    except NameError:
        s = str(s)
    return s

if __name__ == '__main__':
    print read_config()

