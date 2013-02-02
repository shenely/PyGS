import logging

from service.scheduler import Scheduler
import clock,space
from service import broker,web

def main():
    logging.basicConfig(level=logging.INFO)
    
    scheduler = Scheduler()
    
    #broker.main()
    web.main()
        
    clock.main()
    space.main()
    #ground.main()
    #user.main()
    
    scheduler.start()
    
if __name__ == '__main__':
    main()