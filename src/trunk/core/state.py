#!/usr/bin/env python2.7

"""State objects

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   16 January 2013

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
from numpy import matrix,dot,cross,float64
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
           "GeographicState"]
#
##################


####################
# Constant section #
#
__version__ = "0.1"#current version [major.minor]

DEG_TO_RAD = pi / 180
RAD_TO_DEG = 180 / pi

EARTH_RADIUS = 6378
EARTH_GRAVITATION = 368400

EPOCH_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
#
####################


class BaseState(ObjectDict):
    def __init__(self,epoch):
        self.epoch = epoch
        
    def copy(self):
        epoch = datetime.strptime(self.epoch.strftime(EPOCH_FORMAT),EPOCH_FORMAT)
        
        return BaseState(epoch)
        
    @property
    def epoch(self):
        """State Epoch"""
        
        return self["epoch"]
    
    @epoch.setter
    def epoch(self,epoch):
        assert isinstance(epoch,datetime)
        
        self["epoch"] = epoch


class CartesianState(BaseState):
    def __init__(self,epoch,position,velocity):
        BaseState.__init__(self,epoch)
        
        self.position = position
        self.velocity = velocity
        
    def copy(self):
        epoch = datetime.strptime(self.epoch.strftime(EPOCH_FORMAT),EPOCH_FORMAT)
        position = self.position.copy()
        velocity = self.velocity.copy()
        
        return CartesianState(epoch,position,velocity)
        
    @property
    def position(self):
        """Cartesian Position Vector"""
        
        return self["position"]
    
    @position.setter
    def position(self,position):
        assert isinstance(position,matrix)
        assert isinstance(position.dtype.type,float64)
        assert position.shape == (1,3)
        assert norm(position) > EARTH_RADIUS
        
        self["position"] = position
        
    @property
    def velocity(self):
        """Cartesian Velocity Vector"""
        
        return self["velocity"]
    
    @velocity.setter
    def velocity(self,velocity):
        assert isinstance(velocity,matrix)
        assert isinstance(velocity.dtype.type,float64)
        assert velocity.shape == (1,3)
        assert norm(velocity) > EARTH_RADIUS
        
        self["velocity"] = velocity
    
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
    def r(self):
        """Cartesian Radius (read-only)"""
        return norm(self.position)
    
    @property
    def alpha(self):
        """Cartesian Right Ascension (read-only)"""
        return atan2(self.position[1,0],self.position[0,0])
    
    @property
    def delta(self):
        """Cartesian Declination (read-only)"""
        return asin(self.position[2,0] / self.r)
    
    @property
    def V(self):
        """Cartesian U (read-only)"""
        return norm(self.velocity)
    
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
    def epsilon(self):
        """Cartesian Specific Energy (read-only)"""
        return self.V ** 2 / 2 - EARTH_GRAVITATION / self.r
    
    @property
    def h(self):
        """Cartesian Specific Angular Momentum (read-only)"""
        return cross(self.position,self.velocity)
    
    @property
    def e(self):
        """Cartesian Eccentricity Vector (read-only)"""
        return cross(self.position,self.h) / EARTH_GRAVITATION - self.position / self.r


class KeplerianState(BaseState):
    def __init__(self,epoch,
                 semi_major_axis,
                 true_anomaly,
                 eccentricity,
                 argument_of_perigee,
                 inclination,
                 longitude_of_ascending_node):
        BaseState.__init__(self,epoch)
        
        self.a = semi_major_axis
        self.theta = true_anomaly
        self.e = eccentricity
        self.omega = argument_of_perigee
        self.i = inclination
        self.OMEGA = longitude_of_ascending_node
        
    def copy(self):
        epoch = datetime.strptime(self.epoch.strftime(EPOCH_FORMAT),EPOCH_FORMAT)
        semi_major_axis = self.a
        true_anomaly = self.theta
        eccentricity = self.e
        argument_of_perigee = self.omega
        inclination = self.i
        longitude_of_ascending_node = self.OMEGA
        
        return KeplerianState(epoch,
                              semi_major_axis,
                              true_anomaly,
                              eccentricity,
                              argument_of_perigee,
                              inclination,
                              longitude_of_ascending_node)
    
    @property
    def a(self):
        """Keplerian Semi-major Axis"""
        
        return self["a"]
    
    @a.setter
    def a(self,semi_major_axis):
        assert isinstance(semi_major_axis,types.FloatType)
        assert semi_major_axis > EARTH_RADIUS
        
        self["a"] = semi_major_axis
    
    @property
    def theta(self):
        """Keplerian True Anomaly"""
        
        return self["theta"]
    
    @theta.setter
    def theta(self,true_anomaly):
        assert isinstance(true_anomaly,types.FloatType)
        assert true_anomaly >= 0
        assert true_anomaly <  2 * pi
        
        self["theta"] = true_anomaly
    
    @property
    def e(self):
        """Keplerian Eccentricity"""
        
        return self["e"]
    
    @e.setter
    def e(self,eccentricity):
        assert isinstance(eccentricity,types.FloatType)
        assert eccentricity >= 0
        assert eccentricity < 1
        
        self["e"] = eccentricity
    
    @property
    def omega(self):
        """Keplerian Argument of Perigee"""
        
        return self["omega"]
    
    @omega.setter
    def omega(self,argument_of_perigee):
        assert isinstance(argument_of_perigee,types.FloatType)
        assert argument_of_perigee >= 0
        assert argument_of_perigee < 2 * pi
        
        self["omega"] = argument_of_perigee
    
    @property
    def i(self):
        """Keplerian Inclination"""
        
        return self["i"]
    
    @i.setter
    def i(self,inclination):
        assert isinstance(inclination,types.FloatType)
        assert inclination >= 0
        assert inclination < pi
        
        self["i"] = inclination
    
    @property
    def OMEGA(self):
        """Keplerian Right Ascension of the Ascending Node"""
        
        return self["OMEGA"]
    
    @OMEGA.setter
    def OMEGA(self,longitude_of_ascending_node):
        assert isinstance(longitude_of_ascending_node,types.FloatType)
        assert longitude_of_ascending_node >= 0
        assert longitude_of_ascending_node < 2 * pi
        
        self["OMEGA"] = longitude_of_ascending_node
    
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
        return self.a * (1 - self.e ** 2) / (1 + self.e * cos(self.theta))
    
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
    
class GeographicState(BaseState):
    def __init__(self,
                 epoch,
                 arc_length,
                 longitude,
                 latitude):   
        BaseState.__init__(self,epoch)
             
        self.arc = arc_length
        self.long = longitude
        self.lat = latitude
    
    @property
    def arc(self):
        return self["arc"]
    
    @arc.setter
    def arc(self,arc_length):
        assert isinstance(arc_length,types.FloatType)
        assert arc_length >= 0
        assert arc_length < 180
        
        self["arc"] = arc_length
    
    @property
    def long(self):        
        return self["long"]
    
    @long.setter
    def long(self,longitude):
        assert isinstance(longitude,types.FloatType)
        assert longitude >= 0
        assert longitude < 360
        
        self["long"] = longitude
    
    @property
    def lat(self):
        return self["lat"]
    
    @lat.setter
    def lat(self,latitude):
        assert isinstance(latitude,types.FloatType)
        assert abs(latitude) <= 90
        
        self["lat"] = latitude
