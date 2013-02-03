#!/usr/bin/env python2.7

"""Acknowledge messages

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   03 February 2013

Purpose:    
"""


##################
# Import section #
#
#Built-in libraries

#External libraries

#Internal libraries
from core import ObjectDict
from core.message import ResponseMessage
from . import BaseAcknowledge
#
##################


##################
# Export section #
#
__all__ = ["AcknowledgeMessage"]
#
##################


####################
# Constant section #
#
__version__ = "0.1"#current version [major.minor]
#
####################
        

class AcknowledgeMessage(ResponseMessage):
    def __init__(self,result,*args,**kwargs):
        ResponseMessage.__init__(self,*args,**kwargs)
        
        assert isinstance(result,ObjectDict)
        assert hasattr(result,"type")
        
        if not isinstance(result,BaseAcknowledge):
            result = BaseAcknowledge.registry[result.type](result)
        
        self.result = result