#!/usr/bin/env python2.7

"""Control routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   15 February 2013

Provides routines for controlling the flow of data.

Functions:
split -- Split pipeline
merge -- Merge pipeline
allow -- Allow message
block -- Block message

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-02-05    shenely         1.0         Promoted to version 1.0
2013-02-12                    1.1         Split and merge accept nulls
2013-02-15                    1.2         Adding an allow routine

"""


##################
# Import section #
#
#Built-in libraries
import logging
import types

#External libraries

#Internal libraries
from .. import coroutine
#
##################


##################
# Export section #
#
__all__ = ["split",
           "merge",
           "allow",
           "block"]
#
##################


####################
# Constant section #
#
__version__ = "1.2"#current version [major.minor]
#
####################


@coroutine
def split(ipipe,opipes=None):
    """Story:  Split pipeline
    
    IN ORDER TO distribute messages to multiple downstream sinks
    AS A generic segment
    I WANT TO execute multiple tasks in parallel
    
    """
    
    """Specification:  Split pipeline
    
    GIVEN an upstream pipeline
        AND a list of downstream pipelines (default null)
        
    Scenario 1:  Upstream message received
    WHEN a message is received from the upstream source
    THEN the message SHALL be sent to all listed downstream sinks
    
    """
    
    #configuration validation
    assert isinstance(ipipe,types.GeneratorType) or ipipe is None
    assert isinstance(opipes,types.ListType)
    assert filter(lambda opipe:isinstance(opipe,types.GeneratorType) or opipe is None,opipes) or len(opipes) == 0
    
    message = None
    
    logging.debug("Control.Split:  Starting")
    while True:
        try:
            message = yield message,opipes
        except GeneratorExit:
            logging.warn("Control.Split:  Stopping")
            
            #close downstream routines
            [pipeline.close() for pipeline in opipes] if opipes is not None else None
            
            return
        else:
            logging.info("Control.Split:  %d-way split" % len(opipes))

@coroutine
def merge(ipipes,opipe=None):
    """Story:  Split pipeline
    
    IN ORDER TO aggregate messages from multiple upstream sources
    AS A generic segment
    I WANT TO synchronize tasks that were executing in parallel
    
    """
    
    """Specification:  Merge pipeline
    
    GIVEN a list of upstream pipelines
        AND a downstream pipeline (default null)
        
    Scenario 1:  Upstream message received
    WHEN an message is received from an upstream source
        AND the message count is less than the upstream source number
    THEN the message SHALL be stored internally
        AND the message count SHALL be incremented by one (1)
        
    Scenario 2:  Upstream message received from all sources
    WHEN a message is received from an upstream source
        AND the message count is equal the upstream source number
    THEN the stored messages SHALL be sent to the downstream sink
        AND the message count SHALL be reset to zero (0)
    
    """
    
    #configuration validation
    assert isinstance(ipipes,types.ListType)
    assert filter(lambda ipipe:isinstance(ipipe,types.GeneratorType) or ipipe is None,ipipes) or len(ipipes) == 0
    assert isinstance(opipe,types.GeneratorType) or opipe is None
    
    count = 0
    messages = []
    
    logging.debug("Control.Merge:  Starting")
    while True:
        try:
            if count < len(ipipes)-1:
                message = yield None,None
                count += 1
            else:
                message = yield messages,opipe
                messages = []            
                count = 0
            
                logging.info("Control.Merge:  %d-way merge" % len(ipipes))
        except GeneratorExit:
            ipipes.pop()
            
            if len(ipipes) == 0:
                logging.warn("Control.Merge:  Stopping")
            
                #close downstream routine
                opipe.close() if opipe is not None else None
                
                return
        else:
            messages.append(message)

@coroutine
def allow(pipeline=None):
    """Story:  Allow message
    
    IN ORDER TO couple an upstream source from a downstream sink
    AS A generic segment
    I WANT TO allow messages to flow downstream
    
    """
    
    """Specification:  Allow message
    
    GIVEN a downstream pipeline (default null)
        
    Scenario 1:  Upstream message received
    WHEN a message is received from upstream
    THEN the message SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    logging.debug("Control.Allow:  Starting")
    while True:
        try:
            yield None,pipeline
        except GeneratorExit:
            logging.warn("Control.Allow:  Stopping")
            
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            logging.info("Control.Allow:  Message blocked")

@coroutine
def block(pipeline=None):
    """Story:  Block message
    
    IN ORDER TO decouple an upstream source from a downstream sink
    AS A generic segment
    I WANT TO prevent messages from flowing downstream
    
    """
    
    """Specification:  Block message
    
    GIVEN a downstream pipeline (default null)
        
    Scenario 1:  Upstream message received
    WHEN a message is received from upstream
    THEN a blank message SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    logging.debug("Control.Block:  Starting")
    while True:
        try:
            yield None,pipeline
        except GeneratorExit:
            logging.warn("Control.Block:  Stopping")
            
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            logging.info("Control.Block:  Message blocked")
