#!/usr/bin/env python2.7

"""Ephemeris objects

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   10 February 2013

Purpose:    
"""


##################
# Import section #
#
#Built-in libraries
from datetime import datetime
import types

#External libraries
from bson.objectid import ObjectId 

#Internal libraries
from core import ObjectDict,BaseObject
#
##################


##################
# Export section #
#
__all__ = ["BaseEphemeris"]
#
##################


####################
# Constant section #
#
__version__ = "0.1"#current version [major.minor]
#
####################


class BaseEphemeris(BaseObject):
    def __init__(self,type,epoch,states,*args,**kwargs):
        BaseObject.__init__(self,epoch,*args,**kwargs)
        
        assert isinstance(type,types.StringTypes)
        assert isinstance(epoch,ObjectDict)
        assert hasattr(epoch,"start")
        assert isinstance(epoch.start,datetime)
        assert hasattr(epoch,"end")
        assert isinstance(epoch.end,datetime)
        assert epoch.start < epoch.end
        assert isinstance(states,types.ListType)
        assert filter(lambda state:isinstance(state,ObjectId),states)
        
        self.type = type
        self.epoch = epoch
        self.states = states
    
    @staticmethod
    def check(kwargs):
        assert BaseObject.check(kwargs)
        assert hasattr(kwargs,"epoch")
        assert hasattr(kwargs,"states")
        
        return True