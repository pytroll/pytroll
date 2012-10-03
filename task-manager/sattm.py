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

"""Satellite application to the task manager.
"""


import tm
from datetime import datetime, timedelta
from time import sleep


def prepare(sat, orbit, time):
    print "Preparing swath", sat, orbit, time
    
def processing1(sat, orbit, time):
    print "Processing step 1", sat, orbit, time

def processing2(sat, orbit, time):
    print "Processing step 2", sat, orbit, time

def processing3(sat, orbit, time):
    print "Processing step 3", sat, orbit, time


def read_schedule(filename, taskman):
    """Reads a schedule file *filename* and adds corresponding tasks to the
    taskmanager *tm*.
    """
    for line in open(filename):
        sat, orbit, date, time = line.split()
        start_time = datetime.strptime(date + time, "%Y-%m-%d%H:%M:%S")
        
        prepare_time = start_time - timedelta(minutes=20)
        
        prepare_task = tm.Task(tm.Action(prepare, sat, orbit, start_time),
                               prepare_time,
                               label="Prepare "+str(sat)+" "+str(orbit))
        filename = "hrpt-"+sat+"-"+orbit+".hrp"
        proc1_task = tm.Task(tm.Action(processing1, sat, orbit, start_time),
                             prepare_task,
                             filename,
                             label="Proc 1 "+str(sat)+" "+str(orbit))
        proc2_task = tm.Task(tm.Action(processing2, sat, orbit, start_time),
                             proc1_task,
                             label="Proc 2 "+str(sat)+" "+str(orbit))
        proc3_task = tm.Task(tm.Action(processing3, sat, orbit, start_time),
                             proc2_task,
                             label="Proc 3 "+str(sat)+" "+str(orbit))

        taskman.add(proc3_task)

def write_test_schedule(filename):
    fdes = open(filename, "w")
    now = datetime.utcnow() + timedelta(minutes=20)
    thirty_secs = timedelta(seconds=1)
    satinfos = ("noaa19 12345", "noaa18 34525", "aqua 45215")
    for i, satinfo in enumerate(satinfos):
        fdes.write(satinfo + " " +
                   (now + thirty_secs * (i + 1)).strftime("%Y-%m-%d %H:%M:%S") +
                   "\n")
    fdes.close()

TASKMAN = tm.TaskManager()
TASKMAN.start()
write_test_schedule("test_schedule2.txt")
read_schedule("test_schedule2.txt", TASKMAN)
#TASKMAN.print_tasks()
print TASKMAN
sleep(4)
print TASKMAN
TASKMAN.quit()

