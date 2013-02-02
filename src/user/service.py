#!/usr/bin/env python2.7

"""User service

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   02 February 2013

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

#Internal libraries
from core.service.scheduler import Scheduler
from core.routine import control,queue,socket,sequence
from clock.epoch import routine as epoch
from space.state import routine as state
from space.state.routine import transform,interpolate
from view import routine as view
from . import routine
from clock.epoch import EpochState
from space.state import CartesianState,GeographicState
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
VIEW_ADDRESS = "Kepler.View.{!s}"

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
    
    physics = EpochState(datetime.utcnow())
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
        point = GeographicState(datetime(2010,1,1),0.0,0.0,0.0)
        
        publish_view = socket.publish(cls.view_socket)
        view_local = view.local(VIEW_ADDRESS.format("Local"),publish_view)
        merge_tasks_local = control.merge(cls.tasks,view_local)
        horizontal_transform = transform.geographic2horizontal(point,merge_tasks_local)
        view_global2d = view.global2d(VIEW_ADDRESS.format("Global2"),publish_view)
        merge_tasks_global2d = control.merge(cls.tasks,view_global2d)
        split_views_2d = control.split(None,[merge_tasks_global2d,horizontal_transform])
        geographic_transform = transform.cartesian2geographic(split_views_2d)
        view_global3d = view.global3d(VIEW_ADDRESS.format("Global3"),publish_view)
        merge_tasks3d = control.merge(cls.tasks,view_global3d)
        split_views = control.split(None,[merge_tasks3d,geographic_transform])
        
        cls.view_task = split_views

    def task_update_state(self):
        enqueue_state = queue.put(self.state_queue)
        after_system = sequence.after(self.physics,ACCEPT_MARGIN,enqueue_state)
        parse_state = state.parse(after_system)
        subscribe_state = socket.subscribe(self.state_socket,parse_state)
        
        self.state_task = subscribe_state
        self.scheduler.handler(self.state_socket,self.state_task)
    
    def task_interpolate_state(self,coords):
        update_state = state.update(coords,self.view_task)
        interpolate_state = interpolate.hermite(self.physics,istrue=update_state)
        dequeue_state = queue.get(self.state_queue,interpolate_state)
        block_state = control.block(interpolate_state)
        remove_state = queue.get(self.state_queue,block_state)
        after_upper = sequence.after(self.physics,INTERPOLATE_MARGIN,block_state,dequeue_state)
        after_lower = sequence.after(self.physics,REMOVE_MARGIN,after_upper,remove_state)
        inspect_state = queue.peek(self.state_queue,after_lower)
        
        self.tasks.append(inspect_state)
        
def main():
    """Main Function"""

    epoch = datetime(2010,1,1)
    aqua = CartesianState(epoch,
                          matrix([7000.0,0.0,0.0]).T,
                          matrix([0.0,7.5,0.0]).T)
    aura = CartesianState(epoch,
                          matrix([7000.0,0.0,0.0]).T,
                          matrix([0.0,7.5,0.0]).T)
    terra = CartesianState(epoch,
                          matrix([7000.0,0.0,0.0]).T,
                          matrix([0.0,7.5,0.0]).T)
    
    q = UserSegment("Aqua",aqua)
    r = UserSegment("Aura",aura)
    t = UserSegment("Terra",terra)
    
    #scheduler.start()
    
if __name__ == '__main__':
    main()
