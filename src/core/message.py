#!/usr/bin/env python2.7

"""Message objects

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   21 January 2013

Purpose:    
"""


##################
# Import section #
#
#Built-in libraries
import uuid
import types
from datetime import datetime

#External libraries

#Internal libraries
from . import ObjectDict
from .state import CartesianState
#
##################


##################
# Export section #
#
__all__ = ["EpochMessage",
           "StateMessage"]
#
##################


####################
# Constant section #
#
__version__ = "0.1"#current version [major.minor]

EPOCH_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
#
####################


class BaseMessage(ObjectDict):
    def __init__(self):
        self.id = str(uuid.uuid4())
        
class RequestMessage(BaseMessage):
    def __init__(self,method,paramtype=None):
        assert isinstance(method,types.StringTypes)
        assert isinstance(paramtype,type) or paramtype is None
        
        BaseMessage.__init__(self)
        
        self.method = method
        self.params = paramtype() if isinstance(paramtype,type) else None

class EpochMessage(RequestMessage):
    def __init__(self,epoch):
        assert isinstance(epoch,datetime)
        
        RequestMessage.__init__(self,"epoch")
        
        self.params = ObjectDict(epoch=epoch)

class StateMessage(RequestMessage):
    def __init__(self,state):
        assert isinstance(state,CartesianState)
        
        RequestMessage.__init__(self,"state",ObjectDict)        
        
        self.params = state