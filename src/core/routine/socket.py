#!/usr/bin/env python2.7

"""Socket routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   08 August 2013

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
2013-06-29    shenely                     Refactored agenda
2013-06-29    shenely         1.2         Address handled internally
2013-08-09    shenely         1.3         Adding persistance logic

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
from .. import agenda
from .. import persist
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
__version__ = "1.3"#current version [major.minor]
#
####################


subscribe_socket = persist.RoutinePersistance()

@subscribe_socket.type(persist.SOURCE_ROUTINE)
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
    type = agenda.HANDLER
    event = ioloop.POLLIN
    
    def __init__(self):
        SourceRoutine.__init__(self)
        
        self._address = ""
    
    @subscribe_socket.property
    def socket(self):
        return self._socket
    
    @socket.setter
    def socket(self,socket):
        assert isinstance(socket,zmq.Socket)
        assert socket.socket_type is zmq.SUB
        
        self._socket = socket
    
    @property
    def handle(self):
        return self._socket
        
    @subscribe_socket.property
    def address(self):
        return self._address
    
    @address.setter
    def address(self,address):
        assert isinstance(address,types.StringTypes)
        
        self._socket.setsockopt(zmq.UNSUBSCRIBE,self._address)
        
        self._address = address
        
        self._socket.setsockopt(zmq.SUBSCRIBE,self._address)
    
    def _receive(self):
        address,message = self._socket.recv_multipart()
        
        assert isinstance(address,types.StringTypes)
        assert self.address in address
        assert isinstance(message,types.StringTypes)
                
        logging.info("{0}:  From address {1}".\
                     format(self.name,self._address))
        
        return message


publish_socket = persist.RoutinePersistance()

@publish_socket.type(persist.TARGET_ROUTINE)
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
    type = agenda.HANDLER
    event = ioloop.POLLIN
    
    def __init__(self):
        TargetRoutine.__init__(self)
        
        self._address = ""
    
    @publish_socket.property
    def socket(self):
        return self._socket
    
    @socket.setter
    def socket(self,socket):
        assert isinstance(socket,zmq.Socket)
        assert socket.socket_type is zmq.PUB
        
        self._socket = socket
    
    @property
    def handle(self):
        return self._socket
        
    @publish_socket.property
    def address(self):
        return self._address
    
    @address.setter
    def address(self,address):
        assert isinstance(address,types.StringTypes)
        
        self._address = address
           
    def _send(self,message):
        assert isinstance(message,types.StringTypes)
        
        self._socket.send_multipart((self._address,message))
                
        logging.info("{0}:  To address {1}".\
                     format(self.name,self._address))
