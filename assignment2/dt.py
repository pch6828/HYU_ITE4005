import sys
import time
import numpy as np

class DT:
    def __init__(self, mask):
        self.child = {}
        self.attr_idx = None
        self.mask = set()
        self.mask.update(mask)
        self.class_label = None

    def is_leaf(self):
        return len(self.child)==0

    def entropy_of(self, class_labels, data_set):
        entropy = 0
        data_labels = data_set.T[-1]
        for label in class_labels:
            p_i = np.sum(data_labels==label)/data_labels.size
            if p_i==0:
                continue
            entropy += p_i*np.log2(p_i)

        return -entropy

    def entropy_with_attr_of(self, class_labels, data_set, attr_idx):
        entropy = 0
        attr_values = np.unique(data_set.T[attr_idx])

        for attr in attr_values:
            data_subset = data_set[data_set.T[attr_idx]==attr]
            p_i = data_subset.shape[0]/data_set.shape[0]
            entropy += p_i*self.entropy_of(class_labels, data_subset)

        return entropy
    
    def major_label_of(self, class_labels, data_set):
        major_label = None
        max_cnt = 0
        data_labels = data_set.T[-1]
        for label in class_labels:
            cnt = np.sum(data_labels==label)
            if cnt > max_cnt:
                max_cnt = cnt
                major_label = label

        return major_label

    def construct(self, attributes, class_labels, data_set):
        if self.entropy_of(class_labels, data_set) == 0:
            self.class_label = data_set[0][-1]
            return
        
        self.class_label = self.major_label_of(class_labels, data_set)
        if len(self.mask) == attributes.size - 1:
            return

        test_attr_idx = None
        max_info_gain = 0

        for attr_idx in range(attributes.size - 1):
            if attr_idx in self.mask:
                continue
            
            info_gain = self.entropy_of(class_labels, data_set) - self.entropy_with_attr_of(class_labels, data_set, attr_idx)
            if info_gain > max_info_gain:
                max_info_gain = info_gain
                test_attr_idx = attr_idx
        
        new_mask = set()
        new_mask.update(self.mask)
        new_mask.add(test_attr_idx)

        self.attr_idx = test_attr_idx
        attr_values = np.unique(data_set.T[test_attr_idx])
        
        for attr in attr_values:
            data_subset = data_set[data_set.T[test_attr_idx]==attr]
            new_leaf = DT(new_mask)

            new_leaf.construct(attributes, class_labels, data_subset)
            self.child[attr] = new_leaf

    def classify(self, data):
        if self.attr_idx == None:
            return self.class_label
        
        attr = data[self.attr_idx]

        if not (attr in self.child):
            return self.class_label

        return self.child[attr].classify(data)

def input_training_set(filename):
    file = open(filename)
    
    attributes = np.array(file.readline().strip().split('\t'))
    class_labels = []
    training_set = []

    while True:
        line = file.readline()
        if not line:
            break
        data = np.array(line.strip().split('\t'))
        class_labels.append(data[-1])
        training_set.append(data)
    
    training_set = np.array(training_set)
    class_labels = np.unique(class_labels)
    class_labels.sort()
    file.close()
    
    return attributes, class_labels, training_set

def build_decision_tree(attributes, class_labels, training_set):
    decision_tree = DT(set())

    decision_tree.construct(attributes, class_labels, training_set)
    
    return decision_tree

def array_to_str(arr):
    result = ''
    for s in arr:
        result += s
        result += '\t'
    result = result[:-1]
    result += '\n'

    return result

def test_and_output(attributes, decision_tree, test_filename, output_filename): 
    test_file = open(test_filename)
    output_file = open(output_filename, mode='w')

    test_file.readline()
    output_file.write(array_to_str(attributes))

    while True:
        line = test_file.readline()
        if not line:
            break
        data = np.array(line.strip().split('\t'))

        class_label = decision_tree.classify(data)
        data = np.append(data, class_label)
        output_file.write(array_to_str(data))
    
def main(argv):
    if len(argv)<4:
        print('PLEASE, give 3 arguments (training filename, test filename, output filename)')
        return
    attributes, class_labels, training_set = input_training_set(argv[1])
    
    sys.setrecursionlimit(max(attributes.size*10, 10000))
    decision_tree = build_decision_tree(attributes, class_labels, training_set)
    test_and_output(attributes, decision_tree, argv[2], argv[3])

if __name__ == '__main__':
    main(sys.argv)
