The weights file contains the weights corresponding to the predicates included in the circuit files.
In the weights file there can be 3 types of lines:
| the domain line eg. ‘person = {Alice}’
| the simple weight line eg. ‘pre: [1, 1] const[1, 10]’, meaning the predicate pre is assigned weight 1*1 and its negation is assigned weight 1*10
| the complex weight line eg. ‘bmi(x)fun x**2 + 10 bounds[5, 10] const[1, 10]’
Note that for complex weights the negation weight has to be specified seperately eg. ‘neg bmi(x)fun x**2 + 10 bounds[10, 20]’.
The name of the arguments of the weight functions must correspond to the argument names used in the circuit description.
The const[1, 5] indicates the constant multiplier on the weight function and if omitted defaults to 1. This is used for computational speed up. 

An example of the weights file follows. Additional examples can be found in test_input folder.

.. literalinclude:: ../solver/test_input/smokers/weights_complex.txt
   :linenos:
