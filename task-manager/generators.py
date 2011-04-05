#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2010-2011.

# Author(s):
 
#   Martin Raspaud <martin.raspaud@smhi.se>

# This file is part of pytroll.

# Pytroll is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.

# Pytroll is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# pytroll.  If not, see <http://www.gnu.org/licenses/>.

"""Task generators to use with the task manager.
"""

from threading import Thread, Condition
from tm import Task

class TaskTicker(Thread):
    def __init__(self, taskman, action):
        Thread.__init__(self)
        self.taskman = taskman
        self.action = action
        self.loop = True
        self.cond = Condition()
        
    def run(self):
        while self.loop:
            self.taskman.add(Task(self.action))
            self.cond.acquire()
            self.cond.wait(1)
            self.cond.release()

    def stop(self):
        self.loop = False
        self.cond.acquire()
        self.cond.notify()
        self.cond.release()


if __name__ == "__main__":
    def foo(txt="hej"):
        print txt

    from tm import TaskManager
    from datetime import datetime
    from time import sleep
    TASKMAN = TaskManager()
    TASKMAN.start()
    
    print "trying the task ticker"
    tt = TaskTicker(TASKMAN, lambda: foo(datetime.now()))
    tt.start()
    sleep(10)
    tt.stop()
    
    TASKMAN.quit()
