#!/usr/bin/env python2.7

"""Space service

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
from bson.tz_util import utc

#Internal libraries
from core.service.scheduler import Scheduler
from core.routine import control,queue,socket,sequence
from clock.epoch import routine as epoch
from .command import routine as command
#from .status import routine as status
#from space.acknowledge import routine as acknowledge
#from space.result import routine as result
from clock.epoch import EpochState
from .command import ManeuverCommand
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
RESULT_ADDRESS = "Kepler.{name!s}.Result"
STATUS_ADDRESS = "Kepler.{name!s}.Status"

DISCARD_MARGIN = timedelta(seconds=0)
STATUS_MARGIN = timedelta(seconds=120)
COMMAND_MARGIN = timedelta(seconds=420)
#
####################


class GroundSegment(object):
    scheduler = Scheduler()
    context = zmq.Context(1)
    
    epoch_socket = context.socket(zmq.SUB)
    epoch_socket.connect("tcp://localhost:5556")
    epoch_socket.setsockopt(zmq.SUBSCRIBE,EPOCH_ADDRESS)
    
    physics = EpochState(datetime.utcnow())
    tasks = []
    
    def __init__(self,name):
        if not hasattr(self,"epoch_task"):
            self.task_update_epoch()
        
        self.name = name
        
        self.socket = self.context.socket(zmq.PUB)
        self.socket.connect("tcp://localhost:5555")
    
        self.ack_socket = self.context.socket(zmq.SUB)
        self.ack_socket.connect("tcp://localhost:5556")
        self.ack_socket.setsockopt(zmq.SUBSCRIBE,ACKNOWLEDGE_ADDRESS.format(name=self.name))
    
        self.result_socket = self.context.socket(zmq.SUB)
        self.result_socket.connect("tcp://localhost:5556")
        self.result_socket.setsockopt(zmq.SUBSCRIBE,RESULT_ADDRESS.format(name=self.name))

        self.cmd_queue = PriorityQueue()
        self.status_queue = PriorityQueue()
        
        self.task_request_command()
        #self.task_publish_status()
        self.task_schedule_event()

    @classmethod
    def task_update_epoch(cls):
        split_tasks = control.split(None,cls.tasks)
        update_epoch = epoch.update(cls.physics,split_tasks)
        parse_epoch = epoch.parse(update_epoch)
        subscribe_epoch = socket.subscribe(cls.epoch_socket,parse_epoch)
        
        cls.epoch_task = subscribe_epoch
        cls.scheduler.handler(cls.epoch_socket,cls.epoch_task)

    def task_request_command(self):
        request_cmd = socket.publish(self.socket)
        format_cmd = command.format(COMMAND_ADDRESS.format(name=self.name),request_cmd)
        dequeue_cmd = queue.get(self.cmd_queue,format_cmd)
        remove_cmd = queue.get(self.cmd_queue)
        after_system = sequence.after(self.physics,COMMAND_MARGIN,None,dequeue_cmd)
        before_system = sequence.before(self.physics,DISCARD_MARGIN,remove_cmd,after_system)
        inspect_cmd = queue.peek(self.cmd_queue,before_system)
        
        self.tasks.append(inspect_cmd)

    def task_publish_status(self):
        publish_status = socket.publish(self.socket)
        format_status = status.format(STATUS_ADDRESS.format(name=self.name),publish_status)
        dequeue_status = queue.get(self.status_queue,format_status)
        remove_status = queue.get(self.status_queue)
        after_system = sequence.after(self.physics,STATUS_MARGIN,None,dequeue_status)
        before_system = sequence.before(self.physics,DISCARD_MARGIN,remove_status,after_system)
        inspect_status = queue.peek(self.status_queue,before_system)
        
        self.tasks.append(inspect_status)

    def task_schedule_event(self):
        #parse_ack = acknowledge.parse()
        subscribe_ack = socket.subscribe(self.ack_socket)#,parse_ack)
        
        self.ack_task = subscribe_ack
        self.scheduler.handler(self.ack_socket,self.ack_task)
        
        #parse_result = result.parse()
        subscribe_result = socket.subscribe(self.result_socket)#,parse_result)
        
        self.result_task = subscribe_result
        self.scheduler.handler(self.result_socket,self.result_task)
                
def main():
    """Main Function"""
    
    epoch = datetime(2010,1,1,0,12,30,tzinfo=utc)
    aura = ManeuverCommand(epoch,0.0,0.0,1.0)
    
    q = GroundSegment("Aqua")
    r = GroundSegment("Aura")
    t = GroundSegment("Terra")
    
    r.cmd_queue.put((0,aura))
    
    #scheduler.start()
    
if __name__ == '__main__':
    main()