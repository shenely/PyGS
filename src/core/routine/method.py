#!/usr/bin/env python2.7

"""Method routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   29 June 2013

Provides routines for prioritizing messages queues.

Classes:
ExeciteMethod  -- Execute method

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-06-29    shenely         1.0         Initial revision

"""


##################
# Import section #
#
#Built-in libraries
import logging
import types

#External libraries

#Internal libraries
from . import ActionRoutine
#
##################


##################
# Export section #
#
__all__ = ["ExecuteMethod"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]
#
####################


class ExecuteMethod(ActionRoutine):    
    name = "Method.Execute"
    
    def __init__(self,method):
        assert isinstance(method,types.MethodType)
        
        ActionRoutine.__init__(self)
        
        self.method = method
    
    def _execute(self,message):
        logging.info("{0}:  Executing method".\
                     format(self.name))
        
        message = self.method(message)
        
        logging.info("{0}:  Executed method".\
                     format(self.name))
                     
        return message