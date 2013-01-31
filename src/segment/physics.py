#!/usr/bin/env python2.7

"""Physics segment

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   29 January 2013

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
from ..core.scheduler import Scheduler
from ..routine import epoch,socket,iterator
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


class PhysicsSegment(object):
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
        iterate_epoch = iterator.caesium(self.epoch,EPOCH_SCALE,format_epoch)
        
        self.epoch_task = iterate_epoch
        self.scheduler.periodic(self.epoch_task,100).start()

def main():
    """Main Function"""
    
    epoch = datetime(2010,1,1)
        
    p = PhysicsSegment(epoch)
            
    #scheduler.start()

if __name__ == '__main__':main()
