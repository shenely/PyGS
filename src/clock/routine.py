#!/usr/bin/env python2.7

"""Clock routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   05 February 2013

Provides routines for driving the simulation clock.

Functions:
continuous -- Continuous clock routine
discrete   -- Discrete clock routine
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
from datetime import datetime,timedelta
import logging
import types

#External libraries

#Internal libraries
from core import coroutine
#
##################


##################
# Export section #
#
__all__ = ["continuous",
           "discrete"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]

J2000 = datetime(2000,1,1,12)#Julian epoch (2000-01-01T12:00:00Z)

CLOCK_SCALE = 1.0#Clock rate scale (default 1:1, i.e. real-time)
CLOCK_STEP = timedelta(seconds=60)#Clock step (default to 60 seconds)
#
####################


class ModifyClockScale(Exception):
    def __init__(self,value):
        Exception.__init__(self,value)
        
        assert isinstance(value,(types.IntType,types.FloatType))
        
        self.scale = value
        
class ModifyClockStep(Exception):
    def __init__(self,value):
        Exception.__init__(self,value)
        
        assert isinstance(value,timedelta)
        
        self.step = value

@coroutine
def continuous(epoch=J2000,scale=CLOCK_SCALE,pipeline=None):
    """Story:  Continuous clock routine
    
    IN ORDER TO manage the simulation time
    AS THE clock segment
    I WANT TO progress the simulation time based off the progress of
        system time
    
    """
    
    """Specification:  Continuous clock routine
    
    Scenario 1:  Continuous clock created
    GIVEN an initial epoch (default J2000.0)
        AND a clock rate scale (default 1.0)
        AND a pipeline to send current time to (default None)
    WHEN a continuous clock is created
    THEN a continuous clock SHALL be activated
        
    Scenario 2:  Simulation time requested
    GiVEN an active continuous clock
    WHEN the clock value is requested
    THEN the system time since the last request SHALL be determined
        AND the elapsed time SHALL be scaled by the clock rate scale
        AND the simulation time SHALL be increased by the elapsed time
        AND the response SHALL be the simulation time
    
    Scenario 3:  Clock rate scale modified
    GiVEN an active continuous clock
    WHEN a clock rate scale modification is requested
    THEN the clock scale rate SHALL be modified to the requested value
        AND the simulation time SHALL be requested
    
    Scenario 4:  Continuous clock destroyed
    GiVEN an active continuous clock
    WHEN the continuous clock is destroyed
    THEN the downstream routine SHALL be destroyed
        AND the continuous clock SHALL deactivated
    
    """
    
    #Configuration validation
    assert isinstance(epoch,datetime)
    assert isinstance(scale,(types.IntType,types.FloatType))
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    now = datetime.utcnow()
        
    logging.info("Clock.Continuous:  Stating at %s" % epoch)
    while True:
        try:
            yield epoch,pipeline
        except ModifyClockScale as error:           
            scale = error.scale
        except GeneratorExit:
            logging.info("Clock.Continuous:  Stopping at %s" % epoch)
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        finally:
            past = now
            now = datetime.utcnow()
            
            epoch += scale * (now - past)#increase simulation time
            
            logging.debug("Clock.Continuous:  Updated epoch to %s" % epoch)

@coroutine
def discrete(epoch=J2000,step=CLOCK_STEP,pipeline=None):
    """Story:  Discrete clock routine
    
    IN ORDER TO manage the simulation time
    AS THE clock segment
    I WANT TO progress the simulation time at fixed intervals
    
    """
    
    """Specification:  Discrete clock routine
    
    Scenario 1:  Discrete clock created
    GIVEN an initial epoch (default J2000.0)
        AND a clock step (default 60 seconds)
        AND a pipeline to send current time to (default None)
    WHEN a discrete clock is created
    THEN a discrete clock SHALL be activated
        
    Scenario 2:  Simulation time requested
    GiVEN an active discrete clock
    WHEN the clock value is requested
    THEN the simulation time SHALL be increased by the clock step size
        AND the simulation time SHALL be sent downstream
    
    Scenario 3:  Clock step size modified
    GiVEN an active discrete clock
    WHEN a clock step size modification is requested
    THEN the clock step size SHALL be modified to the requested value
        AND the simulation time SHALL be requested
    
    Scenario 4:  Discrete clock destroyed
    GiVEN an active discrete clock
    WHEN the discrete clock is destroyed
    THEN the downstream routine SHALL be destroyed
        AND the discrete clock SHALL deactivated
    
    """
    
    #Configuration validation
    assert isinstance(epoch,datetime)
    assert isinstance(step,timedelta)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
        
    logging.info("Clock.Discrete:  Stating at %s" % epoch)
    while True:
        try:
            yield epoch,pipeline
        except ModifyClockStep as error:
            step = error.step
        except GeneratorExit:
            logging.info("Clock.Discrete:  Stopping at %s" % epoch)
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        finally:
            epoch += step#increase simulation time
            
            logging.debug("Clock.Discrete:  Updated epoch to %s" % epoch)