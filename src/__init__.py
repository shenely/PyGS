import logging

from core.service.scheduler import Scheduler
from core.service import web,broker
from clock import service as clock
from space import service as space
from ground import service as ground
from user import service as user

def main():
    logging.basicConfig(level=logging.DEBUG)
    
    scheduler = Scheduler()
    
    broker.main()
    web.main()
        
    clock.main()
    space.main()
    ground.main()
    user.main()
    
    scheduler.start()
    
if __name__ == '__main__':
    main()