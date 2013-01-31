#!/usr/bin/env python2.7

"""View routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   30 January 2013

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
from ..core import *
from ..core.state import BaseState
from ..core.view import *
#
##################


##################
# Export section #
#
__all__ = ["global2d",
           "global3d",
           "local"]
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
def global2d(address,pipeline=None):
    """Global 2D View Message"""
    
    assert isinstance(address,types.StringTypes)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    message = None
    while True:
        states = yield message,pipeline
        
        #assert isinstance(system,BaseState)
        
        notice = Global2DView(states)
        message = address,encoder(notice)
                        
        logging.info("Routine.View:  Global 2D")


@coroutine
def global3d(address,pipeline=None):
    """Global 3D View Message"""
    
    assert isinstance(address,types.StringTypes)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    message = None
    while True:
        states = yield message,pipeline
        
        #assert isinstance(system,BaseState)
        
        notice = Global3DView(states)
        message = address,encoder(notice)
                        
        logging.info("Routine.View:  Global 3D")


@coroutine
def local(address,pipeline=None):
    """Local View Message"""
    
    assert isinstance(address,types.StringTypes)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    message = None
    while True:
        states = yield message,pipeline
        
        #assert isinstance(system,BaseState)
        
        notice = LocalView(states)
        message = address,encoder(notice)
                        
        logging.info("Routine.View:  Local")