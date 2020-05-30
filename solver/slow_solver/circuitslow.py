from sympy import *
from sympy.abc import *
from termslow import *
import numpy as np

"""The nodes represent the nodes of the cicuit
each node has a compute class which follows the computation step of the algorithm for the given node
the maxDomainSize is used to compute the maximum domain size for the existential node"""


class Node(object):
    def __init__(self, left=None, right=None):
        self.left = left
        self.right = right

    def compute(self):
        raise NotImplementedError("Subclass must implement abstract method")


class ForAllNode(Node):
    def __init__(self, var=None, objects=None):
        super().__init__()
        self.var = var
        self.objects = objects

    def compute(self, setsize=None, removed=None):
        domain, domType, without = self.objects[self.var]
        domain = list(set(domain) - set(without))

        if setsize is None:
            setsize = [len(domain), len(domain)]

        if domType == 'bot':
            exponent = setsize[1]
        elif domType == 'top':
            exponent = setsize[0]
        else:
            exponent = len(domain)

        term = self.left.compute(setsize=setsize, removed=removed)
        result = term.integrate()
        return Term([result.wfs[0] ** exponent], [{}])

    def maxDomainSize(self):
        domain, _, without = self.objects[self.var]
        return len(list(set(domain) - set(without))), without


class ExistsNode(Node):
    def __init__(self, var=None, objects=None):
        super().__init__()
        self.var = var
        self.objects = objects

    def compute(self, setsize=None, removed=None):
        maxSize, removed = self.left.maxDomainSize()

        if setsize is None:
            setsize = [maxSize, maxSize, maxSize]

        result = Term([1], [{}])

        for i in range(0, maxSize + 1):
            coeff = Term([1], [{}], [binomial(maxSize, i)])
            compute = self.left.compute(setsize=[i, setsize[0] - i, maxSize], removed=removed)
            result += coeff * compute
        return result

    def maxDomainSize(self):
        domain, _, without = self.objects[self.var]
        return len(list(set(domain) - set(without))), without


class OrNode(Node):
    def compute(self, setsize=None, removed=None):
        leftTerm = self.left.compute(setsize=setsize, removed=removed)
        rightTerm = self.right.compute(setsize=setsize, removed=removed)
        return leftTerm + rightTerm

    def maxDomainSize(self):
        left = self.left.maxDomainSize()
        right = self.right.maxDomainSize()
        if left[0] > right[0]:
            return left[0], left[1]
        else:
            return right[0], right[1]


class AndNode(Node):
    def compute(self, setsize=None, removed=None):
        leftTerm = self.left.compute(setsize=setsize, removed=removed)
        rightTerm = self.right.compute(setsize=setsize, removed=removed)
        return leftTerm * rightTerm

    def maxDomainSize(self):
        left = self.left.maxDomainSize()
        right = self.right.maxDomainSize()
        if left[0] > right[0]:
            return left[0], left[1]
        else:
            return right[0], right[1]


class ConstantNode(Node):
    def __init__(self, data=None, nodeName=None, varList=None, objects=None):
        super().__init__()
        self.data = data
        self.varList = varList
        self.nodeName = nodeName
        self.objects = objects

    def compute(self, setsize=None, removed=None):
        if setsize is None:
            domain, _, _ = self.objects[self.nodeName + self.varList[0]]
            setsize = [len(domain), len(domain), len(domain)]

        if removed is None:
            removed = []

        exponent = 1
        for var in self.varList:
            key = self.nodeName + var
            domain, domType, without = self.objects[key]

            dec = 0
            for otherVar in self.varList:
                if var != otherVar and otherVar in without:
                    dec = 1

            without = set(without) - set(self.varList)
            without = (without - set(removed))

            if domType == "bot":
                exponent *= max(0, setsize[1] - len(without))
            elif domType == "top":
                exponent *= max(0, setsize[0] - len(without))
            else:
                exponent *= max(0, setsize[2] - len(without))
            exponent = max(0, exponent - dec)

        if self.data == "or":
            leftTerm = self.left.compute(setsize=setsize)
            rightTerm = self.right.compute(setsize=setsize)
            result = leftTerm + rightTerm
        elif self.data == "and":
            leftTerm = self.left.compute(setsize=setsize)
            rightTerm = self.right.compute(setsize=setsize)
            result = leftTerm * rightTerm
        else:
            result = self.left.compute(setsize=setsize)

        result = result.integrate()
        return Term([1], [{}], [result.cst[0] ** exponent])

    def maxDomainSize(self):
        domSize = 0
        without = None
        for var in self.varList:
            key = self.nodeName + var
            domain, _, without = self.objects[key]
            if len(list(set(domain) - set(without))) > domSize:
                domSize = len(list(set(domain) - set(without)))
        return domSize, without


class LeafNode(Node):
    def __init__(self, data=None, weights=None, algoType=None):
        super().__init__()
        self.data = data
        self.weight = weights[data]
        self.algoType = algoType

    def compute(self, setsize=None, removed=None):
        if type(self.weight) == tuple:
            if len(self.weight) > 2:
                wfs = [sympify(self.weight[0])]
                args = [sympify(arg) for arg in self.weight[2]]
                bounds = [list(bound) for bound in self.weight[1]]
                bounds = [dict(zip(args, bounds))]
                result = Term(wfs, bounds)
                return result
            else:
                return Term([sympify(self.weight[0])], [{}])
        else:
            return Term([sympify(self.weight)], [{}])

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


