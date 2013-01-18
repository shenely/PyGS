#!/usr/bin/env python2.7

"""Epoch routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   16 January 2013

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
from numpy import matrix

#Internal libraries
from . import coroutine
from ..core import ObjectDict
from ..core.state import BaseState,CartesianState
from ..core.message import StateMessage
#
##################


##################
# Export section #
#
__all__ = ["before",
           "after",
           "around",
           "update",
           "format",
           "process"]
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
def update(system,pipeline=None):
    """Update System State"""
    
    assert isinstance(system,BaseState)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    while True:
        state = yield system,pipeline
        
        assert isinstance(state,type(system))
        
        system.update(state)
                        
        logging.info("Routine.State:  Updated to %s" % system.epoch)

@coroutine
def format(address,pipeline=None):
    """Format State Message"""
    
    assert isinstance(address,types.StringTypes)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    message = None
    while True:
        state = yield message,pipeline
        
        assert isinstance(state,CartesianState)
        
        notice = StateMessage(state)
        message = address,json.dumps(notice)
                        
        logging.info("Routine.State:  Formatted")

@coroutine
def process(pipeline=None):
    """Process State Message"""
    
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    state = None
    while True:
        address,message = yield state,pipeline
        
        assert isinstance(message,types.StringTypes)
        
        notice = ObjectDict(json.loads(message))
        
        assert hasattr(notice,"method")
        assert notice.method == "state"
        assert hasattr(notice,"params")
        assert isinstance(notice.params,types.DictType)
        
        notice.params = ObjectDict(notice.params)
        
        assert hasattr(notice.params,"epoch")
        assert isinstance(notice.params.epoch,types.StringTypes)
        assert hasattr(notice.params,"position")
        assert isinstance(notice.params.position,types.ListType)
        assert hasattr(notice.params,"velocity")
        assert isinstance(notice.params.velocity,types.ListType)
        
        epoch = datetime.strptime(notice.params.epoch,EPOCH_FORMAT)
        position = matrix(notice.params.position)
        velocity = matrix(notice.params.velocity)
        
        state = CartesianState(epoch,position,velocity)
                
        logging.info("Routine.State:  Processed as %s" % notice.params.epoch)