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
from datetime import datetime,timedelta
from Queue import PriorityQueue

#External libraries
import zmq
from bson.tz_util import utc

#Internal libraries
from core.fluent import service
from core.service.scheduler import Scheduler
from core.routine import control,queue,socket,order
from clock.epoch import routine as epoch
from .command import routine as command
from .status import routine as status
from space.acknowledge import routine as acknowledge
from space.telemetry import routine as telemetry
from model.asset import SpaceAsset
from clock.epoch import EpochState
from .command import ManeuverCommand
from .status import BaseStatus
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

EPOCH_ADDRESS = "Kepler.Epoch"
COMMAND_ADDRESS = "Kepler.{name!s}.Command"
ACKNOWLEDGE_ADDRESS = "Kepler.{name!s}.Acknowledge"
TELEMETRY_ADDRESS = "Kepler.{name!s}.Telemetry"
STATUS_ADDRESS = "Kepler.{name!s}.Status"

DISCARD_MARGIN = timedelta(seconds=0)
STATUS_MARGIN = timedelta(seconds=120)
COMMAND_MARGIN = timedelta(seconds=420)
#
####################

                
def main():
    """Main Function"""
    
    clock = EpochState(datetime(2010,1,1,0,12,30,tzinfo=utc))
    aqua = SpaceAsset("Aqua","#007777")
    aqua.command = ManeuverCommand(clock.epoch,-1.0,0.0,1.0)
    aqua.status = BaseStatus("green",clock.epoch)
    
    scheduler = Scheduler()
    context = zmq.Context(1)
    
    epoch_socket = context.socket(zmq.SUB)
    epoch_socket.connect("tcp://localhost:5556")
    epoch_socket.setsockopt(zmq.SUBSCRIBE,EPOCH_ADDRESS)
    
    command_socket = context.socket(zmq.PUB)
    command_socket.connect("tcp://localhost:5555")
    status_socket = command_socket
    
    acknowledge_socket = context.socket(zmq.SUB)
    acknowledge_socket.connect("tcp://localhost:5556")
    acknowledge_socket.setsockopt(zmq.SUBSCRIBE,ACKNOWLEDGE_ADDRESS.format(name=aqua.name))
    
    telemetry_socket = context.socket(zmq.SUB)
    telemetry_socket.connect("tcp://localhost:5556")
    telemetry_socket.setsockopt(zmq.SUBSCRIBE,TELEMETRY_ADDRESS.format(name=aqua.name))

    command_queue = PriorityQueue()
    status_queue = PriorityQueue()
    
    command_queue.put((0,aqua.command))
    status_queue.put((0,aqua.status))
    
    segment = service("Ground segment").\
        task("Receive epoch").\
            source("Subscribe epoch",socket.subscribe,epoch_socket).\
            sequence("Parse epoch",epoch.parse).\
            sequence("Update epoch",epoch.update,clock).\
            split("Split assets").\
            source("Split assets").\
            sequence("Inspect command",queue.peek,command_queue).\
            choice("Before epoch",order.before,clock,DISCARD_MARGIN).\
                istrue().\
                    sink("Remove command",queue.get,command_queue).\
                isfalse().\
                    choice("After epoch",order.after,clock,COMMAND_MARGIN).\
                        istrue().\
                            sink("Drop task").\
                        isfalse().\
                            sequence("Dequeue command",queue.get,command_queue).\
                            sequence("Format command",command.format,COMMAND_ADDRESS.format(name=aqua.name)).\
                            sink("Request command",socket.publish,command_socket).\
            source("Split assets").\
            sequence("Inspect status",queue.peek,status_queue).\
            choice("Before epoch #2",order.before,clock,DISCARD_MARGIN).\
                istrue().\
                    sink("Remove status",queue.get,status_queue).\
                isfalse().\
                    choice("After epoch #2",order.after,clock,STATUS_MARGIN).\
                        istrue().\
                            sink("Drop task").\
                        isfalse().\
                            sequence("Dequeue status",queue.get,status_queue).\
                            sequence("Format status",status.format,STATUS_ADDRESS.format(name=aqua.name)).\
                            sink("Publish status",socket.publish,status_socket).\
        task("Receive acknowledge").\
            source("Response acknowledge",socket.subscribe,acknowledge_socket).\
            sink("Block acknowledge",control.block).\
        task("Receive telemetry").\
            source("Response telemetry",socket.subscribe,telemetry_socket).\
            sink("Block telemetry",control.block).\
        build()
            
    scheduler.handler(epoch_socket,segment.tasks["Receive epoch"])
    scheduler.handler(acknowledge_socket,segment.tasks["Receive acknowledge"])
    scheduler.handler(telemetry_socket,segment.tasks["Receive telemetry"])
    
    #scheduler.start()
    
if __name__ == '__main__':
    main()
