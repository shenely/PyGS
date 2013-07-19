#!/usr/bin/env python2.7

"""User service

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   19 July 2013

Purpose:    
"""


##################
# Import section #
#
#Built-in libraries

#External libraries
import zmq

#Internal libraries
from core.agenda import *
from core.engine import *
from core.routine import socket,control
from message import INERTIAL_PRODUCT,GEOGRAPHIC_PRODUCT
from message.routine import product
#from . import routine
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

PRODUCT_ADDRESS = "Kepler.Product"
INERTIAL_ADDRESS = "Kepler.Inertial"
GEOGRAPHIC_ADDRESS = "Kepler.Geographic"
#
####################


def main():
    """Main Function"""
    
    processor = Processor()
    context = zmq.Context(1)
            
    product_socket = context.socket(zmq.SUB)
    product_socket.connect("tcp://localhost:5556")
    
    user_socket = context.socket(zmq.PUB)
    user_socket.connect("tcp://localhost:5555")

    product_input = socket.SubscribeSocket(product_socket,PRODUCT_ADDRESS)
    parse_product = product.ParseProduct()
    split_product = control.SplitControl(processor)
    extract_inertial = product.ExtractInertial()
    extract_geographic = product.ExtractGeographic()
    inertial_output = socket.PublishSocket(user_socket,INERTIAL_ADDRESS)
    geographic_output = socket.PublishSocket(user_socket,GEOGRAPHIC_ADDRESS)

    segment = Application("Space segment",processor)
    
    segment.Behavior("Product distribution")
    
    # General asset section
    segment.Scenario("Receive product").\
        From("Subscribe source",product_input).\
        When("Parse product",parse_product).\
        To("Split product",split_product)
    # End section
    
    # Special asset section
    segment.Scenario("Inertial extraction").\
        From("Split product",split_product).\
        When("Extract inertial",extract_inertial).\
        To("Publish inertial",inertial_output)
    
    segment.Scenario("Geographic extraction").\
        From("Split product",split_product).\
        When("Extract geographic",extract_geographic).\
        To("Publish geographic",geographic_output)
    # End section
                
if __name__ == '__main__':main()
