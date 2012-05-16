

from pyinotify import ProcessEvent, Notifier, WatchManager, IN_CLOSE_WRITE, IN_MOVED_TO
import logging

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

class Trigger:
    def __init__(self, collectors, terminator):
        self.collectors = collectors
        self.terminator = terminator

class FileTrigger(ProcessEvent, Trigger):

    def __init__(self, collectors, terminator, decoder, input_dirs ):
        Trigger.__init__(self, collectors, terminator,)
        self.decoder = decoder
        self.input_dirs = input_dirs

    def process_IN_CLOSE_WRITE(self, event):
        LOG.debug("got : " + event.pathname)

    def process_IN_MOVED_TO(self, event):
        LOG.debug("moved to : " + event.pathname)

    def loop(self):
        # inotify interface
        wm = WatchManager()
        mask = IN_CLOSE_WRITE | IN_MOVED_TO
        
        # create notifier 
        notifier = Notifier(wm, self)
        
        # add watches
        for idir in self.input_dirs:
            wm.add_watch(idir, mask)

        notifier.loop()










