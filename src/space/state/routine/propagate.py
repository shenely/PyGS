#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""Propagation routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   18 February 2013

Provides routines for state propagation.

Functions:
kepler    -- Kepler propagation
ephemeris -- Ephemeris propagation
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-02-06    shenely         1.0         Promoted to version 1.0
2013-02-10                    1.1         Ephemeris propagation started
2013-02-18                    1.2         Completed task (awhile ago)

"""


##################
# Import section #
#
#Built-in libraries
from math import *
from datetime import datetime,timedelta
import logging
import types
import copy

#External libraries
from scipy.optimize import newton

#Internal libraries
from core import coroutine
from .. import KeplerianState
from model.ephemeris import BaseEphemeris
#
##################


##################
# Export section #
#
__all__ = ["kepler",
           "ephemeris"]
#
##################


####################
# Constant section #
#
__version__ = "1.1"#current version [major.minor]

CLOCK_STEP = timedelta(seconds=60)#Clock step (default to 60 seconds)

KEPLER_EQUATION = lambda E,M,e:E - e * sin(E) - M#Kepler equation
KEPLER_DERIVATIVE = lambda E,M,e:1 - e * cos(E)#Derivative of Kepler equation
ANOMALY_ERROR = 1e-15#Acceptable error in mean anomaly
#
####################


@coroutine
def kepler(state,step=CLOCK_STEP,pipeline=None):
    """Story:  Kepler propagation
    
    IN ORDER TO generating messages to results for a ground segment
    AS A space segment
    I WANT TO encode a result in a defined string format
        
    """
    
    u"""Specification:  Kepler propagation
    
    GIVEN an initial Keplerian state
        AND a step size (default 60 seconds)
        AND a downstream pipeline (default null)
        
    Scenario 1:  State propagation requested
    WHEN a state value is requested from upstream
    THEN the state epoch shall be incremented by the step size
        AND the mean anomaly shall be incremented by step size
            multiplied by mean motion:
                M+=n*Δt
        AND the eccentric anomaly SHALL be calculated from mean anomaly:
                M=E-e*sin(E)
        AND the true anomaly SHALL be calculated from eccentric anomaly:
                tan(θ/2)=√((1+e)/(1-e))tan(E/2)
        AND the state SHALL be sent downstream
    
    """
        
    #configuration validation
    assert isinstance(state,KeplerianState)
    assert isinstance(step,timedelta)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    message = None
        
    logging.debug("Propagate.Kepler:  Starting at %s" % state.epoch)
    while True:
        try:
            yield message,pipeline
        except GeneratorExit:
            logging.warn("Propagate.Kepler:  Stopping at %s" % state.epoch)
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            state.epoch += step
    
            M = (state.M + state.n * step.total_seconds()) % (2 * pi)
            E = newton(KEPLER_EQUATION,M,KEPLER_DERIVATIVE,(M,state.e),ANOMALY_ERROR)
            state.theta = 2 * atan2(sqrt(1 + state.e) * sin(E / 2),
                                    sqrt(1 - state.e) * cos(E / 2))
                    
            message = copy.deepcopy(state)
                            
            logging.info("Propagate.Kepler:  Propagated to %s" % state.epoch)


@coroutine
def ephemeris(ephemeris,pipeline=None):
    """Story:  Ephemeris propagation
    
    IN ORDER TO generating messages to results for a ground segment
    AS A space segment
    I WANT TO encode a result in a defined string format
        
    """
    
    u"""Specification:  Ephemeris propagation
    
    GIVEN an ephemeris
        AND a downstream pipeline (default null)
        
    Scenario 1:  State propagation requested
    WHEN a state value is requested from upstream
    THEN the next state from the ephemeris SHALL be sent downstream
    
    """
        
    #configuration validation
    assert isinstance(ephemeris,BaseEphemeris)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    message = None
        
    logging.debug("Propagate.Ephemeris:  Starting at %s" % ephemeris.epoch.start)
    for state in ephemeris.states:
        try:
            yield message,pipeline
        except GeneratorExit:
            logging.warn("Propagate.Ephemeris:  Stopping at %s" % state.epoch)
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:                    
            message = state
                            
            logging.info("Propagate.Ephemeris:  Propagated to %s" % state.epoch)
