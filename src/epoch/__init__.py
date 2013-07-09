#!/usr/bin/env python2.7

"""Epoch object

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   03 July 2013

Provides the epoch state object.

Classes:
EpochState  -- Epoch state

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-07-03    shenely         1.0         Initial revision

"""


##################
# Import section #
#
#Built-in libraries
from datetime import datetime

#External libraries

#Internal libraries
from core import BaseObject
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
__version__ = "1.0"#current version [major.minor]
#
####################


class EpochState(BaseObject):
    def __init__(self,epoch,*args,**kwargs):
        BaseObject.__init__(self,*args,**kwargs)
        
        assert isinstance(epoch,datetime)
        
        self.epoch = epoch