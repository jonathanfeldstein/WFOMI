from circuit import *
from sympy.parsing.sympy_parser import parse_expr
import re


class Parser(object):
    def parseCircuit(self, name, weights, domains, algoType):
        print("parsing file:", name)
        
        nodeNumPattern = re.compile('\s*n\d*', re.IGNORECASE)
        nodeDataPattern = re.compile('\s*\w*\s*\w*\(*\w*,*\w*\)*', re.IGNORECASE) 

        linkPattern = re.compile('\s*n\d*\s->', re.IGNORECASE)
        
        with open(name) as f:
            content = f.readlines()
            
        connections = []
        nodes = {}
        maxDomainSize = 0

        for line in content:
            matchLink = linkPattern.match(line)
            matchNum = nodeNumPattern.match(line)
            if matchLink != None:
                matchData = nodeDataPattern.match(line[matchNum.end()+3:]) #+3 for the _->, space+arrow
                node1 = matchNum.group().strip()
                node2 = matchData.group().strip()
                connections.append((node1, node2))
            else:
                matchData = nodeDataPattern.match(line[matchNum.end():])
                node = matchNum.group().strip()
                data = matchData.group().strip()
                if data.find("(") != -1:
                    data = data[0:data.find("(")]
                
                if data == 'A' or data == 'E':
                    varSet = line[line.find("{")+1:line.find("}")].split(",")
                    without = []
                    if len(line[line.find("}")+2:-2].split("/")) > 1:
                        domainSet, without = line[line.find("}")+2:-2].split("/")
                        domainSet, without = domainSet.split(","), without.split(",")
                    else:
                        domainSet = line[line.find("}")+2:-2].split(",")

                    domainType = ""
                    if len(domainSet[0].split("-")) > 1:
                        domainSet, domainType = domainSet[0].split("-")
                        domainSet = [domainSet]

                    objects = {}
                    for dom, var in zip(domainSet, varSet):
                        objects.update({var : (domains[dom], domainType, without)})

                elif data == 'C':
                    varSet = line[line.find("{")+1:line.find("}")].split(",")
                    line = line[line.find("}")+2:]

                    doms = line[0:line.find("}")].split(",")
                    objects = {}
                    without = []
                    domainSet = []
                    domainTypeSet = []
                    withoutSet = []
                    for dom in doms:
                        if len(dom.split("/")) > 1:
                            domainType, without = dom.split("/")
                            without = without.split("+")
                            withoutSet.append(without)
                            if len(domainType.split("-")) > 1:
                                d, domainType = domainType.split("-")
                                domainSet.append(d)
                            else:
                                domainSet.append(domainType)
                            domainTypeSet.append(domainType)
                        else:
                            if len(dom.split("-")) > 1:
                                d, domainType = dom.split("-")
                                domainSet.append(d)
                                domainTypeSet.append(domainType)
                            else:
                                d = dom.split(",")
                                domainSet.append(d[0])
                                domainTypeSet.append("")
                            withoutSet.append("")

                    for dom, var, domType, without in zip(domainSet, varSet, domainTypeSet, withoutSet):
                        objects.update({node + var : (domains[dom.strip()], domType, without)})

                    line = line[line.find("}")+2:]
                    if line.find("or") != -1 or line.find("and") != -1:
                        if line.find("or") != -1:
                            leftData, rightData = line.split("or")
                            mainNode = ConstantNode("or", node, varSet, objects)
                        else:
                            leftData, rightData = line.split("and")
                            mainNode = ConstantNode("and", node, varSet, objects)
                        leftData = leftData.lower().strip()
                        rightData = rightData.lower().strip()

                        leftData = leftData[0:leftData.find('(')]
                        rightData = rightData[0:rightData.find('(')]
                        leftNode = LeafNode(leftData, weights, algoType)
                        rightNode = LeafNode(rightData, weights, algoType)
                        leftName = node + "a"
                        rightName = node + "b"

                        nodes.update({leftName : leftNode})
                        nodes.update({rightName : rightNode})
                        nodes.update({node : mainNode})
                        connections.append((node, leftName))
                        connections.append((node, rightName))
                    else:
                        leftData = line.lower().strip()
                        leftData = leftData[0:leftData.find('(')]
                        rightData = rightData[0:rightData.find('(')]
                        leftNode = LeafNode(leftData, weights, algoType)
                        leftName = node + "a"
                        mainNode = ConstantNode("leaf", node, varSet, objects)
                        nodes.update({leftName : leftNode})
                        nodes.update({node : mainNode})
                        connections.append((node, leftName))
                                                
                else:
                    var = None
                    objects = None

                if data != "C":
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
                if function.find('(') != -1:
                    function = function[0:function.find('(')]
                weight = line[line.find("[")+1:line.find("]")].split(",")
                weights.update({function : float(weight[0])})
                weights.update({"neg " + function : float(weight[1])})
                for item in domains.items():
                    for elem in item[1]:
                        weights.update({function.replace('x', elem) : float(weight[0])})
                        weights.update({"neg " + function.replace('x', elem) : float(weight[1])})
            elif line.find("fun") != -1:
                function = line[0:line.find("fun")]
                if function.find('(') != -1:
                    function = function[0:function.find('(')]
                weight = parse_expr(line[line.find("fun")+4:line.find("bounds")])
                if line.find("bounds") != -1:
                    bounds = tuple(line[line.find("[")+1:line.find("]")].split(","))
                    weights.update({function : (weight, bounds)})
                    for item in domains.items():
                        for elem in item[1]:
                            weights.update({function.replace('x', elem) : (weight, bounds)})
                else:
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
