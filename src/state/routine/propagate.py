#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""Propagation routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   29 June 2013

Provides routines for state propagation.

Functions:
KeplerPropagate    -- Kepler propagation
EphemerisPropagate -- Ephemeris propagation
"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-06-29    shenely         1.0         Initial revision

"""


##################
# Import section #
#
#Built-in libraries
from math import *
from datetime import datetime,timedelta
import logging

#External libraries
from scipy.optimize import newton

#Internal libraries
from core.routine import ActionRoutine
from .. import KeplerianState
#from model.ephemeris import BaseEphemeris
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


class PropagateAction(ActionRoutine):pass

class KeplerPropagate(PropagateAction):
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
    
    name = "Propagate.Kepler"
    
    def __init__(self,state,step=CLOCK_STEP):
        #assert isinstance(state,KeplerianState)
        assert isinstance(step,timedelta)
        
        PropagateAction.__init__(self)
        
        self.state = state
        self.step = step
                      
    def _execute(self,message):
        logging.info("{0}:  Propagating from {1}".\
                     format(self.name,self.state.epoch))

        e = self.state.e
        M = (self.state.M +\
             self.state.n * self.step.total_seconds()) % (2 * pi)
        E = newton(KEPLER_EQUATION,M,KEPLER_DERIVATIVE,(M,e),ANOMALY_ERROR)
                
        self.state = KeplerianState(self.state.epoch + self.step,
                                    self.state.a,
                                    2 * atan2(sqrt(1 + e) * sin(E / 2),
                                           sqrt(1 - e) * cos(E / 2)),
                                    self.state.e,
                                    self.state.omega,
                                    self.state.i,
                                    self.state.OMEGA)

        logging.info("{0}:  Propagated to {1}".\
                     format(self.name,self.state.epoch))
        
        return self.state


#@coroutine
#def ephemeris(ephemeris,pipeline=None):
#    """Story:  Ephemeris propagation
#    
#    IN ORDER TO generating messages to results for a ground segment
#    AS A space segment
#    I WANT TO encode a result in a defined string format
#        
#    """
#    
#    u"""Specification:  Ephemeris propagation
#    
#    GIVEN an ephemeris
#        AND a downstream pipeline (default null)
#        
#    Scenario 1:  State propagation requested
#    WHEN a state value is requested from upstream
#    THEN the next state from the ephemeris SHALL be sent downstream
#    
#    """
#        
#    #configuration validation
#    assert isinstance(ephemeris,BaseEphemeris)
#    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
#    
#    message = None
#        
#    logging.debug("Propagate.Ephemeris:  Starting at %s" % ephemeris.epoch.start)
#    for state in ephemeris.states:
#        try:
#            yield message,pipeline
#        except GeneratorExit:
#            logging.warn("Propagate.Ephemeris:  Stopping at %s" % state.epoch)
#            
#            #close downstream routine (if it exists)
#            pipeline.close() if pipeline is not None else None
#            
#            return
#        else:                    
#            message = state
#                            
#            logging.info("Propagate.Ephemeris:  Propagated to %s" % state.epoch)