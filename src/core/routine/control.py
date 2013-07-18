#!/usr/bin/env python2.7

"""Control routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   16 July 2013

Provides routines for controlling the flow of data.

Classes:
SplitControl -- Split pipeline
MergeControl -- Merge pipeline
AllowControl -- Allow message
BlockControl -- Block message

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-05-02    shenely         1.0         Initial revision
2013-06-26    shenely         1.1         Modifying routine structure
2013-06-29    shenely                     Refactored for agenda
2013-07-17    shenely                     Corrected merge log message


"""

##################
# Import section #
#
#Built-in libraries
import logging
import types

#External libraries

#Internal libraries
from . import *
from ..agenda import *
#
##################


##################
# Export section #
#
__all__ = ["SplitControl",
           "MergeControl",
           "AllowControl",
           "BlockControl"]
#
##################


####################
# Constant section #
#
__version__ = "1.1"#current version [major.minor]
#
####################


class SplitControl(SourceRoutine,TargetRoutine):
    """Story:  Split pipeline
    
    IN ORDER TO distribute messages to multiple downstream sinks
    AS A generic segment
    I WANT TO execute multiple tasks in parallel
    
    """
    
    """Specification:  Split pipeline
    
    GIVEN an upstream pipeline
        AND a list of downstream pipelines (default null)
        
    Scenario 1:  Upstream message received
    WHEN a message is received from the upstream source
    THEN the message SHALL be sent to all listed downstream sinks
    
    """
    
    name = "Control.Split"
    
    def __init__(self,processor):
        assert isinstance(processor,Processor)
        
        TargetRoutine.__init__(self)
        self.target = list()
        
        self.scheduler = processor
    
    def _process(self,message,ipipe):        
        for opipe in self.target:
            self.scheduler.schedule(message,ipipe,opipe)
        else:
            logging.info("{0}:  {1:d}-way split".\
                         format(self.name,len(self.target)))
        
            message = None
            opipe = None
        
        return message,opipe
    
    def set_target(self,target):
        assert isinstance(target,BaseRoutine)
        
        if len(self.target) is None:
            logging.info("{0}:  Single target defined".\
                         format(self.name))
        else:
            logging.info("{0}:  Multiple targets defined".\
                          format(self.name))
        
        self.target.append(target)

class MergeControl(SourceRoutine,TargetRoutine):
    """Story:  Split pipeline
    
    IN ORDER TO aggregate messages from multiple upstream sources
    AS A generic segment
    I WANT TO synchronize tasks that were executing in parallel
    
    """
    
    """Specification:  Merge pipeline
    
    GIVEN a list of upstream pipelines
        AND a downstream pipeline (default null)
        
    Scenario 1:  Upstream message received
    WHEN an message is received from an upstream source
        AND the message count is less than the upstream source number
    THEN the message SHALL be stored internally
        AND the message count SHALL be incremented by one (1)
        
    Scenario 2:  Upstream message received from all sources
    WHEN a message is received from an upstream source
        AND the message count is equal the upstream source number
    THEN the stored messages SHALL be sent to the downstream sink
        AND the message count SHALL be reset to zero (0)
    
    """
    
    name = "Control.Merge"
    
    def __init__(self):
        SourceRoutine.__init__(self)
        self.message = dict()
    
    def _process(self,message,ipipe):
        if ipipe in self.source:
            if ipipe in self.message:
                logging.warn("{0}:  Duplicate source".\
                             format(self.name))

            self.message[ipipe] = message
        else:
            logging.error("{0}:  Undefined source".\
                          format(self.name))
            
        if len(self.message) == len(self.source):
            logging.info("{0}:  {1:d}-way merge".\
                         format(self.name,len(self.source)))
            
            message = self.message.values()
            opipe = self.target
            
            self.message.clear()
        else:
            message = None
            opipe = None
        
        return message,opipe
    
    def set_source(self,source):
        assert isinstance(source,BaseRoutine)
        
        if len(self.source) == 0:
            logging.info("{0}:  Single source defined".\
                         format(self.name))
        else:
            logging.info("{0}:  Multiple sources defined".\
                         format(self.name))
        
        self.source.append(source)

class AllowControl(ConditionRoutine):
    """Story:  Allow message
    
    IN ORDER TO couple an upstream source from a downstream sink
    AS A generic segment
    I WANT TO allow messages to flow downstream
    
    """
    
    """Specification:  Allow message
    
    GIVEN a downstream pipeline (default null)
        
    Scenario 1:  Upstream message received
    WHEN a message is received from upstream
    THEN the message SHALL be sent downstream
    
    """
    
    name = "Control.Allow"
    
    def _satisfy(self,message):
        logging.info("{0}:  Message allowed".\
                     format(self.name))
        
        return True

class BlockControl(ConditionRoutine):
    """Story:  Block message
    
    IN ORDER TO decouple an upstream source from a downstream sink
    AS A generic segment
    I WANT TO prevent messages from flowing downstream
    
    """
    
    """Specification:  Block message
    
    GIVEN a downstream pipeline (default null)
        
    Scenario 1:  Upstream message received
    WHEN a message is received from upstream
    THEN a blank message SHALL be sent downstream
    
    """
    
    name = "Control.Block"
    
    def _satisfy(self,message):
        logging.info("{0}:  Message blocked".\
                     format(self.name))
        
        return False
