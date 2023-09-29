### NNUE namer

So you've [trained a NNUE](https://github.com/official-stockfish/nnue-pytorch)
and want to name it. Well, you've come to the right place.

```
Usage: ./fast_cpu_nnue_namer.py <nnue_filename> <hex_word_list> <core_count>
```

Naming works by:

- making non-functional edits to a comment string in the file header
- making edits in the output layer bytes without changing `bench`
- saving nets where the sha256 hash prefix matches a list of hex words
