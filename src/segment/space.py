#!/usr/bin/env python2.7

"""Space segment

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   26 July 2013

Provides the space segment.

Classes:
SpaceSegment   -- Space segment object

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-07-25    shenely         1.0         Initial revision
2013-07-26    shenely         1.1         Added model behavior

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
from asset.routine import model
#
##################


##################
# Export section #
#
__all__ = ["SpaceSegment"]
#
##################


####################
# Constant section #
#
__version__ = "1.1"#current version [major.minor]

EPOCH_ADDRESS = "{asset!s}.{segment!s}.Epoch"
TELEMETRY_ADDRESS = "{asset!s}.{segment!s}.Telemetry"
MODEL_ADDRESS = "{asset!s}.{segment!s}.Model"
#
####################

    
class SpaceSegment(BaseSegment):
    def __init__(self,application,name="Space"):
        BaseSegment.__init__(self,application,name)
        
        epoch_socket = self.context.socket(zmq.SUB)
        epoch_socket.connect("tcp://localhost:5556")
        
        epoch_address = EPOCH_ADDRESS.format(asset="System",segment="Clock")
    
        sub_epoch = socket.SubscribeSocket()
        sub_epoch.socket = epoch_socket
        sub_epoch.address = epoch_address
        
        parse_epoch = epoch.ParseEpoch()
        self.epoch_split = control.SplitControl(application.processor)
    
        application.Behavior("Receive epoch message")
        
        application.Scenario("Receive epoch from clock").\
            From("Epoch address",sub_epoch).\
            When("Parse epoch from string",parse_epoch).\
            To("Epoch split point",self.epoch_split)
            
        model_socket = self.context.socket(zmq.SUB)
        model_socket.connect("tcp://localhost:5556")
        
        model_address = MODEL_ADDRESS.format(asset="System",segment="Asset")
    
        sub_model = socket.SubscribeSocket()
        sub_model.socket = model_socket
        sub_model.address = model_address
        
        parse_model = model.ParseModel(self)
            
        application.Behavior("Asset model")
        
        application.Scenario("Receive asset model").\
            From("Model address",sub_model).\
            When("Parse asset model",parse_model)