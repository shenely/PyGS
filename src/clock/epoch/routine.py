#!/usr/bin/env python2.7

"""Epoch routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   05 February 2013

Provides routines for manipulating epoch data.

Functions:
update -- Update epoch
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
    """Story:  Update epoch
    
    IN ORDER TO manage the system state
    AS A generic segment
    I WANT TO keep the system epoch synchronized with an upstream 
        source
        
    """
    
    """Specification:  Update epoch
    
    GIVEN a system with epoch defined
        AND a downstream pipeline (default null)
        
    Scenario 1:  Upstream epoch received
    WHEN an epoch is received from upstream
    THEN the system epoch SHALL be set to the epoch
        AND the epoch SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(system,EpochState)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    logging.debug("Epoch.Update:  Starting")
    while True:
        try:
            epoch = yield system,pipeline
        except GeneratorExit:
            logging.warn("Epoch.Update:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:        
            #input validation
            assert isinstance(epoch,datetime)
            
            system.epoch = epoch
                            
            logging.info("Epoch.Update:  Updated to %s" % system.epoch)

@coroutine
def format(address,pipeline=None):
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
    
    #Configuration validation
    assert isinstance(address,types.StringTypes)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    message = None
    
    logging.debug("Epoch.Format:  Starting")
    while True:
        try:
            epoch = yield message,pipeline
        except GeneratorExit:
            logging.warn("Epoch.Format:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:        
            #input validation
            assert isinstance(epoch,datetime)
            
            notice = EpochMessage(epoch)
            message = address,encoder(notice)
                            
            logging.info("Epoch.Format:  Formatted as %s" % notice.params.epoch)

@coroutine
def parse(pipeline=None):
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
    
    #Configuration validation
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    epoch = None
    
    logging.debug("Epoch.Parse:  Starting")
    while True:
        try:
            address,message = yield epoch,pipeline
        except GeneratorExit:
            logging.warn("Epoch.Parse:  Stopping")
            
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
                            
            logging.info("Epoch.Parse:  Parsed as %s" % notice.params.epoch)