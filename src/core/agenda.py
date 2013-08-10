#!/usr/bin/env python2.7

"""Agenda service

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   16 July 2013

Provides a agenda service.

Classes:
Scheduler -- Scheduler
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-06-27    shenely         1.0         Initial revision
2013-06-29    shenely         1.1         Refactored to agenda
2013-06-29    shenely         1.2         Generalized to processor
2013-07-16    shenely         1.3         Fixed pipe issue

"""


##################
# Import section #
#
#Built-in libraries
from datetime import timedelta
from Queue import Queue
import logging

#External libraries
from zmq.eventloop import ioloop

#Internal libraries
#
##################


##################
# Export section #
#
__all__ = ["Processor",
           "PERIODIC",
           "DELAYED",
           "HANDLER"]
#
##################


####################
# Constant section #
#
__version__ = "1.3"#current version [major.minor]

TIMEOUT = timedelta(0,0,0,100)#time between running

PERIODIC = 0#Periodic scenario
DELAYED  = 1#Delayed scenario
HANDLER  = 2#Triggered scenario
#
####################


class Processor(object):
    self = None
    
    queue = Queue()
    
    started = False
    running = False
    
    main = None
    loop = ioloop.IOLoop.instance()
    
    def __new__(cls):
        if cls.self is None:
            cls.self = object.__new__(cls)
            
        return cls.self
                
    def start(self):
        if not self.started:
            self.started = True
            
            self.loop.start()
        
    def stop(self):
        if self.started:
            self.started = False
            
            self.loop.stop()
            
    def pause(self):
        if self.started and self.running:
            self.running = False
            
            self.main = self.loop.remove_timeout(self.main) if self.main is not None else None
                        
    def resume(self):
        if self.started and not self.running:
            self.running = True
            
            self.main = self.loop.add_timeout(TIMEOUT,self.run)

    def agenda(self):
        self.stop()

        for i in range(self.queue.qsize()):
            message,pipeline = self.queue.get()

            logging.debug("{0}:  {1}".\
                     format(pipeline.name,str(message)))

            self.queue.put((message,pipeline))
        else:
            self.start()

    def periodic(self,routine,timeout):
        def callback():
            self.schedule(None,None,routine)
            
        return ioloop.PeriodicCallback(callback,timeout,self.loop)

    def delayed(self,routine,timeout):
        def callback():
            self.schedule((None,None),routine)
            
        return ioloop.DelayedCallback(callback,timeout,self.loop)

    def handler(self,fpipe,handle,event=ioloop.POLLIN):
        def callback(socket,events):
            message,tpipe = fpipe.routine.send((None,None))
            self.schedule(message,fpipe,tpipe)
            
        self.loop.add_handler(handle,callback,event)
    
    def schedule(self,message,fpipe,tpipe):
        if tpipe is not None:
            self.queue.put((message,fpipe,tpipe))
            
        if self.started and not self.running:self.resume()
    
    def dispatch(self):
        message,fpipe,tpipe = self.queue.get()
        
        temp = tpipe
        message,tpipe = tpipe.routine.send((message,fpipe))
        fpipe = temp
        
        return message,fpipe,tpipe
        
    def run(self):
        if self.running:
            while not self.queue.empty():
                self.schedule(*self.dispatch())
            else:
                self.pause()
        else:
            self.resume()
