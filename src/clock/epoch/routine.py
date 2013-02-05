#!/usr/bin/env python2.7

"""Epoch routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   05 February 2013

Provides routines for manipulating epoch data.

Functions:
update -- Update system epoch
format -- Format epoch message
parse  -- Parse epoch message

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-02-05    shenely         1.0         Promoted to version 1.0

"""


##################
# Import section #
#
#Built-in libraries
from datetime import datetime
import logging
import types

#External libraries

#Internal libraries
from core import ObjectDict,coroutine,encoder,decoder
from . import EpochState
from .message import EpochMessage
#
##################


##################
# Export section #
#
__all__ = ["update",
           "format",
           "parse"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]
#
####################


@coroutine
def update(system,pipeline=None):
    """Story:  Update system epoch
    
    IN ORDER TO manage the system state
    AS THE generic segment
    I WANT TO keep the system epoch synchronized with an upstream 
        source
        
    """
    
    """Specification:  Update system epoch
    
    Scenario 1:  Epoch update created
    GIVEN a system state with epoch defined
        AND a pipeline to send epoch to (default None)
    WHEN a epoch update is created
    THEN a epoch update SHALL be activated
        
    Scenario 2:  Upstream epoch received
    GiVEN an active epoch update
    WHEN an epoch is received from an upstream source
    THEN the system epoch SHALL be set to the received epoch
        AND the received epoch SHALL be sent downstream
    
    Scenario 3:  Epoch update destroyed
    GiVEN an active epoch update
    WHEN the epoch update is destroyed
    THEN the downstream routine SHALL be destroyed
        AND the epoch update SHALL deactivated
    
    """
    
    #Configuration validation
    assert isinstance(system,EpochState)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    logging.info("Epoch.Update:  Starting")
    while True:
        try:
            epoch = yield system,pipeline
        except GeneratorExit:
            logging.info("Epoch.Update:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:        
            #input validation
            assert isinstance(epoch,datetime)
            
            system.epoch = epoch
                            
            logging.debug("Epoch.Update:  Updated to %s" % system.epoch)

@coroutine
def format(address,pipeline=None):
    """Story:  Format epoch message
    
    IN ORDER TO generate messages for distributing the current epoch
    AS THE clock segment
    I WANT TO encode the epoch in a defined string format
        
    """
    
    """Specification:  Format epoch message
    
    Scenario 1:  Epoch formatter created
    GIVEN an address for the message envelope
        AND a pipeline to send message to (default None)
    WHEN a epoch formatter is created
    THEN a epoch formatter SHALL be activated
        
    Scenario 2:  Upstream epoch received
    GiVEN an active epoch formatter
    WHEN an epoch is received from an upstream source
    THEN the epoch SHALL be encoded as a message
        AND the encoded message SHALL be sent downstream
    
    Scenario 3:  Epoch formatter destroyed
    GiVEN an active epoch formatter
    WHEN the epoch formatter is destroyed
    THEN the downstream routine SHALL be destroyed
        AND the epoch formatter SHALL deactivated
    
    """
    
    #Configuration validation
    assert isinstance(address,types.StringTypes)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    message = None
    
    logging.info("Epoch.Format:  Starting")
    while True:
        try:
            epoch = yield message,pipeline
        except GeneratorExit:
            logging.info("Epoch.Format:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:        
            #input validation
            assert isinstance(epoch,datetime)
            
            notice = EpochMessage(epoch)
            message = address,encoder(notice)
                            
            logging.debug("Epoch.Format:  Formatted as %s" % notice.params.epoch)

@coroutine
def parse(pipeline=None):
    """Story:  Parse epoch message
    
    IN ORDER TO process messages for synchronizing the current epoch
    AS THE generic segment
    I WANT TO decode the a formatted string as an epoch
        
    """
    
    """Specification:  Parse epoch message
    
    Scenario 1:  Epoch parser created
    GIVEN a pipeline to send epoch to (default None)
    WHEN a epoch parser is created
    THEN a epoch parser SHALL be activated
        
    Scenario 2:  Upstream message received
    GiVEN an active epoch parser
    WHEN an message is received from an upstream source
    THEN the message SHALL be decoded as an epoch
        AND the decoded epoch SHALL be sent downstream
    
    Scenario 3:  Epoch parser destroyed
    GiVEN an active epoch parser
    WHEN the epoch parser is destroyed
    THEN the downstream routine SHALL be destroyed
        AND the epoch parser SHALL deactivated
    
    """
    
    #Configuration validation
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    epoch = None
    
    logging.info("Epoch.Parse:  Starting")
    while True:
        try:
            address,message = yield epoch,pipeline
        except GeneratorExit:
            logging.info("Epoch.Parse:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:        
            assert isinstance(message,types.StringTypes)
        
            notice = decoder(message)
            
            #Output validation
            #NOTE:  this should be handled by the RequestMessage class
            assert hasattr(notice,"method")
            assert notice.method == "epoch"
            assert hasattr(notice,"params")
            assert isinstance(notice.params,ObjectDict)
            assert hasattr(notice.params,"epoch")
            assert isinstance(notice.params.epoch,datetime)
            
            epoch = notice.params.epoch
                            
            logging.debug("Epoch.Parse:  Parsed as %s" % notice.params.epoch)