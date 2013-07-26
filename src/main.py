from math import pi
from datetime import datetime
import logging

from bson.tz_util import utc


from core import broker
from core import agenda
from core import engine
from state import KeplerianState
from segment.clock import ClockSegment
from segment.space import SpaceSegment
from segment.ground import GroundSegment
from segment.user import UserSegment
from asset.model import AssetModel
from asset.controller import AssetController
from asset.view import AssetView
from web import service as web

J2000 = datetime(2000,1,1,12,tzinfo=utc)#Julian epoch (2000-01-01T12:00:00Z)

RAD_TO_DEG = lambda rad:180 * rad / pi
DEG_TO_RAD = lambda deg:pi * deg / 180

def main():
    logging.basicConfig(level=logging.INFO)
    
    broker.main()
    
    processor = agenda.Processor()
    application = engine.Application("Clock test",processor)
    
    state = KeplerianState(J2000,10000.0,0.0,0.2,DEG_TO_RAD(90.0),DEG_TO_RAD(60.0),0.0)
        
    clock = ClockSegment(application)
    space = SpaceSegment(application)
    ground = GroundSegment(application)
    user = UserSegment(application)
    
    model = AssetModel(space,"Aqua",state)
    controller = AssetController(ground,"Aqua",state)
    view = AssetView(user,"Aqua")
    
    web.main()
    
    processor.start()
    
if __name__ == '__main__':
    main()