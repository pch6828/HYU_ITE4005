import sys

# read input file,
# sort each transaction (to simplify merge)
def input_process(filename):
    file = open(filename)
    txns = [];

    while True:
        line = file.readline()
        if not line:
            break
        txn = list(map(int, line.split('\t')))
        txn.sort()
        txns.append(txn)
    file.close()
    return txns

# get initial frequent pattern set
def get_frequent_1_itemset(txns, min_sup):
    num_txn = len(txns)
    cnt = {}
    patterns = {}
    for txn in txns:
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
def get_candidate(patterns, k):
    size = len(patterns)
    i = 0
    j = 0
    candidates = []
    
    while i < size:
        j = 0
        while j < i:
            fp1 = patterns[i]
            fp2 = patterns[j]
            j+=1
            result = tuple(sorted(list(set(fp1+fp2))))

            if len(result)!=k:
                continue
            flag = 0
            for pattern in patterns:
                cnt = 0
                for item in result:
                    if item in pattern:
                        cnt+=1
                if cnt == k-1:
                    flag+=1
            if flag == k:
                candidates.append(result)
        i+=1
    
    return list(set(candidates))

# check whether candidate is frequent or not
# and gather frequent patterns into one list
def frequent_filter(txns, min_sup, candidates):
    num_txn = len(txns)
    patterns = {}
    cnt = {}
    for txn in txns:
        for pattern in candidates:
            flag = len(pattern)
            for item in pattern:
                if item in txn:
                    flag -= 1

            if flag != 0:
                continue
            
            if not (pattern in cnt):
               cnt[pattern] = 0
            
            cnt[pattern] += 1

    for pattern in cnt:
        if cnt[pattern]/num_txn*100 >= min_sup:
            patterns[pattern] = cnt[pattern]

    return patterns

# master APRIORI process
# using all functions above, it returns all frequent patterns
def APRIORI_process(txns, min_sup, initial_patterns):
    num_txn = len(txns)
    patterns = initial_patterns
    result = {}
    k = 1
    while len(patterns) > 0:
        k+=1
        candidates = get_candidate(list(patterns.keys()), k)
        result.update(patterns)
        patterns = frequent_filter(txns, min_sup, candidates)

    return result

def get_association_rules(txns, frequent_patterns):
    num_txn = len(txns)
    result = []
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
            analysis = (sub1, sub2, support, confidence)
            result.append(analysis)
    
    return result

def set_to_str(item_set):
    formatted = '{'
    for item in item_set:
        formatted+=str(item)
        formatted+=','
    formatted = formatted[:-1]
    formatted += '}'

    return formatted

def output_process(filename, associations):
    file = open(filename, mode='w')
    for assoc in associations:
        line = set_to_str(assoc[0])
        line += '\t'
        line += set_to_str(assoc[1])
        line += '\t'
        line += '%.2f' % (assoc[2])
        line += '\t'
        line += '%.2f' % (assoc[3])
        line += '\n'

        file.write(line)
           
def main(argv):
    if len(argv)<4:
        print('PLEASE, give 3 arguments (minimum support, input filename, output filename)')
        return;
    
    txns = input_process(argv[2])
    frequent_patterns = APRIORI_process(txns, float(argv[1]), get_frequent_1_itemset(txns, float(argv[1])))
    associations = get_association_rules(txns, frequent_patterns)
    output_process(argv[3], associations)

if __name__ == '__main__':
    main(sys.argv)
