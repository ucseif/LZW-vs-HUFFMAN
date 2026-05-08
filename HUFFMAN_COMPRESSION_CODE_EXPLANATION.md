# Huffman Compression Code Explanation

This file explains in detail the following two files:

- `Huffman/huffman_compression/main.py`
- `Huffman/huffman_compression/text_compression.py`

The explanation covers:

- every function
- every parameter
- every important variable
- the purpose of each imported module
- the meaning of each class
- the internal flow of the code
- why each part exists

This file is intended for project study, review, and discussion preparation.

---

# Part 1: `Huffman/huffman_compression/main.py`

## Full purpose of this file

This file is the main entry point for Huffman compression.

Its role is not to perform the Huffman algorithm itself.

Instead, it is responsible for:

1. importing the helper compression functions
2. selecting the correct function depending on file type
3. printing the result in a readable console form when the file is run directly

So this file acts as a dispatcher and console runner.

---

## Code section 1: imports

```python
try:
    from .bitmap_file import compress_bitmap_file
    from .text_compression import compress_text_file
except ImportError:
    from bitmap_file import compress_bitmap_file
    from text_compression import compress_text_file
```

### Why is `try / except ImportError` used?

Because this file can be used in two ways:

### Case 1: as part of a package

Example:

```python
from Huffman.huffman_compression.main import compress_file
```

Then relative imports like:

```python
from .text_compression import ...
```

work correctly.

### Case 2: run directly as a script

Example:

```bash
python Huffman/huffman_compression/main.py
```

Then relative imports may fail, so the code falls back to:

```python
from text_compression import ...
```

### Imported functions

#### `compress_bitmap_file`

- imported from `bitmap_file.py`
- used for bitmap file compression

#### `compress_text_file`

- imported from `text_compression.py`
- used for text and repetitive file compression

So this file is not the place where Huffman is built.
It simply calls the correct helper.

---

## Code section 2: `compress_file`

```python
def compress_file(file_path, file_type):
```

### Purpose

This function chooses the correct Huffman compression function based on file type.

### Parameters

#### `file_path`

- type: string
- meaning: full path of the file to compress

Example:

```python
"E:\\InfoProject\\sample_text_document.txt"
```

#### `file_type`

- type: string
- allowed values:
  - `"text"`
  - `"repetitive"`
  - `"bitmap"`

This parameter is only for deciding which helper function to call.

### Internal logic

```python
if file_type == "text":
    return compress_text_file(file_path, "text_document")
```

If file type is `text`:

- call the text compression function
- label the file category as `"text_document"`

---

```python
if file_type == "repetitive":
    return compress_text_file(file_path, "highly_repetitive_data_file")
```

If file type is `repetitive`:

- still use the same text compression function
- only change the category label

This is because the algorithm is the same.
The project classification is what changes.

---

```python
if file_type == "bitmap":
    return compress_bitmap_file(file_path)
```

If file type is `bitmap`:

- call the bitmap compression function

---

```python
raise ValueError("file_type must be: text, repetitive, or bitmap")
```

If the file type is invalid:

- raise an error

This prevents unsupported values from passing silently.

---

## Code section 3: `print_result`

```python
def print_result(result):
```

### Purpose

This function prints the Huffman compression result in a readable way for terminal use.

### Parameter

#### `result`

- type: dictionary
- contains the full output returned by Huffman compression

---

```python
print("\nFile Type:")
print(result["file_type"])
```

This prints the file category.

Examples:

- `text_document`
- `highly_repetitive_data_file`
- `bitmap_image`

---

```python
print("\nCode Table Preview:")
preview = result["code_table"][:10]
for row in preview:
    print(row)
if len(result["code_table"]) > 10:
    print("...")
```

### What is `code_table`?

It is the final Huffman code mapping.

Example:

```python
{"symbol": 65, "code": "101"}
```

which means:

- symbol `65`
- gets Huffman code `"101"`

### Why preview only 10 rows?

Because a full code table can be long, especially for files with many different symbols.

So the function prints:

- the first 10 rows only
- then prints `...` if there are more

---

```python
print("\nStatistics:")
for key, value in result["stats"].items():
    print(f"{key}: {value}")
```

This prints all metrics such as:

