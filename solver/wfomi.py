"""
.. module:: wfomi
   :synopsis: the main file of the solver, computes the wfomi of the given theory and query files given the weights of the predicates
.. moduleauthor:: Marcin Korecki
"""

from parser import *
import time
import sys

def wfomi(partitionFile=None, queryFile=None, weightFile=None):
    """
    the main function of the solver, takes the theory circuit, query circuit and the weight files 
    as arguments from the command line in that order and returns the probability of the query 
    or as arguments if called as a function from a different module
    
    :param partitionFile: the path to the file contiaining the theory circuit which will be used to compute the partition function
    :param queryFile: the path to the file containing the query circuit which will be used to compute unnormalised probability of the query
    :param weightFile: the path to the weight file containing the weights of the predicates in the theory and query circuits

    :returns: the probability of the query. In addition the time to compute is printed along with the partition function and unnormalised query
    """

    if len(sys.argv) == 4:
        partitionFile = sys.argv[1]
        queryFile = sys.argv[2]
        weightFile = sys.argv[3]

    if partitionFile is None:
        print("error: partition file name is not specified")
        return 0
    if queryFile is None:
        print("error: query file name is not specified")
        return 0
    if weightFile is None:
        print("error: weight file name is not specified")
        return 0

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

    print("partition function =", partitionFunc.const[0])
    print("the query =", queryFunc.const[0])
    print("P(query) =", queryProb)

    return queryProb

if __name__ == "__main__":
    wfomi()
