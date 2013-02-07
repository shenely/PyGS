#!/usr/bin/env python2.7

"""View objects

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   06 February 2013

Purpose:    
"""


##################
# Import section #
#
#Built-in libraries
from datetime import datetime
import types

#External libraries

#Internal libraries
from clock.epoch import EpochState
#
##################


##################
# Export section #
#
__all__ = ["BaseView"]
#
##################


####################
# Constant section #
#
__version__ = "0.1"#current version [major.minor]
#
####################


class BaseView(EpochState):
    def __init__(self,epoch,states,type=None,*args,**kwargs):        
        EpochState.__init__(self,epoch,*args,**kwargs)
        
        assert isinstance(type,types.StringTypes) or type is None
        assert isinstance(states,types.ListType)
        assert filter(lambda state:isinstance(state,EpochState),states)
        
        self.type = type
        self.states = states
    
    @staticmethod
    def check(kwargs):
        assert EpochState.check(kwargs)
        assert hasattr(kwargs,"type")
        assert isinstance(kwargs.type,types.StringTypes) or type is None
        assert hasattr(kwargs,"states")
        assert isinstance(kwargs.states,types.ListType)
        assert filter(lambda state:isinstance(state,EpochState),kwargs.states)
        
        return True