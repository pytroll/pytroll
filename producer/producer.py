# -*-python-*- 
#
from datetime import datetime, timedelta
import time
import copy
import socket
import thread
from threading import Thread
import zmq

from pytroll.message import Message

broadcast_port = 21200

#
# Broadcast message:
# pytroll://DC/address info <YYYY-MM-DDTHH:MM:SS> user@host host:port
#

class DCAddressFetcher(Thread):
    def __init__(self, port=broadcast_port, max_age=timedelta(hours=1)):
        self._port = port
        self._max_age = max_age
        self._address_lock = thread.allocate_lock()
        self._addresses = {}
        Thread.__init__(self)
        Thread.start(self)
                    
    def __call__(self):
        now = datetime.now()
        ads = []
        self._address_lock.acquire()
        try:
            for a, s in self._addresses.items():
                if now - s < self._max_age:
                    ads.append(a)
                else:
                    del self._addresses[a]
        finally:
            self._address_lock.release()
        return ads

    def _add(self, adr):
        self._address_lock.acquire()
        try:
            self._addresses[adr] = datetime.now()
        finally:
            self._address_lock.release()
        
    def run(self):
        BUFSIZE = 1024
        host = '0.0.0.0'
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.bind((host, self._port))
        while True:
            data, fromaddr = s.recvfrom(BUFSIZE)
            m = Message.decode(data)
            if m.type == 'info' and m.subject.lower() == 'pytroll://dc/address':
                addr = [i.strip() for i in m.data.split(':')]
                addr[1] = int(addr[1])
                addr = tuple(addr)
                print 'receiving address', addr
                self._add(addr)

context = zmq.Context()
def make_connection(addr):
    s = context.socket(zmq.PUSH)
    dest = 'tcp://' + addr[0] + ':%d'%addr[1]
    print 'connecting to', dest
    s.connect(dest)
    return s

class Connections:
    def __init__(self, address_fetcher):
        self.address_fetcher = address_fetcher
        self.addresses = {}

    def __call__(self):
        ads = self.address_fetcher()
        for a in ads:
            if a not in self.addresses.keys():
                self.addresses[a] = make_connection(a)
        ads = self.address_fetcher()
        for a, c in self.addresses.items():
            if a not in ads:
                try:
                    c.close()
                except:
                    pass
                del self.addresses[a]
        return self.addresses.values()

    def any(self):
        return True
        #return bool(self.addresses)

    def send(self, msg):
        for c in self():
            print 'sending to', str(c), "'%s'"%`msg`
            c.send(`msg`)        

    def clear(self):
        self.close()

    def close(self):
        for v in self.addresses.values():
            v.close()
        self.addresses = {}


class Messager:
    def __init__(self):
        self.count = 0
    def __call__(self):
        self.count += 1        
        return Message('pytroll://test/1/2/3', 'info', "what's up doc #%d"%self.count)

connections = Connections(DCAddressFetcher())

msg = Messager()
while True:
    if connections.any():
        connections.send(msg())
    time.sleep(1)
