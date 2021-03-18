import sys
import time
from bisect import bisect_left

# read input file,
# sort each transaction (to simplify merge)
def input_process(filename):
    file = open(filename)
    TDB = []

    while True:
        line = file.readline()
        if not line:
            break
        txn = list(map(int, line.split('\t')))
        txn.sort()
        TDB.append(txn)
    file.close()
    return TDB

# binary search in sorted list
def search(arr, x):
    idx = bisect_left(arr, x)
    return idx!=len(arr) and arr[idx]==x

def having(A, B):
    i = 0
    size = len(A)
    for item in B:
        while True:
            if i == size or A[i] > item:
                return False
            elif A[i] == item:
                i+=1    
                break
            elif A[i] < item:
                i+=1
    return True
        

# get initial frequent pattern set
def get_frequent_1_itemset(TDB, min_sup):
    num_txn = len(TDB)
    cnt = {}
    patterns = {}
    for txn in TDB:
        for item_id in txn:
            if not ((item_id,) in cnt):
               cnt[(item_id,)] = 0
            cnt[(item_id,)] += 1

    for pattern in cnt:
        if cnt[pattern]/num_txn*100 >= min_sup:
            patterns[pattern] = cnt[pattern]

    return patterns

# get candidate for frequent pattern
# k is candidate's length
# self merge is used
def get_candidate(frequent_patterns, k):
    size = len(frequent_patterns)
    i = 0
    j = 0
    candidates = []
    
    while i < size:
        j = 0
        while j < i:
            fp1 = frequent_patterns[i]
            fp2 = frequent_patterns[j]
            j+=1
            merged_pattern = tuple(sorted(list(set(fp1+fp2))))

            if len(merged_pattern)!=k:
                continue
            flag = 0
            for pattern in frequent_patterns:
                if having(merged_pattern, pattern):
                    flag+=1
            if flag == k:
                candidates.append(merged_pattern)
        i+=1
    
    return list(set(candidates))

# check whether candidate is frequent or not
# and gather frequent patterns into one list
def frequent_filter(TDB, min_sup, candidates):
    num_txn = len(TDB)
    frequent_patterns = {}
    cnt = {}
    for txn in TDB:
        for pattern in candidates:
            if not having(txn, pattern):
                continue
            
            if not (pattern in cnt):
               cnt[pattern] = 0
            
            cnt[pattern] += 1

    for pattern in cnt:
        if cnt[pattern]/num_txn*100 >= min_sup:
            frequent_patterns[pattern] = cnt[pattern]

    return frequent_patterns

# master APRIORI process
# using all functions above, it returns all frequent patterns
def APRIORI_process(TDB, min_sup):
    now_frequent_set = get_frequent_1_itemset(TDB, min_sup)
    frequent_patterns = {}
    k = 1
    while len(now_frequent_set) > 0:
        k+=1
        candidates = get_candidate(list(now_frequent_set.keys()), k)
        frequent_patterns.update(now_frequent_set)
        now_frequent_set = frequent_filter(TDB, min_sup, candidates)

    return frequent_patterns

# get association rules from frequent_patterns
# using bitmask to find all possible subsets
def get_association_rules(TDB, frequent_patterns):
    num_txn = len(TDB)
    association_rules = []
    for pattern in frequent_patterns:
        for bitmask in range(1<<len(pattern)):
            loop = 0
            sub1 = ()
            sub2 = ()
            while loop < len(pattern) :
                if bitmask % 2 == 1:
                    sub1+=(pattern[loop],)
                else:
                    sub2+=(pattern[loop],)
                bitmask //= 2
                loop+=1
            if len(sub1)==0 or len(sub2)==0:
                continue
            support = frequent_patterns[pattern]/num_txn*100
            confidence = frequent_patterns[pattern]/frequent_patterns[sub1]*100
            association = (sub1, sub2, support, confidence)
            association_rules.append(association)
    
    return association_rules

# formatting function for item set
def set_to_str(item_set):
    formatted = '{'
    for item in item_set:
        formatted+=str(item)
        formatted+=','
    formatted = formatted[:-1]
    formatted += '}'

    return formatted

#write output file
def output_process(filename, association_rules):
    file = open(filename, mode='w')
    for association in association_rules:
        line = set_to_str(association[0])
        line += '\t'
        line += set_to_str(association[1])
        line += '\t'
        line += '%.2f' % (association[2])
        line += '\t'
        line += '%.2f' % (association[3])
        line += '\n'

        file.write(line)
    file.close()
           
def main(argv):
    if len(argv)<4:
        print('PLEASE, give 3 arguments (minimum support, input filename, output filename)')
        return
    
    TDB = input_process(argv[2])
    start = time.time()
    frequent_patterns = APRIORI_process(TDB, float(argv[1]))
    association_rules = get_association_rules(TDB, frequent_patterns)
    print('Apriori Time:', time.time()-start)
    output_process(argv[3], association_rules)

if __name__ == '__main__':
    main(sys.argv)
