import logging

from core import broker
from core import agenda
from core import engine
from segment.clock import ClockSegment
from segment.space import SpaceSegment
from segment.ground import GroundSegment
from segment.user import UserSegment
import web

def main():
    logging.basicConfig(level=logging.INFO)
    
    broker.main()
    
    processor = agenda.Processor()
    application = engine.Application("End-to-end test",processor)
        
    clock = ClockSegment(application)
    space = SpaceSegment(application)
    ground = GroundSegment(application)
    user = UserSegment(application)
    
    web.main()
    
    processor.start()
    
if __name__ == '__main__':
    main()