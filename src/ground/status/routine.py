#!/usr/bin/env python2.7

"""Status routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   11 February 2013

Provides routines for broadcasting statuses.

Functions:
format  -- Format status message
parse   -- Parse status message

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-02-11    shenely         1.0         Initial revision

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
from core import coroutine,encoder,decoder
from core.message import RequestMessage
from clock.epoch import EpochState
from . import BaseStatus
from space.result import BaseResult
#
##################


##################
# Export section #
#
__all__ = ["format",
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
    """Story:  Update status
    
    IN ORDER TO manage a system status
    AS A user segment
    I WANT TO update the status after a notification
        
    """
    
    """Specification:  Update status
    
    GIVEN a system with status defined
        AND a downstream pipeline (default null)
        
    Scenario 1:  Upstream state received
    WHEN an status is received from upstream
    THEN the system status SHALL be set to the status
        AND the status SHALL be sent downstream
    
    """
    
    assert isinstance(system,BaseStatus)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    logging.debug("Status.Update:  Starting")
    while True:
        try:
            status = yield system,pipeline
        except GeneratorExit:
            logging.warn("Status.Update:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            assert isinstance(status,type(system))
            
            system.update(status)
                            
            logging.info("Status.Update:  Updated")

@coroutine
def format(address,pipeline=None):
    """Story:  Format status message
    
    IN ORDER TO generate messages for notifying a user segment
    AS A ground segment
    I WANT TO encode a status in a defined string format
        
    """
    
    """Specification:  Format status message
    
    GIVEN an address for the message envelope
        AND a downstream pipeline (default null)
        
    Scenario 1:  Upstream status received
    WHEN a status is received from upstream
    THEN the status SHALL be encoded as a message
        AND the message SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(address,types.StringTypes)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    message = None
        
    logging.debug("Status.Format:  Starting")
    while True:
        try:
            status = yield message,pipeline
        except GeneratorExit:
            logging.warn("Status.Format:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            #input validation
            assert isinstance(status,BaseStatus)
            
            notice = RequestMessage("status",status)
            message = address,encoder(notice)
                            
            logging.info("Status.Format:  Formatted")

@coroutine
def parse(pipeline=None):
    """Parse status message
    
    IN ORDER TO process messages for updating the user segment
    AS A user segment
    I WANT TO decode the a formatted string as a status
        
    """
    
    """Specification:  Parse status message
    
    GIVEN a downstream pipeline (default null)
        
    Scenario 1:  Upstream message received
    WHEN a message is received from upstream
    THEN the message SHALL be decoded as an status
        AND the status SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    status = None
        
    logging.debug("Status.Parse:  Starting")
    while True:
        try:
            address,message = yield status,pipeline
        except GeneratorExit:
            logging.warn("Status.Parse:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            #input validation
            assert isinstance(message,types.StringTypes)
                    
            notice = RequestMessage(**decoder(message))
            
            #output validation
            assert notice.method == "status"
            status = BaseStatus.build(notice.params)
                    
            logging.info("Status.Parse:  Parsed")