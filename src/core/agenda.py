#!/usr/bin/env python2.7

"""Agenda service

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   29 June 2013

Provides a agenda service.

Classes:
Scheduler -- Scheduler
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-06-27    shenely         1.0         Initial revision
2013-06-29    shenely         1.1         Refactored to agenda

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
__all__ = ["Scheduler",
           "PERIODIC",
           "DELAYED",
           "HANDLER"]
#
##################


####################
# Constant section #
#
__version__ = "1.1"#current version [major.minor]

TIMEOUT = timedelta(0,0,0,100)#time between running

PERIODIC = 0#Periodic scenario
DELAYED  = 1#Delayed scenario
HANDLER  = 2#Triggered scenario
#
####################


class Scheduler(object):    
    queue = Queue()
    loop = ioloop.IOLoop.instance()   

    def __init__(self):
                
        self.running = False
                
    def start(self):
        if not self.running:
            self.running = True
            
            self.main = self.loop.add_timeout(TIMEOUT,self.run)
            
            self.loop.start()
        
    def stop(self):
        if self.running:
            self.running = False
            
            self.loop.remove_timeout(self.main)
            
            self.loop.stop()

    def agenda(self):
        self.stop()

        tasks = []

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

    def handler(self,pipeline,handle,event=ioloop.POLLIN):
        def callback(socket,events):
            self.schedule(*pipeline.routine.send((None,None)))
            
        self.loop.add_handler(handle,callback,event)
    
    def schedule(self,message,fpipe,tpipe):
        if tpipe is not None:
            self.queue.put((message,fpipe,tpipe))
        
    def run(self):
        if self.running:
            while not self.queue.empty():
                message,fpipe,tpipe = self.queue.get()
                
                fpipe = tpipe
                message,tpipe = tpipe.routine.send((message,fpipe))
                                                   
                self.schedule(message,fpipe,tpipe)
            else:
                self.loop.add_timeout(TIMEOUT,self.run)
        else:
            self.start()
