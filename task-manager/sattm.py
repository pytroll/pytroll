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
        start_time = datetime.strptime(date + time, "%Y-%m-%d%H:%M")
        
        prepare_time = start_time - timedelta(minutes=20)
        
        prepare_task = tm.Task(lambda: prepare(sat, orbit, start_time),
                               prepare_time,
                               label="Prepare "+str(sat)+" "+str(orbit))
        filename = "hrpt-"+sat+"-"+orbit+".hrp"
        proc1_task = tm.Task(lambda: processing1(sat, orbit, start_time),
                             prepare_task,
                             filename,
                             label="Proc 1 "+str(sat)+" "+str(orbit))
        proc2_task = tm.Task(lambda: processing2(sat, orbit, start_time),
                             proc1_task,
                             label="Proc 2 "+str(sat)+" "+str(orbit))
        proc3_task = tm.Task(lambda: processing3(sat, orbit, start_time),
                             proc2_task,
                             label="Proc 3 "+str(sat)+" "+str(orbit))
        proc3_task
        taskman.add(proc3_task)

TASKMAN = tm.TaskManager()
TASKMAN.start()
read_schedule("test_schedule.txt", TASKMAN)
TASKMAN.print_tasks()
TASKMAN.quit()

