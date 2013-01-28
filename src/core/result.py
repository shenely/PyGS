#!/usr/bin/env python2.7

"""Result objects

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   27 January 2013

Purpose:    
"""


##################
# Import section #
#
#Built-in libraries
import types
import uuid

#External libraries

#Internal libraries
from .state import BaseState
#
##################


##################
# Export section #
#
__all__ = ["BaseResult",
           "ManeuverResult"]
#
##################


####################
# Constant section #
#
__version__ = "0.1"#current version [major.minor]
#
####################


class BaseResult(BaseState):
    def __init__(self,epoch,id=str(uuid.uuid4())):
        BaseState.__init__(self,epoch)
        
        assert isinstance(id,types.StringTypes)
        
        self.id = id

class ManeuverResult(BaseResult):
    def __init__(self,epoch,before,after,id=str(uuid.uuid4())):
        BaseResult.__init__(self,epoch,id)
        
        assert isinstance(before,BaseState)
        assert isinstance(after,BaseState)
        