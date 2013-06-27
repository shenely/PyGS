#!/usr/bin/env python2.7

"""Socket routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   26 June 2013

Provides routines for socket communication.

Classes:
SubscribeSocket -- Subscribe from socket
PublishSocket   -- Publish to socket

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-05-14    shenely         1.0         Initial revision
2013-06-26    shenely         1.1         Modifying routine structure

"""


##################
# Import section #
#
#Built-in libraries
import logging
import types

#External libraries
import zmq
from zmq.eventloop import ioloop

#Internal libraries
from . import SourceRoutine,TargetRoutine
from ..service import schedule
#
##################


##################
# Export section #
#
__all__ = ["SubscribeSocket",
           "PublishSocket"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]
#
####################


class SubscribeSocket(SourceRoutine):
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
    
    name = "Socket.Subscribe"
    type = schedule.HANDLER
    event = ioloop.POLLIN
    
    def __init__(self,socket):
        assert isinstance(socket,zmq.Socket)
        assert socket.socket_type is zmq.SUB
        
        SourceRoutine.__init__(self)
        
        self.handle = socket
    
    def _receive(self):
        message = self.handle.recv_multipart()
        
        assert isinstance(message,types.ListType)
        assert len(message) == 2
        assert isinstance(message[0],types.StringTypes)
        assert isinstance(message[1],types.StringTypes)
                
        logging.info("{0}:  From address {1}".\
                     format(self.name,message[0]))
        
        return message

class PublishSocket(TargetRoutine):
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
    
    name = "Socket.Publish"
    type = schedule.HANDLER
    event = ioloop.POLLIN
    
    def __init__(self,socket):
        assert isinstance(socket,zmq.Socket)
        assert socket.socket_type is zmq.PUB
        
        TargetRoutine.__init__(self)
        
        self.handle = socket
           
    def _send(self,message):
        assert isinstance(message,types.TupleType)
        assert len(message) == 2
        assert isinstance(message[0],types.StringTypes)
        assert isinstance(message[1],types.StringTypes)
        
        self.handle.send_multipart(message)
                
        logging.info("{0}:  To address {1}".\
                     format(self.name,message[0]))
