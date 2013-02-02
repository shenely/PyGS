#!/usr/bin/env python2.7

"""Sequence routines

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

#External libraries

#Internal libraries
from .. import coroutine
from clock.epoch import EpochState
#
##################


##################
# Export section #
#
__all__ = ["before",
           "after",
           "around"]
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
    
    assert isinstance(reference,EpochState)
    assert isinstance(margin,timedelta)
    assert istrue is None or isinstance(istrue,types.GeneratorType)
    assert isfalse is None or isinstance(isfalse,types.GeneratorType)
    
    message,pipeline = None,None
    while True:
        message = yield message,pipeline
                
        assert isinstance(message,EpochState)

        pipeline = istrue \
                   if (message.epoch < reference.epoch - margin) \
                   else isfalse
                
        logging.info("Routine.Epoch:  Before by %s" % (reference.epoch - message.epoch))
    
@coroutine
def after(reference,margin,istrue=None,isfalse=None):
    """Message Epoch after Reference Epoch by Margin"""
    
    assert isinstance(reference,EpochState)
    assert isinstance(margin,timedelta)
    assert isinstance(istrue,types.GeneratorType) or istrue is None
    assert isinstance(isfalse,types.GeneratorType) or isfalse is None
    
    message,pipeline = None,None
    while True:
        message = yield message,pipeline
        
        assert isinstance(message,EpochState)
        
        pipeline = istrue \
                   if (message.epoch > reference.epoch + margin) \
                   else isfalse
                
        logging.info("Routine.Epoch:  After by %s" % (message.epoch - reference.epoch))

@coroutine
def around(reference,margin,istrue=None,isfalse=None):
    """Message Epoch around Reference Epoch by Margin"""
    
    assert isinstance(reference,EpochState)
    assert isinstance(margin,timedelta)
    assert isinstance(istrue,types.GeneratorType) or istrue is None
    assert isinstance(isfalse,types.GeneratorType) or isfalse is None
    
    message,pipeline = None,None
    while True:
        message = yield message,pipeline
        
        assert isinstance(message,EpochState)
    
        pipeline = istrue \
                   if (message.epoch < reference.epoch + margin) or \
                      (message.epoch > reference.epoch - margin) \
                   else isfalse
                
        logging.info("Routine.Epoch:  Around")