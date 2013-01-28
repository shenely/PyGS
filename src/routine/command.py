#!/usr/bin/env python2.7

"""Command Routines

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
from ..core.state import BaseState
from ..core.command import BaseCommand
from ..core.acknowledge import *
from ..core.result import BaseResult
from ..core.message import CommandMessage
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
        
        acknowledge = AcceptAcknowledge(command.epoch,command.id)
                        
        logging.info("Routine.Command:  Accepted at %s" % command.epoch)

@coroutine
def reject(pipeline=None):
    """Reject Command"""
    
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    acknowledge = None
    while True:
        command = yield acknowledge,pipeline
        
        assert isinstance(command,BaseCommand)
        
        acknowledge = RejectAcknowledge(command.epoch,command.id)
                        
        logging.info("Routine.Command:  Rejected at %s" % command.epoch)

@coroutine
def execute(system,pipeline=None):
    """Execute System Command"""
    
    assert isinstance(system,BaseState)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    result = None
    while True:
        command = yield result,pipeline
        
        assert isinstance(command,BaseCommand)
        
        result = command.execute(system)
        
        assert isinstance(result,BaseResult)
                        
        logging.info("Routine.Command:  Executed at %s" % system.epoch)

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
                        
        logging.info("Routine.Command:  Formatted")

@coroutine
def parse(pipeline=None):
    """Parse Command Message"""
    
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    command = None
    while True:
        address,message = yield command,pipeline
        
        assert isinstance(message,types.StringTypes)
        
        notice = decoder(message)
        
        assert hasattr(notice,"id")
        assert hasattr(notice,"method")
        assert hasattr(notice,"params")
        assert isinstance(notice.params,ObjectDict)
        assert hasattr(notice.params,"epoch")
        assert isinstance(notice.params.epoch,datetime)
        
        command = BaseCommand.registry[notice.params.type](notice.params.epoch,
                                                           notice.params.R,
                                                           notice.params.T,
                                                           notice.params.N,
                                                           notice.params.id)
                
        logging.info("Routine.Command:  Parsed as %s" % notice.params.epoch)