import os
import time
import threading

from pytroll.bbmcast import MulticastSender, MC_GROUP

debug = os.environ.get('DEBUG', False)
broadcast_port = 21200

#-----------------------------------------------------------------------------
#
# Generall thread to broadcast addresses.
#
#-----------------------------------------------------------------------------
class AddressBroadcaster(object):
    """Class to broadcast stuff.
    """
    def __init__(self, message, interval):
        # mcgroup = None or '<broadcast>' is broadcast
        # mcgroup = MC_GROUP is default multicast group
        self._sender = MulticastSender(broadcast_port, mcgroup=MC_GROUP)
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
# default
sendaddress = AddressBroadcaster
