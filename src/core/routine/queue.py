#!/usr/bin/env python2.7

"""Queue routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   09 August 2013

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
2013-08-09    shenely         1.2         Adding persistance logic

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
from .. import persist
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
__version__ = "1.2"#current version [major.minor]

J2000 = datetime(2000,1,1,12,tzinfo=utc)#Julian epoch (2000-01-01T12:00:00Z)
#
####################


queue_get = persist.RoutinePersistance()

@queue_get.type(persist.EVENT_ROUTINE)
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
        
    @queue_get.property
    def queue(self):
        return self._queue
    
    @queue.setter
    def queue(self,queue):
        assert isinstance(queue,Queue)
        
        self._queue = queue
    
    def _occur(self,message):
        if not self._queue.empty(): 
            priority,message = self._queue.get()
            
            assert isinstance(priority,(types.IntType,types.FloatType))
                    
            logging.info("{0}:  Got with priority {1}".\
                         format(self.name,priority))
            
            return message
        else:
            logging.warn("{0}:  Queue is empty".\
                         format(self.name))


queue_put = persist.RoutinePersistance()

@queue_put.type(persist.ACTION_ROUTINE)
class QueuePut(ActionRoutine):
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
        
    @queue_get.property
    def queue(self):
        return self._queue
    
    @queue.setter
    def queue(self,queue):
        assert isinstance(queue,Queue)
        
        self._queue = queue
    
    def _execute(self,message):
        assert isinstance(message,EpochState)#TODO:  Create EpochState (also, rename)
        
        priority = (message.epoch - J2000).total_seconds()        
        
        if not self._queue.full():
            self._queue.put((priority,message))
                    
            logging.info("{0}:  Put with priority {1}".\
                         format(self.name,priority))
            
            return message
        else:                    
            logging.warn("{0}:  Queue is full".\
                         format(self.name))