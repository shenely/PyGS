#!/usr/bin/env python2.7

"""Queue routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   16 January 2013

Purpose:    
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

#Internal libraries
from . import coroutine
from ..core.state import BaseState
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
__version__ = "0.1"#current version [major.minor]

J2000 = datetime(2000,1,1,12)
#
####################


@coroutine
def put(queue,pipeline=None):
    """Put Message into Queue"""
    
    assert isinstance(queue,Queue)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    message = None
    while True:
        message = yield message,pipeline
                
        assert isinstance(message,BaseState)
        
        priority = (message.epoch - J2000).total_seconds()
        
        queue.put((priority,message))
                
        logging.info("Routine.Queue:  Put message with priority %s" % priority)

@coroutine
def get(queue,pipeline=None):
    """Get Message from Queue"""
    
    assert isinstance(queue,Queue)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    message = None
    while True:
        yield message,pipeline
        
        priority,message = queue.get()
        
        assert isinstance(priority,(types.IntType,types.FloatType))
                
        logging.info("Routine.Queue:  Got message with priority %s" % priority)

def push():pass

def pop():pass

@coroutine
def peek(queue,pipeline=None,empty=None):
    """Peek at Message in Queue"""
    
    assert isinstance(queue,Queue)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    message = None
    while True:
        if not queue.empty():
            yield message,pipeline
        else:
            yield message,empty
            
        if not queue.empty():           
            priority,message = queue.queue[0]
            
            assert isinstance(priority,(types.IntType,types.FloatType))
                
            logging.info("Routine.Queue:  Peeked at message with priority %s" % priority)