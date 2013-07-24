#!/usr/bin/env python2.7

"""Clock service

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   24 July 2013

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
    
    processor = Processor()
    context = zmq.Context(1)
    
    clock_epoch = datetime(2010,1,1,tzinfo=utc)
        
    clock_socket = context.socket(zmq.PUB)
    clock_socket.connect("tcp://localhost:5555")

    input = routine.ContinuousClock(clock_epoch,EPOCH_SCALE)
    formatter = epoch.FormatEpoch()
    output = socket.PublishSocket(clock_socket,EPOCH_ADDRESS)

    segment = Application("Clock segment",processor)
    
    segment.Behavior("Main clock")
    
    segment.Scenario("Send epoch").\
                From("Clock source",input).\
                Then("Format epoch",formatter).\
                To("Publish target",output)
                
if __name__ == '__main__':main()
