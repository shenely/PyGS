'''
Created on Dec 3, 2012

@author: shenely
'''

from datetime import timedelta
from Queue import Queue
import logging
import types

from zmq.eventloop import ioloop

TIMEOUT = timedelta(0,0,0,100)

class Scheduler(object):
    '''
    classdocs
    '''
    
    
    queue = Queue()
    loop = ioloop.IOLoop.instance()   

    def __init__(self):
        '''
        Constructor
        '''
                
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

    def periodic(self,routine,timeout):
        def callback():
            self.schedule(None,routine)
            
        return ioloop.PeriodicCallback(callback,timeout)

    def handler(self,socket,routine):
        def callback(socket,events):
            self.schedule(*routine.next())
            
        self.loop.add_handler(socket,callback,ioloop.POLLIN)
    
    def schedule(self,message,pipeline):
        if isinstance(pipeline,(types.ListType,types.TupleType)) is True:
            for i in range(len(pipeline)):
                if pipeline[i] is not None:
                    self.queue.put((message,pipeline[i]))
        elif pipeline is not None:
            self.queue.put((message,pipeline))
        
    def run(self):
        if self.running:
            while not self.queue.empty():
                message,pipeline = self.queue.get()
                
                self.schedule(*pipeline.send(message))
            else:
                self.loop.add_timeout(TIMEOUT,self.run)
        else:
            self.start()