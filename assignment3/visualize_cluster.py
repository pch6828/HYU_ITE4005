import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def get_points_map(filename):
    data_set = pd.read_csv(filename, 
                           sep='\t', 
                           header=None).values

    points = {}

    for obj in data_set:
        obj_id = obj[0]
        obj_point = np.array([obj[1], obj[2]])
        points[obj_id] = obj_point

    return points

def get_cluster_points(filename, points):
    file = open(filename)
    X = []
    Y = []

    while True:
        line = file.readline()
        if not line:
            break

        obj_id = int(line)
        X.append(points[obj_id][0])
        Y.append(points[obj_id][1])

        del points[obj_id]
    
    return X, Y

def get_outliers(points):
    X = []
    Y = []

    for outlier_id in points:
        outlier = points[outlier_id]
        X.append(outlier[0])
        Y.append(outlier[1])

    return X, Y

def main(argv):
    if len(argv) < 3:
        print('PLEASE, give 2 arguments (input files, N)')
        return

    input_filename = argv[1]+'.txt'
    points = get_points_map(input_filename)
    
    fig, ax = plt.subplots()
    for idx in range(int(argv[2])):
        cluster_filename = argv[1]+'_cluster_'+str(idx)+'.txt'
        X, Y = get_cluster_points(cluster_filename, points)
        ax.scatter(X, Y, s=0.5)
    X, Y = get_outliers(points)
    ax.scatter(X, Y, s=0.5, c = 'black', marker='^')
    plt.show()

if __name__ == '__main__':
    main(sys.argv)