- `original_size_bytes`
- `compressed_size_bytes`
- `compression_ratio`
- `execution_time_seconds`
- `padding_bits`

### About `.items()`

`dictionary.items()` returns all key-value pairs in a dictionary.

Example:

```python
{"a": 1}.items()
```

gives:

```python
("a", 1)
```

---

```python
print("\nData Structure Efficiency:")
for key, value in result["data_structure_efficiency"].items():
    print(f"{key}: {value}")
```

This prints the descriptive notes about:

- frequency dictionary
- heap priority queue
- code dictionary

---

```python
print("\nCompressed File Path:")
print(result["compressed_file_path"])
```

This prints where the compressed `.huff` file was saved.

---

## Code section 4: direct execution block

```python
if __name__ == "__main__":
```

### Meaning

This is a standard Python pattern.

It means:

- run the code below only when this file is executed directly
- do not run it when the file is imported

---

```python
file_path = input("Enter file path: ").strip()
file_type = input("Enter file type (text / repetitive / bitmap): ").strip().lower()
```

### Explanation

The program asks the user for:

- the file path
- the file type

### About `.strip()`

Removes extra spaces from the beginning and end of the input.

### About `.lower()`

Converts input to lowercase.

Example:

```python
"TEXT".lower() -> "text"
```

This makes input handling more robust.

---

```python
result = compress_file(file_path, file_type)
print_result(result)
```

### Meaning

1. choose the correct compression function
2. run the algorithm
3. print the result

---

# Part 2: `Huffman/huffman_compression/text_compression.py`

## Full purpose of this file

This file contains the real Huffman text compression logic.

Its responsibilities are:

1. read the file as bytes
2. calculate frequencies
3. build the Huffman tree
4. build binary codes for each symbol
5. encode the original file into a bit string
6. pack bits into bytes
7. calculate metrics
8. save the compressed `.huff` file
9. return a structured result

This is the main algorithm file for text-based Huffman compression.

---

## Imports

```python
import heapq
import json
import math
import os
import sys
import time
```

### `heapq`

Used to manage a priority queue implemented as a heap.

This is very important in Huffman because the algorithm repeatedly needs:

- the smallest frequency node
- the second smallest frequency node

### `json`

Used to save the compressed output as JSON inside the `.huff` file.

### `math`

Used for mathematical operations.

In this file it is used in entropy calculation.

### `os`

Used for file path and folder operations.

### `sys`

Used for estimated memory usage with `sys.getsizeof`.

### `time`

Used to measure execution time with `time.perf_counter()`.

---

## Class: `HuffmanNode`

```python
class HuffmanNode:
    def __init__(self, symbol=None, left=None, right=None):
        self.symbol = symbol
        self.left = left
        self.right = right
```

### Purpose

This class represents one node in the Huffman tree.

### Why do we need a class?

Because Huffman coding is based on a tree structure.

Each node must be able to store:

- a symbol, if it is a leaf node
- left child
- right child

### Constructor parameters

#### `symbol`

- default: `None`
- represents the byte/symbol stored in a leaf node

#### `left`

- default: `None`
- left child node

#### `right`

- default: `None`
- right child node

### Attributes created

#### `self.symbol`

- stores the symbol of the node

#### `self.left`

- stores the left child

#### `self.right`

- stores the right child

### Leaf node vs internal node

#### Leaf node

- has a real symbol
- usually has `left = None` and `right = None`

#### Internal node

- has no direct symbol
- has left and right children

---

## Function 1: `build_empty_result`

```python
def build_empty_result(file_path, file_category):
```

### Purpose

Return a default result structure when the input file is empty.

### Parameters

#### `file_path`

- original file path

#### `file_category`

- category label of the file

### Why this function exists

If the file is empty:

- the Huffman algorithm should not continue
- but the program should still return a valid result structure

So this function provides that structure.

### Returned content

- empty frequency table
- empty code table
- zero sizes
- zero ratio
- zero execution time
- empty compressed file path

---

## Function 2: `calculate_entropy`

```python
def calculate_entropy(file_bytes):
```

### Purpose

Calculate Shannon entropy of the original file bytes.

### Parameter

#### `file_bytes`

- bytes object containing the whole original file

### Logic

```python
if not file_bytes:
    return 0
```

Return zero for an empty file.

