#!/usr/bin/env python2.7

"""Acknowledge objects

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
    
    def __init__(self,epoch,id=str(uuid.uuid4())):
        EpochState.__init__(self,epoch)
        
        assert isinstance(id,types.StringTypes)
        
        self.id = id
    
    @classmethod
    def register(cls,key):
        def wrapper(value):
            cls.registry[key] = value.build
            
            return value
        return wrapper
    
    @classmethod    
    def build(cls,result):
        return cls(result.epoch,result.id)
        

@BaseAcknowledge.register("accept")
class AcceptAcknowledge(BaseAcknowledge):
    def __init__(self,epoch,id=str(uuid.uuid4())):
        BaseAcknowledge.__init__(self,epoch,id)
        
        self.message = "accept"

@BaseAcknowledge.register("reject")
class RejectAcknowledge(BaseAcknowledge):
    def __init__(self,epoch,id=str(uuid.uuid4())):
        BaseAcknowledge.__init__(self,epoch,id)
        
        self.message = "reject"
        