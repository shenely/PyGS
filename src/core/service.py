#!/usr/bin/env python2.7

"""Clock segment

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   10 August 2013

Provides the clock segment.

Classes:
ClockSegment   -- Clock segment object

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-08-10    shenely         1.0         Initial revision

"""


##################
# Import section #
#
#Built-in libraries

#External libraries
import zmq

#Internal libraries
from core.engine import Application,Behavior,Scenario
from core.routine import control,database,method,socket,message
#
##################


##################
# Export section #
#
__all__ = ["CoreService"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]

ROUTINE_ADDRESS = "System.Core.Engine"
#
####################

class CoreService(object):
    def __init__(self):
        object.__init__(self)
        
        routine_address = ROUTINE_ADDRESS
        
        context = zmq.Context(1)
        
        routine_socket = context.socket(zmq.DEALER)
        routine_socket.setsockopt(zmq.IDENTITY,routine_address)
        routine_socket.connect("tcp://localhost:5560")
                
        req_routine = socket.SocketRequest()
        req_routine.socket = routine_socket
        
        find_routine = database.DatabaseFind()
        find_routine.collection = "Objects"
        find_routine.query = {}
        
        run_query = method.PropertyTransfer()
        run_query.sourceObj = find_routine
        run_query.sourceProp = "query"
        run_query.targetObj = find_routine
        run_query.targetProp = "query"
        
        res_routine = socket.SocketRespond()
        res_routine.socket = routine_socket
        
        set_address = method.PropertyTransfer()
        set_address.sourceObj = req_routine
        set_address.sourceProp = "address"
        set_address.targetObj = res_routine
        set_address.targetProp = "address"
        
        format_routine = message.MessageFormat()
        
        routine_split = control.SplitControl()
        
        application = Application("PyGS")
        
        behavior = Behavior("Initialize clients with routines")
        
        scenario1 = Scenario("Process incoming routine request")
        behavior.scenarios.append(scenario1)
        
        scenario2 = Scenario("Iterate over routines to respond")
        behavior.scenarios.append(scenario2)
        
        application.behaviors.append(behavior)
        
        application.build()
        
        scenario1 \
        .From("Request for routines",req_routine) \
        .Then("Query for routines",run_query) \
        .And("Address to initialize",set_address) \
        .To("Cyclic split",routine_split)
        
        scenario2 \
        .From("Cyclic split",routine_split) \
        .When("One routine at a time",find_routine) \
        .Then("Format routine as string",format_routine) \
        .To("Respond with routines",res_routine) \
        .And("Cyclic split",routine_split)