from parser import *
from circuit import *

import sys

def main():
    filename = sys.argv[1]
    parser = Parser()
    root, nodes, connections = parser.parseFile(filename)

    for node1, node2 in connections:
        # print(node1, node2)
        if nodes[node1].left == None:
            nodes[node1].left = nodes[node2]
        elif nodes[node1].right == None:
            nodes[node1].right = nodes[node2]
            
    print(nodes[root].compute())

if __name__ == "__main__":
    main()
