#!/usr/bin/env python2.7

"""Notice objects

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   12 February 2013

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
from space import Spacecraft
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
    def __init__(self,epoch,assets,type=None,*args,**kwargs):        
        EpochState.__init__(self,epoch,*args,**kwargs)
        
        assert isinstance(type,types.StringTypes) or type is None
        assert isinstance(assets,types.ListType)
        assert filter(lambda asset:isinstance(asset,Spacecraft),assets)
        
        self.type = type
        self.assets = assets
    
    @staticmethod
    def check(kwargs):
        assert EpochState.check(kwargs)
        assert hasattr(kwargs,"type")
        assert isinstance(kwargs.type,types.StringTypes) or type is None
        assert hasattr(kwargs,"assets")
        assert isinstance(kwargs.assets,types.ListType)
        assert filter(lambda asset:isinstance(asset,Spacecraft),kwargs.assets)
        
        return True