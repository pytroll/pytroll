import socket, traceback
import time
import zmq
import threading
import Queue

import pytroll.message as message
from pytroll.address_broadcaster import sendaddress

MESSAGE_PORT = 21201

def get_own_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('smhi.se', 0))
    ip = s.getsockname()[0]
    s.close()
    return ip

def process_message(msg):
    print "I'm processing a message: ", msg

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

msg = message.Message("/dc/address", "info",
                      str(get_own_ip()) + ":" + str(MESSAGE_PORT)).encode()
print msg
broadcaster = sendaddress(msg, 2).start()

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


