#!/usr/bin/env python2.7

"""Asset model

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   25 July 2013

Provides the asset model.

Classes:
AssetModel   -- Asset model object

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
import message
from core.routine import queue,method,socket
from epoch.routine import order
from state.routine import propagate,transform
from message.routine import telemetry
#
##################


##################
# Export section #
#
__all__ = ["AssetModel"]
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

KEPLER_ITERATOR = 10

ITERATE_MARGIN = timedelta(seconds=300)
PUBLISH_MARGIN = timedelta(seconds=180)
REMOVE_MARGIN = timedelta(seconds=0)

J2000 = datetime(2000,1,1,12,tzinfo=utc)#Julian epoch (2000-01-01T12:00:00Z)
#
####################

class AssetModel(BaseAsset):
    def __init__(self,segment,name,seed,
                 iterator=KEPLER_ITERATOR,
                 remove=REMOVE_MARGIN,
                 publish=PUBLISH_MARGIN,
                 iterate=ITERATE_MARGIN):
        BaseAsset.__init__(self,segment,name)
        
        telemetry_socket = self.context.socket(zmq.PUB)
        telemetry_socket.connect("tcp://localhost:5555")
        
        telemetry_address = TELEMETRY_ADDRESS.format(asset=self.name,segment="Space")

        pub_telemetry = socket.PublishSocket(telemetry_socket,telemetry_address)
        
        state_queue = PriorityQueue()
        
        put_telemetry = queue.PutQueue(state_queue)
        get_telemetry = queue.GetQueue(state_queue)

        publish_after = order.AfterEpoch(seed,publish)
        update_publish = method.ExecuteMethod(publish_after.set_reference)
        
        remove_after = order.AfterEpoch(seed,remove)
        update_remove = method.ExecuteMethod(remove_after.set_reference)
        
        format_telemetry = telemetry.FormatTelemetry()
        
        self.application.Behavior("General asset model")
        
        self.application.Scenario("Update epoch").\
            From("Epoch split",self.segment.epoch_split).\
            Then("Update publish threshold with epoch",update_publish).\
            And("Update remove threshold with epoch",update_remove)
            
        self.application.Scenario("Publish telemetry").\
            From("Epoch split",self.segment.epoch_split).\
            When("Telemetry message is in queue",get_telemetry).\
            Given("Telemetry epoch after remove threshold (is true)",remove_after).Is(True).\
            And("Telemetry epoch after publish threshold (is false)",publish_after).Is(False).\
            Then("Format telemetry to string",format_telemetry).\
            To("Telemetry address",pub_telemetry)
        
        self.application.Scenario("Requeue telemetry").\
            Given("Telemetry epoch after publish threshold (is true)",publish_after).Is(True).\
            Then("Enqueue telemetry message",put_telemetry)
            
        self.application.Behavior("Special asset model")
        
        if iterator is KEPLER_ITERATOR:
            iterate_before = order.BeforeEpoch(seed,iterate)
            update_iterate = method.ExecuteMethod(iterate_before.set_reference)
            
            iterate_state = propagate.KeplerPropagate(seed)
            transform_state = transform.KeplerianToInertialTransform()
            
            generate_telemetry = telemetry.GenerateTelemetry(message.ORBIT_TELEMETRY)
            
            self.application.Scenario("Kepler propagation").\
                From("Epoch split",self.segment.epoch_split).\
                    Given("Clock epoch after iterate threshold",iterate_before).Is(False).\
                    Then("Iterate state via Keplerian propagator",iterate_state).\
                    And("Update iterate threshold with state epoch",update_iterate).\
                    And("Transform state to inertial state",transform_state).\
                    And("Generate telemetry from state",generate_telemetry).\
                    And("Enqueue telemetry message",put_telemetry)