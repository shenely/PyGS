import logging


from core import broker
from core import agenda
from clock import service as clock
from space import service as space
from ground import service as ground
from web import service as web

def main():
    logging.basicConfig(level=logging.INFO)
    
    broker.main()
    
    processor = agenda.Processor()
        
    clock.main()
    space.main()
    ground.main()
    
    web.main()
    
    processor.start()
    
if __name__ == '__main__':
    main()