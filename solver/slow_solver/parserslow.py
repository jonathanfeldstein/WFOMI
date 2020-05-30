# from circuit import *
from circuitslow import *
from sympy.parsing.sympy_parser import parse_expr
import re


class Parser(object):
    def parseCircuit(self, name, weights, domains, algoType):
        # print("parsing file:", name)

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

            # parse the connection line like 'n0 -> n1' else parse the node line
            if matchLink is not None:
                matchData = nodeDataPattern.match(line[matchNum.end() + 3:])  # +3 for the _->, space+arrow
                node1 = matchNum.group().strip()
                node2 = matchData.group().strip()
                connections.append((node1, node2))
            else:
                matchData = nodeDataPattern.match(line[matchNum.end():])
                node = matchNum.group().strip()
                data = matchData.group().strip()
                if data.find("(") != -1:
                    data = data[0:data.find("(")]

                # parse the existential or univesal node
                if data == 'A' or data == 'E':
                    varSet = line[line.find("{") + 1:line.find("}")].split(",")
                    without = []
                    if len(line[line.find("}") + 2:-2].split("/")) > 1:
                        domainSet, without = line[line.find("}") + 2:-2].split("/")
                        domainSet, without = domainSet.split(","), without.split(",")
                    else:
                        domainSet = line[line.find("}") + 2:-2].split(",")

                    domainType = ""
                    if len(domainSet[0].split("-")) > 1:
                        domainSet, domainType = domainSet[0].split("-")
                        domainSet = [domainSet]

                    objects = {}
                    for dom, var in zip(domainSet, varSet):
                        objects.update({var: (domains[dom], domainType, without)})

                # parse the constant node and add it to the list of nodes.
                elif data == 'C':
                    varSet = line[line.find("{") + 1:line.find("}")].split(",")
                    line = line[line.find("}") + 2:]

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
                        objects.update({node + var: (domains[dom.strip()], domType, without)})

                    line = line[line.find("}") + 2:]
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

                        nodes.update({leftName: leftNode})
                        nodes.update({rightName: rightNode})
                        nodes.update({node: mainNode})
                        connections.append((node, leftName))
                        connections.append((node, rightName))
                    else:
                        leftData = line.lower().strip()
                        leftData = leftData[0:leftData.find('(')]
                        rightData = rightData[0:rightData.find('(')]
                        leftNode = LeafNode(leftData, weights, algoType)
                        leftName = node + "a"
                        mainNode = ConstantNode("leaf", node, varSet, objects)
                        nodes.update({leftName: leftNode})
                        nodes.update({node: mainNode})
                        connections.append((node, leftName))
                else:
                    var = None
                    objects = None

                # Add the parsed node to the list of all nodes, the constant node is added seperately due to its different construction step
                if data != "C":
                    newNode = CreateNewNode(data, var, objects, weights, algoType)
                    nodes.update({node: newNode})

        root = nodeNumPattern.match(content[0]).group().strip()
        nodes = self.connectNodes(nodes, connections)
        return root, nodes

    # parse weights file.
    # In the weights file there can be 3 types of lines:
    # the domain line eg. 'person = {Alice}'
    # the simple weight line eg. 'pre: [1, 10]', meaning the predicate pre is assigned weight 1 and its negation is assigned weight 10
    # the complex weight line eg. 'bmi(x)fun x**2 + 10 bounds[5, 10]'
    # note that for complex weights the negation weight has to be specified seperately eg. 'neg bmi(x)fun x**2 + 10 bounds[10, 20]'
    # IMPORTANT - the name of the arguments of the weight functions must correspond to the argument names used in the circuit description
    def parseWeights(self, name):
        # print("parsing file:", name)

        with open(name) as f:
            content = f.readlines()

        weights = {}
        domains = {}
        for line in content:
            function = domain = ""
            weight = objects = []

            # if line contains '=' it must be the domain line, parse it accordingly
            if line.find("=") != -1:
                domain = line[0:line.find("=") - 1]
                objects = line[line.find("{") + 1:line.find("}")].split(",")
                domains.update({domain: objects})
            # if line contains ':' it must be the simple weight line
            elif line.find(":") != -1:
                function = line[0:line.find(":")]
                weight = line[line.find("[") + 1:line.find("]")].split(",")
                # const = [1, 1]
                # if line.find('const') != -1:
                #     const = line[line.find('const')+6:-2].split(",")
                weights.update({function: (float(weight[0]))})
                weights.update({"neg " + function: (float(weight[1]))})
            # if line contains 'fun' it must be the complex weight line
            elif line.find("fun") != -1:
                function = line[0:line.find("fun")]
                if function.find('(') != -1:
                    function = function[0:function.find('(')]
                args = line[line.find('(') + 1:line.find(')')].split(",")
                if line.find("bounds") != -1:
                    weight = parse_expr(line[line.find("fun")+4:line.find("bounds")])
                    bounds = list(line[line.find("[") + 1:line.find("]")].split(","))
                    it = iter(bounds)
                    bounds = list(zip(it, it))
                    # const = 1
                    # if line.find('const') != -1:
                    #     const = line[line.find('const')+6:-2]
                    weights.update({function: (weight, bounds, args)})
                else:
                    # if line.find('const') != -1:
                    #     weight = parse_expr(line[line.find("fun")+4:line.find("const")])
                    #     const = line[line.find('const')+6:-2]
                    # else:
                    weight = parse_expr(line[line.find("fun")+4:])
                    weights.update({function: weight})

        return weights, domains

    def connectNodes(self, nodes, connections):
        for node1, node2 in connections:
            if nodes[node1].left is None:
                nodes[node1].left = nodes[node2]
            elif nodes[node1].right is None:
                nodes[node1].right = nodes[node2]
        return nodes
