#!/usr/bin/env python2.7

"""Command objects

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   02 February 2013

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
    
    def __init__(self,epoch,id=str(uuid.uuid4())):
        EpochState.__init__(self,epoch)
        
        assert isinstance(id,types.StringTypes)
        
        self.id = id
    
    @classmethod
    def register(cls,key):
        def wrapper(value):
            cls.registry[key] = value.build
            
            return value
        return wrapper
    
    @classmethod
    def build(cls,params):
        raise NotImplemented
        

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
    
    @classmethod
    def build(cls,params):
        assert isinstance(params,ObjectDict)
        assert hasattr(params,"R")
        assert isinstance(params.R,types.FloatType)
        assert hasattr(params,"T")
        assert isinstance(params.T,types.FloatType)
        assert hasattr(params,"N")
        assert isinstance(params.N,types.FloatType)
        
        return cls(params.epoch,
                   params.R,params.T,params.N,
                   params.id)
    
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
        
        result = ManeuverResult(self.epoch,copy.deepcopy(state),perturb,id=self.id)
        
        state.update(perturb)
        
        return result
        