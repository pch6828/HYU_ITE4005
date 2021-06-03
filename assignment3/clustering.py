from pathlib import Path
import sys
import time
from collections import deque
import numpy as np
import pandas as pd

# get distance of two points
def distance(p1, p2):
    v = p1-p2
    return np.sqrt(np.dot(v, v))

# DBSCAN clustering algorithm class
class DBSCAN:
    # Constructor
    def __init__(self, N, EPS, MinPTS):
        self.N = N
        self.EPS = EPS
        self.MinPTS = MinPTS

        self.adjacent_list = {}
    
    # read data and make adjacency list with this data
    def set_data(self, filename):
        start_time = time.time()
        data_set = pd.read_csv(filename, 
                               sep='\t', 
                               header=None).values

        sort_idx = data_set.T[1].argsort()
        data_set = data_set[sort_idx]

        points = []
        for obj in data_set:
            obj_id = int(obj[0])
            obj_point = np.array([obj[1], obj[2]])
            self.adjacent_list[obj_id] = []

            for neighbor_obj in reversed(points):
                neighbor_id = neighbor_obj[0]
                neighbor_point = neighbor_obj[1]
                if obj_point[0] - neighbor_point[0]  > self.EPS:
                    break

                if distance(obj_point, neighbor_point) <= self.EPS:
                    self.adjacent_list[obj_id].append(neighbor_id)
                    self.adjacent_list[neighbor_id].append(obj_id)
            
            points.append((obj_id, obj_point))
            
        end_time = time.time()
        print('Data Handling Time :', end_time - start_time)

    # Get cluster 
    # with BFS algorithm
    def get_clusters(self):
        clusters = []
        
        visited = set()
        queue = deque([])
        start_time = time.time()
        for obj_id in self.adjacent_list:
            if obj_id in visited or len(self.adjacent_list[obj_id]) + 1 < self.MinPTS:
                continue

            now_cluster = [obj_id]
            visited.add(obj_id)
            queue.append(obj_id)

            while queue:
                now = queue.popleft()
                
                for nxt in self.adjacent_list[now]:
                    if not (nxt in visited):
                        visited.add(nxt)
                        now_cluster.append(nxt)
                        if len(self.adjacent_list[nxt]) + 1 >= self.MinPTS:
                            queue.append(nxt)

            clusters.append(now_cluster)

        while len(clusters) < self.N:
            clusters.append([])
        
        clusters.sort(key=lambda x:len(x), reverse=True)

        while len(clusters) > self.N:
            del clusters[-1]
        
        end_time = time.time()
        
        print('Traning Time :', end_time - start_time)
        return clusters

# write clustering result to output file
def output_process(file_prefix, clusters, n):
    for cluster_id in range(n):
        cluster = []
        if cluster_id < len(clusters):
            cluster = clusters[cluster_id]
        filename = file_prefix+'_cluster_'+str(cluster_id)+'.txt'
        file = open(filename, mode='w')

        for obj_id in cluster:
            file.write(str(obj_id))
            file.write('\n')

        file.close()
    
def main(argv):
    if len(argv)<5:
        print('PLEASE, give 4 arguments (input filename, N, EPS, MinPTS)')
        return

    file_prefix = Path(argv[1]).stem
    
    dbscan = DBSCAN(int(argv[2]), float(argv[3]), int(argv[4]))
    
    start_time = time.time()
    dbscan.set_data(argv[1])
    clusters = dbscan.get_clusters()
    end_time = time.time()
    
    print('DBSCAN Time :', end_time - start_time)

    output_process(file_prefix, clusters, int(argv[2]))

if __name__ == '__main__':
    main(sys.argv)