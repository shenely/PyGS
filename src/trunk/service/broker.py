#!/usr/bin/env python2.7

"""Broker Service

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   15 January 2013

Purpose:    
"""


##################
# Import section #
#
#Built-in libraries

#External libraries
import zmq

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


def main():
    """Main Function"""
    
    context = zmq.Context(1)
    
    incoming = context.socket(zmq.SUB)
    incoming.bind("tcp://127.0.0.1:5555")
    incoming.setsockopt(zmq.SUBSCRIBE,"")
    
    outgoing = context.socket(zmq.PUB)
    outgoing.bind("tcp://127.0.0.1:5556")
    
    zmq.device(zmq.FORWARDER,incoming,outgoing)

if __name__ == '__main__':main()