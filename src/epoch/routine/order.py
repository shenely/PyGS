#!/usr/bin/env python2.7

"""Order routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   29 June 2013

Provides routines for order tasks.

Classes:
BeforeEpoch -- Before reference
AfterEpoch  -- After reference

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-05-14    shenely         1.0         Initial revision
2013-06-26    shenely         1.1         Modifying routine structure
2013-06-29    shenely         1.2         Adding methods

"""


##################
# Import section #
#
#Built-in libraries
from datetime import timedelta
import logging
import types

#External libraries

#Internal libraries
from core.routine import ConditionRoutine
from . import EpochState
#
##################


##################
# Export section #
#
__all__ = ["BeforeEpoch",
           "AfterEpoch"]
#
##################


####################
# Constant section #
#
__version__ = "1.2"#current version [major.minor]
#
####################


class BeforeEpoch(ConditionRoutine):
    """Story:  Before reference
    
    IN ORDER TO execute tasks at specific time frames
    AS A generic segment
    I WANT TO only process messages before a reference time
    
    """
    
    """Specification:  Before reference
    
    GIVEN a reference with epoch defined
        AND a time margin
        AND a true downstream pipeline (default null)
        AND a false downstream pipeline (default null)
        
    Scenario 1:  Upstream message received before reference
    WHEN a message is received from upstream
        AND the message defines an epoch
        AND the message epoch is before the reference epoch by a margin
    THEN the message SHALL be sent to the true upstream
        
    Scenario 2:  Upstream message received after reference
    WHEN a message is received from upstream
        AND the message defines an epoch
        AND the message epoch is after the reference epoch by a margin
    THEN the message SHALL be sent to the false upstream
    
    """
    
    name = "Epoch.Before"
    
    def __init__(self,reference,margin):
        assert isinstance(reference,EpochState)#TODO:  Define EpochState (also, rename)
        assert isinstance(margin,timedelta)
        
        ConditionRoutine.__init__(self)
        
        self.reference = reference
        self.margin = margin
    
    def _satisfy(self,message):
        return message.epoch < (self.reference.epoch - self.margin)
    
    def set_reference(self,reference):
        assert isinstance(reference,EpochState)
        
        self.reference = reference
        
        return reference
        

class AfterEpoch(ConditionRoutine):
    """Story:  After reference
    
    IN ORDER TO execute tasks at specific time frames
    AS A generic segment
    I WANT TO only process messages after a reference time
    
    """
    
    """Specification:  After reference
    
    GIVEN a reference with epoch defined
        AND a time margin
        AND a true downstream pipeline (default null)
        AND a false downstream pipeline (default null)
        
    Scenario 1:  Upstream message received before reference
    WHEN a message is received from upstream
        AND the message defines an epoch
        AND the message epoch is before the reference epoch by a margin
    THEN the message SHALL be sent to the false upstream
        
    Scenario 2:  Upstream message received after reference
    WHEN a message is received from upstream
        AND the message defines an epoch
        AND the message epoch is after the reference epoch by a margin
    THEN the message SHALL be sent to the true upstream
    
    """
    
    name = "Epoch.After"
    
    def __init__(self,reference,margin):
        assert isinstance(reference,EpochState)
        assert isinstance(margin,timedelta)
        
        ConditionRoutine.__init__(self)
        
        self.reference = reference
        self.margin = margin
    
    def _satisfy(self,message):
        return message.epoch > (self.reference.epoch + self.margin)
    
    def set_reference(self,reference):
        assert isinstance(reference,EpochState)
        
        self.reference = reference
        
        return reference