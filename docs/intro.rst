.. highlight:: console

This is the documentation for the wfomi solver written in python3.
Wfomi stands for weighted first orde model integration.
The solver implements a novel algorithm based on the work of Jonathan Feldstein.
The solver outperforms the wfomc solver - Forclift as well as wmi solver - pywmi in terms of efficiency and expressiveness. 

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
