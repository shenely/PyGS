#!/usr/bin/env python2.7

"""Socket routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   10 August 2013

Provides routines for socket communication.

Classes:
SocketSubscribe -- Subscribe from socket
SocketPublish   -- Publish to socket
SocketRequest   -- Request from socket
SocketRespond   -- Respond to socket

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-05-14    shenely         1.0         Initial revision
2013-06-26    shenely         1.1         Modifying routine structure
2013-06-29    shenely                     Refactored agenda
2013-06-29    shenely         1.2         Address handled internally
2013-08-09    shenely         1.3         Adding persistance logic
2013-08-10    shenely         1.4         Adding request/response

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
from .. import engine
from .. import agenda
from .. import persist
#
##################


##################
# Export section #
#
__all__ = ["SocketObject",
           "SocketSubscribe",
           "SocketPublish",
           "SocketRequest",
           "SocketRespond"]
#
##################


####################
# Constant section #
#
__version__ = "1.4"#current version [major.minor]
#
####################


socket_object = persist.ObjectPersistance()

@socket_object.type(persist.GENERAL_OBJECT)
class SocketObject(object):
    def __init__(self):
        object.__init__(self)
        
        self.context = engine.Application("PyGS").context
        
    @socket_object.property
    def address(self):
        return self._socket.getsockopt(zmq.IDENTITY)
    
    @address.setter
    def address(self,address):
        self._socket.setsockopt(zmq.IDENTITY,address)
    
    @socket_object.property
    def type(self):
        return self._socket.socket_type
    
    @type.setter
    def type(self,type):
        assert isinstance(type,(types.StringType,
                                types.UnicodeType,
                                types.IntType))
        
        if isinstance(type,types.StringTypes):
            self._socket = self.context.socket(getattr(zmq,type))
        elif isinstance(type,types.IntType):
            self._socket = self.context.socket(type)
        
    @socket_object.property
    def socket(self):
        return self._socket
    
    @socket.setter
    def socket(self,socket):
        assert isinstance(socket,zmq.Socket)
        
        self._socket = socket


socket_subscribe = persist.ObjectPersistance()

@socket_subscribe.type(persist.SOURCE_OBJECT)
class SocketSubscribe(SourceRoutine):
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
    
    @socket_subscribe.property
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
        
    @socket_subscribe.property
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


socket_publish = persist.ObjectPersistance()

@socket_publish.type(persist.TARGET_OBJECT)
class SocketPublish(TargetRoutine):
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
    
    @socket_publish.property
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
        
    @socket_publish.property
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


socket_request = persist.ObjectPersistance()

@socket_request.type(persist.SOURCE_OBJECT)
class SocketRequest(SourceRoutine):
    """Story:  Request from socket
    
    IN ORDER TO
    AS A
    I WANT TO
    
    """
    
    """Specification:  Request from socket
    
    GIVEN
        
    Scenario 1:  Socket message received
    WHEN
    THEN
    
    """
    
    name = "Socket.Request"
    type = agenda.HANDLER
    event = ioloop.POLLIN
    
    def __init__(self):
        SourceRoutine.__init__(self)
        
        self._address = ""
    
    @socket_request.property
    def socket(self):
        return self._socket
    
    @socket.setter
    def socket(self,socket):
        assert isinstance(socket,zmq.Socket)
        assert socket.socket_type is zmq.DEALER
        
        self._socket = socket
    
    @property
    def handle(self):
        return self._socket
        
    @socket_request.property
    def address(self):
        return self._address
    
    @address.setter
    def address(self,address):
        assert isinstance(address,types.StringTypes)
        
        self._address = address
    
    def _receive(self):
        address,message = self._socket.recv_multipart()
        
        assert isinstance(address,types.StringTypes)
        assert isinstance(message,types.StringTypes)
        
        self._address = address
                
        logging.info("{0}:  From address {1}".\
                     format(self.name,self._address))
        
        return message


socket_respond = persist.ObjectPersistance()

@socket_respond.type(persist.TARGET_OBJECT)
class SocketRespond(TargetRoutine):
    """Story:  Respond to socket
    
    IN ORDER TO
    AS A
    I WANT TO
    
    """
    
    """Specification:  Respond to socket
    
    GIVEN
        
    Scenario 1:  Upstream message received
    WHEN
    THEN
    
    """
    
    name = "Socket.Respond"
    type = agenda.HANDLER
    event = ioloop.POLLIN
    
    def __init__(self):
        TargetRoutine.__init__(self)
        
        self._address = ""
    
    @socket_respond.property
    def socket(self):
        return self._socket
    
    @socket.setter
    def socket(self,socket):
        assert isinstance(socket,zmq.Socket)
        assert socket.socket_type is zmq.DEALER
        
        self._socket = socket
    
    @property
    def handle(self):
        return self._socket
        
    @socket_respond.property
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
