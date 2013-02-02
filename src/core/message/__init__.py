#!/usr/bin/env python2.7

"""Core messages

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   02 February 2013

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
from .. import ObjectDict
#
##################


##################
# Export section #
#
__all__ = ["RequestMessage",
           "ResponseMessage"]
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