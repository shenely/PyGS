#!/usr/bin/env python2.7

"""View objects

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   16 January 2013

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
from .state import GeographicState
#
##################


##################
# Export section #
#
__all__ = ["GlobalView"]
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
        #assert isinstance(epoch,datetime)
        #assert isinstance(state,GeographicState)
        
        RequestMessage.__init__(self,"global",ObjectDict)
        
        self.params.epoch = states[0].epoch.strftime(EPOCH_FORMAT) if len(states) > 0 else None 
        self.params.states = [{"arc":state.arc,"long":state.long,"lat":state.lat} for state in states]