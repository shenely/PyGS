#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""Interpolation routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   11 July 2013

Provides routines for state interpolation.

Functions:
HermiteInterpolate -- Cubic Hermite spline interpolation
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-07-11    shenely         1.0         Initial revision

"""


##################
# Import section #
#
#Built-in libraries
import logging

#External libraries

#Internal libraries
from core.routine import ActionRoutine
from epoch import EpochState
from .. import InertialState
#
##################


##################
# Export section #
#
__all__ = ["HermiteInterpolate"]
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


class InterpolateAction(ActionRoutine):pass

class HermiteInterpolate(InterpolateAction):
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
        AND the basis functions SHALL be evaluated for the domain:
                h[0,0]=2t³-3t²+1
                h[0,1]=-2t³+3t²
                h[1,0]=t³-2t²+t
                h[1,1]=t³-t²
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
        AND a inertial state is received from upstream
    THEN the next state SHALL be set to undefined
        AND the previous SHALL shall be set to the received state
        AND a blank message SHALL be sent downstream
    
    Scenario 3:  Previous state undefined
    WHEN a state value is requested upstream
        AND the previous state is not defined
        AND a inertial state is received from upstream
    THEN the next state SHALL be set to undefined
        AND the previous SHALL shall be set to the received state
        AND an interpolated state SHALL be requested
    
    Scenario 4:  Next state undefined
    WHEN a state value is requested upstream
        AND the next state is not defined
        AND a inertial state is received from upstream
    THEN the next state SHALL be set to undefined
        AND the previous state SHALL be set to the received state
        AND an interpolated state SHALL be requested
    
    """
    
    name = "Interpolate.Hermite"
    
    def __init__(self):
        InterpolateAction.__init__(self)
        
        self.prev = None
        self.curr = None
        self.next = None
    
    def _execute(self,message):
        assert isinstance(message,EpochState)
        
        if (self.prev is not None) and (self.next is not None):
            logging.info("{0}:  Interpolating from {1}".\
                         format(self.name,self.state.epoch))
            
            x = message.epoch
            t = (x - self.x0).total_seconds() / self.dx
            
            h00 = HERMITE_SPLINE_00(t)
            h01 = HERMITE_SPLINE_01(t)
            h10 = HERMITE_SPLINE_10(t)
            h11 = HERMITE_SPLINE_11(t)
            
            p = h00 * self.p0 + h10 * self.m0 + h01 * self.p1 + h11 * self.m1
            m = (1 - t) * self.m0 + t * self.m1#FIXME:  doesn't use spline
            
            self.curr = InertialState(x,p,m / self.dx)
            
            logging.info("{0}:  Interpolated to {1}".\
                         format(self.name,self.curr.epoch))
            
            return self.curr
        else:
            logging.info("{0}:  Not ready for interpolation".\
                         format(self.name))
    
    def set_state(self,state):
        assert isinstance(state,InertialState)
        
        #cycle the states if a new state is received
        self.prev,self.next = state,self.prev
    
        #set the parameters for interpolation
        if (self.prev is not None) and (self.next is not None):
            self.x0 = self.prev.epoch
            self.x1 = self.next.epoch
            self.dx = (self.x1 - self.x0).total_seconds()
            
            self.p0 = self.prev.position
            self.p1 = self.next.position
            
            self.m0 = self.prev.velocity * self.dx
            self.m1 = self.next.velocity * self.dx
        
        return state