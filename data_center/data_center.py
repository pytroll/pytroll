import socket, traceback
import time
import zmq
import threading
import Queue

import pytroll.message as message

BROADCAST_PORT = 21200
MESSAGE_PORT = 21201

def get_own_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('smhi.se', 0))
    ip = s.getsockname()[0]
    s.close()
    return ip

def process_message(msg):
    print "I'm processing a message: ", msg

class Broadcaster(object):
    """Class to broadcast stuff.
    """

    host = '<broadcast>'

    def __init__(self, message, interval, port):
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.loop = True
        self.interval = interval
        self.message = message
        self.thread = threading.Thread(target=self.loop_send)
        
    def send(self, message):
        """Broadcast a *message*.
        """
        self.socket.sendto(message, (self.host, self.port))

    def loop_send(self):
        """Broadcasts forever.
        """
        while self.loop:
            print "Advertizing."
            self.send(self.message)
            time.sleep(self.interval)

    def start(self):
        """Start the broadcasting.
        """
        self.thread.start()

    def stop(self):
        """Stop the broadcasting.
        """
        self.loop = False


class Receiver(object):
    """Receive messages and process them.
    """
    def __init__(self, process_fun, port):
        self.fun = process_fun
        self.recv_thread = self.thread = threading.Thread(target=self.loop_recv)
        self.fun_thread = self.thread = threading.Thread(target=self.loop_fun)
        self.loop = True
        self.port = port
        self.socket = zmq.Context().socket(zmq.PULL)
        self.socket.bind('tcp://'+get_own_ip()+':'+str(self.port))
        self.message_queue = Queue.Queue()
        
    def loop_recv(self):
        while self.loop:
            try:
                message = self.socket.recv(zmq.NOBLOCK)
                self.message_queue.put(message)
            except zmq.ZMQError:
                pass
            time.sleep(0.5)

    def loop_fun(self):
        while self.loop:
            try:
                message = self.message_queue.get(timeout=0.5)
                self.fun(message)
            except Queue.Empty:
                pass
                
    def start(self):
        self.recv_thread.start()
        self.fun_thread.start()

    def stop(self):
        self.loop = False

msg = message.Message("pytroll://dc/address", "info",
                      str(get_own_ip()) + ":" + str(MESSAGE_PORT)).encode()
print msg
broadcaster = Broadcaster(msg, 2, BROADCAST_PORT)
broadcaster.start()

message_receiver = Receiver(process_message, MESSAGE_PORT)
message_receiver.start()

try:
    while True:
        time.sleep(1)
except (KeyboardInterrupt, SystemExit):
    print "Exiting..."
    broadcaster.stop()
    message_receiver.stop()
except:
    traceback.print_exc()


