from parser import *
from circuit import *
import time
import sys

def main():
    circuitFile = sys.argv[1]
    weightFile = sys.argv[2]
    
    parser = Parser()
    weights, domains = parser.parseWeights(weightFile)
    root, nodes = parser.parseCircuit(circuitFile, weights)

    start = time.time()
    result = nodes[root].compute()
    end = time.time()
    
    print(result)
    print("time to compute:", end - start)


if __name__ == "__main__":
    main()
