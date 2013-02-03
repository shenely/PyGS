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
from . import ObjectDict,BaseObject
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


class BaseMessage(BaseObject):pass
        
class RequestMessage(BaseMessage):
    def __init__(self,method,paramtype=None,*args,**kwargs):
        BaseMessage.__init__(self,*args,**kwargs)
        
        assert isinstance(method,types.StringTypes)
        assert isinstance(paramtype,type) or paramtype is None
        
        self.method = method
        self.params = paramtype() if isinstance(paramtype,type) else None
        
class ResponseMessage(BaseMessage):
    def __init__(self,error=0,resulttype=None,*args,**kwargs):
        BaseMessage.__init__(self,*args,**kwargs)
        
        assert isinstance(error,types.IntType) or error is None
        assert isinstance(resulttype,type) or resulttype is None
        
        self.error = error
        self.result = resulttype() if isinstance(resulttype,type) else None