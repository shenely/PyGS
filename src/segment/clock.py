#!/usr/bin/env python2.7

"""Clock segment

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   25 July 2013

Provides the clock segment.

Classes:
ClockSegment   -- Clock segment object

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-07-25    shenely         1.0         Initial revision

"""


##################
# Import section #
#
#Built-in libraries
from datetime import datetime,timedelta

#External libraries
import zmq
from bson.tz_util import utc

#Internal libraries
from . import BaseSegment
from core.routine import socket
from epoch import routine as epoch
from epoch.routine import clock
#
##################


##################
# Export section #
#
__all__ = ["ClockSegment"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]

EPOCH_ADDRESS = "{asset!s}.{segment!s}.Epoch"

CONTINUOUS_CLOCK = 10
DISCRETE_CLOCK = 20

J2000 = datetime(2000,1,1,12,tzinfo=utc)#Julian epoch (2000-01-01T12:00:00Z)

CLOCK_SCALE = 60#Clock rate scale (default 1:1, i.e. real-time)
CLOCK_STEP = timedelta(seconds=60)#Clock step (default to 60 seconds)
#
####################

class ClockSegment(BaseSegment):
    def __init__(self,application,
                 name="Clock",type=CONTINUOUS_CLOCK,
                 seed=J2000,
                 scale=CLOCK_SCALE,step=CLOCK_STEP):
        BaseSegment.__init__(self,application,name)
        
        self.type = type
        
        epoch_socket = self.context.socket(zmq.PUB)
        epoch_socket.connect("tcp://localhost:5555")
        
        epoch_address = EPOCH_ADDRESS.format(asset="System",segment=self.name)

        if self.type is CONTINUOUS_CLOCK:
            epoch_clock = clock.ContinuousClock(seed,scale)
        elif self.type is DISCRETE_CLOCK:
            epoch_clock = clock.DiscreteClock(seed,step)
            
        format_epoch = epoch.FormatEpoch()
        pub_epoch = socket.PublishSocket(epoch_socket,epoch_address)
        
        application.Behavior("Main clock cycle")
        
        application.Scenario("Send epoch message").\
            From("Epoch clock",epoch_clock).\
            Then("Format epoch to string",format_epoch).\
            To("Epoch address",pub_epoch)