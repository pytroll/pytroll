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

"""Mini task manager.
"""

from time import sleep
from threading import Thread, Condition
from datetime import datetime, timedelta
import os

class FileTrigger(Thread):
    """Wait for a file.
    """
    def __init__(self, filename):
        Thread.__init__(self)
        self.filename = filename
        self.loop = True
        self.cond = Condition()
        #self.start()
        self.exit_status = 0

    def run(self):
        while self.loop:
            self.cond.acquire()
            # Polling is ugly, this should be replaced when possible by inotify.
            if os.path.exists(self.filename):
                # Could we use yield instead ?
                self.cond.release()
                return
            self.cond.wait(1)
            self.cond.release()

    def cancel(self):
        self.loop = False
        self.exit_status = 1
        self.cond.acquire()
        self.cond.notify()
        self.cond.release()

    def __repr__(self):
        return "File trigger " + self.filename

class TimeTrigger(Thread):
    """Wait for a given time.
    """
    def __init__(self, time):
        Thread.__init__(self)
        self.time = time
        self.loop = True
        self.cond = Condition()
        #self.start()
        self.exit_status = 0

    def run(self):
        while self.loop and self.time > datetime.utcnow():
            self.cond.acquire()
            now = datetime.utcnow()
            diff = ((self.time - now).seconds + 
                    (self.time - now).microseconds / 1000000.0)
            self.cond.wait(diff)
            self.cond.release()

    def cancel(self):
        self.loop = False
        self.exit_status = 1
        self.cond.acquire()
        self.cond.notify()
        self.cond.release()

    def __repr__(self):
        return "Time trigger "+str(self.time)

class Action(object):
    """Action class to store non-interpreted functions.
    """
    def __init__(self, function, *args, **kwargs):
        self.action = (function, args, kwargs)

    def __cmp__(self, other):
        try:
            return cmp(self.action, other.action)
        except AttributeError:
            return cmp(self.action, other)

    def get_function(self):
        """Get the function to call.
        """
        return (lambda: self.action[0](*self.action[1], **self.action[2]))

    def __call__(self):
        self.get_function()()

class Task(Thread):
    """Run a given function when *triggers* happen.
    """
    def __init__(self, action, *triggers, **kwargs):
        Thread.__init__(self)
        self.tasks = []
        self.label = kwargs.get("label", "")
        self.action = action
        self._trigger(*triggers)
        self.loop = True
        self.exit_status = 0

    def start(self):
        for task in self.tasks:
            if not task.isAlive():
                task.start()
        Thread.start(self)

    def _trigger(self, *args):
        """Analyse triggers and add them to the subtask 
        """
        for obj in args:
            try:
                (obj.year, obj.month, obj.day, 
                 obj.hour, obj.minute, obj.second)
                self.tasks.append(TimeTrigger(obj))
                continue
            except AttributeError:
                pass
            if isinstance(obj, Task):
                self.tasks.append(obj)
            else:
                self.tasks.append(FileTrigger(obj))

    def run(self):
        while self.loop:
            # Wait until all dependencies are ready, then run.
            start = datetime.utcnow()
            end = start + timedelta(seconds=1)
            dep_status = 0
            for dep in self.tasks:
                now = datetime.utcnow()
                if now < end:
                    diff = ((end - now).seconds + 
                            (end - now).microseconds / 1000000.0)
                    dep.join(min(1, diff))
                    dep_status += dep.exit_status
                else:
                    break
            # If all dependencies where ready and had a clean exit code, run
            # the action.
            if datetime.utcnow() < end and dep_status == 0:
                self.exit_status = self.action() or 0
                self.tasks = []
                try:
                    if self.exit_status == 0:
                        self.parent.tasks.remove(self)
                except AttributeError:
                    pass
                return

    def print_tasks(self, indent=0):
        """Print subtasks.
        """
        print self.format_tasks(indent)

    def format_tasks(self, indent=0):
        """Make a formated list of tasks.
        """
        string = ""
        for task in self.tasks:
            string += " "*indent + str(task) + "\n"
            try:
                if task.tasks:
                    string += task.format_tasks(indent+2)
            except AttributeError:
                pass
        return string
            
    def __str__(self):
        if self.label:
            return self.label
        else:
            return Thread.__str__(self)
        
    def cancel(self):
        """Cancel a task.
        """
        self.loop = False
        self.exit_status = 1
        for task in reversed(self.tasks):
            task.cancel()
            self.tasks.remove(task)

    def __cmp__(self, other):
        try:
            return cmp(self.action, other.action)
        except AttributeError:
            return cmp(self.action, other)

class TaskManager(Task):
    """One task to rule them all. If forever is False, runs the given tasks and
    die.
    """
    def __init__(self, forever=True):
        Task.__init__(self, lambda: [])
        self.forever = forever
        self.cond = Condition()

    def add(self, task):
        """Add a task.
        """
        if not task.isAlive():
            task.start()
        task.parent = self
        self.tasks.append(task)

    def remove(self, task):
        """Remove a task.
        """
        task.cancel()
        self.tasks.remove(task)

    def run(self):
        if self.forever:
            if self.loop:
                self.cond.acquire()
                self.cond.wait()
                self.cond.release()
        else:
            Task.run(self)
        self.cancel()

    def quit(self):
        """End the task manager.
        """
        self.loop = False
        self.cond.acquire()
        self.cond.notify()
        self.cond.release()

    def __str__(self):
        return self.__repr__() + "\n" + self.format_tasks(2)

if __name__ == "__main__":
    def foo(txt="hej"):
        print txt
        
    from generators import TaskTicker
    tm = TaskManager()
    tm.start()
    tm.add(Task(foo, datetime.utcnow() + timedelta(seconds=3)))
    tm.add(Task(lambda: foo("hoj"), datetime.utcnow() + timedelta(seconds=5)))
    txt = "yo"
    task = Task(lambda: foo(txt), datetime.utcnow() + timedelta(seconds=6))
    tm.add(task)
    tm.add(Task(lambda: foo("dep"), task))
    task = Task(lambda: foo("file"), "./toto")
    tm.add(task)
    task2 = Task(lambda: foo("dep2"), task)
    tm.add(task2)
    print "After init"
    tm.print_tasks()
    sleep(10)
    #tm.remove(task)
    #task2.cancel()
    
    print "After 10s"
    tm.print_tasks()
    task.cancel()
    print "After cancel"
    tm.print_tasks()
    sleep(1.1)
    print task2

    print tm.tasks

    tm.quit()

    
