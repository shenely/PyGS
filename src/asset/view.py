#!/usr/bin/env python2.7

"""Asset view

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   25 July 2013

Provides the asset objects.

Classes:
AssetView   -- Asset view object

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-07-25    shenely         1.0         Initial revision

"""


##################
# Import section #
#
#Built-in libraries

#External libraries
import zmq

#Internal libraries
from . import BaseAsset
from message import INERTIAL_PRODUCT,GEOGRAPHIC_PRODUCT
from core.routine import control,socket
from message.routine import product
from epoch import routine as epoch
#
##################


##################
# Export section #
#
__all__ = ["AssetModel",
           "AssetController",
           "AssetView"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]

EPOCH_ADDRESS = "{asset!s}.{segment!s}.Epoch"
TELEMETRY_ADDRESS = "{asset!s}.{segment!s}.Telemetry"
PRODUCT_ADDRESS = "{asset!s}.{segment!s}.Product"
INERTIAL_ADDRESS = "{asset!s}.{segment!s}.Inertial"
GEOGRAPHIC_ADDRESS = "{asset!s}.{segment!s}.Geographic"
#
####################

    
class AssetView(BaseAsset):
    def __init__(self,segment,name,products=[INERTIAL_PRODUCT,GEOGRAPHIC_PRODUCT]):
        BaseAsset.__init__(self,segment,name)
        
        product_socket = self.context.socket(zmq.SUB)
        product_socket.connect("tcp://localhost:5556")
        
        product_address = PRODUCT_ADDRESS.format(asset=self.name,segment="Ground")
    
        sub_product = socket.SubscribeSocket(product_socket,product_address)
        
        parse_product = product.ParseProduct()
        product_split = control.SplitControl(self.application.processor)
        
        self.application.Scenario("Receive product").\
            From("Subscribe source",sub_product).\
            When("Parse product",parse_product).\
            To("Split product",product_split)
        
        if INERTIAL_PRODUCT in products:
            inertial_socket = self.context.socket(zmq.PUB)
            inertial_socket.connect("tcp://localhost:5555")
            
            inertial_address = INERTIAL_ADDRESS.format(asset=self.name,segment=segment.name)
            pub_inertial = socket.PublishSocket(inertial_socket,inertial_address)
    
            extract_inertial = product.ExtractInertial()
            
            format_inertial = epoch.FormatEpoch()
            
            self.application.Scenario("Inertial extraction").\
                From("Split product",product_split).\
                When("Extract inertial",extract_inertial).\
                Then("Format inertial",format_inertial).\
                To("Publish inertial",pub_inertial)
        
        if GEOGRAPHIC_PRODUCT in products:
            if INERTIAL_PRODUCT in products:
                geographic_socket = inertial_socket
            else:
                geographic_socket = self.context.socket(zmq.PUB)
                geographic_socket.connect("tcp://localhost:5555")
                
            geographic_address = GEOGRAPHIC_ADDRESS.format(asset=self.name,segment=segment.name)
            pub_geographic = socket.PublishSocket(geographic_socket,geographic_address)
    
            extract_geographic = product.ExtractGeographic()
            
            format_geographic = epoch.FormatEpoch()
    
            self.application.Scenario("Geographic extraction").\
                From("Split product",product_split).\
                When("Extract geographic",extract_geographic).\
                Then("Format geographic",format_geographic).\
                To("Publish geographic",pub_geographic)