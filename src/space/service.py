#!/usr/bin/env python2.7

"""Space service

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   29 June 2013

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
from state import routine as state
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
STATE_ADDRESS = "Kepler.State"

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
        
    state_socket = context.socket(zmq.PUB)
    state_socket.connect("tcp://localhost:5555")
    
    state_queue = PriorityQueue()
        
#    segment = application("Clock segment")
#
#    segment.workflow("Send epoch").\
#        source("Iterate epoch",routine.continuous,clock.epoch,EPOCH_SCALE).\
#        sequence("Format epoch",epoch.format,EPOCH_ADDRESS).\
#        sink("Publish epoch",socket.publish,epoch_socket)
#    
#    segment.clean()
#    segment.build()
#
#    scheduler.periodic(segment["Send epoch"],200).start()

    input = socket.SubscribeSocket(epoch_socket,EPOCH_ADDRESS)
    parser = epoch.ParseEpoch()
    split = control.SplitControl(processor)
    iterate_before = order.BeforeEpoch(state_epoch,ITERATE_MARGIN)
    publish_after = order.AfterEpoch(clock_epoch,PUBLISH_MARGIN)
    remove_after = order.AfterEpoch(clock_epoch,REMOVE_MARGIN)
    update_publish = method.ExecuteMethod(publish_after.set_reference)
    update_remove = method.ExecuteMethod(remove_after.set_reference)
    iterator = propagate.KeplerPropagate(state_epoch)
    update_iterate = method.ExecuteMethod(iterate_before.set_reference)
    put_state = queue.PutQueue(state_queue)
    get_state = queue.GetQueue(state_queue)
    formatter = state.FormatState()
    transformer = transform.KeplerianToInertialTransform()
    output = socket.PublishSocket(state_socket,STATE_ADDRESS)

    segment = Application("Space segment",processor)
    
    segment.Behavior("Propagate state")
    
    segment.Scenario("Receive epoch").\
        From("Subscribe source",input).\
        When("Parse epoch",parser).\
        Then("Update publish",update_publish).\
        And("Update remove",update_remove).\
        To("Split epoch",split)
    
    segment.Scenario("Propagate state").\
        From("Split epoch",split).\
        Given("After state",iterate_before).Is(False).\
        Then("Keplar propagator",iterator).\
        And("Update iterate",update_iterate).\
        And("Put state",put_state)
    
    segment.Scenario("Publish state").\
        From("Split epoch",split).\
        When("Get state",get_state).\
        Given("After lower",remove_after).Is(True).\
        And("After upper",publish_after).Is(False).\
        Then("Transform state",transformer).\
        And("Format state",formatter).\
        To("Publish target",output)
    
    segment.Scenario("Requeue state").\
        Given("After upper",publish_after).Is(True).\
        Then("Put state",put_state)
    
    segment.Scenario("Remove state").\
        Given("After lower",remove_after).Is(False).\
        Then("Put state",put_state)
                
if __name__ == '__main__':main()
