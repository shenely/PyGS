#!/usr/bin/env python2.7

"""User service

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   28 July 2013

Purpose:    
"""



##################
# Import section #
#
#Built-in libraries

#External libraries
import zmq.eventloop.zmqstream

zmq.eventloop.ioloop.install()

import tornado.web
import tornado.websocket

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
__version__ = "1.0"#current version [major.minor]
#
####################


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

class ZMQWebSocket(tornado.websocket.WebSocketHandler):    
    def open(self):
        context = zmq.Context.instance()
        socket = context.socket(self.type)
        
        self.socket = zmq.eventloop.zmqstream.ZMQStream(socket)
    
    def on_close(self):
        self.socket.close()

class PublishWebSocket(ZMQWebSocket):
    type = zmq.PUB
    
    def on_message(self,message):
        messages = self.address,str(message)
        
        self.socket.send_multipart(messages)
    
    def open(self,path):
        ZMQWebSocket.open(self)
        
        self.address = ".".join(map(str.capitalize,path.split("/")))
        
        self.socket.connect("tcp://127.0.0.1:5555")

class SubscribeWebSocket(ZMQWebSocket):
    type = zmq.SUB
    
    def recv_multipart(self,messages):
        address,message = messages
        
        self.write_message(message)
    
    def open(self,path):
        ZMQWebSocket.open(self)
        
        self.address = ".".join(map(str.capitalize,path.split("/")))
        
        self.socket.connect("tcp://127.0.0.1:5556")
        self.socket.setsockopt(zmq.SUBSCRIBE,self.address)
        
        self.socket.on_recv(self.recv_multipart)

class DealerWebSocket(ZMQWebSocket):
    type = zmq.DEALER
    
    def on_message(self,message):
        messages = self.address,str(message)
        
        self.socket.send_multipart(messages)
    
    def recv_multipart(self,messages):
        address,message = messages
        
        if address == self.address:
            self.write_message(message)
    
    def open(self,path):
        ZMQWebSocket.open(self)
        
        self.address = ".".join(map(str.capitalize,path.split("/")))
        
        self.socket.connect("tcp://127.0.0.1:5560")
        
        self.socket.on_recv(self.recv_multipart)

class WebService(object):
    def __init__(self):
        self.application = tornado.web.Application([(r"/", MainHandler),
                                       (r"/pub/(.*)",PublishWebSocket),
                                       (r"/sub/(.*)",SubscribeWebSocket),
                                       (r"/dealer/(.*)",DealerWebSocket),
                                       (r"/media/(.*)", tornado.web.StaticFileHandler, {"path": "./core/web/static/img"})],
                                      template_path="./core/web/templates",
                                      static_path="./core/web/static")
        
        self.application.listen(8080)
