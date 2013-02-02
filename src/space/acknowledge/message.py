#!/usr/bin/env python2.7

"""Acknowledge messages

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   02 February 2013

Purpose:    
"""


##################
# Import section #
#
#Built-in libraries

#External libraries

#Internal libraries
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
    def __init__(self,acknowledge):
        assert isinstance(acknowledge,BaseAcknowledge)
        
        ResponseMessage.__init__(self,None)
        
        self.id = acknowledge.id
        self.result = acknowledge