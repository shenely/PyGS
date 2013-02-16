#!/usr/bin/env python2.7

"""Space service

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   15 February 2013

Purpose:    
"""


##################
# Import section #
#
#Built-in libraries
from math import pi
from datetime import datetime,timedelta
from Queue import PriorityQueue

#External libraries
import zmq
from bson.tz_util import utc

#Internal libraries
from core.service.scheduler import Scheduler
from core.fluent import service
from core.routine import queue,socket,order,database
from clock.epoch import routine as epoch
from .state import routine as state
from .state.routine import transform,propagate
from ground.command import routine as command
from .acknowledge import routine as acknowledge
from .telemetry import routine as telemetry
from model.asset import SpaceAsset
from clock.epoch import EpochState
from .state import KeplerianState
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

DEG_TO_RAD = pi / 180
RAD_TO_DEG = 180 / pi

EARTH_GRAVITION = 398600.4

EPOCH_ADDRESS = "Kepler.Epoch"
STATE_ADDRESS = "Kepler.{name!s}.State"
COMMAND_ADDRESS = "Kepler.{name!s}.Command"
ACKNOWLEDGE_ADDRESS = "Kepler.{name!s}.Acknowledge"
TELEMETRY_ADDRESS = "Kepler.{name!s}.Telemetry"
ASSET_ADDRESS = "Kepler.Model.Asset"
EPHEMERIS_ADDRESS = "Kepler.Model.Ephemeris"

ITERATE_MARGIN = timedelta(seconds=300)
EXECUTE_MARGIN = timedelta(seconds=30)
PUBLISH_MARGIN = timedelta(seconds=180)
REMOVE_MARGIN = timedelta(seconds=120)
COMMAND_MARGIN = timedelta(seconds=180)

STEP_SIZE = timedelta(seconds=60)

EPOCH_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
#
####################       

                
def main():
    """Main Function"""
    
    clock = EpochState(datetime(2010,1,1,tzinfo=utc))
    aqua = SpaceAsset("Aqua","#007777")
    aqua.state = KeplerianState(clock.epoch,
                                7077.0,
                                0.0 * DEG_TO_RAD,
                                0.0012,
                                90.0 * DEG_TO_RAD,
                                98.2 * DEG_TO_RAD,
                                22.5 * DEG_TO_RAD)
    
    scheduler = Scheduler()
    context = zmq.Context(1)
    
    epoch_socket = context.socket(zmq.SUB)
    epoch_socket.connect("tcp://localhost:5556")
    epoch_socket.setsockopt(zmq.SUBSCRIBE,EPOCH_ADDRESS)
    
    state_socket = context.socket(zmq.PUB)
    state_socket.connect("tcp://localhost:5555")
    acknowledge_socket = state_socket
    telemetry_socket = state_socket

    command_socket = context.socket(zmq.SUB)
    command_socket.connect("tcp://localhost:5556")
    command_socket.setsockopt(zmq.SUBSCRIBE,COMMAND_ADDRESS.format(name=aqua.name))

    state_queue = PriorityQueue()
    command_queue = PriorityQueue()
    
    segment = service("Space segment").\
        task("Receive epoch").\
            source("Subscribe epoch",socket.subscribe,epoch_socket).\
            sequence("Parse epoch",epoch.parse).\
            sequence("Update epoch",epoch.update,clock).\
            split("Split assets").\
            source("Split assets").\
            choice("Before state",order.before,aqua.state,ITERATE_MARGIN).\
                istrue().\
                    sequence("Inspect state",queue.peek,state_queue).\
                    choice("After lower",order.after,clock,REMOVE_MARGIN).\
                        istrue().\
                            choice("After upper",order.after,clock,PUBLISH_MARGIN).\
                                istrue().\
                                    sink("Drop task").\
                                isfalse().\
                                    sequence("Dequeue state",queue.get,state_queue).\
                                    sequence("Transform state",transform.keplerian2inertial).\
                                    sequence("Format state",state.format,STATE_ADDRESS.format(name=aqua.name)).\
                                    sink("Publish state",socket.publish,state_socket).\
                        isfalse().\
                            sink("Remove state",queue.get,state_queue).\
                isfalse().\
                    sequence("Propagate state",propagate.kepler,aqua.state,STEP_SIZE).\
                    sequence("Enqueue state",queue.put,state_queue).\
                    sequence("Inspect state").\
            source("Split assets").\
            sequence("Inspect command",queue.peek,command_queue).\
            choice("Before state #2",order.before,aqua.state,EXECUTE_MARGIN).\
                istrue().\
                    sink("Remove command",queue.get,command_queue).\
                isfalse().\
                    choice("After state",order.after,aqua.state,EXECUTE_MARGIN).\
                        istrue().\
                            sink("Drop task").\
                        isfalse().\
                            sequence("Dequeue command",queue.get,command_queue).\
                            sequence("Execute command",command.execute,aqua.state).\
                            sequence("Format telemetry",telemetry.format,TELEMETRY_ADDRESS.format(name=aqua.name)).\
                            sink("Publish telemetry",socket.publish,telemetry_socket).\
        task("Receive command").\
            source("Subscribe command",socket.subscribe,command_socket).\
            sequence("Parse command",command.parse).\
            choice("After epoch",order.after,clock,COMMAND_MARGIN).\
                istrue().\
                    sequence("Enqueue command",queue.put,command_queue).\
                    sequence("Accept command",acknowledge.accept).\
                    sequence("Format acknowledge",acknowledge.format,ACKNOWLEDGE_ADDRESS.format(name=aqua.name)).\
                    sink("Publish acknowledge",socket.publish,acknowledge_socket).\
                isfalse().\
                    sequence("Reject command",acknowledge.reject).\
                    sequence("Format acknowledge").\
        build()
            
    scheduler.handler(epoch_socket,segment.tasks["Receive epoch"])
    scheduler.handler(command_socket,segment.tasks["Receive command"])
    
    #scheduler.start()
    
if __name__ == '__main__':
    main()
