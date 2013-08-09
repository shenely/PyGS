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
from .. import persist
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


execute_method = persist.RoutinePersistance()

@execute_method.type(persist.ACTION_ROUTINE)
class ExecuteMethod(ActionRoutine):    
    name = "Method.Execute"
        
    @execute_method.property
    def method(self):
        return self._method
    
    @method.setter
    def method(self,method):
        assert isinstance(method,types.MethodType)
        
        self._method = method
    
    def _execute(self,message):
        logging.info("{0}:  Executing method".\
                     format(self.name))
        
        message = self._method(message)
        
        logging.info("{0}:  Executed method".\
                     format(self.name))
                     
        return message