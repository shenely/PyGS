#!/usr/bin/env python2.7

"""Ground service

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   17 July 2013

Purpose:    
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
from core.agenda import *
from core.engine import *
from core.routine import socket,control,queue,method
from epoch import EpochState
from epoch import routine as epoch
from epoch.routine import order
from state import KeplerianState
from message import INERTIAL_PRODUCT,GEOGRAPHIC_PRODUCT
from message.routine import telemetry,product
from state.routine import interpolate,transform
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

EPOCH_ADDRESS = "Kepler.Epoch"
TELEMETRY_ADDRESS = "Kepler.Telemetry"
PRODUCT_ADDRESS = "Kepler.Product"

INTERPOLATE_MARGIN = timedelta(seconds=0)
PUBLISH_MARGIN = timedelta(seconds=180)
REMOVE_MARGIN = timedelta(seconds=0)

STEP_SIZE = timedelta(seconds=60)
#
####################


def main():
    """Main Function"""
    
    processor = Processor()
    context = zmq.Context(1)
    
    clock_epoch = EpochState(datetime(2010,1,1,tzinfo=utc))
        
    epoch_socket = context.socket(zmq.SUB)
    epoch_socket.connect("tcp://localhost:5556")
        
    telemetry_socket = context.socket(zmq.SUB)
    epoch_socket.connect("tcp://localhost:5556")
    
    ground_socket = context.socket(zmq.PUB)
    ground_socket.connect("tcp://localhost:5555")
    
    state_queue = PriorityQueue()
    product_queue = PriorityQueue()

    epoch_input = socket.SubscribeSocket(epoch_socket,EPOCH_ADDRESS)
    parse_epoch = epoch.ParseEpoch()
    split_epoch = control.SplitControl(processor)
    interpolate_after = order.BeforeEpoch(clock_epoch,INTERPOLATE_MARGIN)
    publish_after = order.AfterEpoch(clock_epoch,PUBLISH_MARGIN)
    remove_after = order.AfterEpoch(clock_epoch,REMOVE_MARGIN)
    update_publish = method.ExecuteMethod(publish_after.set_reference)
    update_remove = method.ExecuteMethod(remove_after.set_reference)
    interpolate_state = interpolate.HermiteInterpolate()
    update_interpolate = method.ExecuteMethod(interpolate_after.set_reference)
    transform_geographic = transform.InertialToGeographicTransform()
    telemetry_input = socket.SubscribeSocket(telemetry_socket,TELEMETRY_ADDRESS)
    parse_telemetry = telemetry.ParseTelemetry()
    split_telemetry = control.SplitControl(processor)
    split_state = control.SplitControl(processor)
    put_state = queue.PutQueue(state_queue)
    get_state = queue.GetQueue(state_queue)
    extract_state = telemetry.ExtractState()
    generate_inertial = product.GenerateProduct(INERTIAL_PRODUCT)
    generate_geographic = product.GenerateProduct(GEOGRAPHIC_PRODUCT)
    put_product = queue.PutQueue(product_queue)
    get_product = queue.GetQueue(product_queue)
    format_product = product.FormatProduct()
    
    product_output = socket.PublishSocket(ground_socket,PRODUCT_ADDRESS)

    segment = Application("Space segment",processor)
    
    segment.Behavior("Propagate state")
    
    segment.Scenario("Receive epoch").\
        From("Subscribe source",epoch_input).\
        When("Parse epoch",parse_epoch).\
        To("Split epoch",split_epoch)
    
    segment.Scenario("Receive telemetry").\
        From("Subscribe source",telemetry_input).\
        When("Parse telemetry",parse_telemetry).\
        Then("Update remove",update_remove).\
        And("Update publish",update_publish).\
        To("Split telemetry",split_telemetry)
    
    segment.Scenario("State extraction").\
        From("Split telemetry",split_telemetry).\
        When("Extract state",extract_state).\
        Then("Put state",put_state)
        
    segment.Scenario("Update state").\
        From("Split epoch",split_epoch).\
        When("Get state",get_state).\
        Given("After lower",remove_after).Is(True).\
        And("After upper",interpolate_after).Is(False).\
        Then("Update state",update_interpolate)
    
    segment.Scenario("Requeue state").\
        Given("After upper",interpolate_after).Is(True).\
        Then("Put telemetry",put_state)     
    
    segment.Scenario("Hermite interpolator").\
        From("Split epoch",split_epoch).\
        When("Interpolate state",interpolate_state).\
        To("Split state",split_state)
    
    segment.Scenario("Generate inertial product").\
        From("Split state",split_state).\
        Then("Generate inertial",generate_inertial).\
        And("Put inertial",put_product)
    
    segment.Scenario("Generate geographic product").\
        From("Split state",split_state).\
        Then("Transform geographic",transform_geographic).\
        And("Generate geographic",generate_geographic).\
        And("Put product",put_product)
    
    segment.Scenario("Publish product").\
        From("Split epoch",split_epoch).\
        When("Get product",get_product).\
        Given("After lower",remove_after).Is(True).\
        And("After upper",publish_after).Is(False).\
        Then("Format product",format_product).\
        To("Publish target",product_output)
    
    segment.Scenario("Requeue product").\
        Given("After upper",publish_after).Is(True).\
        Then("Put telemetry",put_product)
                
if __name__ == '__main__':main()
