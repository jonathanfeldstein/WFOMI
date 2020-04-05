from circuit import *
import re

class Parser(object):
    def parseFile(self, name):
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

                newNode = CreateNewNode(data)
                nodes.update({node : newNode})

        root = nodeNumPattern.match(content[0]).group().strip()
        return root, nodes, connections
