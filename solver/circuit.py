from sympy import *
from sympy.stats import Normal, density
import numpy as np

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
        
    def compute(self):
         return Pow(self.left.compute(), len(self.objects)).evalf()
     
class ExistsNode(Node):
     def compute(self):
         raise NotImplementedError("Existential node is not implemented yet")

class OrNode(Node):
    def compute(self):
        return Add(self.left.compute(), self.right.compute())

class AndNode(Node):
    def compute(self):
        return Mul(self.left.compute(), self.right.compute())

class LeafNode(Node):
    def __init__(self, data=None):
        super(LeafNode, self).__init__()
        self.data = data
    def compute(self):
        return weight(self.data)

def CreateNewNode(data=None, var=None, objects=None):
    if data == 'and':
        return AndNode()
    elif data == 'or':
        return OrNode()
    elif data == 'A':
        return ForAllNode(var, objects)
    elif data == 'E':
        return ExistsNode()
    else:
        return LeafNode(data)


x = Symbol('x')
bmi = Normal(x, 27, 36)
diab = Add(Mul(bmi, Pow(10, -1)), -1)
negDiab = Add(8, Mul(-bmi, Pow(10, -1)))
wBmi = integrate(density(bmi)(x), (x, 35, 45))
notWbmi = integrate(density(bmi)(x), (x, 10, 35))

w = {'f_1(x)' : 10, 'neg f_1(x)' : 1, 'diabetes(x)' : diab, 'neg diabetes(x)' : negDiab, 'BMI(x)' : wBmi, 'neg BMI(x)' : notWbmi}

def weight(data):
    return w[data]
