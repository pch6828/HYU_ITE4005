import sys
import time
from os import path
import numpy as np
import pandas as pd

# Recommender System Class (Matrix Multiplication)
class Recommender:
    # Constructor
    def __init__(self, rating_matrix, factor, learning_rate, regularization):
        self.rating_matrix = rating_matrix.values
        self.idx = np.array(self.rating_matrix.nonzero()).T
        self.n = self.idx.size

        self.num_user = rating_matrix.shape[0]
        self.num_item = rating_matrix.shape[1]
        self.factor = factor
        self.regularization = regularization
        
        self.learning_rate = learning_rate

        self.user_idx_map = {}
        self.item_idx_map = {}

        idx = 0
        for user_id in rating_matrix.index:
            self.user_idx_map[user_id] = idx
            idx+=1

        idx = 0
        for item_id in rating_matrix.columns:
            self.item_idx_map[item_id] = idx
            idx+=1
    
    # Training Function
    # using Gradient Descent
    def train(self, num_iterations = 50):
        self.U = np.random.normal(scale=0.1, size=(self.num_user, self.factor))
        self.V = np.random.normal(scale=0.1, size=(self.num_item, self.factor))

        self.U_bias = np.zeros(self.num_user)
        self.V_bias = np.zeros(self.num_item)

        self.bias = self.rating_matrix[self.rating_matrix != 0].mean()

        for _ in range(num_iterations):
            np.random.shuffle(self.idx)
            for user_id, item_id in self.idx:
                predicted_rating = self.predict(user_id, item_id)
                rating = self.rating_matrix[user_id][item_id]

                error = rating - predicted_rating

                self.U_bias[user_id] += self.learning_rate * (error - self.regularization * self.U_bias[user_id])
                self.V_bias[item_id] += self.learning_rate * (error - self.regularization * self.V_bias[item_id])

                dU = error * self.V[item_id] - self.regularization * self.U[user_id]
                dV = error * self.U[user_id] - self.regularization * self.V[item_id]
                
                self.U[user_id] += self.learning_rate * dU
                self.V[item_id] += self.learning_rate * dV

    # prediction function for single user-item pair   
    def predict(self, user_id, item_id):
        return self.bias + self.U_bias[user_id] + self.V_bias[item_id] + np.dot(self.U[user_id], self.V[item_id])

    # test function
    def test(self, test_dataset):
        result = []
        predicted_matrix = self.bias + np.array([self.U_bias]).T + np.array([self.V_bias]) + np.dot(self.U, self.V.T)
        
        for _, row in test_dataset.iterrows():
            user_id = row['user_id']
            item_id = row['item_id']

            predicted_rating = None

            if user_id in self.user_idx_map:
                user_idx = self.user_idx_map[user_id]
                if item_id in self.item_idx_map:
                    item_idx = self.item_idx_map[item_id]

                    predicted_rating = min(5, max(1, predicted_matrix[user_idx][item_idx]))
                else:
                    predicted_rating = min(5, max(1, predicted_matrix[user_idx].mean()))
            else:
                predicted_rating = self.bias

            result.append(predicted_rating)
        
        return result

# read input file(training file, test file)
# it is just wrapper or pandas read_csv
# it adds some column names
def read_data(filename):
    df = pd.read_csv(filename, 
                     sep='\t', 
                     header=None, 
                     names=['user_id', 'item_id', 'rating', 'timestamp'])

    return df

# write test result to output file
def output_process(filename, test_dataset, test_result):
    file = open(filename, mode='w')
    
    for idx, row in test_dataset.iterrows():
        file.write(str(row['user_id']))
        file.write('\t')
        file.write(str(row['item_id']))
        file.write('\t')
        file.write(str(test_result[idx]))
        file.write('\n')

def main(argv):
    if len(argv)<3:
        print('PLEASE, give 2 arguments (train filename, test filename)')
        return

    train_dataset = read_data(argv[1])
    test_dataset = read_data(argv[2])

    rating_matrix = pd.pivot_table(train_dataset, 
                                   index='user_id', 
                                   columns='item_id', 
                                   values='rating').fillna(0)
    
    recommender = Recommender(rating_matrix, 10, 0.005, 0.05)
    start_time = time.time()
    recommender.train()
    end_time = time.time()
    print('Training Time : ', end_time-start_time)
    
    start_time = time.time()
    test_result = recommender.test(test_dataset)
    output_process('./' + path.splitext(path.basename(argv[2]))[0]+'.base_prediction.txt', test_dataset, test_result)
    end_time = time.time()
    print('Test and Output Time : ', end_time-start_time)

if __name__ == '__main__':
    main(sys.argv)
