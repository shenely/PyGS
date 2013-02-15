#!/usr/bin/env python2.7

"""Space service

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   14 February 2013

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
from core.routine import control,queue,socket,order,database
from clock.epoch import routine as epoch
from .state import routine as state
from .state.routine import transform,propagate
from ground.command import routine as command
from .acknowledge import routine as acknowledge
from .result import routine as result
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
RESULT_ADDRESS = "Kepler.{name!s}.Result"
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


class SpaceSegment(object):
    scheduler = Scheduler()
    context = zmq.Context(1)
    
    #connection = MongoClient()
    #database = connection["Kepler"]
    
    epoch_socket = context.socket(zmq.SUB)
    epoch_socket.connect("tcp://localhost:5556")
    epoch_socket.setsockopt(zmq.SUBSCRIBE,EPOCH_ADDRESS)
    
    asset_socket = context.socket(zmq.SUB)
    asset_socket.connect("tcp://localhost:5556")
    asset_socket.setsockopt(zmq.SUBSCRIBE,ASSET_ADDRESS)
    
    ephem_socket = context.socket(zmq.SUB)
    ephem_socket.connect("tcp://localhost:5556")
    ephem_socket.setsockopt(zmq.SUBSCRIBE,EPHEMERIS_ADDRESS)
    
    physics = EpochState(datetime.utcnow())
    tasks = []
    
    def __init__(self,name,elements):
        if not hasattr(self,"epoch_task"):
            self.task_update_epoch()
            #self.task_update_system()
        
        self.name = name
        
        self.socket = self.context.socket(zmq.PUB)
        self.socket.connect("tcp://localhost:5555")
    
        self.cmd_socket = self.context.socket(zmq.SUB)
        self.cmd_socket.connect("tcp://localhost:5556")
        self.cmd_socket.setsockopt(zmq.SUBSCRIBE,COMMAND_ADDRESS.format(name=self.name))

        self.queue = PriorityQueue()
        self.cmd_queue = PriorityQueue()
        
        self.task_iterate_state(elements)
        self.task_acknowledge_command()
        self.task_execute_command(elements)

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
        transform_state = transform.keplerian2inertial(format_state)
        dequeue_state = queue.get(self.queue,transform_state)
        remove_state = queue.get(self.queue)
        after_upper = order.after(self.physics,PUBLISH_MARGIN,None,dequeue_state)
        after_lower = order.after(self.physics,REMOVE_MARGIN,after_upper,remove_state)
        inspect_state = queue.peek(self.queue,after_lower)
        enqueue_state = queue.put(self.queue,inspect_state)
        iterate_state = propagate.kepler(elements,STEP_SIZE,enqueue_state)
        before_state = order.before(elements,ITERATE_MARGIN,inspect_state,iterate_state)
        
        self.tasks.append(before_state)

    def task_acknowledge_command(self):
        publish_ack = socket.publish(self.socket)
        format_ack = acknowledge.format(ACKNOWLEDGE_ADDRESS.format(name=self.name),publish_ack)
        accept_cmd = acknowledge.accept(format_ack)
        enqueue_cmd = queue.put(self.cmd_queue,accept_cmd)
        reject_cmd = acknowledge.reject(format_ack)
        after_epoch = order.after(self.physics,COMMAND_MARGIN,enqueue_cmd,reject_cmd)
        parse_cmd = command.parse(after_epoch)
        subscribe_cmd = socket.subscribe(self.cmd_socket,parse_cmd)
        
        self.cmd_task = subscribe_cmd
        self.scheduler.handler(self.cmd_socket,self.cmd_task)

    def task_execute_command(self,elements):
        publish_result = socket.publish(self.socket)
        format_result = result.format(RESULT_ADDRESS.format(name=self.name),publish_result)
        execute_cmd = command.execute(elements,format_result)
        dequeue_cmd = queue.get(self.cmd_queue,execute_cmd)
        remove_cmd = queue.get(self.cmd_queue)
        after_state = order.after(elements,EXECUTE_MARGIN,None,dequeue_cmd)
        before_state = order.before(elements,EXECUTE_MARGIN,remove_cmd,after_state)
        inspect_cmd = queue.peek(self.cmd_queue,before_state)
        
        self.tasks.append(inspect_cmd)
    
    @classmethod
    def task_publish_system(cls):
        save_asset = database.save(cls.database["asset"])
        parse_asset = asset.parse(save_asset)
        subscribe_asset = socket.subscribe(cls.asset_socket,parse_asset)
        
        cls.asset_task = subscribe_asset
        cls.scheduler.handler(cls.asset_socket,cls.asset_task)
        
        publish_system = socket.publish(cls.socket)
        format_system = system.format(publish_system)
        merge_ephem = control.merge([None,None],format_system)
        find_asset = database.find(cls.database["asset"],merge_ephem)
        query_asset = asset.query(find_asset,find_asset)
        save_ephem = database.save(cls.database["ephemeris"],merge_ephem)
        split_ephem = control.split(None,[save_ephem,query_asset])
        parse_ephem = ephemeris.parse(split_ephem)
        subscribe_ephem = socket.subscribe(cls.ephem_socket,parse_ephem)
        
        cls.ephem_task = subscribe_ephem
        cls.scheduler.handler(cls.ephem_task,cls.ephem_task)
        
    
                
def main():
    """Main Function"""
    
    clock = EpochState(datetime(2010,1,1,tzinfo=utc))
    aqua = KeplerianState(clock.epoch,
                          7077.0,
                          0.0 * DEG_TO_RAD,
                          0.0012,
                          90.0 * DEG_TO_RAD,
                          98.2 * DEG_TO_RAD,
                          22.5 * DEG_TO_RAD)
    aura = KeplerianState(clock.epoch,
                          7077.0,
                          315.0 * DEG_TO_RAD,
                          0.0012,
                          90.0 * DEG_TO_RAD,
                          98.2 * DEG_TO_RAD,
                          22.5 * DEG_TO_RAD)
    terra = KeplerianState(clock.epoch,
                           7077.0,
                           45.0 * DEG_TO_RAD,
                           0.0012,
                           90.0 * DEG_TO_RAD,
                           98.2 * DEG_TO_RAD,
                           157.5 * DEG_TO_RAD)
    
#    scheduler = Scheduler()
#    context = zmq.Context(1)
#    
#    #connection = MongoClient()
#    #database = connection["Kepler"]
#    
#    epoch_socket = context.socket(zmq.SUB)
#    epoch_socket.connect("tcp://localhost:5556")
#    epoch_socket.setsockopt(zmq.SUBSCRIBE,EPOCH_ADDRESS)
#    
#    state_socket = context.socket(zmq.PUB)
#    state_socket.connect("tcp://localhost:5555")
#    acknowledge_socket = state_socket
#
#    command_socket = context.socket(zmq.SUB)
#    command_socket.connect("tcp://localhost:5556")
#    command_socket.setsockopt(zmq.SUBSCRIBE,COMMAND_ADDRESS.format(name="Aqua"))
#
#    state_queue = PriorityQueue()
#    command_queue = PriorityQueue()
    
#    asset_socket = context.socket(zmq.SUB)
#    asset_socket.connect("tcp://localhost:5556")
#    asset_socket.setsockopt(zmq.SUBSCRIBE,ASSET_ADDRESS)
#    
#    ephem_socket = context.socket(zmq.SUB)
#    ephem_socket.connect("tcp://localhost:5556")
#    ephem_socket.setsockopt(zmq.SUBSCRIBE,EPHEMERIS_ADDRESS)
    
    q = SpaceSegment("Aqua",aqua)
    r = SpaceSegment("Aura",aura)
    t = SpaceSegment("Terra",terra)
    
#    segment = service("Space segment").\
#        task("Receive epoch").\
#            source("Subscribe epoch",socket.subscribe,epoch_socket).\
#            sequence("Parse epoch",epoch.parse).\
#            sequence("Update epoch",epoch.update,clock).\
#            split("Split assets",["Iterate state","Execute command"]).\
#        task("Iterate state").\
#            source("Receive epoch").\
#            choice("Before state",order.before,aqua,ITERATE_MARGIN).\
#                istrue().\
#                    sequence("Inspect state",queue.peek,state_queue).\
#                    choice("After lower",order.after,clock,REMOVE_MARGIN).\
#                        istrue().\
#                            choice("After upper",order.after,clock,PUBLISH_MARGIN).\
#                                istrue().\
#                                    sink("Drop task").\
#                                isfalse().\
#                                    sequence("Dequeue state",queue.get,state_queue).\
#                                    sequence("Transform state",transform.keplerian2inertial).\
#                                    sequence("Format state",state.format,STATE_ADDRESS.format(name="Aqua")).\
#                                    sink("Publish state",socket.publish,state_socket).\
#                        isfalse().\
#                            sink("Remove state",queue.get,state_queue).\
#                isfalse().\
#                    sequence("Propagate state",propagate.kepler,aqua,STEP_SIZE).\
#                    sequence("Enqueue state",queue.put,state_queue).\
#                    sequence("Inspect state").\
#        task("Receive command").\
#            source("Subscribe command",socket.subscribe,command_socket).\
#            sequence("Parse command",command.parse).\
#            choice("After epoch",order.after,clock,COMMAND_MARGIN).\
#                istrue().\
#                    sequence("Enqueue command",queue.put,command_queue).\
#                    sequence("Accept command",acknowledge.accept).\
#                    sequence("Format acknowledge",acknowledge.format,ACKNOWLEDGE_ADDRESS.format(name="Aqua")).\
#                    sink("Publish acknowledge",socket.publish,acknowledge_socket).\
#                isfalse().\
#                    sequence("Reject command",acknowledge.reject).\
#                    sequence("Format acknowledge").\
#        task("Execute command").\
#            source("Receive epoch").\
#            sequence("Inspect command",queue.peek,command_queue).\
#            choice("Before state",order.before,aqua,EXECUTE_MARGIN).\
#                istrue().\
#                    sink("Remove command",queue.get,command_queue).\
#                isfalse().\
#                    choice("After state",order.after,aqua,EXECUTE_MARGIN).\
#                        istrue().\
#                            sink("Drop task").\
#                        isfalse().\
#                            sequence("Dequeue command",queue.get,command_queue).\
#                            sequence("Execute command",command.execute,aqua).\
#                            sequence("Format result",result.format,RESULT_ADDRESS.format(name="Aqua")).\
#                            sink("Publish result",socket.publish,socket).\
#        build()
#            
#    scheduler.handler(epoch_socket,segment.tasks["Receive epoch"])
#    scheduler.handler(command_socket,segment.tasks["Receive command"])
    
    #scheduler.start()
    
if __name__ == '__main__':
    main()
