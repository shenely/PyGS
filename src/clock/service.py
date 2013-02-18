#!/usr/bin/env python2.7

"""Clock service

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   17 February 2013

Purpose:    
"""


##################
# Import section #
#
#Built-in libraries
from datetime import datetime

#External libraries
import zmq
from bson.tz_util import utc

#Internal libraries
from core.service.scheduler import Scheduler
from core.fluent import application
from core.routine import socket
from .epoch import EpochState
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

def main():
    """Main Function"""
    
    scheduler = Scheduler()
    context = zmq.Context(1)
    
    clock = EpochState(datetime(2010,1,1,tzinfo=utc))
        
    epoch_socket = context.socket(zmq.PUB)
    epoch_socket.connect("tcp://localhost:5555")
        
    segment = application("Clock segment")

    segment.workflow("Send epoch").\
        source("Iterate epoch",routine.continuous,clock.epoch,EPOCH_SCALE).\
        sequence("Format epoch",epoch.format,EPOCH_ADDRESS).\
        sink("Publish epoch",socket.publish,epoch_socket)
    
    segment.clean()
    segment.build()
    
    scheduler.periodic(segment["Send epoch"],200).start()
    
            
    #scheduler.start()

if __name__ == '__main__':main()
