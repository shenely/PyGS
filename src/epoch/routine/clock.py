#!/usr/bin/env python2.7

"""Clock routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   09 September 2013

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
2013-06-27    shenely         1.2         Properties for scheduler
2013-07-25    shenely                     Adjusted timeout
2013-07-28    shenely                     Upped the timeout (againt)
2013-09-09    shenely         1.3         Adding persistance logic

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
from core import agenda
from core import persist
from .. import EpochState
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
__version__ = "1.3"#current version [major.minor]

J2000 = datetime(2000,1,1,12,tzinfo=utc)#Julian epoch (2000-01-01T12:00:00Z)

CLOCK_SCALE = 1.0#Clock rate scale (default 1:1, i.e. real-time)
CLOCK_STEP = timedelta(seconds=60)#Clock step (default to 60 seconds)

TIMEOUT = 100#time between running
#
####################


continuous_clock = persist.ObjectPersistance()

@continuous_clock.type(persist.SOURCE_OBJECT)
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
    type = agenda.PERIODIC
    timeout = TIMEOUT
    
    def __init__(self,scale=CLOCK_SCALE):
        SourceRoutine.__init__(self)
        
        self.now = datetime.utcnow()
        
    @continuous_clock.property
    def epoch(self):
        return self._epoch
    
    @epoch.setter
    def epoch(self,epoch):
        assert isinstance(epoch,datetime)
        
        self._epoch = epoch
        
    @continuous_clock.property
    def scale(self):
        return self._scale
    
    @scale.setter
    def scale(self,scale):
        assert isinstance(scale,(types.IntType,types.FloatType))
        
        self._scale = scale
    
    def _receive(self):
        logging.info("{0}:  Ticking from {1}".\
                     format(self.name,self._epoch))
        
        self.past = self.now
        self.now = datetime.utcnow()
            
        self._epoch += self._scale * (self.now - self.past)#increase simulation time
        
        logging.info("{0}:  Ticked to {1}".\
                     format(self.name,self._epoch))
        
        return EpochState(self._epoch)

discrete_clock = persist.ObjectPersistance()

@discrete_clock.type(persist.SOURCE_OBJECT)
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
    
    name = "Clock.Discrete"
    type = agenda.PERIODIC
    timeout = TIMEOUT
        
    @discrete_clock.property
    def epoch(self):
        return self._epoch
    
    @epoch.setter
    def epoch(self,epoch):
        assert isinstance(epoch,datetime)
        
        self._epoch = epoch
        
    @discrete_clock.property
    def step(self):
        return self._scale
    
    @step.setter
    def step(self,step):
        assert isinstance(step,timedelta)
        
        self._step = step
        
    def _receive(self):
        logging.info("{0}:  Ticking from {1}".\
                     format(self.name,self._epoch))
        
        self._epoch += self._step#increase simulation time
        
        logging.info("{0}:  Ticked to {1}".\
                     format(self.name,self._epoch))
        
        return EpochState(self._epoch)
