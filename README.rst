Intro
===========

| The repository for the wfomi solver written in python3.
Wfomi stands for weighted first order model integration.
The solver implements a novel algorithm based on the work of Jonathan Feldstein.
The solver outperforms the wfomc solver - Forclift as well as wmi solver - pywmi in terms of efficiency and expressiveness. 

How to run it
===========

To run the solver, change directory to the solver folder and call:

.. code-block:: console
				
   python3 pywfomi.py [circuit1_filename] [circuit2_filename] [weight_filename]
   
without the brackets and with the intended filenames

| circuit 1 represents the partition circuit so the one containing the entire theory
| circuit 2 represents the query circuit
| weights represent the simple and complex weights corresponding to predicates appearing the circuits of interest

Example call would look like this:

.. code-block:: console
				
   python3 pywfomi.py test_input/smokers/theory.txt test_input/smokers/query.txt test_input/smokers/weights_simple.txt

The docs folder contains this documentation.
The test_input folder contains examples that can be run to test the software.


Input files
===========

The solver requires two kinds of input files.
The two files representing the circuits, the theory circuit and the query circuit and the one file representing the weights of the predicates occuring in the two cicuits. In this section we present the syntax of these files. The default parser included in the solver works with the here explained file formats, however it should be easy to extend or introduce new parsers for different file formats. 


Weights files
-----------

The weights file contains the weights corresponding to the predicates included in the circuit files.
In the weights file there can be 3 types of lines:
| the domain line eg. ‘person = {Alice}’
| the simple weight line eg. ‘pre: [1, 1] const[1, 10]’, meaning the predicate pre is assigned weight 1*1 and its negation is assigned weight 1*10
| the complex weight line eg. ‘bmi(x)fun x**2 + 10 bounds[5, 10] const[1, 10]’
Note that for complex weights the negation weight has to be specified seperately eg. ‘neg bmi(x)fun x**2 + 10 bounds[10, 20]’.
The name of the arguments of the weight functions must correspond to the argument names used in the circuit description.
The const[1, 5] indicates the constant multiplier on the weight function and if omitted defaults to 1. This is used for computational speed up. 

An example of the weights file follows. Additional examples can be found in test_input folder.

.. code-block:: console

   person = {Guy, Nima, Wannes, Jesse, Luc}
   friends: [0.1, 0.9]
   smokes(b)fun -0.001*(b-27)**2+0.3  bounds[35, 45] 
   neg smokes(b)fun -0.001*(b-27)**2+0.3  bounds[10, 35] 
   f_1: [7.38905609893065, 1]

Cicuit files
-----------
   
The circuit files contain the theory and query circuits.
There are two types of lines in the circuit file, one corresponding to the contents of the given node and the other indicating the connections between nodes. These lines can be intermixed but for readibility it is customary to first write the contents lines and then the connections lines. 
The lines always begin with the nX eg. n1 where X indicates the unique node number which is used to identify it.

The contens lines are then followed by the description of the node. This can be a connective 'and', 'or', a leaf including the given predicate eg. 'smokes(x)', a quantifier eg. A{x}{persons} or a constant C{x}{persons}. The quantifier and constant lines are of the form Z{x}{persons}, where Z can be A or E indicating a universal or existentiar quantifiers. The first braces store the variable(s) that is quantified over and the second braces store the domain of the variable. If the node quantifies over more than one variable they are listed seperated by commas and so are the domains like: C{x, y}{persons, animals}. Moreover if the domain of the quantifier is constrained not to include a given object we denote it by E{x}{persons/Alice} where persons normally include Alice. Futhermore the type of the domain can be included, eg. if a given quantifier is a descendant of an existential quantifier it must refer to one of the splits of the original domain induced by the existential. Those splits are reffered to as top and bot and are indicated like: A{x}{persons-bot} 

The connections lines are of the form nX -> xY, eg. n0 -> n1 indicating n1 is the child of n0.

An example of the circuit file follows. Additional examples can be found in test_input folder.

.. code-block:: console

   n23 and
   n0  C{X}{person} friends(X,X) or neg friends(X,X) 
   n22 E{x}{person}
   n21 and
   n1  C{X,Y}{person-bot/Y, person-bot} friends(X,Y) or neg friends(X,Y) 
   n20 and
   n2  C{X,Y}{person/Y, person-top} friends(X,Y) or neg friends(X,Y) 
   n19 and
   n3  C{X}{person-top} smokes(X) 
   n18 and
   n4  C{X,Y}{person, person-top} f_1(X,Y) 
   n17 and
   n5  C{X}{person-bot} neg smokes(X) 
   n16 and
   n6  C{X,Y}{person-bot, person-bot} f_1(X,Y) 
   n15 A{x}{person-top}
   n14 A{y}{person-bot}
   n13 or
   n9 and
   n7  f_1(x,y)
   n8  neg friends(x,y)
   n12 and
   n10  neg f_1(x,y)
   n11  friends(x,y)
   n23 -> n0;
   n23 -> n22;
   n22 -> n21;
   n21 -> n1;
   n21 -> n20;
   n20 -> n2;
   n20 -> n19;
   n19 -> n3;
   n19 -> n18;
   n18 -> n4;
   n18 -> n17;
   n17 -> n5;
   n17 -> n16;
   n16 -> n6;
   n16 -> n15;
   n15 -> n14;
   n14 -> n13;
   n13 -> n9;
   n13 -> n12;
   n9 -> n7;
   n9 -> n8;
   n12 -> n10;
   n12 -> n11;

  
