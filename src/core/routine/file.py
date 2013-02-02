#!/usr/bin/env python2.7

"""File routines

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
__all__ = ["read",
           "write"]
#
##################


####################
# Constant section #
#
__version__ = "0.1"#current version [major.minor]
#
####################


@coroutine
def read(descriptor,pipeline=None):
    """Read Message from File"""
    
    assert isinstance(descriptor,types.FileType)
    assert "r" in descriptor.mode
    assert isinstance(pipeline,types.GeneratorType)
    
    for message in descriptor:
        yield message,pipeline
        
        logging.info("Routine.File:  Read from %s" % descriptor.name)

@coroutine
def write(descriptor,pipeline=None):
    """Write Message to File"""
    
    assert isinstance(descriptor,types.FileType)
    assert "w" in descriptor.mode
    assert isinstance(pipeline,types.GeneratorType)
    
    message = None
    while True:
        message = yield message,pipeline
        
        assert isinstance(message,types.StringTypes)
        
        descriptor.write(message)
        descriptor.flush()
        
        logging.info("Routine.File:  Wrote to %s" % descriptor.name)
