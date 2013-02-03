#!/usr/bin/env python2.7

"""Command messages

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   03 February 2013

Purpose:    
"""


##################
# Import section #
#
#Built-in libraries

#External libraries

#Internal libraries
from core import ObjectDict
from core.message import RequestMessage
from . import BaseCommand
#
##################


##################
# Export section #
#
__all__ = ["CommandMessage"]
#
##################


####################
# Constant section #
#
__version__ = "0.1"#current version [major.minor]
#
####################
        

class CommandMessage(RequestMessage):
    def __init__(self,params,*args,**kwargs):
        RequestMessage.__init__(self,method="command")
        
        assert isinstance(params,ObjectDict)
        assert hasattr(params,"type")
        
        if not isinstance(params,BaseCommand):
            params = BaseCommand.registry[params.type](params)
        
        self.params = params