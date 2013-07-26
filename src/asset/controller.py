#!/usr/bin/env python2.7

"""Asset objects

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   25 July 2013

Provides the asset objects.

Classes:
AssetController   -- Asset controller object

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
from datetime import datetime,timedelta
from Queue import PriorityQueue

#External libraries
import zmq
from bson.tz_util import utc

#Internal libraries
from . import BaseAsset
from core.routine import control,queue,method,socket
from message import INERTIAL_PRODUCT,GEOGRAPHIC_PRODUCT
from message.routine import telemetry,product
from epoch.routine import order
from state.routine import interpolate,transform
#
##################


##################
# Export section #
#
__all__ = ["AssetController"]
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

HERMITE_INTERPOLATOR = 10

J2000 = datetime(2000,1,1,12,tzinfo=utc)#Julian epoch (2000-01-01T12:00:00Z)

INTERPOLATE_MARGIN = timedelta(seconds=60)
REMOVE_MARGIN = timedelta(seconds=0)
#
####################

    
class AssetController(BaseAsset):
    def __init__(self,segment,name,seed,
                 interpolator=HERMITE_INTERPOLATOR,
                 products=[INERTIAL_PRODUCT,GEOGRAPHIC_PRODUCT],
                 remove=REMOVE_MARGIN,
                 interpolate1=INTERPOLATE_MARGIN):
        BaseAsset.__init__(self,segment,name)
        
        telemetry_socket = self.context.socket(zmq.SUB)
        telemetry_socket.connect("tcp://localhost:5556")
        
        product_socket = self.context.socket(zmq.PUB)
        product_socket.connect("tcp://localhost:5555")
        
        telemetry_address = TELEMETRY_ADDRESS.format(asset=self.name,segment="Space")
        product_address = PRODUCT_ADDRESS.format(asset=self.name,segment=segment.name)
    
        sub_telemetry = socket.SubscribeSocket(telemetry_socket,telemetry_address)
        pub_product = socket.PublishSocket(product_socket,product_address)
        
        parse_telemetry = telemetry.ParseTelemetry()
        format_product = product.FormatProduct()
        
        telemetry_split = control.SplitControl(self.application.processor)
        
        self.application.Behavior("General asset controller")
               
        self.application.Scenario("Receive telemetry").\
            From("Subscribe source",sub_telemetry).\
            When("Parse telemetry",parse_telemetry).\
            To("Split telemetry",telemetry_split)
        
        self.application.Scenario("Publish product").\
            Then("Format product",format_product).\
            To("Publish target",pub_product)
            
        self.application.Behavior("Special asset controller")
        
        if interpolator is HERMITE_INTERPOLATOR:
            state_queue = PriorityQueue()
            
            put_state = queue.PutQueue(state_queue)
            get_state = queue.GetQueue(state_queue)
            
            extract_state = telemetry.ExtractState()
            
            interpolate_after = order.AfterEpoch(seed,interpolate1)
            update_interpolate = method.ExecuteMethod(interpolate_after.set_reference)
            
            remove_after = order.AfterEpoch(seed,remove)
            update_remove = method.ExecuteMethod(remove_after.set_reference)
            
            interpolate_state = interpolate.HermiteInterpolate()
            rotate_interpolate = method.ExecuteMethod(interpolate_state.set_state)
            
            state_split = control.SplitControl(self.application.processor)
            
            self.application.Scenario("Update epoch").\
                From("Split epoch",self.segment.epoch_split).\
                Then("Update remove",update_remove).\
                And("Update interpolate",update_interpolate)
                
            self.application.Scenario("State extraction").\
                From("Split telemetry",telemetry_split).\
                When("Extract state",extract_state).\
                Then("Put state",put_state)
                
            self.application.Scenario("Update state").\
                From("Split epoch",self.segment.epoch_split).\
                When("Get state",get_state).\
                Given("After lower",remove_after).Is(True).\
                And("After upper",interpolate_after).Is(False).\
                Then("Update state",rotate_interpolate)
            
            self.application.Scenario("Requeue state").\
                Given("After upper",interpolate_after).Is(True).\
                Then("Put state",put_state)
            
            self.application.Scenario("Hermite interpolator").\
                From("Split epoch",self.segment.epoch_split).\
                When("Interpolate state",interpolate_state).\
                To("Split state",state_split)
                
        if INERTIAL_PRODUCT in products:
            generate_inertial = product.GenerateProduct(INERTIAL_PRODUCT)
            
            self.application.Scenario("Generate inertial product").\
                From("Split state",state_split).\
                Then("Generate inertial",generate_inertial).\
                And("Put product",format_product)
                
        if GEOGRAPHIC_PRODUCT in products:
            transform_geographic = transform.InertialToGeographicTransform()
            generate_geographic = product.GenerateProduct(GEOGRAPHIC_PRODUCT)
            
            self.application.Scenario("Generate geographic product").\
                From("Split state",state_split).\
                Then("Transform geographic",transform_geographic).\
                And("Generate geographic",generate_geographic).\
                And("Put product",format_product)