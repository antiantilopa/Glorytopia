import argparse

parser = argparse.ArgumentParser(
                    prog='Glorytopia',
                    description='Host glorytopia server!',
                    epilog='Pssss... I am gay!')

parser.add_argument("-p", "--port")
parser.add_argument("")

def main():
    args = parser.parse_args()



if __name__ == "__main__":
    main()


