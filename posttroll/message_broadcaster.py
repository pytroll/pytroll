import os
import time
import threading

import posttroll.message as message
from posttroll.bbmcast import MulticastSender, MC_GROUP

__all__ = ('MessageBroadcaster', 'AddressBroadcaster', 'sendaddress')

debug = os.environ.get('DEBUG', False)
broadcast_port = 21200

#-----------------------------------------------------------------------------
#
# Generall thread to broadcast messages.
#
#-----------------------------------------------------------------------------
class MessageBroadcaster(object):
    """Class to broadcast stuff.
    """
    def __init__(self, message, port, interval):
        # mcgroup = None or '<broadcast>' is broadcast
        # mcgroup = MC_GROUP is default multicast group
        self._sender = MulticastSender(port, mcgroup=MC_GROUP)
        self._interval = interval
        self._message = message
        self._do_run = False
        self._is_running = False
        self._thread = threading.Thread(target=self._run)
        
    def start(self):
        """Start the broadcasting.
        """
        if not self._is_running:
            self._do_run = True
            self._thread.start()
        return self

    def is_running(self):
        """Are we running.
        """
        return self._is_running

    def stop(self):
        """Stop the broadcasting.
        """
        self._do_run = False
        return self

    def _run(self):
        """Broadcasts forever.
        """
        self._is_running = True
        try:
            while self._do_run:
                if debug:
                    print "Advertizing.", str(self._message)
                self._sender(self._message)
                time.sleep(self._interval)
        finally:
            self._is_running = False
            self._sender.close()

#-----------------------------------------------------------------------------
#
# Generall thread to broadcast addresses.
#
#-----------------------------------------------------------------------------
class AddressBroadcaster(MessageBroadcaster):
    """Class to broadcast stuff.
    """
    def __init__(self, name, address, interval):
        msg = message.Message("/%s/address"%name, "info",
                              "%s:%d"%address).encode()
        MessageBroadcaster.__init__(self, msg, address[1], interval) 
#-----------------------------------------------------------------------------
# default
sendaddress = AddressBroadcaster
