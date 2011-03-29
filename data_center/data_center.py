import socket, traceback
import time
import zmq
import threading
import Queue

#import pytroll.message as message
from posttroll.message_broadcaster import sendaddress

MESSAGE_PORT = 21200

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
        self.recv_thread = threading.Thread(target=self.loop_recv)
        self.fun_thread = threading.Thread(target=self.loop_fun)
        self.loop = True
        self.port = port
        self.socket = zmq.Context().socket(zmq.PULL)
        self.socket.bind('tcp://'+get_own_ip()+':'+str(self.port))
        self.message_queue = Queue.Queue()
        
    def loop_recv(self):
        while self.loop:
            message = self.socket.recv()
            self.message_queue.put(message)

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
        # Send a message to unblock the reciever socket.
        sock = zmq.Context().socket(zmq.PUSH)
        sock.connect('tcp://'+get_own_ip()+':'+str(self.port))
        sock.send("Exiting data center")

broadcaster = sendaddress('dc', (get_own_ip(), MESSAGE_PORT), 2).start()
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


