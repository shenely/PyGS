#!/usr/bin/env python2.7

"""User segment

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   26 July 2013

Provides the user segment.

Classes:
UserSegment   -- User segment object

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-07-25    shenely         1.0         Initial revision
2013-07-26    shenely         1.1         Added view behavior

"""


##################
# Import section #
#
#Built-in libraries

#External libraries
import zmq

#Internal libraries
from . import BaseSegment
from core.routine import socket
from asset.routine import view
#
##################


##################
# Export section #
#
__all__ = ["UserSegment"]
#
##################


####################
# Constant section #
#
__version__ = "1.1"#current version [major.minor]

VIEW_ADDRESS = "{asset!s}.{segment!s}.View"
#
####################

    
class UserSegment(BaseSegment):
    def __init__(self,application,name="User"):
        BaseSegment.__init__(self,application,name)
            
        view_socket = self.context.socket(zmq.SUB)
        view_socket.connect("tcp://localhost:5556")
        
        view_address = VIEW_ADDRESS.format(asset="System",segment="Asset")
    
        sub_view = socket.SubscribeSocket(view_socket,view_address)
        parse_view = view.ParseView(self)
            
        application.Behavior("Asset view")
        
        application.Scenario("Receive asset view").\
            From("View address",sub_view).\
            When("Parse asset view",parse_view)