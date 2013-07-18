#!/usr/bin/env python2.7

"""Message objects

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   16 July 2013

Provides the message objects.

Classes:
TelemetryMessage   -- Telemetry message
CommandMessage     -- Command message
AcknowledgeMessage -- Acknowledge message
ProductMessage     -- Product message

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-07-16    shenely         1.0         Initial revision

"""


##################
# Import section #
#
#Built-in libraries
from math import *
from datetime import datetime,time
import types

#External libraries
from numpy import matrix,dot,inner,cross,float64
from scipy.linalg import norm

#Internal libraries
from epoch import EpochState
#
##################


##################
# Export section #
#
__all__ = ["TelemetryMessage",
           "CommandMessage",
           "AcknowledgeMessage",
           "ProductMessage"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]

ORBIT_TELEMETRY = 10
INERTIAL_PRODUCT = 20
GEOGRAPHIC_PRODUCT = 21
#
####################


class BaseMessage(EpochState):
    def __init__(self,epoch,data,type,*args,**kwargs):
        EpochState.__init__(self,epoch,*args,**kwargs)
        
        assert isinstance(data,EpochState)
        assert isinstance(type,types.IntType)
        
        self.data = data
        self.type = type

class TelemetryMessage(BaseMessage):pass

class CommandMessage(BaseMessage):pass

class AcknowledgeMessage(BaseMessage):pass

class ProductMessage(BaseMessage):pass