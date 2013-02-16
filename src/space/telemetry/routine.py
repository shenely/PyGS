#!/usr/bin/env python2.7

"""Telemetry routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   15 February 2013

Provides routines for asset telemetry.

Functions:
format -- Format telemetry message
parse  -- Parse telemetry message

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-02-06    shenely         1.0         Promoted to version 1.0
2013-02-15                    1.1         Using telemetry, not result

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
from . import BaseTelemetry
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
__version__ = "1.1"#current version [major.minor]
#
####################

@coroutine
def format(address,pipeline=None):
    """Story:  Format telemetry message
    
    IN ORDER TO generating messages to results for a ground segment
    AS A space segment
    I WANT TO encode a telemetry in a defined string format
        
    """
    
    """Specification:  Format telemetry message
    
    GIVEN an address for the message envelope
        AND a downstream pipeline (default null)
        
    Scenario 1:  Upstream result received
    WHEN a telemetry is received from upstream
    THEN the telemetry SHALL be encoded as a message
        AND the message SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(address,types.StringTypes)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    message = None
        
    logging.debug("Telemetry.Format:  Starting")
    while True:
        try:
            telemetry = yield message,pipeline
        except GeneratorExit:
            logging.warn("Telemetry.Format:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            #input validation
            assert isinstance(telemetry,BaseTelemetry)
            
            notice = ResponseMessage(telemetry)
            message = address,encoder(notice)
                            
            logging.info("Telemetry.Format:  Formatted")

@coroutine
def parse(pipeline=None):
    """Story:  Parse telemetry message
    
    IN ORDER TO process messages for results from a space segment
    AS A ground segment
    I WANT TO decode the a formatted string as an telemetry
        
    """
    
    """Specification:  Parse telemetry message
    
    GIVEN a downstream pipeline (default null)
        
    Scenario 1:  Upstream message received
    WHEN a message is received from upstream
    THEN the message SHALL be decoded as an telemetry
        AND the telemetry SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    telemetry = None
        
    logging.debug("Telemetry.Parse:  Starting")
    while True:
        try:
            address,message = yield telemetry,pipeline
        except GeneratorExit:
            logging.warn("Telemetry.Parse:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            #input validation
            assert isinstance(message,types.StringTypes)
    
            notice = ResponseMessage(**decoder(message))
            
            #output validation
            assert notice.error == 0
            telemetry = BaseTelemetry(**notice.result)
                    
            logging.info("Telemetry.Parse:  Parsed")
