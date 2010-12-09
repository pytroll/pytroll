#
# A proccess to check for new pol_L0 files and publish.
#
import os
import time
import logging
import copy
import glob
from multiprocessing import Process
import zmq

from pytroll.message import Message

logger = logging.getLogger('datex-publisher')
#-----------------------------------------------------------------------------
#
# Process manager for the Publisher.
#
#-----------------------------------------------------------------------------
class Publisher(object):
    def __init__(self, *args):
        self._process = Process(target=check_and_publish, args=args)
    
    def start(self):        
        self._process.daemon = True # terminate when parent terminate
        self._process.start()
        return self

    def stop(self):
        #self._process.terminate()
        #self._process.join()
        return self

    def is_running(self):
        return self._process.is_alive()

#-----------------------------------------------------------------------------
#
# In the child process.
#
#-----------------------------------------------------------------------------
def check_and_publish(subject, signal_dir, rpc_metadata, port):

    def signal_files(handle_one=False):
        # Get signal files
        for sfile in glob.glob(signal_dir + '/*.signal'):
            try:
                fp = open(sfile)
                try:
                    signal = fp.readline().strip()
                    yield signal
                    if handle_one:
                        return
                finally:
                    fp.close()
                    os.unlink(sfile)
            except IOError:
                logger.exception('open signal file failed')
                continue                    

    destination = "tcp://eth0:%d"%port
    logger.info(destination)
    context = zmq.Context()
    publish = context.socket(zmq.PUB)
    publish.bind(destination)

    # give the publisher a little time to initialize (reconnections from subscribers)
    time.sleep(1)
    logger.info('publisher starting')
    try:
        while(True):
            for f in signal_files():
                # Publish new files
                data = copy.copy(rpc_metadata)
                data['uri'] += os.path.basename(f)
                m = Message(subject, 'file', data)
                logger.info('sending: ' + `m`)
                try:
                    publish.send(`m`)
                except zmq.ZMQError:
                    logger.exception('publish failed')
            time.sleep(5)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        logger.info('publisher stopping')
        publish.close()
