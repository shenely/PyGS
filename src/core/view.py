#!/usr/bin/env python2.7

"""View objects

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   22 January 2013

Purpose:    
"""


##################
# Import section #
#
#Built-in libraries
from datetime import datetime

#External libraries

#Internal libraries
from . import ObjectDict
from .message import RequestMessage
from .state import *
#
##################


##################
# Export section #
#
__all__ = ["GlobalView",
           "LocalView"]
#
##################


####################
# Constant section #
#
__version__ = "0.1"#current version [major.minor]

EPOCH_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
#
####################


class GlobalView(RequestMessage):
    def __init__(self,states):
        assert filter(lambda state:isinstance(state,GeographicState),states)
        
        RequestMessage.__init__(self,"global",ObjectDict)
        
        self.params.epoch = states[0].epoch.strftime(EPOCH_FORMAT) if len(states) > 0 else None 
        self.params.states = states


class LocalView(RequestMessage):
    def __init__(self,states):
        assert filter(lambda state:isinstance(state,HorizontalState),states)
        
        RequestMessage.__init__(self,"local",ObjectDict)
        
        self.params.epoch = states[0].epoch.strftime(EPOCH_FORMAT) if len(states) > 0 else None 
        self.params.states = states