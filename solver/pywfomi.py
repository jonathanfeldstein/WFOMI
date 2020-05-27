"""
.. module:: wfomi
   :synopsis: the main file of the solver, computes the wfomi of the given theory and query files given the weights of the predicates
.. moduleauthor:: Marcin Korecki
"""

from parser import *
from circuit import *
import time
import sys
from statistics import mean

def pywfomi():
    """
    the main function of the solver, takes the theory circuit, query circuit and the weight files 
    as arguments from the command line in that order and returns the probability of the query
    """
    partitionFile = sys.argv[1]
    queryFile = sys.argv[2]
    weightFile = sys.argv[3]

    parser = Parser()
    weights, domains = parser.parseWeights(weightFile)
    partitionRoot, partitionNodes = parser.parseCircuit(partitionFile, weights, domains)
    queryRoot, queryNodes = parser.parseCircuit(queryFile, weights, domains)

    startTime = time.time()
    partitionFunc = partitionNodes[partitionRoot].compute().integrate()
    queryFunc = queryNodes[queryRoot].compute().integrate()
    queryProb = queryFunc.const[0] / partitionFunc.const[0]
    endTime = time.time()
    resultTime = endTime - startTime
    print("time to compute:", resultTime)
    # print(round(mean(time_100), 3))

    print("partition function =", partitionFunc.const[0])
    print("the query =", queryFunc.const[0])
    print("P(query) =", queryProb)

if __name__ == "__main__":
    pywfomi()
