#!/usr/bin/env python2.7

"""Epoch routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   09 September 2013

Provides routines for order tasks.

Classes:
EpochParse  -- Parse epoch message
EpochFormat -- Format epoch message

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-05-14    shenely         1.0         Initial revision
2013-06-26    shenely         1.1         Modifying routine structure
2013-06-29    shenely                     Accounted for address
2013-06-29    shenely         1.2         Addresses handled by sockets
2013-07-11    shenely                     Added assert statements
2013-09-09    shenely         1.3         Adding persistance logic

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
from core import persist
from .. import EpochState
#
##################


##################
# Export section #
#
__all__ = ["EpochParse",
           "EpochFormat"]
#
##################


####################
# Constant section #
#
__version__ = "1.3"#current version [major.minor]
#
####################


epoch_parse = persist.ObjectPersistance()

@epoch_parse.type(persist.EVENT_OBJECT)
class EpochParse(EventRoutine):
    """Story:  Parse epoch message
    
    IN ORDER TO process messages for synchronizing the current epoch
    AS A generic segment
    I WANT TO decode the a formatted string as an epoch
        
    """
    
    """Specification:  Parse epoch message
    
    GIVEN a downstream pipeline (default null)
        
    Scenario 1:  Upstream message received
    WHEN a message is received from upstream
    THEN the message SHALL be decoded as an epoch
        AND the epoch SHALL be sent downstream
    
    """
    
    name = "Epoch.Parse"
    
    def _occur(self,message):
        assert isinstance(message,types.StringTypes)
        
        logging.info("{0}:  Parsing from {1}".\
                     format(self.name,message))
        
        epoch =  EpochState(**decoder(message))
        
        logging.info("{0}:  Parsed to {1}".\
                     format(self.name,epoch.epoch))
                     
        return epoch


epoch_format = persist.ObjectPersistance()

@epoch_format.type(persist.ACTION_OBJECT)
class EpochFormat(ActionRoutine):
    """Story:  Format epoch message
    
    IN ORDER TO generate messages for distributing the current epoch
    AS A clock segment
    I WANT TO encode a epoch in a defined string format
        
    """
    
    """Specification:  Format epoch message
    
    GIVEN an address for the message envelope
        AND a downstream pipeline (default null)
        
    Scenario 1:  Upstream epoch received
    WHEN an epoch is received from upstream
    THEN the epoch SHALL be encoded as a message
        AND the message SHALL be sent downstream
    
    """
    
    name = "Epoch.Format"
    
    def _execute(self,epoch):
        assert isinstance(epoch,EpochState)
        
        logging.info("{0}:  Formatting from {1}".\
                     format(self.name,epoch.epoch))
        
        message = encoder(epoch)
        
        logging.info("{0}:  Formatted to {1}".\
                     format(self.name,message))
                     
        return message