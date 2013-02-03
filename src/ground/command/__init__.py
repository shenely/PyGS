#!/usr/bin/env python2.7

"""Command objects

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   03 February 2013

Purpose:    
"""


##################
# Import section #
#
#Built-in libraries
from math import pi,sqrt,cos,sin,tan,acos,asin,atan2
from datetime import datetime
import uuid
import types
import copy

#External libraries
from scipy.optimize import newton

#Internal libraries
from core import ObjectDict
from clock.epoch import EpochState
from space.state import KeplerianState
from space.result import ManeuverResult
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


class BaseCommand(EpochState):
    registry = dict()
    
    def __init__(self,type,epoch,*args,**kwargs):
        EpochState.__init__(self,epoch,*args,**kwargs)
        
        assert isinstance(type,types.StringTypes)
        
        self.type = type
    
    @staticmethod
    def check(kwargs):
        assert EpochState.check(kwargs)
        assert hasattr(kwargs,"type")
        
        return True
    
    @classmethod
    def register(cls,key):
        def wrapper(value):
            cls.registry[key] = value.build
            
            return value
        return wrapper
        
@BaseCommand.register("maneuver")
class ManeuverCommand(BaseCommand):    
    def __init__(self,epoch,R,T,N,type="maneuver",*args,**kwargs):
        BaseCommand.__init__(self,type,epoch,*args,**kwargs)

        assert isinstance(R,types.FloatType)
        assert isinstance(T,types.FloatType)
        assert isinstance(N,types.FloatType)
        
        self.R = R
        self.T = T
        self.N = N
    
    @staticmethod
    def check(kwargs):
        assert BaseCommand.check(kwargs)
        assert hasattr(kwargs,"R")
        assert hasattr(kwargs,"T")
        assert hasattr(kwargs,"N")
        
        return True
    
    def execute(self,state):
        assert isinstance(state,KeplerianState)
        
        t = (self.epoch - state.epoch).total_seconds()
        M = state.M + state.n * t
        E = newton(KEPLER_EQUATION,M,KEPLER_DERIVATIVE,(M,state.e),ANOMALY_ERROR)
        state.theta = 2 * atan2(sqrt(1 + state.e) * sin(E / 2),
                                sqrt(1 - state.e) * cos(E / 2))
        
        c = cos(state.theta)
        s = sin(state.theta)
        A = 2 / (state.n * sqrt(1 - state.e ** 2))
        B = state.h / EARTH_GRAVITATION
        C = state.r / state.h
        
        h = state.e * sin(state.omega)
        k = state.e * cos(state.omega)
        
        h += - B * cos(state.u) * self.R +\
             C * (sin(state.u) * (2 + state.e * c) + h) * self.T
        k += B * sin(state.u) * self.R +\
             C * (cos(state.u) * (2 + state.e * c) + k) * self.T
    
        e = sqrt(h ** 2 + k ** 2)
        omega = atan2(h,k)
        
        a = state.a +\
            A * (state.e * s * self.R +\
                 (1 + state.e * c) * self.T)
        theta = state.u - omega
        
        i = state.i +\
            C * cos(state.u) * self.N
        OMEGA = state.OMEGA +\
                C * (sin(state.u) / sin(state.i)) * self.N
        omega += - C * (sin(state.u) / tan(state.i)) * self.N
        
        perturb = KeplerianState(state.epoch,a,theta,e,omega,i,OMEGA)
        
        result = ManeuverResult(self.epoch,copy.deepcopy(state),perturb,_id=self._id)
        
        state.update(perturb)
        
        return result
        