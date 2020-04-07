from parser import *
from circuit import *

import sys

def main():
    filename = sys.argv[1]
    parser = Parser()
    root, nodes = parser.parseCircuit(filename)

            
    print(nodes[root].compute())

if __name__ == "__main__":
    main()
