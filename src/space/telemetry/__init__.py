#!/usr/bin/env python2.7

"""Telemetry objects

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   15 February 2013

Purpose:    
"""


##################
# Import section #
#
#Built-in libraries
import types
import uuid

#External libraries

#Internal libraries
from clock.epoch import EpochState
#
##################


##################
# Export section #
#
__all__ = ["BaseTelemetry",
           "ManeuverTelemetry"]
#
##################


####################
# Constant section #
#
__version__ = "0.1"#current version [major.minor]
#
####################


class BaseTelemetry(EpochState):
    def __init__(self,type,epoch,*args,**kwargs):
        EpochState.__init__(self,epoch,*args,**kwargs)
        
        assert isinstance(type,types.StringTypes)
        
        self.type = type
    
    @staticmethod
    def check(kwargs):
        assert EpochState.check(kwargs)
        assert hasattr(kwargs,"type")
        
        return True

class ManeuverTelemetry(BaseTelemetry):
    def __init__(self,epoch,before,after,*args,**kwargs):
        BaseTelemetry.__init__(self,"maneuver",epoch,*args,**kwargs)
        
        assert isinstance(before,EpochState)
        assert isinstance(after,EpochState)
        
        self.before = before
        self.after = after
    
    @staticmethod
    def check(kwargs):
        assert BaseTelemetry.check(kwargs)
        assert hasattr(kwargs,"before")
        assert hasattr(kwargs,"after")
        
        return True
        