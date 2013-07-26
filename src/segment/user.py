#!/usr/bin/env python2.7

"""User segment

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   25 July 2013

Provides the user segment.

Classes:
UserSegment   -- User segment object

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

#Internal libraries
from . import BaseSegment
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
__version__ = "1.0"#current version [major.minor]
#
####################

    
class UserSegment(BaseSegment):
    def __init__(self,application,name="User"):
        BaseSegment.__init__(self,application,name)