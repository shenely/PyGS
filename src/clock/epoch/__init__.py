#!/usr/bin/env python2.7

"""Epoch objects

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   02 February 2013

Purpose:    
"""


##################
# Import section #
#
#Built-in libraries
from datetime import datetime

#External libraries

#Internal libraries
from core import ObjectDict,BaseObject
#
##################


##################
# Export section #
#
__all__ = ["EpochState"]
#
##################


####################
# Constant section #
#
__version__ = "0.1"#current version [major.minor]
#
####################


class EpochState(BaseObject):
    def __init__(self,epoch,*args,**kwargs):
        BaseObject.__init__(self,*args,**kwargs)
        
        assert isinstance(epoch,datetime)
        
        self.epoch = epoch
    
    @staticmethod
    def check(kwargs):
        assert BaseObject.check(kwargs)
        assert hasattr(kwargs,"epoch")
        
        return True