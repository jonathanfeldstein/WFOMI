from parser import *
from circuit import *
import time
import sys

def main():
    partitionFile = sys.argv[1]
    queryFile = sys.argv[2]
    weightFile = sys.argv[3]
    algoType = int(sys.argv[4])
    
    parser = Parser()
    weights, domains = parser.parseWeights(weightFile)
    partitionRoot, partitionNodes = parser.parseCircuit(partitionFile, weights, domains, algoType)
    queryRoot, queryNodes = parser.parseCircuit(queryFile, weights, domains, algoType)

    startTime = time.time()
    partitionFunc = partitionNodes[partitionRoot].compute().integrate()
    queryFunc = queryNodes[queryRoot].compute().integrate()
    queryProb = queryFunc / partitionFunc
    endTime = time.time()
    
    print("partition function =", partitionFunc)
    print("the query =", queryFunc)
    print("P(query) =", queryProb)
    print("time to compute:", endTime - startTime)


if __name__ == "__main__":
    main()
