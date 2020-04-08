from sympy import *
from sympy.stats import Normal, density 

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
        return Pow(self.left.compute(), len(self.objects)).evalf()
    
class ExistsNode(Node):
    def __init__(self, var=None, objects=None):
        super(ExistsNode, self).__init__()
        self.var = var
        self.objects = objects
        
    def compute(self, setsize=None):
        if setsize == None:
            #TODO: correction needed for the setsize - not len(objects) but use second input
            setsize = len(self.objects)
        d = Symbol('d')
        return Sum(Mul(binomial(setsize, d), self.left.compute(setsize=d)), (d, 1, setsize)).evalf()

class OrNode(Node):
    def compute(self, setsize=None):
        return Add(self.left.compute(), self.right.compute())

class AndNode(Node):
    def compute(self, setsize=None):
        return Mul(self.left.compute(), self.right.compute())

class LeafNode(Node):
    def __init__(self, data=None, weights=None):
        super(LeafNode, self).__init__()
        self.data = data
        self.weight = weights[data]
        
    def compute(self, setsize=None):
        return self.weight

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


# x = Symbol('x')
# bmi = Normal(x, 27, 36)
# diab = 10# Add(Mul(Symbol('bmi(x)'), Pow(10, -1)), -1)
# negDiab = 1# Add(8, Mul(-Symbol('bmi(x)'), Pow(10, -1)))
# wBmi = 0.2# integrate(density(bmi)(x), (x, 35, 45))
# notWbmi = 0.8# integrate(density(bmi)(x), (x, 10, 35))

# w = {'f_1(x)' : 10, 'neg f_1(x)' : 1, 'diabetes(x)' : diab, 'neg diabetes(x)' : negDiab, 'BMI(x)' : wBmi, 'neg BMI(x)' : notWbmi}
