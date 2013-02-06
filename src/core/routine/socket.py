#!/usr/bin/env python2.7

"""Socket routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   05 February 2013

Provides routines for socket communication.

Functions:
publish   -- Publish to socket
subscribe -- Subscribe from socket

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-02-05    shenely         1.0         Promoted to version 1.0

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
from .. import coroutine
#
##################


##################
# Export section #
#
__all__ = ["publish",
           "subscribe"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]
#
####################


@coroutine
def publish(socket,pipeline=None):
    """Story:  Publish to socket
    
    IN ORDER TO synchronize multiple segments 
    AS A generic segment
    I WANT TO send a message to multiple segments simultaneously
    
    """
    
    """Specification:  Publish to socket
    
    GIVEN a publish socket
        AND a downstream pipeline (default null)
        
    Scenario 1:  Upstream message received
    WHEN a message is received from upstream
        AND the message defines an envelope
        AND the message defines the content
    THEN the message SHALL be sent to the socket
        AND the message SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(socket,zmq.Socket)
    assert socket.socket_type is zmq.PUB
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    message = None
    
    logging.debug("Socket.Publish:  Starting")
    while True:
        try:
            message = yield message,pipeline
        except GeneratorExit:
            logging.warn("Socket.Publish:  Stopping")
            
            #close downstream routines (if they exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:          
            #input validation
            assert isinstance(message,types.TupleType)
            assert len(message) == 2
            assert isinstance(message[0],types.StringTypes)
            assert isinstance(message[1],types.StringTypes)
            
            socket.send_multipart(message)
                    
            logging.info("Socket.Publish:  To address %s" % message[0])

@coroutine
def subscribe(socket,pipeline=None):
    """Story:  Subscribe from socket
    
    IN ORDER TO be synchronized with multiple segments
    AS A generic segment
    I WANT TO receive a message simultaneously with multiple segments
    
    """
    
    """Specification:  Subscribe from socket
    
    GIVEN a subscribe socket
        AND a downstream pipeline (default null)
        
    Scenario 1:  Socket message received
    WHEN a message is received from the socket
        AND the message defines an envelope
        AND the message defines the content
    THEN the message SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(socket,zmq.Socket)
    assert socket.socket_type is zmq.SUB
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    message = None
    
    logging.debug("Socket.Subscribe:  Starting")
    while True:
        try:
            message = yield message,pipeline
        except GeneratorExit:
            logging.warn("Socket.Subscribe:  Stopping")
            
            #close downstream routines (if they exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            message = socket.recv_multipart()
            
            #output validation
            assert isinstance(message,types.ListType)
            assert len(message) == 2
            assert isinstance(message[0],types.StringTypes)
            assert isinstance(message[1],types.StringTypes)
                    
            logging.info("Socket.Subscribe:  From address %s" % message[0])

@coroutine
def request(socket,pipeline=None):
    """Story:  Request from socket
    
    IN ORDER TO synchronize with another segment
    AS A generic segment
    I WANT TO receive a message to another segment
    
    """
    
    """Specification:  Request from socket
    
    GIVEN a request socket
        AND a downstream pipeline (default null)
        
    Scenario 1:  Socket message received
    WHEN a message is received from the socket
        AND the message defines an envelope
        AND the message defines the content
    THEN the message SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(socket,zmq.Socket)
    assert socket.socket_type is zmq.REQ
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None

@coroutine
def respond(socket,pipeline=None):
    """Story:  Respond to socket
    
    IN ORDER TO synchronize with another segment
    AS A generic segment
    I WANT TO send a message to another segment
    
    """
    
    """Specification:  Respond to socket
    
    GIVEN a response socket
        AND a downstream pipeline (default null)
        
    Scenario 1:  Upstream message received
    WHEN a message is received from upstream
        AND the message defines an envelope
        AND the message defines the content
    THEN the message SHALL be sent to the socket
        AND the message SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(socket,zmq.Socket)
    assert socket.socket_type is zmq.REP
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None