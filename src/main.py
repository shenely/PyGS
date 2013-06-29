import logging

from clock import service as clock

def main():
    logging.basicConfig(level=logging.DEBUG)
        
    clock.main()
    
if __name__ == '__main__':
    main()