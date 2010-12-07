# -*-python-*- 
#
# Receive broadcasted addresses in a standard pytroll Message:
# /<server-name>/address info ... host:port
#
import os
from datetime import datetime, timedelta
import thread
import threading

from pytroll.message import Message
from pytroll.bbmcast import MulticastReceiver, SocketTimeout

__all__ = ('AddressReceiver', 'getaddress')

debug = os.environ.get('DEBUG', False)
broadcast_port = 21200

#-----------------------------------------------------------------------------
#
# Generall thread to receive broadcast addresses.
#
#-----------------------------------------------------------------------------
class AddressReceiver(object):
    def __init__(self, name, max_age=timedelta(hours=1)):
        self._max_age = max_age
        self._address_lock = thread.allocate_lock()
        self._addresses = {}
        self._subject = '/%s/address'%name
        self._do_run = False
        self._is_running = False
        self._thread = threading.Thread(target=self._run)        

    def start(self):
        if not self._is_running:
            self._do_run = True
            self._thread.start()
        return self

    def stop(self):
        self._do_run = False
        return self

    def is_running(self):
        return self._is_running

    def get(self):
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

    def _run(self):
        port = broadcast_port
        recv = MulticastReceiver(port).settimeout(2.0)
        self._is_running = True
        try:
            while self._do_run:
                try:
                    data, fromaddr = recv()
                except SocketTimeout:
                    continue
                m = Message.decode(data)
                if m.type == 'info' and m.subject.lower() == self._subject:
                    addr = [i.strip() for i in m.data.split(':')]
                    addr[1] = int(addr[1])
                    addr = tuple(addr)
                    if debug:
                        print 'receiving address', addr
                    self._add(addr)
        finally:
            self._is_running = False
            recv.close()

    def _add(self, adr):
        self._address_lock.acquire()
        try:
            self._addresses[adr] = datetime.now()
        finally:
            self._address_lock.release()

#-----------------------------------------------------------------------------
# default
getaddress = AddressReceiver
#getaddress = AddressFile

