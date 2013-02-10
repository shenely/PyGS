#!/usr/bin/env python2.7

"""State routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   10 February 2013

Provides routines for manipulating states.

Functions:
update -- Update state
format -- Format state message
parse  -- Parse state message

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-02-06    shenely         1.0         Promoted to version 1.0
2013-02-10                                Using InertialState now

"""


##################
# Import section #
#
#Built-in libraries
from datetime import datetime
import logging
import types

#External libraries
from numpy import matrix

#Internal libraries
from core import ObjectDict,coroutine,encoder,decoder
from core.message import RequestMessage
from clock.epoch import EpochState
from .. import InertialState
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
    """Story:  Update state
    
    IN ORDER TO manage a system state
    AS A space segment
    I WANT TO update the state after commanding or propagation
        
    """
    
    """Specification:  Update state
    
    GIVEN a system with epoch defined
        AND a downstream pipeline (default null)
        
    Scenario 1:  Upstream state received
    WHEN an state is received from upstream
    THEN the system state SHALL be set to the state
        AND the state SHALL be sent downstream
    
    """
    
    assert isinstance(system,EpochState)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    logging.debug("State.Format:  Starting")
    while True:
        try:
            state = yield system,pipeline
        except GeneratorExit:
            logging.warn("Epoch.Parse:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            assert isinstance(state,type(system))
            
            system.update(state)
                            
            logging.info("Space.State:  Updated to %s" % system.epoch)

@coroutine
def format(address,pipeline=None):
    """Story:  Format state message
    
    IN ORDER TO generate messages for distributing the current state
    AS A space segment
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
    
    #input validation
    assert isinstance(address,types.StringTypes)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    message = None
    
    logging.debug("State.Format:  Starting")
    while True:
        try:
            state = yield message,pipeline
        except GeneratorExit:
            logging.warn("Epoch.Parse:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            assert isinstance(state,InertialState)
            
            notice = RequestMessage("state",state)
            message = address,encoder(notice)
                            
            logging.info("State.Format:  Formatted")

@coroutine
def parse(pipeline=None):
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
    
    #input validation
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    state = None
    
    logging.debug("State.Parse:  Starting")
    while True:
        try:
            address,message = yield state,pipeline
        except GeneratorExit:
            logging.warn("Epoch.Parse:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            #input validation
            assert isinstance(message,types.StringTypes)
            
            notice = RequestMessage(**decoder(message))
            
            #output validation
            assert notice.method == "state"
            state = InertialState(**notice.params)
                    
            logging.info("Space.State:  Parsed")