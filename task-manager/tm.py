from time import sleep
from threading import Thread, Condition
from datetime import datetime, timedelta
import os

class FileWatcher(Thread):
    
    def __init__(self, filename):
        Thread.__init__(self)
        self.filename = filename
        self.loop = True
        self.cond = Condition()
        self.start()

    def run(self):
        while self.loop:
            self.cond.acquire()
            # Polling is ugly, this should be replaced when possible by inotify.
            if os.path.exists(self.filename):
                # Could we use yield instead ?
                return
            self.cond.wait(1)
            self.cond.release()

    def cancel(self):
        self.loop = False
        self.cond.acquire()
        self.cond.notify()
        self.cond.release()

class Timer(Thread):
    
    def __init__(self, time):
        Thread.__init__(self)
        self.time = time
        self.loop = True
        self.cond = Condition()
        self.start()

    def run(self):
        while self.loop and self.time > datetime.utcnow():
            self.cond.acquire()
            now = datetime.utcnow()
            diff = ((self.time - now).seconds + 
                    (self.time - now).microseconds / 1000000.0)
            self.cond.wait(min(1, diff))
            self.cond.release()

    def cancel(self):
        self.loop = False
        self.cond.acquire()
        self.cond.notify()
        self.cond.release()

class Task(Thread):
    
    def __init__(self, action, *triggers):
        Thread.__init__(self)
        self.tasks = []
        self.action = action
        self._trigger(*triggers)
        self.loop = True
        
    def _trigger(self, *args):
        for obj in args:
            try:
                (obj.year, obj.month, obj.day, 
                 obj.hour, obj.minute, obj.second)
                self.tasks.append(Timer(obj))
                continue
            except AttributeError:
                pass
            if isinstance(obj, Task):
                self.tasks.append(obj)
            else:
                self.tasks.append(FileWatcher(obj))

    def run(self):
        while self.loop:
            start = datetime.utcnow()
            end = start + timedelta(seconds=1)
            for dep in self.tasks:
                now = datetime.utcnow()
                if now < end:
                    diff = ((end - now).seconds + 
                            (end - now).microseconds / 1000000.0)
                    dep.join(min(1, diff))
                else:
                    break
            if datetime.utcnow() < end:
                self.action()
                return

    def print_tasks(self, indent=0):
        for task in self.tasks:
            print " "*indent, task
            try:
                if task.tasks:
                    task.print_tasks(indent+2)
            except AttributeError:
                pass
        
    def cancel(self):
        self.loop = False
        for task in self.tasks:
            if not isinstance(task, Task):
                task.cancel()
                self.tasks.remove(task)

        

class TaskManager(Task):
    
    def __init__(self, forever=True):
        Task.__init__(self, lambda: [])
        self.forever = forever
        self.cond = Condition()

    def add(self, task):
        if not task.isAlive():
            task.start()
        self.tasks.append(task)

    def remove(self, task):
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

    def quit(self):
        self.loop = False
        self.cond.acquire()
        self.cond.notify()
        self.cond.release()
            

def foo(txt="hej"):
    print txt

if __name__ == "__main__":
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

    
