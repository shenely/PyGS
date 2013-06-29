#!/usr/bin/env python2.7

"""Queue routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   26 June 2013

Provides routines for prioritizing messages queues.

Classes:
GetQueue  -- Get from queue
PutQueue  -- Put to queue

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-05-02    shenely         1.0         Initial revision
2013-06-26    shenely         1.1         Modifying routine structure

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
from . import EventRoutine,ActionRoutine
from epoch import EpochState
#
##################


##################
# Export section #
#
__all__ = ["GetQueue",
           "PutQueue"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]

J2000 = datetime(2000,1,1,12,tzinfo=utc)#Julian epoch (2000-01-01T12:00:00Z)
#
####################


class GetQueue(EventRoutine):
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
    
    name = "Queue.Get"
    
    def __init__(self,queue):
        assert isinstance(queue,Queue)
        
        EventRoutine.__init__(self)
        
        self.queue = queue
    
    def _occur(self,message):
        if not self.queue.empty(): 
            priority,message = self.queue.get()
            
            assert isinstance(priority,(types.IntType,types.FloatType))
                    
            logging.info("{0}:  Got with priority {1}".\
                         format(self.name,priority))
            
            return message
        else:
            logging.warn("{0}:  Queue is empty".\
                         format(self.name))

class PutQueue(ActionRoutine):
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
    
    name = "Queue.Put"
    
    def __init__(self,queue):
        assert isinstance(queue,Queue)
        
        ActionRoutine.__init__(self)
        
        self.queue = queue
    
    def _execute(self,message):
        assert isinstance(message,EpochState)#TODO:  Create EpochState (also, rename)
        
        priority = (message.epoch - J2000).total_seconds()        
        
        if not self.queue.full():
            self.queue.put((priority,message))
                    
            logging.info("{0}:  Put with priority {1}".\
                         format(self.name,priority))
            
            return message
        else:                    
            logging.warn("{0}:  Queue is full".\
                         format(self.name))