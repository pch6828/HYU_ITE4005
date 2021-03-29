import sys
import time
import numpy as np

def input_training_set(filename):
    file = open(filename)
    training_set = []
    file.close()
    return training_set

def build_decision_tree(training_set):
    decision_tree = []
    return decision_tree

def test_and_output(decision_tree, test_filename, output_filename):
    test_file = open(test_filename)
    output_file = open(output_filename, mode='w')
    pass

def main(argv):
    if len(argv)<4:
        print('PLEASE, give 3 arguments (training filename, test filename, output filename)')
        return

    training_set = input_training_set(argv[1])
    decision_tree = build_decision_tree(training_set)
    test_and_output(decision_tree, argv[2], argv[3])

if __name__ == '__main__':
    main(sys.argv)
