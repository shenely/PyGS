#!/usr/bin/env python2.7

"""State objects

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   29 January 2013

Purpose:    
"""


##################
# Import section #
#
#Built-in libraries
from math import pi,sqrt,cos,sin,tan,acos,asin,atan,atan2
from datetime import datetime,time
import types

#External libraries
from numpy import matrix,dot,inner,cross,float64
from scipy.linalg import norm

#Internal libraries
from . import ObjectDict
#
##################


##################
# Export section #
#
__all__ = ["BaseState",
           "CartesianState",
           "KeplerianState",
           "GeographicState",
           "HorizontalState"]
#
##################


####################
# Constant section #
#
__version__ = "0.1"#current version [major.minor]

DEG_TO_RAD = pi / 180
RAD_TO_DEG = 180 / pi

EARTH_RADIUS = 6378
EARTH_GRAVITATION = 398600.4

EPOCH_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
#
####################


class BaseState(ObjectDict):
    def __init__(self,epoch):
        assert isinstance(epoch,datetime)
        
        self.epoch = epoch
        
    @property
    def epoch(self):
        """State Epoch"""
        
        return self["epoch"]


class CartesianState(BaseState):
    def __init__(self,epoch,position,velocity):
        BaseState.__init__(self,epoch)
        
        assert isinstance(position,matrix)
        assert position.dtype.type is float64
        assert position.shape == (3,1)
        assert norm(position) > EARTH_RADIUS
        
        assert isinstance(velocity,matrix)
        assert velocity.dtype.type is float64
        assert velocity.shape == (3,1)
        assert velocity.T * velocity * norm(position) < 2 * EARTH_GRAVITATION
        
        self.position = position
        self.velocity = velocity
        
    @property
    def position(self):
        """Cartesian Position Vector"""
        
        return self["position"]
        
    @property
    def velocity(self):
        """Cartesian Velocity Vector"""
        
        return self["velocity"]
    
    @property
    def x(self):
        """Cartesian X (read-only)"""
        return self.position[0,0]
    
    @property
    def y(self):
        """Cartesian Y (read-only)"""
        return self.position[1,0]
    
    @property
    def z(self):
        """Cartesian Z (read-only)"""
        return self.position[2,0]
    
    @property
    def u(self):
        """Cartesian U (read-only)"""
        return self.velocity[0,0]
    
    @property
    def v(self):
        """Cartesian V (read-only)"""
        return self.velocity[1,0]
    
    @property
    def w(self):
        """Cartesian W (read-only)"""
        return self.velocity[2,0]
    
    @property
    def R(self):
        """Cartesian Radius (read-only)"""
        return norm(self.position)
    
    @property
    def V(self):
        """Cartesian U (read-only)"""
        return norm(self.velocity)
    
    @property
    def alpha(self):
        """Cartesian Right Ascension (read-only)"""
        return atan2(self.position[1,0],self.position[0,0])
    
    @property
    def delta(self):
        """Cartesian Declination (read-only)"""
        return asin(self.position[2,0] / self.R)
    
    @property
    def epsilon(self):
        """Cartesian Specific Energy (read-only)"""
        return self.V ** 2 / 2 - EARTH_GRAVITATION / self.R
    
    @property
    def h(self):
        """Cartesian Specific Angular Momentum (read-only)"""
        return cross(self.position,self.velocity)
    
    @property
    def e(self):
        """Cartesian Eccentricity Vector (read-only)"""
        return cross(self.position,self.h) / EARTH_GRAVITATION - self.position / self.R


