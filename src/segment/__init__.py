#!/usr/bin/env python2.7

"""Segment

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   25 July 2013

Provides the segment objects.

Classes:
BaseSegment   -- Base segement object

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-07-25    shenely         1.0         Initial revision

"""


##################
# Import section #
#
#Built-in libraries

#External libraries
import zmq

#Internal libraries
from core import BaseObject
#
##################


##################
# Export section #
#
__all__ = ["BaseSegment"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]
#
####################


class BaseSegment(BaseObject):
    def __init__(self,application,name):
        BaseObject.__init__(self)
        
        self.application = application
        self.name = name
        
        self.context = zmq.Context(1)