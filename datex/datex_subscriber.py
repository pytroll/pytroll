#
# Listen for new pol_L0 files.
#
# We can do this in the main process and thread, cuz
# zmq keeps a threaded queue of incomming messages (I hope).
#
import logging
import zmq

from posttroll.message import Message

logger = logging.getLogger('datex_client')

context = zmq.Context() 
class Subscriber(object):
    def __init__(self, subject, addr):
        subscriber = context.socket(zmq.SUB)
        subscriber.setsockopt(zmq.SUBSCRIBE, subject)
        self.subscriber = subscriber
        self.destination = "tcp://%s:%d"%addr
        logger.info(self.destination)

    def __call__(self):
        return self.get()

    def get(self, timeout=None):
        if timeout:
            timeout *= 1000.
        self.subscriber.connect(self.destination)
        poller = zmq.Poller()
        poller.register(self.subscriber, zmq.POLLIN)
        try:
            while(True):
                try:
                    s = poller.poll(timeout=timeout)
                    if s:
                        if s[0][0] == self.subscriber:
                            m = Message.decode(self.subscriber.recv(zmq.NOBLOCK))
                            yield m
                        else:
                            logger.error("WHAT THE HECK")
                    else:
                        # timeout
                        yield None
                except zmq.ZMQError:
                    logger.exception('recv failed')
        finally:
            poller.unregister(self.subscriber)
            self.subscriber.close()        
