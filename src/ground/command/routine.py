#!/usr/bin/env python2.7

"""Command Routines

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
from clock.epoch import EpochState
from . import BaseCommand
from space.acknowledge import *
from space.result import BaseResult
from .message import CommandMessage
#
##################


##################
# Export section #
#
__all__ = ["accept",
           "reject",
           "execute",
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
def accept(pipeline=None):
    """Accept Command"""
    
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    acknowledge = None
    while True:
        command = yield acknowledge,pipeline
        
        assert isinstance(command,BaseCommand)
        
        acknowledge = AcceptAcknowledge(command.epoch,_id=command._id)
                        
        logging.info("Command.Accept")

@coroutine
def reject(pipeline=None):
    """Reject Command"""
    
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    acknowledge = None
    while True:
        command = yield acknowledge,pipeline
        
        assert isinstance(command,BaseCommand)
        
        acknowledge = RejectAcknowledge(command.epoch,_id=command._id)
                        
        logging.info("Command.Reject")

@coroutine
def execute(system,pipeline=None):
    """Execute System Command"""
    
    assert isinstance(system,EpochState)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    result = None
    while True:
        command = yield result,pipeline
        
        assert isinstance(command,BaseCommand)
        
        result = command.execute(system)
        
        assert isinstance(result,BaseResult)
                        
        logging.info("Command.Executed:  Performed %s at %s" % (command.type,system.epoch))

@coroutine
def format(address,pipeline=None):
    """Format Command Message"""
    
    assert isinstance(address,types.StringTypes)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    message = None
    while True:
        command = yield message,pipeline
        
        assert isinstance(command,BaseCommand)
        
        notice = CommandMessage(command)
        message = address,encoder(notice)
                        
        logging.info("Command.Formatted")

@coroutine
def parse(pipeline=None):
    """Parse Command Message"""
    
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    command = None
    while True:
        address,message = yield command,pipeline
        
        assert isinstance(message,types.StringTypes)
                
        notice = CommandMessage.build(decoder(message))
        command = notice.params
                
        logging.info("Command.Parsed")