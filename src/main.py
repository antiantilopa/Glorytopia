import argparse
import asyncio
from pygame_tools_tafh import *

from client.scenes.epilog_scene import TestEpilogScene

engine = Engine("Glorytopia", 60, (800, 600))

def main():
    parser = argparse.ArgumentParser(
                    prog='Glorytopia',
                    description='Play glorytopia!',
                    epilog='Pssss... I am not gay!')
    engine.register(TestEpilogScene("test"))
    asyncio.run(engine.load_scene("test", None))
    

if __name__ == "__main__":
    main()