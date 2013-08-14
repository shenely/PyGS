#!/usr/bin/env python2.7

"""Broker Service

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   10 August 2013

Purpose:    
"""


##################
# Import section #
#
#Built-in libraries
from threading import Thread

#External libraries
import zmq
from zmq.devices import ThreadDevice

#Internal libraries
#
##################


##################
# Export section #
#
#
##################


####################
# Constant section #
#
__version__ = "0.1"#current version [major.minor]
#
####################


class ThreadRouter(object):
    def __init__(self):
        context = zmq.Context(1)
        
        self.socket = context.socket(zmq.ROUTER)
        
        self.poller = zmq.Poller()
        
        self.poller.register(self.socket, zmq.POLLIN)
        
        self.thread = Thread(target=self)
    
    def __call__(self):
        while True:
            sockets = dict(self.poller.poll())
            
            if (self.socket in sockets and sockets[self.socket] == zmq.POLLIN):
                source,target,message = self.socket.recv_multipart()
                
                self.socket.send_multipart((target,source,message))
                
    def bind(self,address):
        self.socket.bind(address)
        
    def start(self):
        self.thread.start()

def main():
    """Main Function"""
    
    device = ThreadDevice(zmq.FORWARDER, zmq.SUB, zmq.PUB)
    
    device.bind_in("tcp://127.0.0.1:5555")
    device.bind_out("tcp://127.0.0.1:5556")
    device.setsockopt_in(zmq.SUBSCRIBE,"")
    
    device.start()
    
    router = ThreadRouter()
    router.bind("tcp://127.0.0.1:5560")
    
    router.start()

if __name__ == '__main__':main()