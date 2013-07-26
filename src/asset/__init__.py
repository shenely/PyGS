#!/usr/bin/env python2.7

"""Asset objects

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   25 July 2013

Provides the asset objects.

Classes:
BaseAsset   -- Base asset object

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
from core import BaseObject
#
##################


##################
# Export section #
#
__all__ = ["BaseAsset"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]
#
####################


class BaseAsset(BaseObject):
    def __init__(self,segment,name):
        BaseObject.__init__(self)
        
        self.segment = segment
        self.name = name
        
        self.application = segment.application
        self.context = segment.context