run with python3 main.py circuit1_filename circuit2_filename weight_filename algo_type

where circuit 1 represents the partition circuit so the one on the entire theory
and circuit 2 represents the query circuit
algo_type = 0 or 1, 0 -> slow algorithm, 1 -> fast, hashing algorithm

eg.
python3 main.py test_input/diabetes/theory.txt test_input/diabetes/query.txt test_input/diabetes/weights_simple.txt 0

