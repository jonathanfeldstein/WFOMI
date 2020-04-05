from sympy import *

class Node(object):
    def __init__(self, left=None, right=None):
        self.left = left
        self.right = right

    def compute(self):
        raise NotImplementedError("Subclass must implement abstract method")

class ForAllNode(Node):
     def compute(self):
         # f = self.left.compute() # assume that a univsersal can only have one child
         # x = Symbol('x')
         # return integrate(f, (x, 0, 10))
         return self.left.compute()
     
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

def CreateNewNode(data):
    if data == 'and':
        return AndNode()
    elif data == 'or':
        return OrNode()
    elif data == 'A':
        return ForAllNode()
    elif data == 'E':
        return ExistsNode()
    else:
        return LeafNode(data)


bmi = Symbol('BMI(x)')
diab = Add(Mul(bmi, Pow(10, -1)), -1)
negDiab = Add(8, Mul(-bmi, Pow(10, -1)))
wBmi = Symbol('w(BMI(x))')
notWbmi = Symbol('!w(BMI(x))')
x = Symbol('x')
w = {'f_1(x)' : 10, 'neg f_1(x)' : 1, 'diabetes(x)' : diab, 'neg diabetes(x)' : negDiab, 'BMI(x)' : wBmi, 'neg BMI(x)' : notWbmi}

def weight(data):
    return w[data]
