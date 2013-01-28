#!/usr/bin/env python2.7

"""Message objects

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   27 January 2013

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
from .command import BaseCommand
from .acknowledge import BaseAcknowledge
from .result import BaseResult
#
##################


##################
# Export section #
#
__all__ = ["EpochMessage",
           "StateMessage",
           "CommandMessage",
           "AcknowledgeMessage",
           "ResultMessage"]
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
        
class ResponseMessage(BaseMessage):
    def __init__(self,error,resulttype=None):
        assert isinstance(error,types.IntType) or error is None
        assert isinstance(resulttype,type) or resulttype is None
        
        BaseMessage.__init__(self)
        
        self.error = error
        self.params = resulttype() if isinstance(resulttype,type) else None

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

class CommandMessage(RequestMessage):
    def __init__(self,command):
        assert isinstance(command,BaseCommand)
        
        RequestMessage.__init__(self,"command",ObjectDict)
        
        self.id = command.id
        self.params = command

class AcknowledgeMessage(ResponseMessage):
    def __init__(self,acknowledge):
        assert isinstance(acknowledge,BaseAcknowledge)
        
        ResponseMessage.__init__(self,None,ObjectDict)
        
        self.id = acknowledge.id
        self.result = acknowledge

class ResultMessage(ResponseMessage):
    def __init__(self,result):
        assert isinstance(result,BaseResult)
        
        ResponseMessage.__init__(self,None,ObjectDict)
        
        self.id = result.id
        self.result = result