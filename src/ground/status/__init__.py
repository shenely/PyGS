#!/usr/bin/env python2.7

"""Status objects

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   11 February 2013

Purpose:    
"""


##################
# Import section #
#
#Built-in libraries
import types

#External libraries

#Internal libraries
from core import ObjectDict
from clock.epoch import EpochState
#
##################


##################
# Export section #
#
__all__ = ["BaseStatus"]
#
##################


####################
# Constant section #
#
__version__ = "0.1"#current version [major.minor]
#
####################


class BaseStatus(EpochState):    
    def __init__(self,type,epoch,*args,**kwargs):
        EpochState.__init__(self,epoch,*args,**kwargs)
        
        assert isinstance(type,types.StringTypes)
        
        self.type = type
    
    @staticmethod
    def check(kwargs):
        assert EpochState.check(kwargs)
        assert hasattr(kwargs,"type")
        
        return True
        