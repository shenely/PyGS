#!/usr/bin/env python2.7

"""User service

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   17 February 2013

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
from numpy import matrix
from bson.tz_util import utc

#Internal libraries
from core.fluent import application
from core.service.scheduler import Scheduler
from core.routine import control,queue,socket,order
from clock.epoch import routine as epoch
from space.state import routine as state
from ground.status import routine as status
from space.state.routine import transform,interpolate
from view.notice import routine as notice
from model.asset import SpaceAsset
from clock.epoch import EpochState
from ground.status import BaseStatus
from space.state import InertialState,GeographicState
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

EARTH_GRAVITION = 398600.4

EPOCH_ADDRESS = "Kepler.Epoch"
STATE_ADDRESS = "Kepler.{name!s}.State"
STATUS_ADDRESS = "Kepler.{name!s}.Status"
NOTICE_ADDRESS = "Kepler.Notice.{!s}"

ACCEPT_MARGIN = timedelta(seconds=0)
INTERPOLATE_MARGIN = timedelta(seconds=60)
STATUS_MARGIN = timedelta(seconds=60)
REMOVE_MARGIN = timedelta(seconds=0)

EPOCH_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
#
####################

        
def main():
    """Main Function"""
    
    scheduler = Scheduler()
    context = zmq.Context(1)

    clock = EpochState(datetime(2010,1,1,tzinfo=utc))
    
    aqua = SpaceAsset("Aqua","#007777")
    aqua.status = BaseStatus("blue",clock.epoch)
    aqua.state = InertialState(clock.epoch,
                               matrix([7000.0,0.0,0.0]).T,
                               matrix([0.0,7.5,0.0]).T)
    
    epoch_socket = context.socket(zmq.SUB)
    epoch_socket.connect("tcp://localhost:5556")
    epoch_socket.setsockopt(zmq.SUBSCRIBE,EPOCH_ADDRESS)
    
    status_socket = context.socket(zmq.SUB)
    status_socket.connect("tcp://localhost:5556")
    status_socket.setsockopt(zmq.SUBSCRIBE,STATUS_ADDRESS.format(name=aqua.name))
    
    state_socket = context.socket(zmq.SUB)
    state_socket.connect("tcp://localhost:5556")
    state_socket.setsockopt(zmq.SUBSCRIBE,STATE_ADDRESS.format(name=aqua.name))
    
    view_socket = context.socket(zmq.PUB)
    view_socket.connect("tcp://localhost:5555")
    
    status_queue = PriorityQueue()
    state_queue = PriorityQueue()
    
    segment = application("User segment")
    
    segment.workflow("Receive epoch").\
        source("Subscribe epoch",socket.subscribe,epoch_socket).\
        sequence("Parse epoch",epoch.parse).\
        sequence("Update epoch",epoch.update,clock).\
        split("Split assets")
        
    segment.source("Split assets").\
        sequence("Inspect status",queue.peek,status_queue).\
        choice("After lower",order.after,clock,REMOVE_MARGIN).\
            istrue().\
                choice("After upper",order.after,clock,STATUS_MARGIN).\
                    istrue().\
                        sink("Drop task").\
                    isfalse().\
                        sequence("Dequeue status",queue.get,status_queue).\
                        sink("Update status",status.update,aqua.status).\
            isfalse().\
                sink("Remove status",queue.get,status_queue)
    
    segment.assets().source("Split assets").\
        sequence("Inspect state",queue.peek,state_queue).\
        choice("After lower #2",order.after,clock,REMOVE_MARGIN).\
            istrue().\
                choice("After upper #2",order.after,clock,INTERPOLATE_MARGIN).\
                    istrue().\
                        sequence("Block state",control.block).\
                        choice("Interpolate state",interpolate.hermite,clock).\
                             istrue().\
                                sequence("Update state",state.update,aqua.state).\
                                split("Split geographic").\
                            isfalse().\
                                sink("Drop task").\
                    isfalse().\
                        sequence("Dequeue state",queue.get,state_queue).\
                        sequence("Interpolate state").\
            isfalse().\
                sink("Remove state",queue.get,state_queue)
        
    segment.assets().source("Split geographic").\
        sink("Merge inertial")
        
    segment.merge("Merge inertial").\
        sequence("Inertial notice",notice.inertial,[aqua],NOTICE_ADDRESS.format("Inertial")).\
        sink("Publish notice",socket.publish,view_socket)
        
    segment.assets().source("Split geographic").\
        sequence("Geographic transform",transform.inertial2geographic).\
        sink("Merge geographic")
        
    segment.merge("Merge geographic").\
        sequence("Geographic notice",notice.geographic,[aqua],NOTICE_ADDRESS.format("Geographic")).\
        sink("Publish notice")

    segment.workflow("Receive status").assets().\
        source("Subscribe status",socket.subscribe,status_socket).\
        sequence("Parse status",status.parse).\
        choice("After clock",order.after,clock,ACCEPT_MARGIN).\
            istrue().\
                sink("Enqueue status",queue.put,status_queue).\
            isfalse().\
                sink("Drop task")

    segment.workflow("Receive state").assets().\
        source("Subscribe state",socket.subscribe,state_socket).\
        sequence("Parse state",state.parse).\
        choice("After clock",order.after,clock,ACCEPT_MARGIN).\
            istrue().\
                sink("Enqueue state",queue.put,state_queue).\
            isfalse().\
                sink("Drop task")
    
    segment.clean()
    segment.build()
    
    scheduler.handler(epoch_socket,segment["Receive epoch"])
    scheduler.handler(status_socket,segment["Receive status"])
    scheduler.handler(state_socket,segment["Receive state"])
    
    #scheduler.start()
    
if __name__ == '__main__':
    main()
