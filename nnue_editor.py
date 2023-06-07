import hashlib
from multiprocessing import cpu_count, Process, Value
import secrets
import sys
from time import time

if len(sys.argv) != 2:
    print('Usage: ./nnue_editor.py <nnue_filename>')
    sys.exit(0)

def get_nnue_data(nnue_filename):
    with open(nnue_filename, 'rb') as f:
        return bytearray(f.read())

def random_non_functional_edit(nnue_data):
    for i in range(33, 36):  # the
        nnue_data[i] = list(secrets.token_bytes(1))[0]
    for i in range(79, 85):  # traine
        nnue_data[i] = list(secrets.token_bytes(1))[0]

def edit_nnue_file(nnue_filename):
    t0 = time()
    print(f'Editing {nnue_filename}')
    nnue_data = get_nnue_data(nnue_filename)
    nnue_data_copy = nnue_data.copy()
    # random_non_functional_edit(nnue_data_copy)
    h = hashlib.sha256()

    nnue_data_copy[-37] = 255
    nnue_data_copy[-38] = 255

    nnue_data_copy[-69] = 255
    nnue_data_copy[-70] = 255

    nnue_data_copy[-101] = 255
    nnue_data_copy[-102] = 255

    h.update(nnue_data_copy)
    sha256 = h.hexdigest()
    sha256_prefix = sha256[:12]
    new_nnue_filename = f'nn-{sha256_prefix}.nnue'
    print(f'Writing nnue data to {new_nnue_filename}')
    with open(new_nnue_filename, 'wb') as f:
        f.write(nnue_data_copy)

nnue_filename = sys.argv[1]
edit_nnue_file(nnue_filename)