---

```python
frequencies = {}
for byte in file_bytes:
    frequencies[byte] = frequencies.get(byte, 0) + 1
```

Count how many times each byte appears.

### About `get(byte, 0)`

This returns:

- existing count if the key already exists
- otherwise `0`

Then adds 1.

---

```python
entropy = 0
total = len(file_bytes)
```

- `entropy` accumulates the result
- `total` is total number of bytes

---

```python
for count in frequencies.values():
    probability = count / total
    entropy -= probability * math.log2(probability)
```

This applies the Shannon entropy formula:

```text
H(X) = - Σ p(x) log2 p(x)
```

---

```python
return round(entropy, 6)
```

Rounds the value to 6 decimal places.

---

## Function 3: `build_frequency_table`

```python
def build_frequency_table(file_bytes):
```

### Purpose

Build the frequency dictionary for all symbols in the file.

### Parameter

#### `file_bytes`

- input file bytes

### Logic

```python
frequencies = {}

for byte in file_bytes:
    frequencies[byte] = frequencies.get(byte, 0) + 1

return frequencies
```

### Return value

A dictionary such as:

```python
{
    65: 20,
    66: 5,
    32: 17
}
```

meaning:

- byte `65` appeared 20 times
- byte `66` appeared 5 times
- byte `32` appeared 17 times

This frequency table is the starting point of Huffman coding.

---

## Function 4: `build_huffman_tree`

```python
def build_huffman_tree(frequencies):
```

### Purpose

Build the Huffman tree from the frequency table.

### Parameter

#### `frequencies`

- dictionary mapping each symbol to its count

---

## Step A: create heap

```python
heap = []
order = 0
```

### `heap`

- list used with `heapq`
- represents the priority queue

### `order`

- integer used as a tie-breaker
- important when two symbols have the same frequency

Without it, Python might fail when comparing node objects directly.

---

## Step B: push all leaf nodes into heap

```python
for symbol in sorted(frequencies):
    heapq.heappush(heap, (frequencies[symbol], order, HuffmanNode(symbol=symbol)))
    order += 1
```

### About `sorted(frequencies)`

This sorts the dictionary keys (symbols) so the process is deterministic.

### About `heapq.heappush`

This inserts an element into the min-heap while preserving heap order.

### The pushed tuple

Each heap item is:

```python
(frequency, order, HuffmanNode(...))
```

Why three items?

1. `frequency` -> heap priority
2. `order` -> tie-breaker
3. `HuffmanNode` -> actual node

---

## Step C: special case if only one symbol exists

```python
if len(heap) == 1:
    return heap[0][2]
```

If the file contains only one unique symbol:

- there is no real tree merging process
- just return the only node

`heap[0][2]` means:

- first item in heap
- third element in the tuple
- which is the node itself

---

## Step D: repeatedly merge smallest nodes

```python
while len(heap) > 1:
```

Repeat until only one node remains.

That final node becomes the root of the Huffman tree.

---

```python
left_frequency, _, left_node = heapq.heappop(heap)
right_frequency, _, right_node = heapq.heappop(heap)
```

### About `heapq.heappop`

This removes and returns the smallest item from the heap.

So these two lines extract:

- the smallest frequency node
- the second smallest frequency node

### About `_`

`_` is a common Python placeholder variable.

It means:

- we unpacked a value
- but we do not need to use it

Here `_` receives the `order` value and ignores it.

---

```python
merged_node = HuffmanNode(left=left_node, right=right_node)
```

Create a new internal node whose children are:

- left smallest node
- right smallest node

This node has:

- no direct symbol
- only children

---

```python
heapq.heappush(heap, (left_frequency + right_frequency, order, merged_node))
order += 1
```

Push the merged node back into the heap.

Its frequency becomes:

- sum of left and right frequencies

Then increment `order` for future tie-breaking.

---

```python
return heap[0][2]
```

After the loop ends:

- only one node remains
- that node is the root of the final Huffman tree

---

## Function 5: `build_codes`

```python
def build_codes(node, current_code="", codes=None):
```

### Purpose

Traverse the Huffman tree and assign binary codes to each symbol.

### Parameters

#### `node`

- current Huffman tree node

#### `current_code`

- string representing the path so far
- default is empty string

#### `codes`

