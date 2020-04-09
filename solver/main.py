from parser import *
from circuit import *
import time
import sys

def main():
    partitionFile = sys.argv[1]
    queryFile = sys.argv[2]
    weightFile = sys.argv[3]
    
    parser = Parser()
    weights, domains = parser.parseWeights(weightFile)
    partitionRoot, partitionNodes = parser.parseCircuit(partitionFile, weights, domains)
    queryRoot, queryNodes = parser.parseCircuit(queryFile, weights, domains)

    start = time.time()
    partitionF = partitionNodes[partitionRoot].compute()
    queryF = queryNodes[queryRoot].compute()
    queryProb = queryF / partitionF
    end = time.time()
    
    print("partition function =", partitionF)
    print("the query =", queryF)
    print("P(query) =", queryProb)
    print("time to compute:", end - start)


if __name__ == "__main__":
    main()
