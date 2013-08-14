import logging

from core import broker
from core import engine
from core import persist
from core import service
from segment.user import UserSegment

def main():
    logging.basicConfig(level=logging.DEBUG)
    
    broker.main()
    persist.main()
    
    application = engine.Application("PyGS")
        
    #clock = ClockSegment(application)
    #space = SpaceSegment(application)
    #ground = GroundSegment(application)
    user = UserSegment(application)
    
    service.CoreService()
    
    application.start()
    
if __name__ == '__main__':
    main()