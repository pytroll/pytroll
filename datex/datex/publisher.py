#
# A proccess to check for new pol_L0 files and publish.
#
import os
import time
from datetime import datetime, timedelta
import logging
import copy
import glob
#from multiprocessing import Process
from threading import Thread
import zmq

from posttroll.message import Message

from datex import logger, datetime_format, datex_config
from datex.services import _get_file_list
from datex.config import DatexLastStamp

time_wakeup = 15
time_epsilon = timedelta(microseconds=10)
#-----------------------------------------------------------------------------
#
# Process manager for the Publisher.
#
#-----------------------------------------------------------------------------
class Publisher(object):
    def __init__(self, *args):
        try:
            self.publish
        except AttributeError:
            raise AttributeError, "You need to bind Publisher class before instantiating"
        self._process = Thread(target=check_and_publish, args=args+(self.publish,))

    @classmethod
    def bind(cls, port):
        cls.destination = "tcp://eth0:%d"%port
        logger.info(cls.destination)
        cls.context = zmq.Context()
        cls.publish = cls.context.socket(zmq.PUB)
        cls.publish.bind(cls.destination)
    
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
def check_and_publish(datatype, rpc_metadata, publish):

    stamp_config = DatexLastStamp(datatype)

    def younger_than_stamp_files():
        fdir, fglob = datex_config.get_path(datatype)
        fstamp = stamp_config.get_last_stamp()
        for f, t in _get_file_list(datatype, time_start=fstamp + time_epsilon):
            if datex_config.distribute(datatype):
                yield os.path.join(fdir, f)
            stamp_config.update_last_stamp(t)

    # give the publisher a little time to initialize (reconnections from subscribers)
    time.sleep(1)
    logger.info('publisher starting')
    try:
        while(True):
            for f in younger_than_stamp_files():
                # Publish new files
                data = copy.copy(rpc_metadata)
                data['uri'] += os.path.basename(f)
                m = Message('/' + datatype, 'file', data)
                logger.info('sending: ' + `m`)
                try:
                    publish.send(`m`)
                except zmq.ZMQError:
                    logger.exception('publish failed')
            time.sleep(time_wakeup)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        logger.info('publisher stopping')
        publish.close()
