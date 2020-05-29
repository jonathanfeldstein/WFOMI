The circuit files contain the theory and query circuits.
There are two types of lines in the circuit file, one corresponding to the contents of the given node and the other indicating the connections between nodes. These lines can be intermixed but for readibility it is customary to first write the contents lines and then the connections lines. 
The lines always begin with the nX eg. n1 where X indicates the unique node number which is used to identify it.

The contens lines are then followed by the description of the node. This can be a connective 'and', 'or', a leaf including the given predicate eg. 'smokes(x)', a quantifier eg. A{x}{persons} or a constant C{x}{persons}. The quantifier and constant lines are of the form Z{x}{persons}, where Z can be A or E indicating a universal or existentiar quantifiers. The first braces store the variable(s) that is quantified over and the second braces store the domain of the variable. If the node quantifies over more than one variable they are listed seperated by commas and so are the domains like: C{x, y}{persons, animals}. Moreover if the domain of the quantifier is constrained not to include a given object we denote it by E{x}{persons/Alice} where persons normally include Alice. Futhermore the type of the domain can be included, eg. if a given quantifier is a descendant of an existential quantifier it must refer to one of the splits of the original domain induced by the existential. Those splits are reffered to as top and bot and are indicated like: A{x}{persons-bot} 

The connections lines are of the form nX -> xY, eg. n0 -> n1 indicating n1 is the child of n0.

An example of the circuit file follows. Additional examples can be found in test_input folder.

.. literalinclude:: ../solver/test_input/smokers/theory.txt
   :linenos:
