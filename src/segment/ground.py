#!/usr/bin/env python2.7

"""Ground segment

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   26 July 2013

Provides the ground segment.

Classes:
GroundSegment   -- Ground segment object

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-07-25    shenely         1.0         Initial revision
2013-07-26    shenely         1.1         Added controller behavior

"""


##################
# Import section #
#
#Built-in libraries

#External libraries
import zmq

#Internal libraries
from . import BaseSegment
from core.routine import control,socket
from epoch import routine as epoch
from asset.routine import controller
#
##################


##################
# Export section #
#
__all__ = ["GroundSegment"]
#
##################


####################
# Constant section #
#
__version__ = "1.1"#current version [major.minor]

EPOCH_ADDRESS = "{asset!s}.{segment!s}.Epoch"
TELEMETRY_ADDRESS = "{asset!s}.{segment!s}.Telemetry"
PRODUCT_ADDRESS = "{asset!s}.{segment!s}.Product"
CONTROLLER_ADDRESS = "{asset!s}.{segment!s}.Controller"
#
####################

    
class GroundSegment(BaseSegment):
    def __init__(self,application,name="Ground"):
        BaseSegment.__init__(self,application,name)
        
        epoch_socket = self.context.socket(zmq.SUB)
        epoch_socket.connect("tcp://localhost:5556")
        
        epoch_address = EPOCH_ADDRESS.format(asset="System",segment="Clock")
    
        sub_epoch = socket.SubscribeSocket(epoch_socket,epoch_address)
        parse_epoch = epoch.ParseEpoch()
        self.epoch_split = control.SplitControl(application.processor)
    
        application.Behavior("Receive epoch message")
        
        application.Scenario("Receive epoch from clock").\
            From("Epoch address",sub_epoch).\
            When("Parse epoch from string",parse_epoch).\
            To("Epoch split point",self.epoch_split)
            
        controller_socket = self.context.socket(zmq.SUB)
        controller_socket.connect("tcp://localhost:5556")
        
        controller_address = CONTROLLER_ADDRESS.format(asset="System",segment="Asset")
    
        sub_controller = socket.SubscribeSocket(controller_socket,controller_address)
        parse_controller = controller.ParseController(self)
            
        application.Behavior("Asset controller")
        
        application.Scenario("Receive asset controller").\
            From("Controller address",sub_controller).\
            When("Parse asset controller",parse_controller)