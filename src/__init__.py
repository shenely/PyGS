import logging

from core.service.scheduler import Scheduler
from core.service import web,broker
from clock import service as clock
from space import service as space
from user import service as user

def main():
    logging.basicConfig(level=logging.INFO)
    
    scheduler = Scheduler()
    
    broker.main()
    web.main()
        
    clock.main()
    space.main()
    #ground.main()
    user.main()
    
    scheduler.start()
    
if __name__ == '__main__':
    main()