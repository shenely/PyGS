#!/usr/bin/env python2.7

"""User service

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   12 February 2013

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
from core.service.scheduler import Scheduler
from core.routine import control,queue,socket,sequence
from clock.epoch import routine as epoch
from space.state import routine as state
from ground.status import routine as status
from space.state.routine import transform,interpolate
from view.notice import routine as notice
from space import Spacecraft
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
    spacecraft = []
    
    def __init__(self,spacecraft):        
        self.spacecraft.append(spacecraft)
                
        self.state_socket = self.context.socket(zmq.SUB)
        self.state_socket.connect("tcp://localhost:5556")
        self.state_socket.setsockopt(zmq.SUBSCRIBE,STATE_ADDRESS.format(name=spacecraft.name))

        self.state_queue = PriorityQueue()
                
        self.status_socket = self.context.socket(zmq.SUB)
        self.status_socket.connect("tcp://localhost:5556")
        self.status_socket.setsockopt(zmq.SUBSCRIBE,STATUS_ADDRESS.format(name=spacecraft.name))

        self.status_queue = PriorityQueue()
        
        self.socket = self.context.socket(zmq.PUB)
        self.socket.connect("tcp://localhost:5555")

        self.queue = PriorityQueue()
        
        if not hasattr(self,"epoch_task"):
            self.task_update_epoch()
            self.task_generate_view()
        
        self.task_update_state()
        self.task_subscribe_status()
        self.task_interpolate_state(spacecraft.state)
        self.task_update_status(spacecraft.status)

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
        view_local = notice.horizontal(cls.spacecraft,NOTICE_ADDRESS.format("Horizontal"),publish_view)
        merge_tasks_local = control.merge(cls.tasks,view_local)
        horizontal_transform = transform.geographic2horizontal(point,merge_tasks_local)
        view_global2d = notice.geographic(cls.spacecraft,NOTICE_ADDRESS.format("Geographic"),publish_view)
        merge_tasks_global2d = control.merge(cls.tasks,view_global2d)
        split_views_2d = control.split(None,[merge_tasks_global2d,horizontal_transform])
        geographic_transform = transform.inertial2geographic(split_views_2d)
        view_global3d = notice.inertial(cls.spacecraft,NOTICE_ADDRESS.format("Inertial"),publish_view)
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

    def task_subscribe_status(self):
        enqueue_status = queue.put(self.status_queue)
        after_system = sequence.after(self.physics,ACCEPT_MARGIN,enqueue_status)
        parse_status = status.parse(after_system)
        subscribe_status = socket.subscribe(self.status_socket,parse_status)
        
        self.status_task = subscribe_status
        self.scheduler.handler(self.status_socket,self.status_task)
    
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
    
    def task_update_status(self,color):
        update_status = status.update(color)
        dequeue_status = queue.get(self.status_queue,update_status)
        remove_status = queue.get(self.status_queue)
        after_upper = sequence.after(self.physics,STATUS_MARGIN,None,dequeue_status)
        after_lower = sequence.after(self.physics,REMOVE_MARGIN,after_upper,remove_status)
        inspect_status = queue.peek(self.status_queue,after_lower)
        
        self.tasks.append(inspect_status)
        
def main():
    """Main Function"""

    epoch = datetime(2010,1,1,tzinfo=utc)
    aqua = Spacecraft("Aqua",
                      "#007777",
                      BaseStatus("blue",epoch),
                      InertialState(epoch,
                                    matrix([7000.0,0.0,0.0]).T,
                                    matrix([0.0,7.5,0.0]).T))
    aura = Spacecraft("Aura",
                      "#ff7700",
                      BaseStatus("blue",epoch),
                      InertialState(epoch,
                                    matrix([7000.0,0.0,0.0]).T,
                                    matrix([0.0,7.5,0.0]).T))
    terra = Spacecraft("Terra",
                      "#007700",
                      BaseStatus("blue",epoch),
                      InertialState(epoch,
                                    matrix([7000.0,0.0,0.0]).T,
                                    matrix([0.0,7.5,0.0]).T))
    
    q = UserSegment(aqua)
    r = UserSegment(aura)
    t = UserSegment(terra)
    
    #scheduler.start()
    
if __name__ == '__main__':
    main()