- dictionary that stores final symbol -> code mapping
- default is `None`

### Why use `codes=None` instead of `codes={}`?

Because mutable default arguments in Python are risky.

If we wrote:

```python
def f(codes={}):
```

that same dictionary could be reused across calls.

So the safe approach is:

```python
if codes is None:
    codes = {}
```

---

```python
if codes is None:
    codes = {}
```

Initialize the result dictionary if this is the first call.

---

```python
if node.left is None and node.right is None:
    codes[node.symbol] = current_code or "0"
    return codes
```

### Meaning

If both children are `None`, then this node is a leaf node.

That means:

- it represents a real symbol
- assign the accumulated binary code to that symbol

### About `current_code or "0"`

This is important for the special case of a one-symbol file.

If the tree has only one node:

- `current_code` would still be empty
- but the symbol still needs a valid code

So it gets `"0"`.

---

```python
if node.left is not None:
    build_codes(node.left, current_code + "0", codes)
```

Going left means:

- append `"0"` to the code

---

```python
if node.right is not None:
    build_codes(node.right, current_code + "1", codes)
```

Going right means:

- append `"1"` to the code

---

```python
return codes
```

Return the full dictionary after recursive traversal finishes.

### Example output

```python
{
    65: "0",
    66: "101",
    67: "111"
}
```

---

## Function 6: `pack_bits`

```python
def pack_bits(bit_string):
```

### Purpose

Convert a long bit string into a list of packed bytes.

### Parameter

#### `bit_string`

- string containing only `0` and `1`

Example:

```python
"01001101101"
```

### Why needed?

Huffman codes are generated as bits, but files are stored in bytes.

So we need to group bits into chunks of 8.

---

```python
if not bit_string:
    return [], 0
```

If there is no data:

- return empty packed bytes
- return zero padding bits

---

```python
padding_bits = (8 - (len(bit_string) % 8)) % 8
```

### Purpose

Find how many zero bits must be added so the total length becomes divisible by 8.

### Example

If bit string length is 14:

- `14 % 8 = 6`
- need `2` padding bits

### Why the second `% 8`?

If the string length is already divisible by 8:

- `len(bit_string) % 8 = 0`
- then `8 - 0 = 8`

but we actually want `0` padding, not `8`.

So the final `% 8` fixes that.

---

```python
bit_string += "0" * padding_bits
```

Append zero bits for padding.

### Example

If `padding_bits = 3`, then:

```python
"101" * 3 -> "000"
```

The string becomes longer and aligned to 8-bit boundaries.

---

```python
packed_bytes = []
```

This will store each 8-bit group converted to an integer byte.

---

```python
for index in range(0, len(bit_string), 8):
    packed_bytes.append(int(bit_string[index:index + 8], 2))
```

### What this does

Take the bit string in chunks of 8 bits.

For each chunk:

1. slice the substring
2. convert it from binary string to integer
3. append to the byte list

### About `int(binary_string, 2)`

This converts a binary string to an integer using base 2.

Example:

```python
int("10100011", 2)
```

returns the integer represented by that binary value.

---

```python
return packed_bytes, padding_bits
```

Returns:

1. list of packed byte values
2. number of padding bits added

The decompressor needs `padding_bits` later.

---

## Function 7: `estimate_memory_usage`

```python
def estimate_memory_usage(frequencies, codes, packed_bytes):
```

### Purpose

Estimate memory usage of the main Huffman data structures.

### Parameters

#### `frequencies`

- frequency dictionary

#### `codes`

- final symbol-to-code mapping

#### `packed_bytes`

- list of packed compressed bytes

### Logic

```python
return (
    sys.getsizeof(frequencies)
    + sys.getsizeof(codes)
    + sys.getsizeof(packed_bytes)
)
```

This gives an approximate memory usage in bytes.

Important:

It is educational and approximate, not full OS-level profiling.

---

## Function 8: `build_data_structure_efficiency`

```python
def build_data_structure_efficiency(symbol_count):
```

### Purpose

Return human-readable notes about why the chosen data structures are appropriate.

### Parameter

#### `symbol_count`

- number of unique symbols in the file

### Return value

A dictionary containing notes about:

- frequency dictionary
- heap priority queue
- code dictionary

