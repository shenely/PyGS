#!/usr/bin/env python2.7

"""Acknowledge Routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   27 January 2013

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
from . import coroutine
from ..core import *
from ..core.acknowledge import *
from ..core.result import BaseResult
from ..core.message import AcknowledgeMessage
#
##################


##################
# Export section #
#
__all__ = ["format",
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
def format(address,pipeline=None):
    """Format Acknowledge Message"""
    
    assert isinstance(address,types.StringTypes)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    message = None
    while True:
        acknowledge = yield message,pipeline
        
        assert isinstance(acknowledge,BaseAcknowledge)
        
        notice = AcknowledgeMessage(acknowledge)
        message = address,encoder(notice)
                        
        logging.info("Routine.Acknowledge:  Formatted")

@coroutine
def parse(pipeline=None):
    """Parse Acknowledge Message"""
    
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    command = None
    while True:
        address,message = yield command,pipeline
        
        assert isinstance(message,types.StringTypes)
        
        notice = decoder(message)
        
        assert hasattr(notice,"id")
        assert hasattr(notice,"result")
        assert hasattr(notice,"error")
        assert notice.error is None
        
        command = BaseAcknowledge.registry[notice.result.message](notice.result.epoch,notice.result.id)
                
        logging.info("Routine.Acknowledge:  Parsed")