class KeplerianState(BaseState):
    def __init__(self,epoch,
                 semi_major_axis,
                 true_anomaly,
                 eccentricity,
                 argument_of_perigee,
                 inclination,
                 longitude_of_ascending_node):
        BaseState.__init__(self,epoch)
        
        assert isinstance(semi_major_axis,types.FloatType)
        assert semi_major_axis > EARTH_RADIUS
        assert isinstance(eccentricity,types.FloatType)
        if eccentricity < 0:
            eccentricity = - eccentricity
            #argument_of_perigee += pi
        assert eccentricity < 1
        assert isinstance(inclination,types.FloatType)
        inclination %= 2 * pi
        if inclination < 0 or inclination >= pi:
            inclination -= pi
            argument_of_perigee += pi
        assert inclination < pi
        assert isinstance(true_anomaly,types.FloatType)
        true_anomaly %= 2 * pi
        assert isinstance(argument_of_perigee,types.FloatType)
        argument_of_perigee %= 2 * pi
        assert isinstance(longitude_of_ascending_node,types.FloatType)
        argument_of_perigee %= 2 * pi
        
        self.a = semi_major_axis
        self.theta = true_anomaly
        self.e = eccentricity
        self.omega = argument_of_perigee
        self.i = inclination
        self.OMEGA = longitude_of_ascending_node
    
    @property
    def a(self):
        """Keplerian Semi-major Axis"""
        
        return self["a"]
    
    @property
    def theta(self):
        """Keplerian True Anomaly"""
        
        return self["theta"]
    
    @property
    def e(self):
        """Keplerian Eccentricity"""
        
        return self["e"]
    
    @property
    def omega(self):
        """Keplerian Argument of Perigee"""
        
        return self["omega"]
    
    @property
    def i(self):
        """Keplerian Inclination"""
        
        return self["i"]
    
    @property
    def OMEGA(self):
        """Keplerian Right Ascension of the Ascending Node"""
        
        return self["OMEGA"]
    
    @property
    def epsilon(self):
        """Keplerian Specific Energy (read-only)"""
        return - EARTH_GRAVITATION / self.a / 2
    
    @property
    def h(self):
        """Keplerian Specific Angular Momentum (read-only)"""
        return sqrt(EARTH_GRAVITATION * self.p)
    
    @property
    def r(self):
        """Keplerian Radius (read-only)"""
        return self.p / (1 + self.e * cos(self.theta))
    
    @property
    def p(self):
        """Keplerian Semi-latus Rectum (read-only)"""
        return self.a * (1 - self.e ** 2)
    
    @property
    def b(self):
        """Keplerian Semi-minor Axis (read-only)"""
        return self.a * sqrt(1 - self.e ** 2)
    
    @property
    def A(self):
        """Keplerian Apogee (read-only)"""
        return self.a * (1 + self.e)
    
    @property
    def P(self):
        """Keplerian Perigee (read-only)"""
        return self.a * (1 - self.e)
    
    @property
    def n(self):
        """Keplerian Mean Motion (read-only)"""
        return sqrt(EARTH_GRAVITATION / self.a ** 3)
    
    @property
    def T(self):
        """Keplerian Period (read-only)"""
        return 2 * pi * sqrt(self.a ** 3 / EARTH_GRAVITATION)
    
    @property
    def E(self):
        """Keplerian Eccentric Anomaly (read-only)"""
        return 2 * atan(sqrt((1 - self.e) / (1 + self.e)) * tan(self.theta / 2))
    
    @property
    def M(self):
        """Keplerian Mean Anomaly (read-only)"""
        return self.E - self.e * sin(self.E)
    
    @property
    def u(self):
        """Keplerian Argument of Latitude (read-only)"""
        return self.theta + self.omega
   

class GeographicState(BaseState):
    def __init__(self,
                 epoch,
                 arc_length,
                 longitude,
                 latitude):   
        BaseState.__init__(self,epoch)
        
        assert isinstance(arc_length,types.FloatType)
        assert arc_length >= 0
        assert arc_length < 180
        assert isinstance(longitude,types.FloatType)
        assert longitude >= 0
        assert longitude < 360
        assert isinstance(latitude,types.FloatType)
        assert abs(latitude) <= 90
             
        self.arc = arc_length
        self.long = longitude
        self.lat = latitude
    
    @property
    def arc(self):
        return self["arc"]
    
    @property
    def long(self):        
        return self["long"]
    
    @property
    def lat(self):
        return self["lat"]


class HorizontalState(BaseState):
    def __init__(self,
                 epoch,
                 azimuth,
                 elevation,
                 range):
        BaseState.__init__(self,epoch)
        
        assert isinstance(azimuth,types.FloatType)
        assert azimuth >= 0
        assert azimuth < 360
        assert isinstance(elevation,types.FloatType)
        assert abs(elevation) <= 90
        assert isinstance(range,types.FloatType)
        assert abs(range) >= 0
             
        self.az = azimuth
        self.el = elevation
        self.r = range
    
    @property
    def az(self):
        return self["az"]
    
    @property
    def el(self):        
        return self["el"]
    
    @property
    def r(self):
        return self["r"]
