#!/usr/bin/env python2.7

"""View messages

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
import types

#External libraries

#Internal libraries
from core import ObjectDict
from core.message import RequestMessage
from clock.epoch import EpochState
from space.state import CartesianState,GeographicState,HorizontalState
#
##################


##################
# Export section #
#
__all__ = ["Global2DView",
           "Global3DView",
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


class BaseView(RequestMessage):
    def __init__(self,objects,method,*args,**kwargs):        
        RequestMessage.__init__(self,method,paramtype=ObjectDict,*args,**kwargs)
        
        assert isinstance(objects,types.ListType)
        assert filter(lambda state:isinstance(state,EpochState),objects)
        
        self.params.epoch = objects[0].epoch if len(objects) > 0 else None 
        self.params.objects = objects

class Global2DView(BaseView):
    def __init__(self,objects,*args,**kwargs):        
        BaseView.__init__(self,objects,"global2d",*args,**kwargs)
        
        assert filter(lambda state:isinstance(state,GeographicState),objects)

class Global3DView(BaseView):
    def __init__(self,objects,*args,**kwargs):
        BaseView.__init__(self,objects,"global3d",*args,**kwargs)
        
        assert filter(lambda state:isinstance(state,CartesianState),objects)

class LocalView(BaseView):
    def __init__(self,objects,*args,**kwargs):
        BaseView.__init__(self,objects,"local",*args,**kwargs)
        
        assert filter(lambda state:isinstance(state,HorizontalState),objects)