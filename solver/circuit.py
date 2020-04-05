class Node(object):
    def __init__(self, left=None, right=None):
        self.left = left
        self.right = right

    def compute(self):
        raise NotImplementedError("Subclass must implement abstract method")

class ForAllNode(Node):
     def compute(self):
        print("for all")

class ExistsNode(Node):
     def compute(self):
        print("exists")

class OrNode(Node):
    def compute(self):
        print("or")

class AndNode(Node):
    def compute(self):
        print("and")

class LeafNode(Node):
    def __init__(self, data=None):
        super(LeafNode, self).__init__()
        self.data = data
    def compute(self):
        print(self.data)

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
