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
from core import ObjectDict
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


class EpochState(ObjectDict):
    def __init__(self,epoch):
        assert isinstance(epoch,datetime)
        
        self.epoch = epoch
        
    @property
    def epoch(self):
        """State Epoch"""
        
        return self["epoch"]