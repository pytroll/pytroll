#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2012 Martin Raspaud

# Author(s):

#   Kristian Rune Larsen <krl@dmi.dk>
#   Martin Raspaud <martin.raspaud@smhi.se>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Triggers for region_collectors
"""

from pyinotify import (ProcessEvent, Notifier, WatchManager,
                       IN_CLOSE_WRITE, IN_MOVED_TO)
import logging
from datetime import datetime

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

def total_seconds(td):
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6

class Trigger:
    """Abstract trigger class.
    """
    def __init__(self, collectors, terminator):
        self.collectors = collectors
        self.terminator = terminator

    def _do(self, metadata):
        """Execute the collectors and terminator.
        """
        for collector in self.collectors:
            res = collector(metadata)
            if res:
                return self.terminator(res)
        

from threading import Thread, Event

class FileTrigger(ProcessEvent, Trigger, Thread):
    """File trigger, acting upon inotify events.
    """
    def __init__(self, collectors, terminator, decoder, input_dirs ):
        ProcessEvent.__init__(self)
        Thread.__init__(self)
        Trigger.__init__(self, collectors, terminator)
        self.decoder = decoder
        self.input_dirs = input_dirs
        self._running = True
        self.new_file = Event()

    def _do(self, pathname):
        Trigger._do(self, self.decoder(pathname))

    def process_IN_CLOSE_WRITE(self, event):
        """On closing a file.
        """
        LOG.debug("New file detected (close write): " + event.pathname)
        self._do(event.pathname)
        self.new_file.set()
    
    def process_IN_MOVED_TO(self, event):
        """On moving a file into the directory.
        """
        LOG.debug("New file detected(moved to): " + event.pathname)
        self._do(event.pathname)
        self.new_file.set()

    def run(self):
        """The timeouts are handled here.
        """
        # The wait for new files is handled through the event mechanism of the
        # threading module:
        # - first a new file arrives, and an event is triggered
        # - then the new timeouts are computed
        # - if a timeout occurs during the wait, the wait is interrupted and
        #   the timeout is handled.
        
        while self._running:
            timeouts = [(collector, collector.timeout)
                        for collector in self.collectors
                        if collector.timeout is not None]

            if timeouts:
                next_timeout = min(timeouts, key=(lambda(x): x[1]))
                if next_timeout[1] and (next_timeout[1] < datetime.utcnow()):
                    LOG.info("Timeout detected, terminating collector")
                    self.terminator(next_timeout[0].finish())
                else:
                    self.new_file.wait(total_seconds(next_timeout[1] -
                                                     datetime.utcnow()))
                    self.new_file.clear()
            else:
                self.new_file.wait()
                self.new_file.clear()


    def stop(self):
        """Stopping everything.
        """
        self._running = False
        self.new_file.set()

    def loop(self):
        """The main function.
        """
        self.start()
        try:
            # inotify interface
            wm_ = WatchManager()
            mask = IN_CLOSE_WRITE | IN_MOVED_TO

            # create notifier 
            notifier = Notifier(wm_, self)

            # add watches
            for idir in self.input_dirs:
                wm_.add_watch(idir, mask)

            notifier.loop()
        finally:
            self.stop()
            self.join()
