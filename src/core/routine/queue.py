#!/usr/bin/env python2.7

"""Queue routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   05 February 2013

Provides routines for prioritizing messages queues.

Functions:
put  -- Put to queue
get  -- Get from queue
peek -- Peek at queue

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
from Queue import Queue
import logging
import types

#External libraries
from bson.tz_util import utc

#Internal libraries
from .. import coroutine
from clock.epoch import EpochState
#
##################


##################
# Export section #
#
__all__ = ["put",
           "get",
           "peek"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]

J2000 = datetime(2000,1,1,12,tzinfo=utc)#Julian epoch (2000-01-01T12:00:00Z)
#
####################


@coroutine
def put(queue,pipeline=None,full=None):
    """Story:  Put to queue
    
    IN ORDER TO process important messages first
    AS A generic segment
    I WANT TO prioritize messages in a queue
    
    """
    
    """Specification:  Put to queue
    
    GIVEN a priority queue
        AND a downstream pipeline (default null)
        AND a alternate (if full) pipeline (default null)
        
    Scenario 1:  Upstream message received
    WHEN a message is received from upstream
        AND the message defines an epoch
    THEN lower (earlier) epochs SHALL be given higher priority
        AND the message (with priority) SHALL be added to the queue
        AND the message SHALL be sent downstream
        
    Scenario 2:  Queue is full
    WHEN a message is received from upstream
        AND the queue is full
    THEN the message SHALL be sent downstream (alternate route)
    
    """
    
    #configuration validation
    assert isinstance(queue,Queue)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    flag = True
    message = None
    
    logging.debug("Queue.Put:  Starting")
    while True:
        try:
            message = yield message,pipeline if flag else full
        except GeneratorExit:
            logging.warn("Queue.Put:  Stopping")
            
            #close downstream routines (if they exists)
            pipeline.close() if pipeline is not None else None
            full.close() if full is not None else None
            
            return
        else:
            #input validation
            assert isinstance(message,EpochState)
            
            priority = (message.epoch - J2000).total_seconds()        
            
            if not queue.full():
                queue.put((priority,message))
                        
                logging.info("Queue.Put:  Put message with priority %s" % priority)
                
                flag = True
            else:
                flag = False
                        
                logging.warn("Queue.Put:  Queue is full")

@coroutine
def get(queue,pipeline=None,empty=None):
    """Story:  Get from Queue
    
    IN ORDER TO process important messages first
    AS A generic segment
    I WANT TO retrieve the highest priority message from a queue
    
    """
    
    """Specification:  Get from queue
    
    GIVEN a priority queue
        AND a downstream pipeline (default null)
        AND a alternate (if empty) pipeline (default null)
        
    Scenario 1:  Message requested
    WHEN a message is requested from upstream
    THEN highest priority message SHALL be removed from the queue
        AND the message SHALL be sent downstream
        
    Scenario 2:  Queue is empty
    WHEN a message is requested from upstream
        AND the queue is empty
    THEN a blank message SHALL be sent downstream (alternate route)
    
    """
    
    #configuration validation
    assert isinstance(queue,Queue)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    flag = True
    message = None
    
    logging.debug("Queue.Get:  Starting")
    while True:
        try:
            yield message,pipeline if flag else empty
        except GeneratorExit:
            logging.warn("Queue.Get:  Stopping")
            
            #close downstream routines (if they exists)
            pipeline.close() if pipeline is not None else None
            empty.close() if empty is not None else None
            
            return
        else:
            if not queue.empty(): 
                priority,message = queue.get()
                
                #output validation
                assert isinstance(priority,(types.IntType,types.FloatType))
                        
                logging.info("Queue.Get:  Got message with priority %s" % priority)
                
                flag = True
            else:
                flag = False
                message = None
                        
                logging.warn("Queue.Get:  Queue is empty")

@coroutine
def peek(queue,pipeline=None,empty=None):
    """Story:  Peek at queue
    
    IN ORDER TO validate messages before processing
    AS A generic segment
    I WANT TO know which message is currently the highest priority
    
    """
    
    """Specification:  Peek at queue
    
    GIVEN a priority queue
        AND a downstream pipeline (default null)
        AND a alternate (if empty) pipeline (default null)
        
    Scenario 1:  Message requested
    WHEN a message is requested from upstream
    THEN highest priority message SHALL be copied from the queue
        AND the message SHALL be sent downstream
        
    Scenario 2:  Queue is empty
    WHEN a message is requested from upstream
        AND the queue is empty
    THEN a blank message SHALL be sent downstream (alternate route)
    
    """
    
    #configuration validation
    assert isinstance(queue,Queue)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    flag = True
    message = None
    
    logging.debug("Queue.Peek:  Starting")
    while True:
        try:
            message = yield message,pipeline if flag else empty
        except GeneratorExit:
            logging.warn("Queue.Peek:  Stopping")
            
            #close downstream routines (if they exists)
            pipeline.close() if pipeline is not None else None
            empty.close() if empty is not None else None
            
            return
        else:
            if not queue.empty():           
                priority,message = queue.queue[0]
                
                #output validation
                assert isinstance(priority,(types.IntType,types.FloatType))
                    
                logging.info("Queue.Peek:  Peeked at message with priority %s" % priority)
                
                flag = True
            else:
                flag = False
                message = None
                        
                logging.warn("Queue.Peek:  Queue is empty")