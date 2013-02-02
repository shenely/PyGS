#!/usr/bin/env python2.7

"""Web Service

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   02 February 2013

Purpose:    
"""



##################
# Import section #
#
#Built-in libraries

#External libraries
import zmq
import zmq.eventloop
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
__version__ = "0.1"#current version [major.minor]

VIEW_ADDRESS = "Kepler.View.{!s}"
#
####################


class ZMQWebSocket(tornado.websocket.WebSocketHandler):
    sockets = dict()
    
    def send_message(self,messages):
        address,message = messages
        
        self.write_message(message)
    
    def open(self,view):
        
        context = zmq.Context.instance()
        
        socket = context.socket(zmq.SUB)
        socket.connect("tcp://127.0.0.1:5556")
        socket.setsockopt(zmq.SUBSCRIBE,VIEW_ADDRESS.format(view.capitalize()))
        
        stream = zmq.eventloop.zmqstream.ZMQStream(socket)
        stream.on_recv(self.send_message)
        
        self.sockets[self] = stream
    
    def on_close(self):
        stream = self.sockets[self]
        stream.close()
        
        del self.sockets[self]

def main():
    app = tornado.web.Application([(r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "./service/"}),
                                   (r"/view/(.*)",ZMQWebSocket)])
    app.listen(8080)
    
if __name__ == '__main__':
    main()
