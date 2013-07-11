#!/usr/bin/env python2.7

"""State routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   08 July 2013

Provides routines for state manipulation.

Classes:
ParseState  -- Parse state message
FormatState -- Format state message

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-07-11    shenely         1.0         Initial revision

"""


##################
# Import section #
#
#Built-in libraries
import logging
import types

#External libraries

#Internal libraries
from core import encoder,decoder
from core.routine import EventRoutine,ActionRoutine
from .. import InertialState
#
##################


##################
# Export section #
#
__all__ = ["ParseState",
           "FormatState"]
#
##################


####################
# Constant section #
#
__version__ = "1.2"#current version [major.minor]
#
####################


class ParseState(EventRoutine):
    """Story:  Parse state message
    
    IN ORDER TO process messages for synchronizing the current state
    AS A generic segment
    I WANT TO decode the a formatted string as an state
        
    """
    
    """Specification:  Parse state message
    
    GIVEN a downstream pipeline (default null)
        
    Scenario 1:  Upstream message received
    WHEN a message is received from upstream
    THEN the message SHALL be decoded as an state
        AND the state SHALL be sent downstream
    
    """
    
    name = "State.Parse"
    
    def _occur(self,message):
        assert isinstance(message,types.StringTypes)
        
        logging.info("{0}:  Parsing from {1}".\
                     format(self.name,message))
        
        state =  InertialState(**decoder(message))
        
        logging.info("{0}:  Parsed to {1}".\
                     format(self.name,state.epoch))
                     
        return state

class FormatState(ActionRoutine):
    """Story:  Format state message
    
    IN ORDER TO generate messages for distributing the current state
    AS A generic segment
    I WANT TO encode a state in a defined string format
        
    """
    
    """Specification:  Format state message
    
    GIVEN an address for the message envelope
        AND a downstream pipeline (default null)
        
    Scenario 1:  Upstream state received
    WHEN an state is received from upstream
    THEN the state SHALL be encoded as a message
        AND the message SHALL be sent downstream
    
    """
    
    name = "State.Format"
    
    def _execute(self,state):
        assert isinstance(state,InertialState)
        
        logging.info("{0}:  Formatting from {1}".\
                     format(self.name,state.epoch))
        
        message = encoder(state)
        
        logging.info("{0}:  Formatted to {1}".\
                     format(self.name,message))
                     
        return message