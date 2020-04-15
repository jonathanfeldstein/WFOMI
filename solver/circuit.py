from sympy import *
from term import *
import numpy as np

hashed_inegrals = {}

class Node(object):
    def __init__(self, left=None, right=None):
        self.left = left
        self.right = right

    def compute(self):
        raise NotImplementedError("Subclass must implement abstract method")
    
class ForAllNode(Node):
    def __init__(self, var=None, objects=None):
        super(ForAllNode, self).__init__()
        self.var = var
        self.objects = objects
        
    def compute(self, setsize=[]):
        if setsize == []:
            setsize = [len(self.objects[self.var])]

        print("allsize", setsize)
        if len(setsize) != 1:
            part1 = setsize[0]
            part2 = setsize[1]
        else:
            part1 = part2 = setsize[0]
            
        term = self.left.compute(setsize=[part1])
        result = term.integrate()
        print("ALL", part1, part2, result, Pow(result, part2))
        return Term(Pow(result, part2))
    
class ExistsNode(Node):
    def __init__(self, var=None, objects=None):
        super(ExistsNode, self).__init__()
        self.var = var
        self.objects = objects
        
    def compute(self, setsize=[]):
        if setsize == []:
            setsize = [len(self.objects[self.var])]

        result = Term(0)
        for i in range(0, setsize[0]+1):
            coeff = Term(binomial(setsize[0], i))
            compute = self.left.compute(setsize=[i, setsize[0]-i])
            result += coeff * compute
            print("EXISTS", coeff.data, (compute.data), sum(result.data))
        return result

class OrNode(Node):
    def compute(self, setsize=[]):
        leftTerm = self.left.compute(setsize=setsize)
        rightTerm = self.right.compute(setsize=setsize)
        # print("ADD", leftTerm, rightTerm)
        result = leftTerm + rightTerm
        # print("ADD result", result)
        return result
    
class AndNode(Node):
    def compute(self, setsize=[]):
        leftTerm = self.left.compute(setsize=setsize)
        rightTerm = self.right.compute(setsize=setsize)
        # print("MUL", leftTerm, rightTerm)
        result = leftTerm * rightTerm
        # print("MUL result", result)
        return result

class ConstantNode(Node):
    def __init__(self, data=None, nodeName=None,  varSet=None, objects=None):
        super(ConstantNode, self).__init__()
        self.data = data
        self.varSet = varSet
        self.nodeName = nodeName
        self.objects = objects

    def compute(self, setsize=[]):
        # print(self.data, self.nodeName, self.varSet, self.objects)
        # objects.update({node + var : (domains[dom.strip()], domType, without)})

        exponent = 1
        setsizes = []
        for var in self.varSet:
            key = self.nodeName + var
            domain, domType, without = self.objects[key]
            if domType == "bot":
                exponent *= setsize[1]
            elif domType == "top":
                exponent *= setsize[0]
            else:
                exponent *= (len(domain) - int(without != ''))

        print(self.nodeName, exponent)
        if self.data == "or":
            leftTerm = sum(self.left.compute(setsize=setsize).data)
            rightTerm = sum(self.right.compute(setsize=setsize).data)
            result = Term(Pow(leftTerm + rightTerm, exponent))
        elif self.data == "and":
            leftTerm = sum(self.left.compute(setsize=setsize).data)
            rightTerm = sum(self.right.compute(setsize=setsize).data)
            result = Term(Pow(leftTerm * rightTerm, exponent))
        else:
            leftTerm = sum(self.left.compute(setsize=setsize).data)
            result = Term(Pow(leftTerm, exponent))

        return result
            
class LeafNode(Node):
    def __init__(self, data=None, weights=None, algoType=None):
        super(LeafNode, self).__init__()
        self.data = data
        self.weight = weights[data]
        self.algoType = algoType

    def compute(self, setsize=[]):
        if type(self.weight) == tuple:
            return Term(self.weight[0], (int(self.weight[1][0]), int(self.weight[1][1])))
        else:
            return Term(self.weight, ())

def CreateNewNode(data=None, var=None, objects=None, weights=None, algoType=None):
    if data == 'and':
        return AndNode()
    elif data == 'or':
        return OrNode()
    elif data == 'A':
        return ForAllNode(var, objects)
    elif data == 'E':
        return ExistsNode(var, objects)
    else:
        return LeafNode(data, weights, algoType)
    
