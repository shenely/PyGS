#!/usr/bin/env python2.7

"""File routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   05 February 2013

Provides routines for accessing the file system.

Functions:
read  -- Read file
write -- Write file

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
__version__ = "1.0"#current version [major.minor]
#
####################


@coroutine
def read(filename,pipeline=None):
    """Story:  Read file
    
    IN ORDER TO process text files
    AS A generic segment
    I WANT TO read files from the file system
    
    """
    
    """Specification:  Read files
    
    GIVEN a valid filename
        AND a downstream pipeline (default null)
        
    Scenario 1:  File line requested
    WHEN a file line is requested from upstream
    THEN next line in the file SHALL be read
        AND the next line SHALL be sent downstream
        
    Scenario 2:  End of file reached
    WHEN a file line is requested from upstream
        AND the end of file has been reached
    THEN the downstream pipeline SHALL be closed
        AND the file read routine SHALL be closed
    
    """
    
    #configuration validation
    assert isinstance(filename,types.StringTypes)
    assert isinstance(pipeline,types.GeneratorType)
    
    with open(filename,"r") as descriptor:
        logging.debug("File.Read:  Starting")
        for message in descriptor:
            try:
                yield message,pipeline
            except GeneratorExit:
                logging.warn("File.Read:  Stopping")
                
                #close downstream routine (if it exists)
                pipeline.close() if pipeline is not None else None
                
                return
            else:
                logging.info("File.Read:  Read from %s" % descriptor.name)
        else:
            logging.warn("File.Read:  End of file %s" % descriptor.name)
                
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return

@coroutine
def write(filename,pipeline=None):
    """Story:  Write file
    
    IN ORDER TO generate text files
    AS A generic segment
    I WANT TO write files to the file system
    
    """
    
    """Specification:  Write files
    
    GIVEN a valid filename
        AND a downstream pipeline (default null)
        
    Scenario 1:  Upstream message received
    WHEN a message is received from upstream
    THEN the message SHALL be written to the file
        AND the message SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(filename,types.StringTypes)
    assert isinstance(pipeline,types.GeneratorType)
    
    with open(filename,"w") as descriptor:
        message = None
        
        logging.debug("File.Write:  Starting")
        while True:
            try:
                message = yield message,pipeline
            except GeneratorExit:
                logging.warn("File.Write:  Stopping")
                            
                #close downstream routine (if it exists)
                pipeline.close() if pipeline is not None else None
                
                return
            else:
                #input validation
                assert isinstance(message,types.StringTypes)
                
                descriptor.write(message)
                
                logging.info("File.Write:  Wrote to %s" % descriptor.name)