These notes are used in project analysis and discussion.

---

## Function 9: `save_compressed_file`

```python
def save_compressed_file(file_path, result, frequencies, packed_bytes, padding_bits):
```

### Purpose

Save the Huffman compressed output into a `.huff` file.

### Parameters

#### `file_path`

- original source file path

#### `result`

- result dictionary from compression

#### `frequencies`

- frequency dictionary

#### `packed_bytes`

- compressed byte list

#### `padding_bits`

- number of padded zero bits added during packing

---

## Step A: create output folder

```python
output_folder = os.path.join(os.path.dirname(__file__), "compressed_files")
os.makedirs(output_folder, exist_ok=True)
```

This creates or reuses:

- `Huffman/huffman_compression/compressed_files/`

---

## Step B: build output file name

```python
file_name = os.path.basename(file_path) + ".huff"
compressed_file_path = os.path.join(output_folder, file_name)
```

This creates the output file name by taking the original name and adding `.huff`.

Example:

```text
sample.txt -> sample.txt.huff
```

---

## Step C: build compressed JSON object

```python
compressed_data = {
    "algorithm": "Huffman",
    "file_type": result["file_type"],
    "original_file_path": file_path,
    "original_extension": os.path.splitext(file_path)[1],
    "original_length": result["stats"]["original_size_bytes"],
    "frequencies": {str(symbol): count for symbol, count in frequencies.items()},
    "padding_bits": padding_bits,
    "packed_bytes": packed_bytes,
}
```

### Explanation of fields

#### `"algorithm"`

- name of the algorithm

#### `"file_type"`

- project category

#### `"original_file_path"`

- path of source file

#### `"original_extension"`

- original extension like `.txt` or `.bmp`

#### `"original_length"`

- original size before compression

#### `"frequencies"`

- frequency table

### Why convert symbols to strings?

```python
{str(symbol): count for symbol, count in frequencies.items()}
```

Because JSON object keys must be strings.

This is a dictionary comprehension.

### About dictionary comprehension

This syntax:

```python
{expression for ...}
```

builds a dictionary in one expression.

Here it means:

- for each symbol-count pair
- convert symbol to string
- keep count as value

#### `"padding_bits"`

- number of zeros added to align the final bits into full bytes

#### `"packed_bytes"`

- actual compressed data stored as byte integers

---

## Step D: write JSON file

```python
with open(compressed_file_path, "w", encoding="utf-8") as file:
    json.dump(compressed_data, file)
```

This writes the compressed data to the `.huff` file in JSON format.

---

```python
return compressed_file_path
```

Return the saved output path.

---

## Function 10: `compress_text_file`

```python
def compress_text_file(file_path, file_category="text_document"):
```

This is the main Huffman compression function.

### Parameters

#### `file_path`

- path of the source file

#### `file_category`

- descriptive label of the file type
- default:

```python
"text_document"
```

It may also be:

- `"highly_repetitive_data_file"`

---

## Step A: read file as bytes

```python
with open(file_path, "rb") as file:
    file_bytes = file.read()
```

### Why `"rb"`?

It reads the file in binary mode.

This is safer and more general for byte-based processing.

---

## Step B: handle empty input

```python
if not file_bytes:
    return build_empty_result(file_path, file_category)
```

If file is empty:

- stop immediately
- return default result

---

## Step C: start timing

```python
start_time = time.perf_counter()
```

High-precision timer starts here.

---

## Step D: build frequency table

```python
frequencies = build_frequency_table(file_bytes)
```

Creates the frequency dictionary.

Example:

```python
{65: 20, 66: 4, 32: 17}
```

---

## Step E: build Huffman tree

```python
tree = build_huffman_tree(frequencies)
```

Creates the tree using the frequency table and heap merging.

---

## Step F: build final codes

```python
codes = build_codes(tree)
```

Traverses the tree and assigns a binary string to each symbol.

Example:

```python
{65: "0", 66: "101", 67: "111"}
```

---

## Step G: encode file into a bit string

```python
bit_string = "".join(codes[byte] for byte in file_bytes)
```

### Meaning

For every byte in the original file:

- find its Huffman code
- concatenate all codes together into one big bit string

### About `"".join(...)`

`join()` is a common Python string method.

Example:

```python
"".join(["10", "111", "0"])
```

