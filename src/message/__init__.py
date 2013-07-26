#!/usr/bin/env python2.7

"""Message objects

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   26 July 2013

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
2013-07-18    shenely         1.1         Builds data from message type
2013-07-24    shenely         1.2         Exports constants
2013-07-26    shenely         1.3         Moved type check out of base

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
from state import InertialState,GeographicState
#
##################


##################
# Export section #
#
__all__ = ["TelemetryMessage",
           "CommandMessage",
           "AcknowledgeMessage",
           "ProductMessage",
           "ORBIT_TELEMETRY",
           "INERTIAL_PRODUCT",
           "GEOGRAPHIC_PRODUCT"]
#
##################


####################
# Constant section #
#
__version__ = "1.3"#current version [major.minor]

ORBIT_TELEMETRY = 10
INERTIAL_PRODUCT = 20
GEOGRAPHIC_PRODUCT = 21
#
####################


class BaseMessage(EpochState):
    def __init__(self,epoch,data,type,*args,**kwargs):
        EpochState.__init__(self,epoch,*args,**kwargs)
        
        assert isinstance(type,types.IntType)
        
        self.data = data
        self.type = type

class TelemetryMessage(BaseMessage):
    def __init__(self,epoch,data,type,*args,**kwargs):
        BaseMessage.__init__(self,epoch,data,type,*args,**kwargs)
        
        if type == ORBIT_TELEMETRY:
            self.data = InertialState(**self.data)

class CommandMessage(BaseMessage):pass

class AcknowledgeMessage(BaseMessage):pass

class ProductMessage(BaseMessage):
    def __init__(self,epoch,data,type,*args,**kwargs):
        BaseMessage.__init__(self,epoch,data,type,*args,**kwargs)
        
        if type == INERTIAL_PRODUCT:
            self.data = InertialState(**self.data)
        elif type == GEOGRAPHIC_PRODUCT:
            self.data = GeographicState(**self.data)