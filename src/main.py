import logging

from core import broker 
from core import agenda
from clock import service as clock
from space import service as space

def main():
    logging.basicConfig(level=logging.INFO)
    
    broker.main()
    
    scheduler = agenda.Scheduler()
        
    clock.main()
    space.main()
    
    scheduler.start()
    
if __name__ == '__main__':
    main()