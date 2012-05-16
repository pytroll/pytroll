

from pyinotify import ProcessEvent, Notifier, WatchManager, IN_CLOSE_WRITE, IN_MOVED_TO
import logging

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

class FileTrigger(ProcessEvent):

    def process_IN_CLOSE_WRITE(self, event):
        LOG.debug("got : " + event.pathname)

    def process_IN_MOVED_TO(self, event):
        LOG.debug("moved to : " + event.pathname)

if __name__ == '__main__':

    wdir = 'tests/data'

    # inotify interface
    wm = WatchManager()
    mask = IN_CLOSE_WRITE | IN_MOVED_TO
    
    # create notifier 
    notifier = Notifier(wm, FileTrigger())
    
    # add watches
    wm.add_watch(wdir, mask)
    try:
        notifier.loop()
    except KeyboardInterrupt:
        # destroy the inotify's instance on this interrupt (stop monitoring)
        notifier.stop()










