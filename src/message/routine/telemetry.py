#!/usr/bin/env python2.7

"""Telemetry routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   19 July 2013

Provides routines for telemetry manipulation.

Classes:
ParseTelemetry  -- Parse telemetry message
FormatTelemetry -- Format telemetry message
GenerateTelemetry -- Generate telemetry message
Extract state -- Extract state object

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-07-16    shenely         1.0         Initial revision
2013-07-17    shenely         1.1         Added ExtractState
2013-07-19    shenely         1.2         Mirrored changes in product

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
from .. import TelemetryMessage
from epoch import EpochState
from .. import ORBIT_TELEMETRY
#
##################


##################
# Export section #
#
__all__ = ["ParseTelemetry",
           "FormatTelemetry",
           "GenerateTelemetry",
           "ExtractState"]
#
##################


####################
# Constant section #
#
__version__ = "1.2"#current version [major.minor]
#
####################


class ParseTelemetry(EventRoutine):
    """Story:  Parse telemetry message
    
    IN ORDER TO process messages for synchronizing the current state
    AS A generic segment
    I WANT TO decode the a formatted string as an state
        
    """
    
    """Specification:  Parse telemetry message
    
    GIVEN a downstream pipeline (default null)
        
    Scenario 1:  Upstream message received
    WHEN a message is received from upstream
    THEN the message SHALL be decoded as an state
        AND the state SHALL be sent downstream
    
    """
    
    name = "Telemetry.Parse"
    
    def _occur(self,message):
        assert isinstance(message,types.StringTypes)
        
        logging.info("{0}:  Parsing from {1}".\
                     format(self.name,message))
        
        telemetry =  TelemetryMessage(**decoder(message))
        
        logging.info("{0}:  Parsed to {1}".\
                     format(self.name,telemetry.epoch))
                     
        return telemetry

class FormatTelemetry(ActionRoutine):
    """Story:  Format telemetry message
    
    IN ORDER TO generate messages for distributing the current state
    AS A generic segment
    I WANT TO encode a state in a defined string format
        
    """
    
    """Specification:  Format telemetry message
    
    GIVEN an address for the message envelope
        AND a downstream pipeline (default null)
        
    Scenario 1:  Upstream state received
    WHEN an state is received from upstream
    THEN the state SHALL be encoded as a message
        AND the message SHALL be sent downstream
    
    """
    
    name = "Telemetry.Format"
    
    def _execute(self,telemetry):
        assert isinstance(telemetry,TelemetryMessage)
        
        logging.info("{0}:  Formatting from {1}".\
                     format(self.name,telemetry.epoch))
        
        message = encoder(telemetry)
        
        logging.info("{0}:  Formatted to {1}".\
                     format(self.name,message))
                     
        return message

class GenerateTelemetry(ActionRoutine):
    """Story:  Generate telemetry message
    
    IN ORDER TO 
    AS A 
    I WANT TO 
        
    """
    
    """Specification:  Generate telemetry message
    
    GIVEN 
        
    Scenario 1:  
    WHEN 
    THEN 
    
    """
    
    name = "Telemetry.Generate"
    
    def __init__(self,type):
        ActionRoutine.__init__(self)
        
        assert isinstance(type,types.IntType)
        
        self.type = type
    
    def _execute(self,message):
        assert isinstance(message,EpochState)
        
        epoch = message.epoch
        
        telemetry = TelemetryMessage(epoch,message,self.type)
        
        logging.info("{0}:  Formatted at {1}".\
                     format(self.name,telemetry.epoch))
                     
        return telemetry

class ExtractState(EventRoutine):
    """Story:  Extract state object
    
    IN ORDER TO 
    AS A 
    I WANT TO 
        
    """
    
    """Specification:  Extract state object
    
    GIVEN 
        
    Scenario 1:  
    WHEN 
    THEN 
    
    """
    
    name = "State.Extract"
    
    def _occur(self,message):
        assert isinstance(message,TelemetryMessage)
        assert message.type == ORBIT_TELEMETRY
        
        state = message.data
        
        return state