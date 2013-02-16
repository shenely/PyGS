#!/usr/bin/env python2.7

"""Acknowledge routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   15 February 2013

Provides routines for acknowledging commands.

Functions:
accept -- Accept command
reject -- Reject command
format -- Format acknowledge message
parse  -- Parse acknowledge message

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-02-06    shenely         1.0         Promoted to version 1.0
2013-02-15                    1.1         Bad format log messages

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
from core.message import ResponseMessage
from . import BaseAcknowledge,AcceptAcknowledge,RejectAcknowledge
from ground.command import BaseCommand
#
##################


##################
# Export section #
#
__all__ = ["accept",
           "reject",
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
def accept(pipeline=None):
    """Story:  Accept command
    
    IN ORDER TO tell a ground segment that command will be executed
    AS A space segment
    I WANT TO acknowledge that the command was accepted
        
    """
    
    """Specification:  Accept command
    
    GIVEN a downstream pipeline (default null)
        
    Scenario 1:  Upstream command received
    WHEN a command is received from upstream
    THEN an acceptance acknowledge SHALL be generated
        AND the acknowledge SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    acknowledge = None
        
    logging.debug("Acknowledge.Reject:  Starting")
    while True:
        try:
            command = yield acknowledge,pipeline
        except GeneratorExit:
            logging.warn("Acknowledge.Reject:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            #input validation
            assert isinstance(command,BaseCommand)
            
            acknowledge = AcceptAcknowledge(command.epoch,_id=command._id)
                            
            logging.info("Acknowledge.Accept")

@coroutine
def reject(pipeline=None):
    """Story:  Reject command
    
    IN ORDER TO tell a ground segment that command will not be executed
    AS A space segment
    I WANT TO acknowledge that the command was rejected
        
    """
    
    """Specification:  Reject command
    
    GIVEN a downstream pipeline (default null)
        
    Scenario 1:  Upstream command received
    WHEN a command is received from upstream
    THEN an rejection acknowledge SHALL be generated
        AND the acknowledge SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    acknowledge = None
        
    logging.debug("Acknowledge.Reject:  Starting")
    while True:
        try:
            command = yield acknowledge,pipeline
        except GeneratorExit:
            logging.warn("Acknowledge.Reject:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            #input validation
            assert isinstance(command,BaseCommand)
            
            acknowledge = RejectAcknowledge(command.epoch,_id=command._id)
                            
            logging.info("Acknowledge.Reject")

@coroutine
def format(address,pipeline=None):
    """Story:  Format acknowledge message
    
    IN ORDER TO generate messages for acknowledging a ground segment
    AS A ground segment
    I WANT TO encode an acknowledge in a defined string format
        
    """
    
    """Specification:  Format acknowledge message
    
    GIVEN an address for the message envelope
        AND a downstream pipeline (default null)
        
    Scenario 1:  Upstream acknowledge received
    WHEN a acknowledge is received from upstream
    THEN the acknowledge SHALL be encoded as a message
        AND the message SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(address,types.StringTypes)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    message = None
        
    logging.debug("Acknowledge.Format:  Starting")
    while True:
        try:
            acknowledge = yield message,pipeline
        except GeneratorExit:
            logging.warn("Acknowledge.Format:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            #input validation
            assert isinstance(acknowledge,BaseAcknowledge)
            
            notice = ResponseMessage(acknowledge)
            message = address,encoder(notice)
                            
            logging.info("Acknowledge.Format:  Formatted")

@coroutine
def parse(pipeline=None):
    """Story:  Parse acknowledge message
    
    IN ORDER TO process messages for acknowledges from a space segment
    AS A ground segment
    I WANT TO decode the a formatted string as an acknowledge
        
    """
    
    """Specification:  Parse acknowledge message
    
    GIVEN a downstream pipeline (default null)
        
    Scenario 1:  Upstream message received
    WHEN a message is received from upstream
    THEN the message SHALL be decoded as an acknowledge
        AND the acknowledge SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    acknowledge = None
        
    logging.debug("Acknowledge.Parse:  Starting")
    while True:
        try:
            address,message = yield acknowledge,pipeline
        except GeneratorExit:
            logging.warn("Acknowledge.Parse:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            #input validation
            assert isinstance(message,types.StringTypes)
    
            notice = ResponseMessage(**decoder(message))
            
            #output validation
            assert notice.error == 0
            acknowledge = BaseAcknowledge.registry[notice.result.type](notice.result)
                    
            logging.info("Acknowledge.Parse:  Parsed")
