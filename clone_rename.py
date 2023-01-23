import hashlib
import os
import secrets
import sys

if len(sys.argv) != 3:
    print('Usage: ./clone_rename.py <nnue_filename> <sha256_prefix>')
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

nnue_filename = sys.argv[1]
sha256_prefix = sys.argv[2]

print(f'Finding {nnue_filename} version with sha256 prefix: {sha256_prefix}')
nnue_data = get_nnue_data(nnue_filename)
sha256 = get_sha256_hash(nnue_data)
num_tries = 0
while not sha256.startswith(sha256_prefix):
    random_non_functional_edit(nnue_data)
    sha256 = get_sha256_hash(nnue_data)
    num_tries += 1
    if num_tries % 100 == 0:
        print(f'Tried {num_tries} times')

print(f'Found {sha256} after {num_tries} tries')
new_nnue_filename = f'nn-{sha256[:12]}.nnue'
print(f'Writing data to {new_nnue_filename}')
with open(new_nnue_filename, 'wb') as f:
    f.write(nnue_data)
