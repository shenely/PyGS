#!/usr/bin/env python2.7

"""Command objects

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   30 January 2013

Purpose:    
"""


##################
# Import section #
#
#Built-in libraries
from math import pi,sqrt,cos,sin,tan,atan2
from datetime import datetime
import uuid
import types
import copy

#External libraries
from scipy.optimize import newton

#Internal libraries
from .state import BaseState
from .state import KeplerianState
from .result import ManeuverResult
#
##################


##################
# Export section #
#
__all__ = ["BaseCommand",
           "ManeuverCommand"]
#
##################


####################
# Constant section #
#
__version__ = "0.1"#current version [major.minor]

ANOMALY_ERROR = 1e-15

KEPLER_EQUATION = lambda E,M,e:E - e * sin(E) - M
KEPLER_DERIVATIVE = lambda E,M,e:1 - e * cos(E)

EARTH_GRAVITATION = 398600.4
#
####################

class BaseCommand(BaseState):
    registry = dict()
    
    def __init__(self,epoch,id=str(uuid.uuid4())):
        BaseState.__init__(self,epoch)
        
        assert isinstance(id,types.StringTypes)
        
        self.id = id
    
    @classmethod
    def register(cls,key):
        def wrapper(value):
            cls.registry[key] = value
            
            return value
        return wrapper
        

@BaseCommand.register("maneuver")
class ManeuverCommand(BaseCommand):    
    def __init__(self,epoch,radial,tangent,normal,id=str(uuid.uuid4())):
        BaseCommand.__init__(self,epoch,id)

        assert isinstance(radial,types.FloatType)
        assert isinstance(tangent,types.FloatType)
        assert isinstance(normal,types.FloatType)
        
        self.type = "maneuver"
        self.R = radial
        self.T = tangent
        self.N = normal
    
    def execute(self,state):
        assert isinstance(state,KeplerianState)
        
        t = (self.epoch - state.epoch).total_seconds()
        state.M += state.n * t
        
        c = cos(state.theta)
        s = sin(state.theta)
        A = 2 / (state.n * sqrt(1 - state.e ** 2))
        B = state.h / EARTH_GRAVITATION
        C = state.r / state.h
        D = 1 / (state.n * state.a ** 2 * state.e)
        
        a = state.a +\
            A * (state.e * s * self.R +\
                 (1 + state.e * c) * self.T)
        e = state.e +\
            B * (s * self.R +\
                 (c + cos(state.E)) * self.T)
        i = state.i +\
            C * cos(state.u) * self.N
        omega = state.omega -\
                B * (c / state.e) * self.R +\
                C * ((s / state.e) * (2 + state.e * c) * self.T -\
                     (sin(state.u) / tan(state.i)) * self.N)
        OMEGA = state.OMEGA +\
                C * (sin(state.u) / sin(state.i)) * self.N 
        
        M = state.M - state.n * t +\
            D * ((state.p * c - 2 * state.e * state.r) * self.R -\
                 (state.p + state.r) * s * self.T)
        E = newton(KEPLER_EQUATION,M,KEPLER_DERIVATIVE,(M,e),ANOMALY_ERROR)
        theta = 2 * atan2(sqrt(1 + e) * sin(E / 2),
                          sqrt(1 - e) * cos(E / 2))
        
        perturb = KeplerianState(state.epoch,a,theta,e,omega,i,OMEGA)
        
        result = ManeuverResult(self.epoch,copy.deepcopy(state),perturb,id=self.id)
        
        state.update(perturb)
        
        return result
        