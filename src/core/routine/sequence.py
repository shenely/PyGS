#!/usr/bin/env python2.7

"""Sequence routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   05 February 2013

Provides routines for sequencing tasks.

Functions:
before  -- Before reference
after   -- After reference
around  -- Around reference

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
from datetime import timedelta
import logging
import types

#External libraries

#Internal libraries
from .. import coroutine
from clock.epoch import EpochState
#
##################


##################
# Export section #
#
__all__ = ["before",
           "after",
           "around"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]
#
####################


@coroutine
def before(reference,margin,istrue=None,isfalse=None):
    """Story:  Before reference
    
    IN ORDER TO execute tasks at specific time frames
    AS A generic segment
    I WANT TO only process messages before a reference time
    
    """
    
    """Specification:  Before reference
    
    GIVEN a reference with epoch defined
        AND a time margin
        AND a true downstream pipeline (default null)
        AND a false downstream pipeline (default null)
        
    Scenario 1:  Upstream message received before reference
    WHEN a message is received from upstream
        AND the message defines an epoch
        AND the message epoch is before the reference epoch by a margin
    THEN the message SHALL be sent to the true upstream
        
    Scenario 2:  Upstream message received after reference
    WHEN a message is received from upstream
        AND the message defines an epoch
        AND the message epoch is after the reference epoch by a margin
    THEN the message SHALL be sent to the false upstream
    
    """
    
    #configuration validation
    assert isinstance(reference,EpochState)
    assert isinstance(margin,timedelta)
    assert istrue is None or isinstance(istrue,types.GeneratorType)
    assert isfalse is None or isinstance(isfalse,types.GeneratorType)
    
    message,pipeline = None,None
    
    logging.debug("Epoch.Before:  Starting")
    while True:
        try:
            message = yield message,pipeline
        except GeneratorExit:
            logging.warn("Epoch.Before:  Stopping")
            
            #close downstream routines (if they exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:        
            #input validation
            assert isinstance(message,EpochState)
    
            pipeline = istrue \
                       if (message.epoch < reference.epoch - margin) \
                       else isfalse
                    
            logging.info("Epoch.Before:  %s", pipeline is istrue)
    
@coroutine
def after(reference,margin,istrue=None,isfalse=None):
    """Story:  After reference
    
    IN ORDER TO execute tasks at specific time frames
    AS A generic segment
    I WANT TO only process messages after a reference time
    
    """
    
    """Specification:  After reference
    
    GIVEN a reference with epoch defined
        AND a time margin
        AND a true downstream pipeline (default null)
        AND a false downstream pipeline (default null)
        
    Scenario 1:  Upstream message received before reference
    WHEN a message is received from upstream
        AND the message defines an epoch
        AND the message epoch is before the reference epoch by a margin
    THEN the message SHALL be sent to the false upstream
        
    Scenario 2:  Upstream message received after reference
    WHEN a message is received from upstream
        AND the message defines an epoch
        AND the message epoch is after the reference epoch by a margin
    THEN the message SHALL be sent to the true upstream
    
    """
    
    #configuration validation
    assert isinstance(reference,EpochState)
    assert isinstance(margin,timedelta)
    assert isinstance(istrue,types.GeneratorType) or istrue is None
    assert isinstance(isfalse,types.GeneratorType) or isfalse is None
    
    message,pipeline = None,None
    
    logging.debug("Epoch.After:  Starting")
    while True:
        try:
            message = yield message,pipeline
        except GeneratorExit:
            logging.warn("Epoch.After:  Stopping")
            
            #close downstream routines (if they exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:    
            #input validation
            assert isinstance(message,EpochState)
            
            pipeline = istrue \
                       if (message.epoch > reference.epoch + margin) \
                       else isfalse
                    
            logging.info("Epoch.After:  %s", pipeline is istrue)

@coroutine
def around(reference,margin,istrue=None,isfalse=None):
    """Story:  Around reference
    
    IN ORDER TO execute tasks at specific time frames
    AS A generic segment
    I WANT TO only process messages around a reference time
    
    """
    
    """Specification:  Around reference
    
    GIVEN a reference with epoch defined
        AND a time margin
        AND a true downstream pipeline (default null)
        AND a false downstream pipeline (default null)
        
    Scenario 1:  Upstream message received around reference
    WHEN a message is received from upstream
        AND the message defines an epoch
        AND the message epoch is around the reference epoch by a margin
    THEN the message SHALL be sent to the true upstream
        
    Scenario 2:  Upstream message received beyond reference
    WHEN a message is received from upstream
        AND the message defines an epoch
        AND the message epoch is beyond the reference epoch by a margin
    THEN the message SHALL be sent to the false upstream
    
    """
    
    #configuration validation
    assert isinstance(reference,EpochState)
    assert isinstance(margin,timedelta)
    assert isinstance(istrue,types.GeneratorType) or istrue is None
    assert isinstance(isfalse,types.GeneratorType) or isfalse is None
    
    message,pipeline = None,None
    
    logging.debug("Epoch.Around:  Starting")
    while True:
        try:
            message = yield message,pipeline
        except GeneratorExit:
            logging.warn("Epoch.Around:  Stopping")
            
            #close downstream routines (if they exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            #input validation
            assert isinstance(message,EpochState)
        
            pipeline = istrue \
                       if (message.epoch < reference.epoch + margin) or \
                          (message.epoch > reference.epoch - margin) \
                       else isfalse
                    
            logging.info("Epoch.Around:  %s", pipeline is istrue)