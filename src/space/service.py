#!/usr/bin/env python2.7

"""Space service

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   19 July 2013

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
from message import ORBIT_TELEMETRY
from message.routine import telemetry
from state.routine import propagate,transform
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

ITERATE_MARGIN = timedelta(seconds=300)
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
    state_epoch = KeplerianState(datetime(2010,1,1,tzinfo=utc),
                                 7000.0,0.0,0.0,0.0,0.0,0.0)
        
    epoch_socket = context.socket(zmq.SUB)
    epoch_socket.connect("tcp://localhost:5556")
        
    space_socket = context.socket(zmq.PUB)
    space_socket.connect("tcp://localhost:5555")
    
    state_queue = PriorityQueue()

    clock_input = socket.SubscribeSocket(epoch_socket,EPOCH_ADDRESS)
    parse_epoch = epoch.ParseEpoch()
    split_epoch = control.SplitControl(processor)
    iterate_before = order.BeforeEpoch(state_epoch,ITERATE_MARGIN)
    publish_after = order.AfterEpoch(clock_epoch,PUBLISH_MARGIN)
    remove_after = order.AfterEpoch(clock_epoch,REMOVE_MARGIN)
    update_publish = method.ExecuteMethod(publish_after.set_reference)
    update_remove = method.ExecuteMethod(remove_after.set_reference)
    iterate_state = propagate.KeplerPropagate(state_epoch)
    update_iterate = method.ExecuteMethod(iterate_before.set_reference)
    state_transformer = transform.KeplerianToInertialTransform()
    merge_telemetry = control.MergeControl()
    generate_telemetry = telemetry.GenerateTelemetry(ORBIT_TELEMETRY)
    put_telemetry = queue.PutQueue(state_queue)
    get_telemetry = queue.GetQueue(state_queue)
    format_telemetry = telemetry.FormatTelemetry()
    telemetry_output = socket.PublishSocket(space_socket,TELEMETRY_ADDRESS)

    segment = Application("Space segment",processor)
    
    segment.Behavior("Propagate state")
    
    segment.Scenario("Receive epoch").\
        From("Subscribe source",clock_input).\
        When("Parse epoch",parse_epoch).\
        To("Split epoch",split_epoch)
    
    # General asset section
    segment.Scenario("Publish telemetry").\
        From("Split epoch",split_epoch).\
        When("Get telemetry",get_telemetry).\
        Given("After lower",remove_after).Is(True).\
        And("After upper",publish_after).Is(False).\
        Then("Format telemetry",format_telemetry).\
        To("Publish target",telemetry_output)
    
    segment.Scenario("Requeue telemetry").\
        Given("After upper",publish_after).Is(True).\
        Then("Put telemetry",put_telemetry)
    # End section
    
    # Special asset section
    segment.Scenario("Update epoch").\
        From("Split epoch",split_epoch).\
        Then("Update publish",update_publish).\
        And("Update remove",update_remove)
        
    segment.Scenario("Propagate state").\
        From("Split epoch",split_epoch).\
        Given("After state",iterate_before).Is(False).\
        Then("Iterate state",iterate_state).\
        And("Update iterate",update_iterate).\
        And("Transform state",state_transformer).\
        And("Generate telemetry",generate_telemetry).\
        And("Put state",put_telemetry)
    # End section
                
if __name__ == '__main__':main()
