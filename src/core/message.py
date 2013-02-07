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

        
class RequestMessage(BaseObject):
    def __init__(self,method,params=None,*args,**kwargs):
        BaseObject.__init__(self,*args,**kwargs)
        
        assert isinstance(method,types.StringTypes)
        
        self.method = method
        self.params = params
        
class ResponseMessage(BaseObject):
    def __init__(self,result,error=0,*args,**kwargs):
        BaseObject.__init__(self,*args,**kwargs)
        
        assert isinstance(error,types.IntType)
    
        self.result = result
        self.error = error