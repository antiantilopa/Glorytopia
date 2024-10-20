import argparse
import asyncio
from pygame_tools_tafh import *

from scenes.opening_scene import OpeningScene

engine = Engine("Glorytopia", 60, (800, 600))

def main():
    parser = argparse.ArgumentParser(
                    prog='Glorytopia',
                    description='Play glorytopia!',
                    epilog='Pssss... I am not gay!')
    
    asyncio.run(engine.run(OpeningScene))
    
    


if __name__ == "__main__":
    main()