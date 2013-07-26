#!/usr/bin/env python2.7

"""Model routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   26 July 2013

Provides routines for model manipulation.

Classes:
ParseModel  -- Parse asset model

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
from ..model import AssetModel
#
##################


##################
# Export section #
#
__all__ = ["ParseModel"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]
#
####################


class ParseModel(EventRoutine):
    """Story:  Parse asset model
    
    IN ORDER TO process messages for synchronizing the current state
    AS A generic segment
    I WANT TO decode the a formatted string as an state
        
    """
    
    """Specification:  Parse asset model
    
    GIVEN a downstream pipeline (default null)
        
    Scenario 1:  Upstream message received
    WHEN a message is received from upstream
    THEN the message SHALL be decoded as an state
        AND the state SHALL be sent downstream
    
    """
    
    name = "Model.Parse"
    
    def __init__(self,segment):
        EventRoutine.__init__(self)
        
        self.segment = segment
    
    def _occur(self,message):
        assert isinstance(message,types.StringTypes)
        
        logging.info("{0}:  Parsing from {1}".\
                     format(self.name,message))
        
        model =  AssetModel(self.segment,**decoder(message))
        
        logging.info("{0}:  Parsed to {1}".\
                     format(self.name,model.name))
                     
        return model