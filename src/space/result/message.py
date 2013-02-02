#!/usr/bin/env python2.7

"""Result messages

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   02 February 2013

Purpose:    
"""


##################
# Import section #
#
#Built-in libraries

#External libraries

#Internal libraries
from core.message import ResponseMessage
from . import BaseResult
#
##################


##################
# Export section #
#
__all__ = ["ResultMessage"]
#
##################


####################
# Constant section #
#
__version__ = "0.1"#current version [major.minor]
#
####################
        

class ResultMessage(ResponseMessage):
    def __init__(self,result):
        assert isinstance(result,BaseResult)
        
        ResponseMessage.__init__(self,None)
        
        self.id = result.id
        self.result = result