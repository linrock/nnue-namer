import hashlib
from multiprocessing import Process, Value
import secrets
import sys

NUM_PROCESSES = 4

if len(sys.argv) != 3:
    print('Usage: ./multi_cpu_nnue_namer.py <nnue_filename> <hex_word_list>')
    sys.exit(0)

def get_nnue_data(nnue_filename):
    with open(nnue_filename, 'rb') as f:
        return bytearray(f.read())

def random_non_functional_edit(nnue_data):
    for i in range(33, 36):  # the
        nnue_data[i] = list(secrets.token_bytes(1))[0]
    for i in range(79, 85):  # traine
        nnue_data[i] = list(secrets.token_bytes(1))[0]

def get_sha256_hash(nnue_data):
    h = hashlib.sha256()
    h.update(nnue_data)
    return h.hexdigest()

def find_variants(nnue_filename, hex_word_list, counter):
    print(f'Searching for {nnue_filename} variants with sha256 matching {len(hex_word_list)} words')
    nnue_data = get_nnue_data(nnue_filename)
    while True:
        random_non_functional_edit(nnue_data)
        sha256 = get_sha256_hash(nnue_data)
        sha256_prefix = sha256[:12]
        with counter.get_lock():
            counter.value += 1
        if any(word in sha256_prefix for word in hex_word_list):
            print(f'Found {sha256_prefix} after {counter.value} tries')
            new_nnue_filename = f'nn-{sha256_prefix}.nnue'
            print(f'Writing nnue data to {new_nnue_filename}')
            with open(new_nnue_filename, 'wb') as f:
                f.write(nnue_data)
        elif counter.value % 100 == 0:
            print(f'Tried {counter.value} times')

nnue_filename = sys.argv[1]
hex_word_list = open(sys.argv[2], 'r').read().strip().split('\n')
counter = Value('i', 0)
processes = [
    Process(target=find_variants, args=(nnue_filename, hex_word_list, counter))
    for i in range(NUM_PROCESSES)
]
for p in processes: p.start()
for p in processes: p.join()
