#!/usr/bin/env python2.7

"""User segment

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   22 January 2013

Purpose:    
"""


##################
# Import section #
#
#Built-in libraries
from datetime import datetime,timedelta
from Queue import PriorityQueue
import logging

#External libraries
import zmq

#Internal libraries
from ..core.scheduler import Scheduler
from ..routine import control,queue,socket,epoch,state,transform,interpolate,view
from ..core.state import *
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

EARTH_GRAVITION = 368400

EPOCH_ADDRESS = "Kepler.Physics.Epoch"
STATE_ADDRESS = "Kepler.Space.{name!s}.State"
VIEW_ADDRESS = "Kepler.View.Global"

ACCEPT_MARGIN = timedelta(seconds=0)
INTERPOLATE_MARGIN = timedelta(seconds=60)
REMOVE_MARGIN = timedelta(seconds=0)

EPOCH_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
#
####################


class UserSegment(object):
    scheduler = Scheduler()
    context = zmq.Context(1)
    
    epoch_socket = context.socket(zmq.SUB)
    epoch_socket.connect("tcp://localhost:5556")
    epoch_socket.setsockopt(zmq.SUBSCRIBE,EPOCH_ADDRESS)
    
    view_socket = context.socket(zmq.PUB)
    view_socket.connect("tcp://localhost:5555")
    
    physics = BaseState(datetime.utcnow())
    tasks = []
    
    def __init__(self,name,coords):
        if not hasattr(self,"epoch_task"):
            self.task_update_epoch()
            self.task_generate_view()
        
        self.name = name
        
        self.state_socket = self.context.socket(zmq.SUB)
        self.state_socket.connect("tcp://localhost:5556")
        self.state_socket.setsockopt(zmq.SUBSCRIBE,STATE_ADDRESS.format(name=self.name))

        self.state_queue = PriorityQueue()
        
        self.socket = self.context.socket(zmq.PUB)
        self.socket.connect("tcp://localhost:5555")

        self.queue = PriorityQueue()
        
        self.task_update_state()
        self.task_interpolate_state(coords)

    @classmethod
    def task_update_epoch(cls):
        split_tasks = control.split(None,cls.tasks)
        update_epoch = epoch.update(cls.physics,split_tasks)
        parse_epoch = epoch.parse(update_epoch)
        subscribe_epoch = socket.subscribe(cls.epoch_socket,parse_epoch)
        
        cls.epoch_task = subscribe_epoch
        cls.scheduler.handler(cls.epoch_socket,cls.epoch_task)
    
    @classmethod
    def task_generate_view(cls):
        publish_view = socket.publish(cls.view_socket)
        generate_view = view.vglobal(VIEW_ADDRESS,publish_view)
        merge_tasks = control.merge(cls.tasks,generate_view)
        
        cls.view_task = merge_tasks

    def task_update_state(self):
        enqueue_state = queue.put(self.state_queue)
        after_system = epoch.after(self.physics,ACCEPT_MARGIN,enqueue_state)
        parse_state = state.parse(after_system)
        subscribe_state = socket.subscribe(self.state_socket,parse_state)
        
        self.state_task = subscribe_state
        self.scheduler.handler(self.state_socket,self.state_task)
    
    def task_interpolate_state(self,coords):
        update_state = state.update(coords,self.view_task)
        transform_state = transform.cartesian2geographic(update_state)
        interpolate_state = interpolate.hermite(self.physics,istrue=transform_state)
        dequeue_state = queue.get(self.state_queue,interpolate_state)
        block_state = control.block(interpolate_state)
        remove_state = queue.get(self.state_queue,block_state)
        after_upper = epoch.after(self.physics,INTERPOLATE_MARGIN,block_state,dequeue_state)
        after_lower = epoch.after(self.physics,REMOVE_MARGIN,after_upper,remove_state)
        inspect_state = queue.peek(self.state_queue,after_lower)
        
        self.tasks.append(inspect_state)
        
def main():
    """Main Function"""

    physics = BaseState(datetime(2010,1,1))
    aqua = GeographicState(physics.epoch,0.0,0.0,0.0)
    aura = GeographicState(physics.epoch,0.0,0.0,0.0)
    terra = GeographicState(physics.epoch,0.0,0.0,0.0)
    
    q = UserSegment("Aqua",aqua)
    r = UserSegment("Aura",aura)
    t = UserSegment("Terra",terra)
    
    #scheduler.start()
    
if __name__ == '__main__':
    main()
