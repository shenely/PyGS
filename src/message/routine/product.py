#!/usr/bin/env python2.7

"""Product routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   17 July 2013

Provides routines for product manipulation.

Classes:
ParseProduct  -- Parse product message
FormatProduct -- Format product message
GenerateProduct -- Generate product message

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-07-17    shenely         1.0         Initial revision

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
from .. import ProductMessage
from epoch import EpochState
#
##################


##################
# Export section #
#
__all__ = ["ParseProduct",
           "FormatProduct",
           "GenerateProduct"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]
#
####################


class ParseProduct(EventRoutine):
    """Story:  Parse product message
    
    IN ORDER TO process messages for synchronizing the current state
    AS A generic segment
    I WANT TO decode the a formatted string as an state
        
    """
    
    """Specification:  Parse product message
    
    GIVEN a downstream pipeline (default null)
        
    Scenario 1:  Upstream message received
    WHEN a message is received from upstream
    THEN the message SHALL be decoded as an state
        AND the state SHALL be sent downstream
    
    """
    
    name = "Product.Parse"
    
    def _occur(self,message):
        assert isinstance(message,types.StringTypes)
        
        logging.info("{0}:  Parsing from {1}".\
                     format(self.name,message))
        
        telemetry =  ProductMessage(**decoder(message))
        
        logging.info("{0}:  Parsed to {1}".\
                     format(self.name,telemetry.epoch))
                     
        return telemetry

class FormatProduct(ActionRoutine):
    """Story:  Format product message
    
    IN ORDER TO generate messages for distributing the current state
    AS A generic segment
    I WANT TO encode a state in a defined string format
        
    """
    
    """Specification:  Format product message
    
    GIVEN an address for the message envelope
        AND a downstream pipeline (default null)
        
    Scenario 1:  Upstream state received
    WHEN an state is received from upstream
    THEN the state SHALL be encoded as a message
        AND the message SHALL be sent downstream
    
    """
    
    name = "Product.Format"
    
    def _execute(self,telemetry):
        assert isinstance(telemetry,ProductMessage)
        
        logging.info("{0}:  Formatting from {1}".\
                     format(self.name,telemetry.epoch))
        
        message = encoder(telemetry)
        
        logging.info("{0}:  Formatted to {1}".\
                     format(self.name,message))
                     
        return message

class GenerateProduct(ActionRoutine):
    """Story:  Generate product message
    
    IN ORDER TO 
    AS A 
    I WANT TO 
        
    """
    
    """Specification:  Generate product message
    
    GIVEN 
        
    Scenario 1:  
    WHEN 
    THEN 
    
    """
    
    name = "Product.Generate"
    
    def __init__(self,type):
        ActionRoutine.__init__(self)
        
        assert isinstance(type,types.IntType)
        
        self.type = type
    
    def _execute(self,message):
        assert isinstance(message,EpochState)
        
        epoch = message.epoch
        
        product = ProductMessage(epoch,message,self.type)
        
        logging.info("{0}:  Formatted at {1}".\
                     format(self.name,product.epoch))
                     
        return product