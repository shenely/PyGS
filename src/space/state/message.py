#!/usr/bin/env python2.7

"""State message

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
from core.message import RequestMessage
from . import CartesianState
#
##################


##################
# Export section #
#
__all__ = ["StateMessage"]
#
##################


####################
# Constant section #
#
__version__ = "0.1"#current version [major.minor]

EPOCH_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
#
####################


class StateMessage(RequestMessage):
    def __init__(self,state,*args,**kwargs):
        RequestMessage.__init__(self,method="state",*args,**kwargs)
        
        assert isinstance(state,CartesianState)
        
        self.params = state