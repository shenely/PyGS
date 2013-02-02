#!/usr/bin/env python2.7

"""Control routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   02 February 2013

Purpose:    
"""


##################
# Import section #
#
#Built-in libraries
import logging
import types

#External libraries

#Internal libraries
from .. import coroutine
#
##################


##################
# Export section #
#
__all__ = ["split",
           "merge",
           "block"]
#
##################


####################
# Constant section #
#
__version__ = "0.1"#current version [major.minor]
#
####################


@coroutine
def split(ipipe,opipes=None):
    """Split Pipeline"""
    
    assert isinstance(ipipe,types.GeneratorType) or ipipe is None
    assert isinstance(opipes,types.ListType)
    assert filter(lambda opipe:isinstance(opipe,types.GeneratorType),opipes) or len(opipes) == 0
    
    message = None
    while True:
        message = yield message,opipes
        
        logging.info("Routine.Control:  %d-way split" % len(opipes))

@coroutine
def merge(ipipes,opipe=None):
    """Merge Pipeline"""
    
    assert isinstance(ipipes,types.ListType)
    assert filter(lambda ipipe:isinstance(ipipe,types.GeneratorType),ipipes) or len(ipipes) == 0
    assert isinstance(opipe,types.GeneratorType) or opipe is None
    
    count = 1
    messages = []
    while True:        
        if count < len(ipipes):
            message,pipeline = None,None
            
            count += 1
        else:
            message,pipeline = messages,opipe
            
            count = 1
            messages = []
        
            logging.info("Routine.Control:  %d-way merge" % len(ipipes))
        
        message = yield message,pipeline
        messages.append(message)

@coroutine
def block(pipeline=None):
    """Block Message"""
    
    assert isinstance(pipeline,types.GeneratorType)
    
    while True:
        yield None,pipeline
        
        logging.info("Routine.Control:  Message blocked")
