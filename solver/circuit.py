from sympy import *
from sympy.abc import *
from term import *

"""The nodes represent the nodes of the cicuit
each node has a compute class which follows the computation step of the algorithm for the given node
the maxDomainSize is used to compute the maximum domain size for the existential node"""

class Node(object):
    """The base class defining a node, all other nodes inherit from it"""
    def __init__(self, left=None, right=None):
        self.left = left
        self.right = right

    def compute(self):
        raise NotImplementedError("Subclass must implement abstract method")
    def maxDomainSize(self):
        """used to compute the maximum domain size for the existential node"""
        raise NotImplementedError("Subclass must implement abstract method")

class ForAllNode(Node):
    def __init__(self, var=None, domData=None):
        """initialises the universal node with the variables it quantifies over and the data on the domain that 
           the variables correspond to"""
        super().__init__()
        self.var = var
        self.domData = domData

    def compute(self, domSize=None, removed=None):
        """computes the numerical value at the universal node based on the size of the domain it quantifies over taking into account the 
        objects that have been removed from it"""
        domain, domType, without, _ = self.domData[self.var]
        domain = list(set(domain) - set(without))

        if domSize is None:
            domSize = [len(domain), len(domain)]

        if domType == 'bot':
            exponent = domSize[1]
        elif domType == 'top':
            exponent = domSize[0]
        else:
            exponent = len(domain)

        term = self.left.compute(domSize=domSize, removed=removed)
        result = term.integrate()
        return Term([1], [{}], [result.const[0]**exponent])

    def maxDomainSize(self):
        """used to compute the maximum domain size for the existential node"""
        domain, _, without, _ = self.domData[self.var]
        return len(list(set(domain) - set(without))), without

class ExistsNode(Node):
    def __init__(self, var=None, domData=None):
        """initialises the existential node with the variables it quantifies over and the data on the corresponding domains"""
        super().__init__()
        self.var = var
        self.domData = domData

    def compute(self, domSize=None, removed=None):
        """computes the symbolic value at the existential node based on the size of the domain it quantifies over and taking into account the
        objects removed from it"""
        maxSize, removed = self.left.maxDomainSize()

        if domSize is None:
            domSize = [maxSize, maxSize, maxSize]

        result = Term([1], [{}], [0])

        for i in range(0, maxSize + 1):
            coeff = Term([1], [{}], [binomial(maxSize, i)])
            compute = self.left.compute(domSize=[i, domSize[0] - i, maxSize], removed=removed)
            result += coeff * compute
        return result

    def maxDomainSize(self):
        """used to compute the maximum domain size for the existential node"""
        domain, _, without = self.domData[self.var]
        return len(list(set(domain) - set(without))), without

class OrNode(Node):
    def compute(self, domSize=None, removed=None):
        """computes the symbolic value at the or node by adding two terms at its child nodes, the setsize and removed are passed for potential 
        existential and universals that may be the node's descendants"""
        leftTerm = self.left.compute(domSize=domSize, removed=removed)
        rightTerm = self.right.compute(domSize=domSize, removed=removed)
        return leftTerm + rightTerm

    def maxDomainSize(self):
        """used to compute the maximum domain size for the existential node"""
        left = self.left.maxDomainSize()
        right = self.right.maxDomainSize()
        if left[0] > right[0]:
            return left[0], left[1]
        else:
            return right[0], right[1]

class AndNode(Node):
    def compute(self, domSize=None, removed=None):
        """computes the symbolic value at the and node by multiplying two terms at its child nodes. the domSize and removed are passed for 
        potential existential and universals that may be the node's descendants"""
        leftTerm = self.left.compute(domSize=domSize, removed=removed)
        rightTerm = self.right.compute(domSize=domSize, removed=removed)
        return leftTerm * rightTerm

    def maxDomainSize(self):
        """used to compute the maximum domain size for the existential node"""
        left = self.left.maxDomainSize()
        right = self.right.maxDomainSize()
        if left[0] > right[0]:
            return left[0], left[1]
        else:
            return right[0], right[1]

class ConstNode(Node):
    def __init__(self, data=None, nodeName=None, varList=None, domData=None):
        """initialises the constant node with the data representing the type of a constant node it is (and, or, leaf), the nodeName used 
        as a key in a dictionary storing the domains of the nodes, the varList representing the list of variables the constant node deals 
        with and domSize which is the dictionary storing the domains of the nodes it quantifies over and the objects in the corresponding 
        domains"""
        super().__init__()
        self.data = data
        self.varList = varList
        self.nodeName = nodeName
        self.domData = domData
        self.shouldIntegrate = True

    def compute(self, domSize=None, removed=None):
        """Computes the symbolic value at the constant node depending on its type"""
        if domSize is None:
            domain, _, _ = self.domData[self.nodeName + self.varList[0]]
            domSize = [len(domain), len(domain), len(domain)]

        if removed is None:
            removed = []

        exponent = 1
        for var in self.varList:
            key = self.nodeName + var
            domain, domType, without = self.domData[key]

            dec = 0
            for otherVar in self.varList:
                if var != otherVar and otherVar in without:
                    dec = 1

            without = set(without) - set(self.varList)
            without = (without - set(removed))

            if domType == "bot":
                exponent *= max(0, domSize[1] - len(without))
            elif domType == "top":
                exponent *= max(0, domSize[0] - len(without))
            else:
                exponent *= max(0, domSize[2] - len(without))
            exponent = max(0, exponent - dec)

        if self.data == "or":
            leftTerm = self.left.compute(domSize=domSize)
            rightTerm = self.right.compute(domSize=domSize)
            result = leftTerm + rightTerm
        elif self.data == "and":
            leftTerm = self.left.compute(domSize=domSize)
            rightTerm = self.right.compute(domSize=domSize)
            result = leftTerm * rightTerm
        else:
            result = self.left.compute(domSize=domSize)

        if self.shouldIntegrate:
            result = result.integrate()
            return Term([1], [{}], [result.const[0]**exponent])
        else:
            return result
    
    def maxDomainSize(self):
        """used to compute the maximum domain size for the existential node"""
        domSize = 0
        without = None
        for var in self.varList:
            key = self.nodeName + var
            domain, _, without = self.domData[key]
            if len(list(set(domain) - set(without))) > domSize:
                domSize = len(list(set(domain) - set(without)))
        return domSize, without


class LeafNode(Node):
    def __init__(self, data=None, weights=None):
        super().__init__()
        self.data = data
        self.weight = weights[data]

    def compute(self, domSize=None, removed=None):
        """computes the symbolic value at the leaves depending on weather the corresponding weight is a float or a function"""
        if type(self.weight) == tuple:
            if len(self.weight) > 2:
                wfs = [sympify(self.weight[0])]
                args = [sympify(arg) for arg in self.weight[2]]
                const = int(self.weight[3])
                bounds = [list(bound) for bound in self.weight[1]]
                bounds = [dict(zip(args, bounds))]
                result = Term(wfs, bounds, [const])
                return result
            else:
                return Term([sympify(self.weight[0])], [{}], [self.weight[1]])
        else:
            return Term([sympify(self.weight)], [{}], [1])

    def maxDomainSize(self):
        """used to compute the maximum domain size for the existential node"""
        return 0


def CreateNewNode(data=None, var=None, objects=None, weights=None):
    if data == 'and':
        return AndNode()
    elif data == 'or':
        return OrNode()
    elif data == 'A':
        return ForAllNode(var, objects)
    elif data == 'E':
        return ExistsNode(var, objects)
    else:
        return LeafNode(data, weights)

 
