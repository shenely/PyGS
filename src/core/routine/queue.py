#!/usr/bin/env python2.7

"""Queue routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   02 February 2013

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
__version__ = "0.1"#current version [major.minor]

J2000 = datetime(2000,1,1,12)
#
####################


@coroutine
def put(queue,pipeline=None,full=None):
    """Put Message into Queue"""
    
    assert isinstance(queue,Queue)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    flag = True
    message = None
    while True:
        message = yield message,pipeline if flag else full
                
        assert isinstance(message,EpochState)
        
        priority = (message.epoch - J2000).total_seconds()        
        
        if not queue.full():
            queue.put((priority,message))
                    
            logging.info("Routine.Queue:  Put message with priority %s" % priority)
            
            flag = True
        else:
            flag = False

@coroutine
def get(queue,pipeline=None,empty=None):
    """Get Message from Queue"""
    
    assert isinstance(queue,Queue)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    flag = True
    message = None
    while True:
        message = yield message,pipeline if flag else empty
        
        if not queue.empty(): 
            priority,message = queue.get()
            
            assert isinstance(priority,(types.IntType,types.FloatType))
                    
            logging.info("Routine.Queue:  Got message with priority %s" % priority)
            
            flag = True
        else:
            flag = False

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