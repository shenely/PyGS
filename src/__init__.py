import logging

from .core.scheduler import Scheduler
from .segment import physics,space,user
from .service import broker,web

def main():
    logging.basicConfig(level=logging.INFO)
    
    scheduler = Scheduler()
    
    #broker.main()
    web.main()
        
    physics.main()
    space.main()
    user.main()
    
    scheduler.start()
    
if __name__ == '__main__':
    main()