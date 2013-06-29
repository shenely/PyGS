#!/usr/bin/env python2.7

"""Clock service

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   29 June 2013

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
from core.agenda import *
from core.engine import *
from core.routine import socket
from epoch import routine as epoch
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
__version__ = "1.0"#current version [major.minor]

EPOCH_ADDRESS = "Kepler.Epoch"
EPOCH_SCALE = 60
#
####################


def main():
    """Main Function"""
    
    scheduler = Scheduler()
    context = zmq.Context(1)
    
    clock_epoch = datetime(2010,1,1,tzinfo=utc)
        
    epoch_socket = context.socket(zmq.PUB)
    epoch_socket.connect("tcp://localhost:5555")
        
#    segment = application("Clock segment")
#
#    segment.workflow("Send epoch").\
#        source("Iterate epoch",routine.continuous,clock.epoch,EPOCH_SCALE).\
#        sequence("Format epoch",epoch.format,EPOCH_ADDRESS).\
#        sink("Publish epoch",socket.publish,epoch_socket)
#    
#    segment.clean()
#    segment.build()
#
#    scheduler.periodic(segment["Send epoch"],200).start()

    input = routine.ContinuousClock(clock_epoch,EPOCH_SCALE)
    formatter = epoch.FormatEpoch(EPOCH_ADDRESS)
    output = socket.PublishSocket(epoch_socket)

    segment = Application("Clock segment",scheduler).\
        Behavior("Main clock").\
            Scenario("Send epoch").\
                From("Clock source",input).\
                Then("Format epoch",formatter).\
                To("Publish target",output)
                
if __name__ == '__main__':main()
