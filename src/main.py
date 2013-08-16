import logging

from core import broker
from core import engine
from core import persist
from core import service
from core import web

def main():
    logging.basicConfig(level=logging.DEBUG)
    
    broker.main()
    persist.main()
    
    application = engine.Application("PyGS")
        
    #clock = ClockSegment(application)
    #space = SpaceSegment(application)
    #ground = GroundSegment(application)
    web.WebService()
    
    service.CoreService()
    
    application.start()
    
if __name__ == '__main__':
    main()