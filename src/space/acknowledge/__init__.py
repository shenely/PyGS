#!/usr/bin/env python2.7

"""Acknowledge objects

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   03 February 2013

Purpose:    
"""


##################
# Import section #
#
#Built-in libraries
from datetime import datetime
import types
import uuid

#External libraries

#Internal libraries
from core import ObjectDict
from clock.epoch import EpochState
#
##################


##################
# Export section #
#
__all__ = ["BaseAcknowledge",
           "AcceptAcknowledge",
           "RejectAcknowledge"]
#
##################


####################
# Constant section #
#
__version__ = "0.1"#current version [major.minor]
#
####################

class BaseAcknowledge(EpochState):
    registry = dict()
    
    def __init__(self,type,epoch,*args,**kwargs):
        EpochState.__init__(self,epoch,*args,**kwargs)
        
        assert isinstance(type,types.StringTypes)
        
        self.type = type
    
    @staticmethod    
    def check(kwargs):
        assert EpochState.check(kwargs)
        assert hasattr(kwargs,"type")
        
        return True
    
    @classmethod
    def register(cls,key):
        def wrapper(value):
            cls.registry[key] = value.build
            
            return value
        return wrapper
        

@BaseAcknowledge.register("accept")
class AcceptAcknowledge(BaseAcknowledge):
    def __init__(self,epoch,type="accept",*args,**kwargs):
        BaseAcknowledge.__init__(self,type,epoch,*args,**kwargs)

@BaseAcknowledge.register("reject")
class RejectAcknowledge(BaseAcknowledge):
    def __init__(self,epoch,type="accept",*args,**kwargs):
        BaseAcknowledge.__init__(self,type,epoch,*args,**kwargs)
        