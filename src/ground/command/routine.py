#!/usr/bin/env python2.7

"""Command routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   05 February 2013

Provides routines for command execution.

Functions:
execute -- Execute command
format  -- Format command message
parse   -- Parse command message

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-02-05    shenely         1.0         Promoted to version 1.0

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
from clock.epoch import EpochState
from . import BaseCommand
from space.result import BaseResult
from .message import CommandMessage
#
##################


##################
# Export section #
#
__all__ = ["execute",
           "format",
           "parse"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]
#
####################


@coroutine
def execute(system,pipeline=None):
    """Story:  Execute command
    
    IN ORDER TO maintain a constraint set by a ground segment
    AS A space segment
    I WANT TO modify the current system state based off a command
        
    """
    
    """Specification:  Execute command
    
    GIVEN a system with epoch defined
        AND a downstream pipeline (default null)
        
    Scenario 1:  Upstream command received
    WHEN a command is received from upstream
    THEN the command SHALL be execute on the system state
        AND the result SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(system,EpochState)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    result = None
        
    logging.debug("Command.Execute:  Starting")
    while True:
        try:
            command = yield result,pipeline
        except GeneratorExit:
            logging.warn("Command.Execute:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            #input validation
            assert isinstance(command,BaseCommand)
            
            result = command.execute(system)
            
            #output validation
            assert isinstance(result,BaseResult)
                            
            logging.info("Command.Execute:  Performed %s at %s" % (command.type,system.epoch))

@coroutine
def format(address,pipeline=None):
    """Story:  Format command message
    
    IN ORDER TO generate messages for commanding a space segment
    AS A ground segment
    I WANT TO encode a command in a defined string format
        
    """
    
    """Specification:  Format command message
    
    GIVEN an address for the message envelope
        AND a downstream pipeline (default null)
        
    Scenario 1:  Upstream command received
    WHEN a command is received from upstream
    THEN the command SHALL be encoded as a message
        AND the message SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(address,types.StringTypes)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    message = None
        
    logging.debug("Command.Format:  Starting")
    while True:
        try:
            command = yield message,pipeline
        except GeneratorExit:
            logging.warn("Command.Format:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            #input validation
            assert isinstance(command,BaseCommand)
            
            notice = CommandMessage(command)
            message = address,encoder(notice)
                            
            logging.info("Command.Format:  Formatted")

@coroutine
def parse(pipeline=None):
    """Parse command message
    
    IN ORDER TO process messages for commanding from a ground segment
    AS A space segment
    I WANT TO decode the a formatted string as a command
        
    """
    
    """Specification:  Parse command message
    
    GIVEN a downstream pipeline (default null)
        
    Scenario 1:  Upstream message received
    WHEN a message is received from upstream
    THEN the message SHALL be decoded as an command
        AND the command SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    command = None
        
    logging.debug("Command.Parse:  Starting")
    while True:
        try:
            address,message = yield command,pipeline
        except GeneratorExit:
            logging.warn("Command.Parse:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            #input validation
            assert isinstance(message,types.StringTypes)
                    
            notice = CommandMessage.build(decoder(message))
            command = notice.params
                    
            logging.info("Command.Parse:  Parsed")