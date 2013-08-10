#!/usr/bin/env python2.7

"""Queue routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   10 August 2013

Provides routines for messages queues.

Classes:
QueueGet  -- Get from queue
QueuePut  -- Put to queue

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-05-02    shenely         1.0         Initial revision
2013-06-26    shenely         1.1         Modifying routine structure
2013-08-09    shenely         1.2         Adding persistance logic
2013-08-10    shenely         1.3         Removed epoch dependency

"""


##################
# Import section #
#
#Built-in libraries
from Queue import Queue,PriorityQueue
import logging
import types

#External libraries

#Internal libraries
from . import EventRoutine,ActionRoutine
from .. import persist
#
##################


##################
# Export section #
#
__all__ = ["QueueObject",
           "QueueGet",
           "QueuePut"]
#
##################


####################
# Constant section #
#
__version__ = "1.3"#current version [major.minor]
#
####################


queue_object = persist.ObjectPersistance()

@queue_object.type(persist.GENERAL_OBJECT)
class QueueObject(object):
    @queue_object.property
    def type(self):
        if isinstance(self._queue,Queue):
            return "standard"
        elif isinstance(self._queue,PriorityQueue):
            return "priority"
    
    @type.setter
    def type(self,type):
        assert isinstance(type,types.StringTypes)
        
        if type == "standard":
            self._queue = Queue()
        elif type == "priority":
            self._queue = PriorityQueue()
        
    @queue_object.property
    def queue(self):
        return self._queue
    
    @queue.setter
    def queue(self,queue):
        self._queue = queue


queue_get = persist.ObjectPersistance()

@queue_get.type(persist.EVENT_OBJECT)
class QueueGet(EventRoutine):
    """Story:  Get from Queue
    
    IN ORDER TO process messages
    AS A generic segment
    I WANT TO retrieve the next message from a queue
    
    """
    
    """Specification:  Get from queue
    
    GIVEN a queue
        AND a downstream pipeline (default null)
        AND a alternate (if empty) pipeline (default null)
        
    Scenario 1:  Message requested
    WHEN a message is requested from upstream
    THEN first message SHALL be removed from the queue
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
            message = self._queue.get()
                                
            logging.info("{0}:  Got from queue".\
                         format(self.name))
            
            return message
        else:
            logging.warn("{0}:  Queue is empty".\
                         format(self.name))


queue_put = persist.ObjectPersistance()

@queue_put.type(persist.ACTION_OBJECT)
class QueuePut(ActionRoutine):
    """Story:  Put to queue
    
    IN ORDER TO process messages
    AS A generic segment
    I WANT TO queue messages
    
    """
    
    """Specification:  Put to queue
    
    GIVEN a queue
        AND a downstream pipeline (default null)
        AND a alternate (if full) pipeline (default null)
        
    Scenario 1:  Upstream message received
    WHEN a message is received from upstream
    THEN the message SHALL be added to the queue
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
        if not self._queue.full():
            self._queue.put(message)
                    
            logging.info("{0}:  Put to queue".\
                         format(self.name))
            
            return message
        else:                    
            logging.warn("{0}:  Queue is full".\
                         format(self.name))