becomes:

```python
"101110"
```

### About generator expression

```python
codes[byte] for byte in file_bytes
```

This is a generator expression.

It produces each code one by one without first building a separate list.

---

## Step H: pack bits into bytes

```python
packed_bytes, padding_bits = pack_bits(bit_string)
```

This converts the bit string into real byte-sized pieces for storage.

---

## Step I: stop timing

```python
end_time = time.perf_counter()
execution_time = end_time - start_time
```

Compute total time used by compression.

---

## Step J: compute metrics

```python
original_size_bytes = len(file_bytes)
compressed_size_bytes = len(packed_bytes)
compression_ratio = original_size_bytes / compressed_size_bytes if compressed_size_bytes else 0
memory_usage_bytes = estimate_memory_usage(frequencies, codes, packed_bytes)
```

### Variables

#### `original_size_bytes`

- size of original input

#### `compressed_size_bytes`

- size of packed compressed data

#### `compression_ratio`

- original size divided by compressed size

Higher means stronger compression.

#### `memory_usage_bytes`

- estimated size of important Huffman objects

---

## Step K: build result dictionary

```python
result = {
    ...
}
```

### Main keys

#### `file_type`

- category label

#### `file_path`

- input file path

#### `frequency_table`

- list version of frequency dictionary

Built as:

```python
[
    {"symbol": symbol, "count": count}
    for symbol, count in sorted(frequencies.items())
]
```

This is easier to read and JSON-friendly.

#### `code_table`

- list version of code mapping

Built as:

```python
[
    {"symbol": symbol, "code": code}
    for symbol, code in sorted(codes.items())
]
```

This is useful for debugging and display.

#### `stats`

- all computed performance metrics

#### `data_structure_efficiency`

- explanatory notes

---

### Inside `stats`

#### `original_size_bytes`

- original input size

#### `compressed_size_bytes`

- packed compressed size

#### `compression_ratio`

- rounded to 4 decimal places

#### `execution_time_seconds`

- rounded to 6 decimal places

#### `compression_speed_bytes_per_second`

- how many bytes were processed per second

#### `entropy_bits_per_symbol`

- Shannon entropy of original file

#### `memory_usage_bytes`

- estimated memory used by main structures

#### `padding_bits`

- number of zeros added to complete the last byte

---

## Step L: save compressed file

```python
result["compressed_file_path"] = save_compressed_file(
    file_path=file_path,
    result=result,
    frequencies=frequencies,
    packed_bytes=packed_bytes,
    padding_bits=padding_bits,
)
```

This writes the `.huff` file and stores its path.

### Why named arguments are used?

Named arguments make the call clearer and safer.

Instead of depending only on argument order, the reader can see exactly what each value represents.

---

## Step M: save real output file size

```python
result["stats"]["saved_compressed_file_size_bytes"] = os.path.getsize(result["compressed_file_path"])
```

### Purpose

Get the actual stored file size on disk.

This is useful because:

- `compressed_size_bytes` = algorithm-side packed byte size
- `saved_compressed_file_size_bytes` = real size of the JSON `.huff` file

These are different concepts.

---

## Step N: return final result

```python
return result
```

Returns the complete structured result to:

- `main.py`
- Flask backend
- tests
- any importing module

---

# Final conceptual summary

## What `main.py` does

- imports helper functions
- selects correct function based on file type
- supports direct console execution
- prints readable output

## What `text_compression.py` does

- reads file bytes
- counts symbol frequencies
- builds the Huffman tree
- generates symbol codes
- encodes the file into bits
- packs bits into bytes
- calculates metrics
- saves `.huff` file
- returns a full structured result

## Most important Huffman variables

- `frequencies` = how many times each symbol appears
- `heap` = priority queue for choosing smallest nodes
- `order` = tie-breaker for heap stability
- `tree` = root of the Huffman tree
- `codes` = final mapping from symbol to binary code
- `bit_string` = full compressed bit stream before packing
- `packed_bytes` = bit stream converted into byte chunks
- `padding_bits` = zeros added at the end for byte alignment

## Most important Huffman idea in this file

The algorithm gives:

- shorter codes to more frequent symbols
- longer codes to less frequent symbols

This reduces the total number of bits needed to represent the file.

