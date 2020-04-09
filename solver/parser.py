from circuit import *
from sympy.parsing.sympy_parser import parse_expr
import re

class Parser(object):
    def parseCircuit(self, name, weights, domains, algoType):
        print("parsing file:", name)
        
        nodeNumPattern = re.compile('\s*n\d*', re.IGNORECASE)
        nodeDataPattern = re.compile('\s*\w*\s*\w*\(*\w*\)*', re.IGNORECASE) 

        linkPattern = re.compile('\s*n\d*\s->', re.IGNORECASE)
        
        with open(name) as f:
            content = f.readlines()
            
        connections = []
        nodes = {}

        for line in content:
            matchLink = linkPattern.match(line)
            matchNum = nodeNumPattern.match(line)
            if matchLink != None:
                matchData = nodeDataPattern.match(line[matchNum.end()+3:-1]) #+3 for the _->, space+arrow
                node1 = matchNum.group().strip()
                node2 = matchData.group().strip()
                connections.append((node1, node2))
            else:
                matchData = nodeDataPattern.match(line[matchNum.end():-1])
                node = matchNum.group().strip()
                data = matchData.group().strip()

                if data == 'A' or data == 'E':
                    varSet = line[line.find("{")+1:line.find("}")].split(",")
                    without = []
                    if len(line[line.find("}")+2:-2].split("/")) > 1:
                        domainSet, without = line[line.find("}")+2:-2].split("/")
                        domainSet, without = domainSet.split(","), without.split(",")
                    else:
                        domainSet = line[line.find("}")+2:-2].split(",")
                    objects = {}
                    for dom, var in zip(domainSet, varSet):
                        members = [x for x in domains[dom] if x not in without]
                        objects.update({var : members})
                else:
                    var = None
                    objects = None

                newNode = CreateNewNode(data, var, objects, weights, algoType)
                nodes.update({node : newNode})

        root = nodeNumPattern.match(content[0]).group().strip()
        nodes = self.connectNodes(nodes, connections)
        return root, nodes

    def parseWeights(self, name):
        print("parsing file:", name)

        with open(name) as f:
            content = f.readlines()

        weights = {}
        domains = {}
        for line in content:
            function = domain = ""
            weight = objects = []
                
            if line.find("=") != -1:
                domain = line[0:line.find("=")-1]
                objects = line[line.find("{")+1:line.find("}")].split(",")
                domains.update({domain : objects})
            elif line.find(":") != -1:
                function = line[0:line.find(":")]
                weight = line[line.find("[")+1:line.find("]")].split(",")
                weights.update({function : float(weight[0])})
                weights.update({"neg " + function : float(weight[1])})
                for item in domains.items():
                    for elem in item[1]:
                        weights.update({function.replace('x', elem) : float(weight[0])})
                        weights.update({"neg " + function.replace('x', elem) : float(weight[1])})
            elif line.find("fun") != -1:
                function = line[0:line.find("fun")]
                weight = parse_expr(line[line.find("fun")+4:line.find("bounds")])
                if line.find("bounds") != -1:
                    bounds = line[line.find("[")+1:line.find("]")].split(",")
                    weights.update({function : (weight, bounds[0:2])})
                    weights.update({"neg " + function : (weight, bounds[2:4])})
                    for item in domains.items():
                        for elem in item[1]:
                            weights.update({function.replace('x', elem) : (weight, bounds[0:2])})
                            weights.update({"neg " + function.replace('x', elem) : (weight, bounds[2:4])})
                else:
                    # weight = line[line.find("fun")+4:-1]
                    weights.update({function : weight})
                    for item in domains.items():
                        for elem in item[1]:
                            weights.update({function.replace('x', elem) : weight})
        return weights, domains

    def connectNodes(self, nodes, connections):
        for node1, node2 in connections:
            if nodes[node1].left == None:
                nodes[node1].left = nodes[node2]
            elif nodes[node1].right == None:
                nodes[node1].right = nodes[node2]
        return nodes
