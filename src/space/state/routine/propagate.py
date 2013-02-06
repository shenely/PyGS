#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""Propagation routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   06 February 2013

Provides routines for state propagation.

Functions:
kepler -- Kepler propagation
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
#
##################


##################
# Export section #
#
__all__ = ["kepler"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]

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
        AND the message SHALL be sent downstream
    
    """
    
    #TODO:  consider moving this under the state routines
    
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
