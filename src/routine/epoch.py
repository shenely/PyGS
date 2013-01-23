#!/usr/bin/env python2.7

"""Epoch routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   21 January 2013

Purpose:    
"""


##################
# Import section #
#
#Built-in libraries
from datetime import datetime,timedelta
import logging
import types
import json

#External libraries

#Internal libraries
from . import coroutine
from ..core import *
from ..core.state import BaseState
from ..core.message import EpochMessage
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
def before(reference,margin,istrue=None,isfalse=None):
    """Message Epoch before Reference Epoch by Margin"""
    
    assert isinstance(reference,BaseState)
    assert isinstance(margin,timedelta)
    assert istrue is None or isinstance(istrue,types.GeneratorType)
    assert isfalse is None or isinstance(isfalse,types.GeneratorType)
    
    message,pipeline = None,None
    while True:
        message = yield message,pipeline
                
        assert isinstance(message,BaseState)

        pipeline = istrue \
                   if (message.epoch < reference.epoch - margin) \
                   else isfalse
                
        logging.info("Routine.Epoch:  Before by %s" % (reference.epoch - message.epoch))
    
@coroutine
def after(reference,margin,istrue=None,isfalse=None):
    """Message Epoch after Reference Epoch by Margin"""
    
    assert isinstance(reference,BaseState)
    assert isinstance(margin,timedelta)
    assert isinstance(istrue,types.GeneratorType) or istrue is None
    assert isinstance(isfalse,types.GeneratorType) or isfalse is None
    
    message,pipeline = None,None
    while True:
        message = yield message,pipeline
        
        assert isinstance(message,BaseState)
        
        pipeline = istrue \
                   if (message.epoch > reference.epoch + margin) \
                   else isfalse
                
        logging.info("Routine.Epoch:  After by %s" % (message.epoch - reference.epoch))

@coroutine
def around(reference,margin,istrue=None,isfalse=None):
    """Message Epoch around Reference Epoch by Margin"""
    
    assert isinstance(reference,BaseState)
    assert isinstance(margin,timedelta)
    assert isinstance(istrue,types.GeneratorType) or istrue is None
    assert isinstance(isfalse,types.GeneratorType) or isfalse is None
    
    message,pipeline = None,None
    while True:
        message = yield message,pipeline
        
        assert isinstance(message,BaseState)
    
        pipeline = istrue \
                   if (message.epoch < reference.epoch + margin) or \
                      (message.epoch > reference.epoch - margin) \
                   else isfalse
                
        logging.info("Routine.Epoch:  Around")

@coroutine
def update(system,pipeline=None):
    """Update System Epoch"""
    
    assert isinstance(system,BaseState)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    while True:
        epoch = yield system,pipeline
        
        assert isinstance(epoch,datetime)
        
        system.epoch = epoch
                        
        logging.info("Routine.Epoch:  Updated to %s" % system.epoch)

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
        
        logging.info("Routine.Epoch:  Formatted as %s" % notice.params.epoch)

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
                
        logging.info("Routine.Epoch:  Parsed as %s" % notice.params.epoch)