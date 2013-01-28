#!/usr/bin/env python2.7

"""Result Routines

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
from ..core.result import BaseResult
from ..core.message import ResultMessage
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
    """Format Result Message"""
    
    assert isinstance(address,types.StringTypes)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    message = None
    while True:
        result = yield message,pipeline
        
        assert isinstance(result,BaseResult)
        
        notice = ResultMessage(result)
        message = address,encoder(notice)
                        
        logging.info("Routine.Result:  Formatted")

@coroutine
def parse(pipeline=None):
    """Parse Result Message"""
    
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    result = None
    while True:
        address,message = yield result,pipeline
        
        assert isinstance(message,types.StringTypes)
        
        notice = decoder(message)
        
        assert hasattr(notice,"id")
        assert hasattr(notice,"result")
        assert hasattr(notice,"error")
        assert notice.error is None
        
        result = BaseResult(notice.id,**notice.result)
                
        logging.info("Routine.Result:  Parsed")