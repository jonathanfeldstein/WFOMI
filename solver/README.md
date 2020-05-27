run with python3 main.py circuit1_filename circuit2_filename weight_filename

where circuit 1 represents the partition circuit so the one on the entire theory
and circuit 2 represents the query circuit

eg. python3 main.py test_input/diabetes/theory.txt test_input/diabetes/query.txt test_input/diabetes/weights_simple.txt

The weight file
In the weights file there can be 3 types of lines:
the domain line eg. 'person = {Alice}'
the simple weight line eg. 'pre: [1, 10]', meaning the predicate pre is assigned weight 1 and its negation is assigned weight 10
the complex weight line eg. 'bmi(x)fun x**2 + 10 bounds[5, 10]'
note that for complex weights the negation weight has to be specified seperately eg. 'neg bmi(x)fun x**2 + 10 bounds[10, 20]'
IMPORTANT - the name of the arguments of the weight functions must correspond to the argument names used in the circuit description