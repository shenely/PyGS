#!/usr/bin/env python2.7

"""Acknowledge objects

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   27 January 2013

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
from .state import BaseState
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

class BaseAcknowledge(BaseState):
    registry = dict()
    
    def __init__(self,epoch,id=str(uuid.uuid4())):
        BaseState.__init__(self,epoch)
        
        assert isinstance(id,types.StringTypes)
        
        self.id = id
    
    @classmethod
    def register(cls,key):
        def wrapper(value):
            cls.registry[key] = value
            
            return value
        return wrapper
        

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
        