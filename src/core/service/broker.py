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


def main():
    """Main Function"""
    
    device = ThreadDevice(zmq.FORWARDER, zmq.SUB, zmq.PUB)
    
    device.bind_in("tcp://127.0.0.1:5555")
    device.bind_out("tcp://127.0.0.1:5556")
    device.setsockopt_in(zmq.SUBSCRIBE,"")
    
    device.start()

if __name__ == '__main__':main()