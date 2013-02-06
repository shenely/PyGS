#!/usr/bin/env python2.7

"""Interpolation routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   06 February 2013

Provides routines for state interpolation.

Functions:
hermite -- Cubic Hermite spline
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
import logging
import types

#External libraries

#Internal libraries
from core import coroutine
from clock.epoch import EpochState
from .. import CartesianState
#
##################


##################
# Export section #
#
__all__ = ["hermite"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]

HERMITE_SPLINE_00 = lambda t: 2 * t ** 3 - 3 * t ** 2 + 1 
HERMITE_SPLINE_10 = lambda t: t ** 3 - 2 * t ** 2 + t
HERMITE_SPLINE_01 = lambda t: - 2 * t ** 3 + 3 * t ** 2
HERMITE_SPLINE_11 = lambda t: t ** 3 - t ** 2
#
####################

@coroutine
def hermite(system,prev=None,next=None,istrue=None,isfalse=None):
    """Story:  Cubic Hermite spline
    
    IN ORDER TO approximate the state between propagation points
    AS A user segment
    I WANT TO interpolate the state based off the position and velocity
        
    """
    
    u"""Specification:  Cubic Hermite spline
    
    GIVEN a system with epoch defined
        AND the previous state (default null)
        AND the next state (default null)
        AND a true downstream pipeline (default null)
        AND a false downstream pipeline (default null)
        
    Scenario 1:  State interpolation requested
    WHEN a state value is requested from upstream
        AND the previous state is defined
        AND the next state is defined
    THEN the domain SHALL be scaled to be between zero (0) and one (1)
                x0=epoch[0]
                x1=epoch[1]
                x=epoch
                t=(x-x0)/(x0-x1)
        AND range for position and velocity SHALL be scaled:
                p0=position[0]
                p1=position[1]
                m0=velocity[0]*(x1-x0)
                m1=velocity[1]*(x1-x0)
        AND the basis functions SHALL be evaluated at for the domain:
                h[0,0]=2t\u00b3-3t\u00b2+1
                h[0,1]=-2t\u00b3+3t\u00b2
                h[1,0]=t\u00b3-2t\u00b2+t
                h[1,1]=t\u00b3-t\u00b2
        AND the scaled position and velocity SHALL be calculated with
            the basis functions:
                p(t)=h[0,0]*p0+h[1,0]*m0+h[0,1]*p1+h[1,1]*m1
                m(t)=
        AND the position and velocity SHALL be unscaled:
                position=p(t)
                velocity=m(t)/(x1-x0)
        AND an interpolated state SHALL be created from the epoch,
            position and velocity
        AND the interpolated state SHALL be sent downstream
    
    Scenario 2:  Upstream state received
    WHEN a state value is requested upstream
        AND the previous state is defined
        AND the next state is defined
        AND a Cartesian state is received from upstream
    THEN the next state SHALL be set to undefined
        AND the previous SHALL shall be set to the received state
        AND a blank message SHALL be sent downstream
    
    Scenario 3:  Previous state undefined
    WHEN a state value is requested upstream
        AND the previous state is not defined
        AND a Cartesian state is received from upstream
    THEN the next state SHALL be set to undefined
        AND the previous SHALL shall be set to the received state
        AND an interpolated state SHALL be requested
    
    Scenario 4:  Next state undefined
    WHEN a state value is requested upstream
        AND the next state is not defined
        AND a Cartesian state is received from upstream
    THEN the next state SHALL be set to undefined
        AND the previous state SHALL be set to the received state
        AND an interpolated state SHALL be requested
    
    """
    
    #configuration validation
    assert isinstance(system,EpochState)
    assert isinstance(prev,CartesianState) or prev is None
    assert isinstance(next,CartesianState) or next is None
    assert isinstance(istrue,types.GeneratorType) or istrue is None
    assert isinstance(isfalse,types.GeneratorType) or isfalse is None
    
    state,pipeline = None,None
        
    logging.debug("State.Kepler:  Starting at %s" % system.epoch)
    while True:
        try:
            state = yield state,pipeline
        except GeneratorExit:
            logging.warn("State.Kepler:  Stopping at %s" % system.epoch)
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            #input validation
            assert isinstance(state,CartesianState) or state is None
            
            #cycle the states if a new state is received
            if state is not None:
                prev,next = state,prev
            
                #set the parameters for interpolation
                if (prev is not None) and (next is not None):
                    x0 = prev.epoch
                    x1 = next.epoch
                    dx = (x1 - x0).total_seconds()
                    
                    p0 = prev.position
                    p1 = next.position
                    
                    m0 = prev.velocity * dx
                    m1 = next.velocity * dx
            
            #calculate the current interpolated value
            if (prev is not None) and (next is not None):
                x = system.epoch
                t = (x - x0).total_seconds() / dx
                
                h00 = HERMITE_SPLINE_00(t)
                h01 = HERMITE_SPLINE_01(t)
                h10 = HERMITE_SPLINE_10(t)
                h11 = HERMITE_SPLINE_11(t)
                
                p = h00 * p0 + h10 * m0 + h01 * p1 + h11 * m1
                m = (1 - t) * m0 + t * m1#FIXME:  doesn't use spline
                
                state = CartesianState(x,p,m / dx)
            
                logging.info("Interpolate.Hermite:  Interpolated to %s" % state.epoch)
            else:
                state = None
        
            pipeline = istrue \
                       if (state is not None) \
                       else isfalse
