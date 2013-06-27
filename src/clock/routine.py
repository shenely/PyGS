#!/usr/bin/env python2.7

"""Clock routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   26 June 2013

Provides routines for driving the simulation clock.

Classes:
ContinuousClock -- Continuous clock routine
DiscreteClock   -- Discrete clock routine
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-05-02    shenely         1.0         Initial revision
2013-06-26    shenely         1.1         Modifying routine structure

"""


##################
# Import section #
#
#Built-in libraries
from datetime import datetime,timedelta
import logging
import types

#External libraries
from bson.tz_util import utc

#Internal libraries
from core.routine import SourceRoutine
from epoch import EpochState
#
##################


##################
# Export section #
#
__all__ = ["ContinuousClock",
           "DiscreteClock"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]

J2000 = datetime(2000,1,1,12,tzinfo=utc)#Julian epoch (2000-01-01T12:00:00Z)

CLOCK_SCALE = 1.0#Clock rate scale (default 1:1, i.e. real-time)
CLOCK_STEP = timedelta(seconds=60)#Clock step (default to 60 seconds)
#
####################


class ContinuousClock(SourceRoutine):
    """Story:  Continuous clock
    
    IN ORDER TO manage the simulation time
    AS A clock segment
    I WANT TO progress the simulation time based off the progress of
        system time
    
    """
    
    """Specification:  Continuous clock
    
    GIVEN an initial epoch (default J2000.0)
        AND a clock rate scale (default 1.0)
        AND a downstream pipeline (default null)
        
    Scenario 1:  Simulation time requested
    WHEN the clock value is requested from upstream
    THEN the system time since the last request SHALL be determined
        AND the elapsed time SHALL be scaled by the clock rate scale
        AND the simulation time SHALL be increased by the elapsed time
        AND the simulation time SHALL be sent downstream
    
    Scenario 2:  Clock rate scale modified
    WHEN a clock rate scale is sent from upstream
        AND the clock scale rate is a numeric value
    THEN the clock scale rate SHALL be modified to the upstream value
        AND the simulation time SHALL be requested
    
    """
    
    name = "Clock.Continuous"
    
    def __init__(self,epoch=J2000,scale=CLOCK_SCALE):
        assert isinstance(epoch,datetime)
        assert isinstance(scale,(types.IntType,types.FloatType))
        
        SourceRoutine.__init__(self)
        
        self.epoch = epoch
        self.scale = scale
        
        self.now = datetime.utcnow()
    
    def _receive(self):
        logging.info("{0}:  Ticking from {1}".\
                     format(self.name,self.epoch))
        
        self.past = self.now
        self.now = datetime.utcnow()
            
        self.epoch += self.scale * (self.now - self.past)#increase simulation time
        
        logging.info("{0}:  Ticked to {1}".\
                     format(self.name,self.epoch))
        
        return EpochState(self.epoch)

class DiscreteClock(SourceRoutine):
    """Story:  Discrete clock
    
    IN ORDER TO manage the simulation time
    AS A clock segment
    I WANT TO progress the simulation time at fixed intervals
    
    """
    
    """Specification:  Discrete clock
    
    GIVEN an initial epoch (default J2000.0)
        AND a clock step (default 60 seconds)
        AND a downstream pipeline (default null)
        
    Scenario 1:  Simulation time requested
    WHEN the clock value is requested from upstream
    THEN the simulation time SHALL be increased by the clock step size
        AND the simulation time SHALL be sent downstream
    
    Scenario 2:  Clock step size modified
    WHEN a clock step size sent from upstream
        AND the clock step size represents a change in time
    THEN the clock step size SHALL be modified to the upstream value
        AND the simulation time SHALL be requested
    
    """
    
    def __init__(self,epoch=J2000,step=CLOCK_STEP):
        assert isinstance(epoch,datetime)
        assert isinstance(step,timedelta)
        
        SourceRoutine.__init__(self)
        
        self.epoch = epoch
        self.step = step
        
    def _receive(self):
        logging.info("{0}:  Ticking from {1}".\
                     format(self.name,self.epoch))
        
        self.epoch += self.step#increase simulation time
        
        logging.info("{0}:  Ticked to {1}".\
                     format(self.name,self.epoch))
        
        return EpochState(self.epoch)
