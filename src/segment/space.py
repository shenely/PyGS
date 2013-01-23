#!/usr/bin/env python2.7

"""Space segment

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   22 January 2013

Purpose:    
"""


##################
# Import section #
#
#Built-in libraries
from math import pi
from datetime import datetime,timedelta
from Queue import PriorityQueue
import logging

#External libraries
import zmq

#Internal libraries
from ..core.scheduler import Scheduler
from ..routine import control,queue,socket,epoch,state,transform,iterator
from ..core.state import BaseState,KeplerianState
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

EARTH_GRAVITION = 398600

EPOCH_ADDRESS = "Kepler.Physics.Epoch"
STATE_ADDRESS = "Kepler.Space.{name!s}.State"

ITERATE_MARGIN = timedelta(seconds=300)
PUBLISH_MARGIN = timedelta(seconds=180)
REMOVE_MARGIN = timedelta(seconds=120)

STEP_SIZE = timedelta(seconds=60)

EPOCH_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
#
####################


class SpaceSegment(object):
    scheduler = Scheduler()
    context = zmq.Context(1)
    
    epoch_socket = context.socket(zmq.SUB)
    epoch_socket.connect("tcp://localhost:5556")
    epoch_socket.setsockopt(zmq.SUBSCRIBE,EPOCH_ADDRESS)
    
    physics = BaseState(datetime.utcnow())
    tasks = []
    
    def __init__(self,name,elements):
        if not hasattr(self,"epoch_task"):
            self.task_update_epoch()
        
        self.name = name
        
        self.socket = self.context.socket(zmq.PUB)
        self.socket.connect("tcp://localhost:5555")

        self.queue = PriorityQueue()
        
        self.task_iterate_state(elements)

    @classmethod
    def task_update_epoch(cls):
        split_tasks = control.split(None,cls.tasks)
        update_epoch = epoch.update(cls.physics,split_tasks)
        parse_epoch = epoch.parse(update_epoch)
        subscribe_epoch = socket.subscribe(cls.epoch_socket,parse_epoch)
        
        cls.epoch_task = subscribe_epoch
        cls.scheduler.handler(cls.epoch_socket,cls.epoch_task)
            
    def task_iterate_state(self,elements):
        publish_state = socket.publish(self.socket)
        format_state = state.format(STATE_ADDRESS.format(name=self.name),publish_state)
        transform_state = transform.keplerian2cartesian(format_state)
        dequeue_state = queue.get(self.queue,transform_state)
        remove_state = queue.get(self.queue)
        after_upper = epoch.after(self.physics,PUBLISH_MARGIN,None,dequeue_state)
        after_lower = epoch.after(self.physics,REMOVE_MARGIN,after_upper,remove_state)
        inspect_state = queue.peek(self.queue,after_lower)
        enqueue_state = queue.put(self.queue,inspect_state)
        iterate_state = iterator.kepler(elements,STEP_SIZE,pipeline=enqueue_state)
        before_state = epoch.before(elements,ITERATE_MARGIN,inspect_state,iterate_state)
        
        self.tasks.append(before_state)
                
def main():
    """Main Function"""
    
    physics = BaseState(datetime(2010,1,1))
    aqua = KeplerianState(physics.epoch,
                          7077.0,
                          0.0 * DEG_TO_RAD,
                          0.0012,
                          90.0 * DEG_TO_RAD,
                          98.2 * DEG_TO_RAD,
                          45.0 * DEG_TO_RAD)
    aura = KeplerianState(physics.epoch,
                          7077.0,
                          315.0 * DEG_TO_RAD,
                          0.0012,
                          90.0 * DEG_TO_RAD,
                          98.2 * DEG_TO_RAD,
                          45.0 * DEG_TO_RAD)
    terra = KeplerianState(physics.epoch,
                           7077.0,
                           45.0 * DEG_TO_RAD,
                           0.0012,
                           90.0 * DEG_TO_RAD,
                           98.2 * DEG_TO_RAD,
                           225.0 * DEG_TO_RAD)
    
    q = SpaceSegment("Aqua",aqua)
    r = SpaceSegment("Aura",aura)
    t = SpaceSegment("Terra",terra)
    
    #scheduler.start()
    
if __name__ == '__main__':
    main()