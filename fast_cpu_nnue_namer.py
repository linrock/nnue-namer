import hashlib
from multiprocessing import cpu_count, Process, RawValue
from ctypes import c_ulonglong
import random
import re
import string
import sys
from time import sleep, time

if len(sys.argv) < 3:
    print('Usage: ./cpu_nnue_namer.py <nnue_filename> <hex_word_list> <core_count>')
    sys.exit(0)


CHARS = [ord(c) for c in string.ascii_uppercase + string.ascii_lowercase + string.digits]
ALPHANUMERIC_STRING = r"^[a-z0-9]+$"


def get_nnue_data(nnue_filename):
    with open(nnue_filename, 'rb') as f:
        return bytearray(f.read())

def random_non_functional_edit(nnue_data):
    nnue_data[12:26] = [random.choice(CHARS) for c in range(14)]

def matches_hex_word_list(hex_word_list, sha256_prefix):
    for word in hex_word_list:
        if re.match(ALPHANUMERIC_STRING, sha256_prefix) and sha256_prefix.startswith(word):
            return True
        elif re.match(word, sha256_prefix):
            return True
    return False

def find_variants(nnue_filename, hex_word_list, counter):
    print(f'Searching for {nnue_filename} variants with sha256 matching {len(hex_word_list)} words')
    nnue_data = get_nnue_data(nnue_filename)
    BOUNDARY = -39
    while True:
        nnue_data_copy = nnue_data.copy()
        random_non_functional_edit(nnue_data_copy)
        h = hashlib.sha256()
        h.update(nnue_data_copy[:BOUNDARY])
        # non-functional edits to bytes near the end of the file
        for hex1 in range(1, 256):
            nnue_data_copy[-37] = hex1
            for hex2 in range(1, 256):
                nnue_data_copy[-38] = hex2
                h2 = h.copy()
                h2.update(nnue_data_copy[BOUNDARY:])
                sha256 = h2.hexdigest()
                sha256_prefix = sha256[:12]
                counter.value += 1
                if matches_hex_word_list(hex_word_list, sha256_prefix):
                    print(f'Found {sha256_prefix} after {counter.value:,} tries')
                    new_nnue_filename = f'nn-{sha256_prefix}.nnue'
                    print(f'Writing nnue data to {new_nnue_filename}')
                    with open(new_nnue_filename, 'wb') as f:
                        f.write(nnue_data_copy)

def print_stats(counter):
    t0 = time()
    while True:
        sleep(10)
        hashes_per_second = int(counter.value / (time() - t0))
        print(f'Tried {counter.value:,} times ({hashes_per_second:,} hashes/s)')

nnue_filename = sys.argv[1]
hex_word_list = open(sys.argv[2], 'r').read().strip().split('\n')
core_count = int(sys.argv[3]) if len(sys.argv) == 4 else cpu_count() - 1
print(f"naming {nnue_filename} with {core_count} cores")

counter = RawValue(c_ulonglong, 0)
processes = [
    Process(target=find_variants, args=(nnue_filename, hex_word_list, counter))
    for i in range(core_count)
]
for p in processes: p.start()
stats_printer = Process(target=print_stats, args=(counter,))
stats_printer.start()

for p in processes: p.join()
stats_printer.join()
