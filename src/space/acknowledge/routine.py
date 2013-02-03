#!/usr/bin/env python2.7

"""Acknowledge routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   03 February 2013

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
from core import ObjectDict,coroutine,encoder,decoder
from . import BaseAcknowledge
from ..result import BaseResult
from .message import AcknowledgeMessage
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
                        
        logging.info("Acknowledge.Formatted")

@coroutine
def parse(pipeline=None):
    """Parse Acknowledge Message"""
    
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    command = None
    while True:
        address,message = yield command,pipeline
        
        assert isinstance(message,types.StringTypes)

        notice = AcknowledgeMessage.build(decoder(message))
        acknowledge = notice.params
                
        logging.info("Acknowledge.Parsed")