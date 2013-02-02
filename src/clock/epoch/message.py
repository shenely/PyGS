#!/usr/bin/env python2.7

"""Epoch messages

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
from core.message import RequestMessage
from space.state import BaseState
#
##################


##################
# Export section #
#
__all__ = ["EpochMessage"]
#
##################


####################
# Constant section #
#
__version__ = "0.1"#current version [major.minor]
#
####################
        

class EpochMessage(RequestMessage):
    def __init__(self,epoch):
        assert isinstance(epoch,datetime)
        
        RequestMessage.__init__(self,"epoch")
        
        self.params = BaseState(epoch=epoch)