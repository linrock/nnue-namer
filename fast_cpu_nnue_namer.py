import hashlib
from multiprocessing import cpu_count, Process, Value
import secrets
import sys

if len(sys.argv) != 3:
    print('Usage: ./cpu_nnue_namer.py <nnue_filename> <hex_word_list>')
    sys.exit(0)

def get_nnue_data(nnue_filename):
    with open(nnue_filename, 'rb') as f:
        return bytearray(f.read())

def random_non_functional_edit(nnue_data):
    for i in range(33, 36):  # the
        nnue_data[i] = list(secrets.token_bytes(1))[0]
    for i in range(79, 85):  # traine
        nnue_data[i] = list(secrets.token_bytes(1))[0]

def find_variants(nnue_filename, hex_word_list, counter):
    print(f'Searching for {nnue_filename} variants with sha256 matching {len(hex_word_list)} words')
    nnue_data = get_nnue_data(nnue_filename)
    while True:
        nnue_data_copy = nnue_data.copy()
        random_non_functional_edit(nnue_data_copy)
        h = hashlib.sha256()
        h.update(nnue_data_copy[:-12])
        # minimally functional edits to last byte
        for last_12 in range(38, 45):         # 26 to 2c
            nnue_data_copy[-12] = last_12
            for last_9 in range(206, 211):        # ce to d2
                nnue_data_copy[-9] = last_9
                for last_4 in range(16, 32):      # 10 to 20
                    nnue_data_copy[-4] = last_4
                    for last_1 in range(78, 91):  # 4e to 5a
                        nnue_data_copy[-1] = last_1
                        h2 = h.copy()
                        h2.update(nnue_data_copy[-12:])
                        sha256 = h2.hexdigest()
                        sha256_prefix = sha256[:12]
                        with counter.get_lock():
                            counter.value += 1
                        if any(sha256_prefix.startswith(word) for word in hex_word_list):
                            print(f'Found {sha256_prefix} after {counter.value} tries')
                            new_nnue_filename = f'nn-{sha256_prefix}.nnue'
                            print(f'Writing nnue data to {new_nnue_filename}')
                            with open(new_nnue_filename, 'wb') as f:
                                f.write(nnue_data_copy)
                        elif counter.value % 100_000 == 0:
                            print(f'Tried {counter.value} times')

nnue_filename = sys.argv[1]
hex_word_list = open(sys.argv[2], 'r').read().strip().split('\n')
counter = Value('i', 0)
processes = [
    Process(target=find_variants, args=(nnue_filename, hex_word_list, counter))
    for i in range(cpu_count() - 1)
]
for p in processes: p.start()
for p in processes: p.join()
