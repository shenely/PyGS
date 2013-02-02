#!/usr/bin/env python2.7

"""Command messages

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
    def __init__(self,command):
        assert isinstance(command,BaseCommand)
        
        RequestMessage.__init__(self,"command")
        
        self.id = command.id
        self.params = command