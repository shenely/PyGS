#!/usr/bin/env python2.7

"""State routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   02 February 2013

Purpose:    
"""


##################
# Import section #
#
#Built-in libraries
from datetime import datetime
import logging
import types

#External libraries
from numpy import matrix

#Internal libraries
from core import ObjectDict,coroutine,encoder,decoder
from clock.epoch import EpochState
from . import CartesianState
from .message import StateMessage
#
##################


##################
# Export section #
#
__all__ = ["update",
           "format",
           "parse"]
#
##################


####################
# Constant section #
#
__version__ = "0.1"#current version [major.minor]
#
####################


@coroutine
def update(system,pipeline=None):
    """Update System State"""
    
    assert isinstance(system,EpochState)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    while True:
        state = yield system,pipeline
        
        assert isinstance(state,type(system))
        
        system.update(state)
                        
        logging.info("Space.State:  Updated to %s" % system.epoch)

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
        message = address,encoder(notice)
                        
        logging.info("Space.State:  Formatted")

@coroutine
def parse(pipeline=None):
    """Parse State Message"""
    
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    state = None
    while True:
        address,message = yield state,pipeline
        
        assert isinstance(message,types.StringTypes)
        
        notice = decoder(message)
        
        assert hasattr(notice,"method")
        assert notice.method == "state"
        assert hasattr(notice,"params")
        assert isinstance(notice.params,ObjectDict)        
        assert hasattr(notice.params,"epoch")
        assert isinstance(notice.params.epoch,datetime)
        assert hasattr(notice.params,"position")
        assert isinstance(notice.params.position,matrix)
        assert hasattr(notice.params,"velocity")
        assert isinstance(notice.params.velocity,matrix)
        
        state = CartesianState(**notice.params)
                
        logging.info("Space.State:  Parsed as %s" % notice.params.epoch)