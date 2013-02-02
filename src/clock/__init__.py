#!/usr/bin/env python2.7

"""Clock segment

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   02 February 2013

Purpose:    
"""


##################
# Import section #
#
#Built-in libraries
from datetime import datetime
import logging
import types

#External libraries
import zmq

#Internal libraries
from service.scheduler import Scheduler
from core.routine import socket
from .epoch import routine as epoch
from . import routine
#
##################


##################
# Export section #
#
#
##################


####################
# Constant section #
#
__version__ = "0.1"#current version [major.minor]

EPOCH_ADDRESS = "Kepler.Epoch"
EPOCH_SCALE = 60
#
####################


class ClockSegment(object):
    scheduler = Scheduler()
    context = zmq.Context(1)
    
    def __init__(self,epoch):        
        self.epoch = epoch
        
        self.socket = self.context.socket(zmq.PUB)
        self.socket.connect("tcp://localhost:5555")
        
        self.task_update_epoch()

    def task_update_epoch(self):
        publish_epoch = socket.publish(self.socket)
        format_epoch = epoch.format(EPOCH_ADDRESS,publish_epoch)
        iterate_epoch = routine.continuous(self.epoch,EPOCH_SCALE,format_epoch)
        
        self.epoch_task = iterate_epoch
        self.scheduler.periodic(self.epoch_task,200).start()

def main():
    """Main Function"""
    
    epoch = datetime(2010,1,1)
        
    p = ClockSegment(epoch)
            
    #scheduler.start()

if __name__ == '__main__':main()
