from pathlib import Path
import sys
import time
from collections import deque
import numpy as np
import pandas as pd

def distance(p1, p2):
    v = p1-p2
    return np.sqrt(np.dot(v, v))

class DBSCAN:
    def __init__(self, N, EPS, MinPTS):
        self.N = N
        self.EPS = EPS
        self.MinPTS = MinPTS

        self.adjacent_list = {}
    
    def set_data(self, filename):
        data_set = pd.read_csv(filename, 
                     sep='\t', 
                     header=None).values

        points = {}

        for obj in data_set:
            obj_id = int(obj[0])
            obj_point = np.array([obj[1], obj[2]])
            self.adjacent_list[obj_id] = []

            for neighbor_id in points:
                neighbor_point = points[neighbor_id]

                if distance(obj_point, neighbor_point) <= self.EPS:
                    self.adjacent_list[obj_id].append(neighbor_id)
                    self.adjacent_list[neighbor_id].append(obj_id)
            
            points[obj_id] = obj_point
    
    def get_clusters(self):
        clusters = []
        
        visited = set()
        queue = deque([])

        for obj_id in self.adjacent_list:
            if obj_id in visited or len(self.adjacent_list[obj_id]) < self.MinPTS:
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
                        if len(self.adjacent_list[nxt]) >= self.MinPTS:
                            queue.append(nxt)

            clusters.append(now_cluster)

        while len(clusters) < self.N:
            clusters.append([])
        
        clusters.sort(key=lambda x:len(x), reverse=True)

        while len(clusters) > self.N:
            del clusters[-1]

        return clusters

def output_process(file_prefix, clusters):
    for cluster_id, cluster in enumerate(clusters):
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

    output_process(file_prefix, clusters)

if __name__ == '__main__':
    main(sys.argv)
