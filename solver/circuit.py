from sympy import *
from term import *

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
        
    def compute(self, setsize=None):
        term = self.left.compute()
        result = term.integrate()
        return Term(Pow(result, len(self.objects[self.var])), ())
    
class ExistsNode(Node):
    def __init__(self, var=None, objects=None):
        super(ExistsNode, self).__init__()
        self.var = var
        self.objects = objects
        
    def compute(self, setsize=None):
        if setsize == None:
            setsize = len(self.objects[self.var])
        d = Symbol('d')
        return Sum(Mul(binomial(setsize, d), self.left.compute(setsize=d)[0]), (d, 1, setsize))

class OrNode(Node):
    def compute(self, setsize=None):
        leftTerm = self.left.compute()
        rightTerm = self.right.compute()
        # print("ADD", leftTerm, rightTerm)
        result = leftTerm + rightTerm
        # print("ADD result", result)
        return result
    
class AndNode(Node):
    def compute(self, setsize=None):
        leftTerm = self.left.compute()
        rightTerm = self.right.compute()
        # print("MUL", leftTerm, rightTerm)
        result = leftTerm * rightTerm
        # print("MUL result", result)
        return result
        
class LeafNode(Node):
    def __init__(self, data=None, weights=None, algoType=None):
        super(LeafNode, self).__init__()
        self.data = data
        self.weight = weights[data]
        self.algoType = algoType

    def compute(self, setsize=None):
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
    
