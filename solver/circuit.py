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
        
    def compute(self, setsize=[], removed=[]):
        domain, domType, without = self.objects[self.var]
        domain = list(set(domain) - set(without))
        
        if setsize == []:
            setsize = [len(domain), len(domain)]
        
        if domType == 'bot':
            exponent = setsize[1]
        elif domType == 'top':
            exponent = setsize[0]
        else:
            exponent = len(domain)
        
        term = self.left.compute(setsize=setsize, removed=removed)
        result = term.integrate()
        return Term(Pow(result, (exponent)))
    
    def maxDomainSize(self):
        domain, _, without = self.objects[self.var]
        return (len(list(set(domain) - set(without))), without)
    
class ExistsNode(Node):
    def __init__(self, var=None, objects=None):
        super(ExistsNode, self).__init__()
        self.var = var
        self.objects = objects
        
    def compute(self, setsize=[], removed=[]):
        domain, _, without = self.objects[self.var]
        domain = list(set(domain) - set(without))

        maxSize, removed = self.left.maxDomainSize()

        if setsize == []:
            setsize = [maxSize, maxSize, maxSize]
            
        result = Term(0)
        
        for i in range(0, maxSize+1):
            coeff = Term(binomial(maxSize, i))
            compute = self.left.compute(setsize=[i, setsize[0]-i, maxSize], removed=removed)
            result += coeff * compute
        return result

    def maxDomainSize(self):
        domain, _, without = self.objects[self.var]
        return (len(list(set(domain) - set(without))), without)

class OrNode(Node):
    def compute(self, setsize=[], removed=[]):
        leftTerm = self.left.compute(setsize=setsize, removed=removed)
        rightTerm = self.right.compute(setsize=setsize, removed=removed)
        result = leftTerm + rightTerm
        return result
    
    def maxDomainSize(self):
        left = self.left.maxDomainSize()
        right = self.right.maxDomainSize()
        if left[0] > right[0]:
            return (left[0], left[1])
        else:
            return (right[0], right[1])
    
class AndNode(Node):
    def compute(self, setsize=[], removed=[]):
        leftTerm = self.left.compute(setsize=setsize, removed=removed)
        rightTerm = self.right.compute(setsize=setsize, removed=removed)
        result = leftTerm * rightTerm
        return result
    
    def maxDomainSize(self):
        left = self.left.maxDomainSize()
        right = self.right.maxDomainSize()
        if left[0] > right[0]:
            return (left[0], left[1])
        else:
            return (right[0], right[1])
        
class ConstantNode(Node):
    def __init__(self, data=None, nodeName=None,  varSet=None, objects=None):
        super(ConstantNode, self).__init__()
        self.data = data
        self.varSet = varSet
        self.nodeName = nodeName
        self.objects = objects

    def compute(self, setsize=[], removed=[]):
        if setsize == []:
            domain, _, _ = self.objects[self.nodeName + 'X']
            setsize = [len(domain), len(domain), len(domain)]
            
        exponent = 1
        for var in self.varSet:
            key = self.nodeName + var
            domain, domType, without = self.objects[key]
                
            dec = 0
            if var != 'X' and 'X' in without or var != 'Y' and 'Y' in without:
                dec = 1

            without = set(without) - set(['X', 'Y'])
            without = (without - set(removed))

            if domType == "bot":
                dom = max(0, setsize[1] - len(without))
            elif domType == "top":
                dom = max(0, setsize[0] - len(without))
            else:
                dom = max(0, setsize[2] - len(without))
                
            if dom - dec < 1 and exponent - dec >= 0:
                exponent -= dec
                exponent *= dom
            else:
                exponent *= max(0, dom - dec)

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

    def maxDomainSize(self):
        domSize = 0
        for var in self.varSet:
            key = self.nodeName + var
            domain, _, without = self.objects[key]
            if len(list(set(domain) - set(without))) > domSize:
                domSize = len(list(set(domain) - set(without)))
        return (domSize, without)
            
class LeafNode(Node):
    def __init__(self, data=None, weights=None, algoType=None):
        super(LeafNode, self).__init__()
        self.data = data
        self.weight = weights[data]
        self.algoType = algoType

    def compute(self, setsize=[], removed=[]):
        if type(self.weight) == tuple:
            return Term(self.weight[0], (int(self.weight[1][0]), int(self.weight[1][1])))
        else:
            return Term(self.weight, ())

    def maxDomainSize(self):
        return 0

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
    
