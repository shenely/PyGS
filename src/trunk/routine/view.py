#!/usr/bin/env python2.7

"""View routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   15 January 2013

Purpose:    
"""


##################
# Import section #
#
#Built-in libraries
from datetime import datetime
import logging
import types
import json

#External libraries

#Internal libraries
from . import coroutine
from ..core.state import BaseState
from ..core.view import GlobalView
#
##################


##################
# Export section #
#
__all__ = ["generate"]
#
##################


####################
# Constant section #
#
__version__ = "0.1"#current version [major.minor]

EPOCH_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
#
####################


@coroutine
def generate(address,pipeline=None):
    """Generate View Message"""
    
    assert isinstance(address,types.StringTypes)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    message = None
    while True:
        states = yield message,pipeline
        
        #assert isinstance(system,BaseState)
        
        notice = GlobalView(states)
        message = address,json.dumps(notice)
                        
        logging.info("Routine.View:  Generated")