import random
import sys

def output_process(filename, TDB):
    file = open(filename, mode='w')
    for txn in TDB:
        line = ''
        for item in txn:
            line += str(item)
            line += '\t'
        line = line[:-1]
        line += '\n'
        file.write(line)

    file.close()

def main(argv):
    filename = 'input.txt'
    num_txn = 500
    num_item = 20
    len_txn = 10

    if len(argv)>1:
        filename = argv[1]
    if len(argv)>2:
        num_txn = int(argv[2])
    if len(argv)>3:
        num_item = int(argv[3])
    if len(argv)>4:
        len_txn = int(argv[4])

    txn = list(range(num_item))

    TDB = []

    for _ in range(num_txn):
        random.shuffle(txn)
        TDB.append(txn[:random.randint(1, len_txn)])

    output_process(filename, TDB)
    
if __name__ == '__main__':
    main(sys.argv)