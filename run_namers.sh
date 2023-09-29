#!/bin/bash

if [ $# -ne 1 ]; then
  echo "Usage: ./run_namers.sh <nnue_filename>"
  exit 0
fi

nnue=$1
num_workers=$(( $(nproc) - 1 ))

for core in $(seq 0 $(( $num_workers - 1 ))); do
  taskset -c $core python3 fast_cpu_nnue_namer.py $nnue hexword-list.txt 1 &
done

wait
