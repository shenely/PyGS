#!/usr/bin/env python2.7

"""Epoch routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   26 June 2013

Provides routines for order tasks.

Classes:
BeforeEpoch  -- Before reference
AfterEpoch   -- After reference

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-05-14    shenely         1.0         Initial revision
2013-06-26    shenely         1.1         Modifying routine structure

"""


##################
# Import section #
#
#Built-in libraries
from datetime import timedelta
import logging
import types

#External libraries

#Internal libraries
from core import encoder,decoder
from core.routine import EventRoutine,ActionRoutine
from .. import EpochState
#
##################


##################
# Export section #
#
__all__ = ["ParseEpoch",
           "FormatEpoch"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]
#
####################


class ParseEpoch(EventRoutine):
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
        logging.info("{0}:  Parsing from {1}".\
                     format(self.name,message))
        
        epoch =  EpochState(**decoder(message))
        
        logging.info("{0}:  Parsed to {1}".\
                     format(self.name,epoch.epoch))
                     
        return epoch

class FormatEpoch(ActionRoutine):
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
    
    def __init__(self,address):
        assert isinstance(address,basestring)
        
        ActionRoutine.__init__(self)
        
        self.address = address
    
    def _execute(self,epoch):
        
        logging.info("{0}:  Formatting from {1}".\
                     format(self.name,epoch.epoch))
        
        message = encoder(epoch)
        
        logging.info("{0}:  Formatted to {1}".\
                     format(self.name,message))
                     
        return self.address,message