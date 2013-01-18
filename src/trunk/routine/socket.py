#!/usr/bin/env python2.7

"""Socket routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   11 January 2013

Purpose:    
"""


##################
# Import section #
#
#Built-in libraries
import logging
import types

#External libraries
import zmq

#Internal libraries
from . import coroutine
#
##################


##################
# Export section #
#
__all__ = ["publish",
           "subscribe",
           "request",
           "respond"]
#
##################


####################
# Constant section #
#
__version__ = "0.1"#current version [major.minor]
#
####################


@coroutine
def publish(socket,pipeline=None):
    """Publish Message to Socket"""
    
    assert isinstance(socket,zmq.Socket)
    assert socket.socket_type is zmq.PUB
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    message = None
    while True:
        message = yield message,pipeline
        
        assert isinstance(message,types.TupleType)
        assert len(message) == 2
        assert isinstance(message[0],types.StringTypes)
        assert isinstance(message[1],types.StringTypes)
        
        socket.send_multipart(message)
                
        logging.info("Routine.Socket:  Published to %s" % message[0])

@coroutine
def subscribe(socket,pipeline=None):
    """Subscribe Message from Socket"""
    
    assert isinstance(socket,zmq.Socket)
    assert socket.socket_type is zmq.SUB
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    message = None
    while True:
        yield message,pipeline
        
        message = socket.recv_multipart()
        
        assert isinstance(message,types.ListType)
        assert len(message) == 2
        assert isinstance(message[0],types.StringTypes)
        assert isinstance(message[1],types.StringTypes)
                
        logging.info("Routine.Socket:  Subscribed from %s" % message[0])

@coroutine
def request(socket,pipeline=None):
    """Request Message from Socket"""
    
    assert isinstance(socket,zmq.Socket)
    assert socket.socket_type is zmq.REQ
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    message = None
    while True:
        yield message,pipeline
        
        message = socket.recv_multipart()
        
        assert isinstance(message,types.ListType)
        assert len(message) == 3
        assert isinstance(message[0],types.StringTypes)
        assert isinstance(message[1],types.StringTypes)
        assert message[1] == ""
        assert isinstance(message[2],types.StringTypes)
                
        logging.info("Routine.Socket:  Requested from %s" % message[0])

@coroutine
def respond(socket,pipeline=None):
    """Respond Message from Socket"""
    
    assert isinstance(socket,zmq.Socket)
    assert socket.socket_type is zmq.REP
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    message = None
    while True:
        message = yield message,pipeline
        
        assert isinstance(message,types.ListType)
        assert len(message) == 3
        assert isinstance(message[0],types.StringTypes)
        assert isinstance(message[1],types.StringTypes)
        assert message[1] == ""
        assert isinstance(message[2],types.StringTypes)
        
        socket.send_multipart(message)
                
        logging.info("Routine.Socket:  Responded to %s" % message[0])