#!/usr/bin/env python2.7

"""Result routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   06 February 2013

Provides routines for command results.

Functions:
format -- Format result message
parse  -- Parse result message

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-02-06    shenely         1.0         Promoted to version 1.0

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
from . import BaseResult
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
__version__ = "1.0"#current version [major.minor]
#
####################

@coroutine
def format(address,pipeline=None):
    """Story:  Format result message
    
    IN ORDER TO generating messages to results for a ground segment
    AS A space segment
    I WANT TO encode a result in a defined string format
        
    """
    
    """Specification:  Format result message
    
    GIVEN an address for the message envelope
        AND a downstream pipeline (default null)
        
    Scenario 1:  Upstream result received
    WHEN a result is received from upstream
    THEN the result SHALL be encoded as a message
        AND the message SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(address,types.StringTypes)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    message = None
        
    logging.debug("Result.Format:  Starting")
    while True:
        try:
            result = yield message,pipeline
        except GeneratorExit:
            logging.warn("Result.Format:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            #input validation
            assert isinstance(result,BaseResult)
            
            notice = ResponseMessage(result)
            message = address,encoder(notice)
                            
            logging.info("Result.Format:  Formatted")

@coroutine
def parse(pipeline=None):
    """Story:  Parse result message
    
    IN ORDER TO process messages for results from a space segment
    AS A ground segment
    I WANT TO decode the a formatted string as an result
        
    """
    
    """Specification:  Parse result message
    
    GIVEN a downstream pipeline (default null)
        
    Scenario 1:  Upstream message received
    WHEN a message is received from upstream
    THEN the message SHALL be decoded as an result
        AND the result SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    result = None
        
    logging.debug("Result.Parse:  Starting")
    while True:
        try:
            address,message = yield result,pipeline
        except GeneratorExit:
            logging.warn("Result.Parse:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            #input validation
            assert isinstance(message,types.StringTypes)
    
            notice = ResponseMessage(**decoder(message))
            
            #output validation
            assert notice.error == 0
            result = BaseResult(**notice.result)
                    
            logging.info("Result.Parse:  Parsed")
