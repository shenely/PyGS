#!/usr/bin/env python2.7

"""Command objects

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   27 January 2013

Purpose:    
"""


##################
# Import section #
#
#Built-in libraries
from math import pi,sqrt,cos,sin,tan,atan
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
        M = state.M + state.n * t
        E = newton(KEPLER_EQUATION,M,KEPLER_DERIVATIVE,(M,state.e),ANOMALY_ERROR)
        state.theta = 2 * atan(sqrt((1 + state.e) / (1 - state.e)) * tan(E / 2))        
        
        a = state.a
        e = state.e
        i = state.i + state.r * cos(state.u) * self.N / (state.n * state.a ** 2 * sqrt(1 - state.e ** 2))
        omega = state.omega - state.r * sin(state.u) * self.N / (state.h * tan(state.i))
        OMEGA = state.OMEGA - state.r * sin(state.u) * self.N / (state.n * state.a ** 2 * sqrt(1 - state.e ** 2) * sin(state.i))
        
        M = state.M - state.n * t
        E = newton(KEPLER_EQUATION,M,KEPLER_DERIVATIVE,(M,state.e),ANOMALY_ERROR)
        theta = 2 * atan(sqrt((1 + state.e) / (1 - state.e)) * tan(E / 2))
        
        theta %= 2 * pi
        omega %= 2 * pi
        
        perturb = KeplerianState(state.epoch,a,theta,e,omega,i,OMEGA)
        
        result = ManeuverResult(self.epoch,copy.deepcopy(state),perturb,id=self.id)
        
        state.update(perturb)
        
        return result
        