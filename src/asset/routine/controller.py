#!/usr/bin/env python2.7

"""Controller routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   26 July 2013

Provides routines for controller manipulation.

Classes:
ParseController  -- Parse asset controller

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-07-26    shenely         1.0         Initial revision

"""


##################
# Import section #
#
#Built-in libraries
import logging
import types

#External libraries

#Internal libraries
from core import decoder
from core.routine import EventRoutine
from ..controller import AssetController
#
##################


##################
# Export section #
#
__all__ = ["ParseController"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]
#
####################


class ParseController(EventRoutine):
    """Story:  Parse asset controller
    
    IN ORDER TO process messages for synchronizing the current state
    AS A generic segment
    I WANT TO decode the a formatted string as an state
        
    """
    
    """Specification:  Parse asset controller
    
    GIVEN a downstream pipeline (default null)
        
    Scenario 1:  Upstream message received
    WHEN a message is received from upstream
    THEN the message SHALL be decoded as an state
        AND the state SHALL be sent downstream
    
    """
    
    name = "Controller.Parse"
    
    def __init__(self,segment):
        EventRoutine.__init__(self)
        
        self.segment = segment
    
    def _occur(self,message):
        assert isinstance(message,types.StringTypes)
        
        logging.info("{0}:  Parsing from {1}".\
                     format(self.name,message))
        
        controller =  AssetController(self.segment,**decoder(message))
        
        logging.info("{0}:  Parsed to {1}".\
                     format(self.name,controller.name))
                     
        return controller