#!/usr/bin/env python2.7

"""Epoch routines

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

#Internal libraries
from core import coroutine,encoder,decoder
from space.state import BaseState
from .message import EpochMessage
#
##################


##################
# Export section #
#
__all__ = ["update",
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
    """Update System Epoch"""
    
    assert isinstance(system,BaseState)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    while True:
        epoch = yield system,pipeline
        
        assert isinstance(epoch,datetime)
        
        system.epoch = epoch
                        
        logging.info("Ground.Epoch:  Updated to %s" % system.epoch)

@coroutine
def format(address,pipeline=None):
    """Format Epoch Message"""
    
    assert isinstance(address,types.StringTypes)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    message = None
    while True:
        epoch = yield message,pipeline
        
        assert isinstance(epoch,datetime)
        
        notice = EpochMessage(epoch)
        message = address,encoder(notice)
        
        logging.info("Ground.Epoch:  Formatted as %s" % notice.params.epoch)

@coroutine
def parse(pipeline=None):
    """Parse Epoch Message"""
    
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    epoch = None
    while True:
        address,message = yield epoch,pipeline
        
        assert isinstance(message,types.StringTypes)
        
        notice = decoder(message)
        
        assert hasattr(notice,"method")
        assert notice.method == "epoch"
        assert hasattr(notice,"params")
        assert isinstance(notice.params,ObjectDict)
        assert hasattr(notice.params,"epoch")
        assert isinstance(notice.params.epoch,datetime)
        
        epoch = notice.params.epoch
                
        logging.info("Ground.Epoch:  Parsed as %s" % notice.params.epoch)