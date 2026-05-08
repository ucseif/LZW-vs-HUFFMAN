# LZW Compression Code Explanation

This file explains in detail the following two files:

- `LZW/lzw_compression/main.py`
- `LZW/lzw_compression/text_compression.py`

The explanation covers:

- every function
- every parameter
- every important variable
- the purpose of each imported module
- the internal flow of the code
- why each part exists

This file is intended for project review, discussion, and personal understanding before presentation.

---

# Part 1: `LZW/lzw_compression/main.py`

## Full purpose of this file

This file is the main entry point for LZW compression.

Its job is not to implement the compression algorithm itself.

Instead, its responsibility is:

1. import the correct helper functions
2. decide which compression function to call based on file type
3. print the result in a readable form when the file is run directly

So this file acts like a controller or dispatcher.

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

### Why is `try / except ImportError` used here?

Because this file may be run in two different ways:

### Case 1: run as part of a package

Example:

```python
from LZW.lzw_compression.main import compress_file
```

In this case Python expects relative imports like:

```python
from .bitmap_file import ...
```

### Case 2: run directly as a standalone script

Example:

```bash
python LZW/lzw_compression/main.py
```

In this case relative imports may fail, so the code falls back to:

```python
from bitmap_file import ...
```

### Meaning of the imported functions

#### `compress_bitmap_file`

- imported from `bitmap_file.py`
- used when the file type is `bitmap`
- handles bitmap compression

#### `compress_text_file`

- imported from `text_compression.py`
- used when the file type is `text` or `repetitive`
- handles text-based compression

So `main.py` does not compress anything itself.
It just forwards the file to the correct compression function.

---

## Code section 2: `compress_file`

```python
def compress_file(file_path, file_type):
```

### Purpose

This function selects the correct LZW compression function depending on the user’s chosen file type.

### Parameters

#### `file_path`

- type: string
- meaning: the path of the file that should be compressed
- example:

```python
"E:\\InfoProject\\sample_text_document.txt"
```

#### `file_type`

- type: string
- meaning: a label describing the kind of file
- allowed values:
  - `"text"`
  - `"repetitive"`
  - `"bitmap"`

This parameter is used to decide which compression module should be called.

### Internal logic

```python
if file_type == "text":
    return compress_text_file(file_path, "text_document")
```

If the user selected `text`, then:

- call `compress_text_file`
- pass the original file path
- pass the category `"text_document"`

Why `"text_document"`?

Because inside the project we want a more descriptive category than just `"text"`.

---

```python
if file_type == "repetitive":
    return compress_text_file(file_path, "highly_repetitive_data_file")
```

If the user selected `repetitive`, then:

- still use the same text compression function
- but change the category string to:

```python
"highly_repetitive_data_file"
```

Why?

Because the actual compression logic is the same as text compression.
The difference is only the project classification and analysis context.

---

```python
if file_type == "bitmap":
    return compress_bitmap_file(file_path)
```

If the user selected `bitmap`, then:

- call the bitmap compression function
- because bitmap files are treated as binary image input

---

```python
raise ValueError("file_type must be: text, repetitive, or bitmap")
```

If none of the expected file types were provided, the function raises an error.

### Why this is useful

It protects the function from invalid input such as:

```python
compress_file("file.txt", "audio")
```

Without this check, the code could silently fail or behave unpredictably.

---

## Code section 3: `print_result`

```python
def print_result(result):
```

### Purpose

This function prints the compression result in a readable console format.

It is mainly useful when running `main.py` directly from terminal or PowerShell.

### Parameter

#### `result`

- type: dictionary
- meaning: the full result returned by the compression function

This dictionary includes:

- file type
- codes
- stats
- data structure notes
- output path

### Internal logic

```python
codes = result["codes"]
```

This extracts the list of compressed LZW codes from the result dictionary.

---

```python
print("\nFile Type:")
print(result["file_type"])
```

This prints the file category such as:

- `text_document`
- `highly_repetitive_data_file`
- `bitmap_image`

---

```python
print("\nCompressed Codes:")
if len(codes) > 80:
    print(codes[:80], "...")
    print(f"Total codes: {len(codes)}")
else:
    print(codes)
```

### Why is this done?

Because some files generate very long code lists.

If the list is longer than 80 items:

- print only the first 80 codes
- print the total count

This avoids flooding the terminal.

If the list is short:

- print the whole list

---

```python
print("\nStatistics:")
for key, value in result["stats"].items():
    print(f"{key}: {value}")
```

This loops through the statistics dictionary and prints each metric.

Examples of metrics:

- `original_size_bytes`
- `compressed_size_bytes`
- `compression_ratio`
- `execution_time_seconds`

### About `.items()`

`dictionary.items()` is a common Python function.

It returns key-value pairs from a dictionary.

Example:

```python
{"a": 1, "b": 2}.items()
```

returns something like:

```python
("a", 1), ("b", 2)
```

So the loop:

```python
for key, value in result["stats"].items():
```

means:

- take each metric name as `key`
- take its value as `value`

---

```python
print("\nData Structure Efficiency:")
for key, value in result["data_structure_efficiency"].items():
    print(f"{key}: {value}")
```

This prints the explanatory notes about:

- dictionary efficiency
- list efficiency
- step tracing structure

These are descriptive notes for analysis and discussion.

---

```python
print("\nCompressed File Path:")
print(result["compressed_file_path"])
```

This prints where the compressed `.lzw` file was saved.

---

## Code section 4: direct execution block

```python
if __name__ == "__main__":
```

### Meaning

This is a standard Python pattern.

It means:

- if this file is run directly, execute the code below
- if this file is imported from somewhere else, do not execute the code below

### Why it is useful here

It allows the file to work in two ways:

1. importable from other modules
2. executable directly for testing

---

```python
file_path = input("Enter file path: ").strip()
```

### What this does

- asks the user to type the file path
- `input(...)` reads text from the console
- `.strip()` removes extra spaces at the beginning and end

### About `.strip()`

`strip()` is a common Python string function.

Example:

```python
"  hello  ".strip()
```

becomes:

```python
"hello"
```

---

```python
file_type = input("Enter file type (text / repetitive / bitmap): ").strip().lower()
```

### What this does

- asks the user for the file type
- removes surrounding spaces with `.strip()`
- converts text to lowercase with `.lower()`

### About `.lower()`

`lower()` is a common Python string function.

It converts uppercase letters to lowercase.

Example:

```python
"TEXT".lower()
```

becomes:

```python
"text"
```

This makes user input safer and more flexible.

---

```python
result = compress_file(file_path, file_type)
print_result(result)
```

### What happens here

1. call the dispatcher function
2. get the compression result
3. print it in a readable format

---

# Part 2: `LZW/lzw_compression/text_compression.py`

## Full purpose of this file

This file contains the real LZW text compression logic.

Its responsibilities are:

1. read a file as bytes
2. build the initial dictionary
3. perform LZW compression
4. record steps
5. calculate statistics
6. save the compressed `.lzw` file
7. return a structured result

This is the main algorithm file for text-based LZW compression.

---

## Imports

```python
import math
import json
import os
import sys
import time
```

### `math`

Used for mathematical operations.

In this file it is mainly used for:

- `log2`
- `ceil`

These help estimate the compressed size.

### `json`

Used to save compressed output as JSON inside the `.lzw` file.

### `os`

Used for file path and directory operations.

Examples in this file:

- `os.path.join`
- `os.path.dirname`
- `os.makedirs`
- `os.path.basename`
- `os.path.splitext`
- `os.path.getsize`

### `sys`

Used for memory estimation with:

- `sys.getsizeof(...)`

### `time`

Used to measure execution time with:

- `time.perf_counter()`

---

## Function 1: `build_empty_result`

```python
def build_empty_result(file_path, file_category):
```

### Purpose

This function creates a default result when the input file is empty.

### Why needed?

If the file contains no bytes:

- compression logic should not continue
- but the program still needs to return a valid result structure

### Parameters

#### `file_path`

- string
- the path of the input file

#### `file_category`

- string
- the project category of the file

### Returned structure

This function returns a dictionary with default empty values:

- empty `codes`
- empty `steps`
- zero sizes
- zero ratio
- zero execution time

### Why return this instead of `None`?

Because the rest of the project expects a consistent result dictionary format.

Returning `None` would force the caller to treat empty files as a completely different case.

---

## Function 2: `build_initial_dictionary`

```python
def build_initial_dictionary():
```

### Purpose

Creates the initial LZW dictionary.

### Internal logic

```python
dictionary = {}
```

Creates an empty Python dictionary.

### Then:

```python
for number in range(256):
    dictionary[bytes([number])] = number
```

### Explanation

For every number from `0` to `255`:

- convert the number into a one-byte object
- store it in the dictionary with the same numeric code

Examples:

- `bytes([65])` becomes `b'A'`
- `bytes([66])` becomes `b'B'`

So:

- `b'A' -> 65`
- `b'B' -> 66`

### About `range(256)`

`range(256)` produces numbers:

```python
0, 1, 2, ..., 255
```

### About `bytes([number])`

This creates a one-byte sequence from a numeric value.

Examples:

```python
bytes([65]) -> b'A'
bytes([10]) -> b'\n'
```

### Why use bytes and not strings?

Because the project handles files generally, including:

- text
- repetitive data
- bitmap images

Working with bytes makes the method more general and consistent.

---

## Function 3: `estimate_compressed_size`

```python
def estimate_compressed_size(codes):
```

### Purpose

Estimate how many bytes the compressed code sequence would need.

### Parameter

#### `codes`

- list of integers
- each integer is an LZW output code

### Logic

```python
if not codes:
    return 0
```

If the list is empty, the compressed size is zero.

### About `if not codes`

In Python, an empty list is treated as `False`.

So this means:

- if the list is empty -> return 0

---

```python
max_code = max(codes)
```

Find the largest code in the list.

Why?

Because the largest code determines how many bits are needed per code.

---

```python
bits_per_code = max(1, math.ceil(math.log2(max_code + 1)))
```

### Meaning

This estimates how many bits are needed to represent the largest code.

#### `math.log2(max_code + 1)`

Finds the binary logarithm.

Example:

- if max code is `255`, then roughly 8 bits are needed
- if max code is `511`, then roughly 9 bits are needed

#### `math.ceil(...)`

Rounds upward to the next integer.

#### `max(1, ...)`

Ensures the number of bits is never less than 1.

---

```python
return math.ceil((len(codes) * bits_per_code) / 8)
```

This estimates:

- number of codes × bits per code = total bits
- divide by 8 to convert bits to bytes
- round upward to whole bytes

---

## Function 4: `calculate_entropy`

```python
def calculate_entropy(file_bytes):
```

### Purpose

Calculate Shannon entropy of the original file bytes.

### Parameter

#### `file_bytes`

- bytes object
- contains the full original file content

### Logic

```python
if not file_bytes:
    return 0
```

If the file is empty, entropy is zero.

---

```python
frequencies = {}
for byte in file_bytes:
    frequencies[byte] = frequencies.get(byte, 0) + 1
```

This counts how many times each byte appears.

### About `dictionary.get(key, default)`

`get()` is a common Python dictionary method.

Example:

```python
frequencies.get(byte, 0)
```

means:

- if `byte` already exists in the dictionary, return its current count
- otherwise return `0`

Then add 1.

This is a standard frequency counting pattern.

---

```python
entropy = 0
total_size = len(file_bytes)
```

- `entropy` will accumulate the final result
- `total_size` is the number of bytes in the file

---

```python
for count in frequencies.values():
    probability = count / total_size
    entropy -= probability * math.log2(probability)
```

This applies the Shannon entropy formula:

```text
H(X) = - Σ p(x) log2 p(x)
```

### About `frequencies.values()`

This returns only the counts, not the keys.

---

```python
return round(entropy, 6)
```

Rounds the entropy to 6 decimal places for readability.

---

## Function 5: `estimate_memory_usage`

```python
def estimate_memory_usage(dictionary, codes, steps):
```

### Purpose

Estimate memory usage of the main LZW data structures.

### Parameters

#### `dictionary`

- the LZW dictionary used during compression

#### `codes`

- the list of output codes

#### `steps`

- the list containing tracing information for each step

### Logic

```python
return (
    sys.getsizeof(dictionary)
    + sys.getsizeof(codes)
    + sys.getsizeof(steps)
)
```

This adds the approximate memory size of the three objects.

### About `sys.getsizeof`

This is a Python function that gives an approximate memory size of an object in bytes.

Important:

It is an educational estimate, not a full operating system memory profiler.

---

## Function 6: `build_data_structure_efficiency`

```python
def build_data_structure_efficiency(final_dictionary_size):
```

### Purpose

Return human-readable notes about why the chosen Python data structures are efficient.

### Parameter

#### `final_dictionary_size`

- integer
- the number of entries in the final dictionary after compression

### Return value

A dictionary with three notes:

- about the main dictionary
- about the output codes list
- about the steps list

This is used in analysis and presentation.

---

## Function 7: `save_compressed_file`

```python
def save_compressed_file(file_path, result):
```

### Purpose

Save the compressed output into a `.lzw` file.

### Parameters

#### `file_path`

- original file path

#### `result`

- the result dictionary produced by compression

### Step 1: define output folder

```python
output_folder = os.path.join(os.path.dirname(__file__), "compressed_files")
```

### Meaning

- `__file__` = current Python file path
- `os.path.dirname(__file__)` = folder of this script
- then join with `"compressed_files"`

So the output goes inside:

- `LZW/lzw_compression/compressed_files/`

---

```python
os.makedirs(output_folder, exist_ok=True)
```

Creates the folder if it does not already exist.

### About `exist_ok=True`

This prevents an error if the folder already exists.

---

```python
file_name = os.path.basename(file_path) + ".lzw"
```

Takes only the file name from the original path and adds `.lzw`.

Example:

```text
sample.txt -> sample.txt.lzw
```

---

```python
compressed_file_path = os.path.join(output_folder, file_name)
```

Build the full save path.

---

```python
compressed_data = {
    "algorithm": "LZW",
    "file_type": result["file_type"],
    "original_file_path": file_path,
    "original_extension": os.path.splitext(file_path)[1],
    "initial_dictionary": "ASCII_0_TO_255",
    "codes": result["codes"],
}
```

This is the content written into the compressed file.

### About `os.path.splitext(file_path)[1]`

`splitext()` separates file name and extension.

Example:

```python
os.path.splitext("sample.txt")
```

returns something like:

```python
("sample", ".txt")
```

Index `[1]` means:

- get the extension only

This is useful for restoring the file later during decompression.

---

```python
with open(compressed_file_path, "w", encoding="utf-8") as file:
    json.dump(compressed_data, file)
```

### Meaning

- open output file for writing
- use UTF-8 encoding
- write the JSON object into the file

### About `json.dump(...)`

`json.dump(data, file)` writes a Python object directly into a file in JSON format.

Difference:

- `json.dump(...)` -> write to file
- `json.dumps(...)` -> return JSON string

---

```python
return compressed_file_path
```

Returns the final saved file path.

---

## Function 8: `compress_text_file`

```python
def compress_text_file(file_path, file_category="text_document"):
```

This is the main LZW compression function.

### Parameters

#### `file_path`

- path of the file to compress

#### `file_category`

- descriptive category string
- default is `"text_document"`

It can also be:

- `"highly_repetitive_data_file"`

---

## Step A: read file as bytes

```python
with open(file_path, "rb") as file:
    file_bytes = file.read()
```

### Why `"rb"`?

`"rb"` means:

- read binary

This allows the code to work on raw bytes, which is more general and safer.

### About `file.read()`

Reads the entire file into memory as bytes.

---

## Step B: handle empty file

```python
if not file_bytes:
    return build_empty_result(file_path, file_category)
```

If the file is empty, stop early and return the default empty result.

---

## Step C: start timing

```python
start_time = time.perf_counter()
```

### About `time.perf_counter()`

This is a high-precision timer used for measuring execution time.

It is preferred over simpler timing methods when benchmarking code.

---

## Step D: initialize compression state

```python
dictionary = build_initial_dictionary()
next_code = 256
current = bytes([file_bytes[0]])
codes = []
steps = []
```

### Variables

#### `dictionary`

- the current LZW dictionary
- starts with 256 single-byte entries

#### `next_code`

- the next available code number for a newly discovered pattern
- starts at `256`
because `0..255` are already used

#### `current`

- the current byte sequence being tracked
- starts with the first byte of the file

#### `codes`

- the final compressed output code list

#### `steps`

- stores step-by-step trace information for explanation and debugging

### About `bytes([file_bytes[0]])`

`file_bytes[0]` gives the first byte as an integer.

Then `bytes([...])` converts it into a one-byte bytes object.

---

## Step E: main compression loop

```python
for step_number, next_byte in enumerate(file_bytes[1:], start=1):
```

### What this means

Loop over the remaining bytes in the file, starting from the second byte.

### About `file_bytes[1:]`

This means:

- take all bytes except the first one

because the first one is already stored in `current`

### About `enumerate(..., start=1)`

`enumerate()` is a common Python function.

It gives:

- the index number
- the actual item

So here:

- `step_number` = logical step index
- `next_byte` = next byte from the file

---

### Convert next byte to symbol

```python
next_symbol = bytes([next_byte])
combined = current + next_symbol
```

#### `next_symbol`

- one-byte bytes object for the next input symbol

#### `combined`

- candidate sequence formed by current sequence + next symbol

This is the key LZW pattern test.

---

### Build step record

```python
step = {
    "step": step_number,
    "current": list(current),
    "next": next_byte,
    "combined": list(combined),
    "in_dict": combined in dictionary,
    "dict_code": dictionary.get(combined),
    "output_code": None,
    "add_to_dict": None,
}
```

This creates a dictionary containing all information about the current step.

### Why convert `current` and `combined` to lists?

Because bytes objects are harder to read in debug output.

A list of integers is clearer and JSON-friendly.

Example:

```python
b'AB' -> [65, 66]
```

### About `combined in dictionary`

Checks whether the candidate sequence already exists in the LZW dictionary.

### About `dictionary.get(combined)`

Gets its code if it exists, otherwise returns `None`.

---

## Step F: LZW decision

### Case 1: `combined` already exists

```python
if combined in dictionary:
    current = combined
```

### Meaning

If the longer sequence is already known:

- keep extending the current pattern
- do not output anything yet

This means the algorithm is still trying to build the longest known pattern.

---

### Case 2: `combined` does not exist

```python
else:
    step["output_code"] = dictionary[current]
    step["add_to_dict"] = {
        "sequence": list(combined),
        "code": next_code,
    }
    codes.append(dictionary[current])
    dictionary[combined] = next_code
    next_code += 1
    current = next_symbol
```

This is the heart of LZW compression.

#### `step["output_code"] = dictionary[current]`

Store which code will be output for this step.

#### `step["add_to_dict"] = ...`

Record the new pattern that will be added to the dictionary.

#### `codes.append(dictionary[current])`

Actually add the output code to the final compressed stream.

#### `dictionary[combined] = next_code`

Add the new pattern into the dictionary.

Example:

- current = `A`
- next symbol = `B`
- combined = `AB`
- if `AB` is not in dictionary:
  - output code for `A`
  - add `AB -> 256`

#### `next_code += 1`

Move to the next available dictionary code.

#### `current = next_symbol`

Reset current pattern to start from the latest single symbol.

---

## Step G: save the step

```python
steps.append(step)
```

Store the step information regardless of which branch happened.

---

## Step H: output the final current pattern

After the loop ends:

```python
codes.append(dictionary[current])
```

### Why is this necessary?

Because at the end of the loop there is still one final current pattern that has not yet been output.

LZW always needs to output the last known pattern after scanning finishes.

---

```python
steps.append({
    "step": len(steps) + 1,
    "current": list(current),
    "next": "-",
    "combined": "-",
    "in_dict": None,
    "dict_code": None,
    "output_code": dictionary[current],
    "add_to_dict": None,
})
```

This records a final step for explanation:

- no next byte
- no combined candidate
- only the final output code

### About `len(steps) + 1`

This gives the number of the last step.

---

## Step I: stop timing

```python
end_time = time.perf_counter()
```

Used with `start_time` to calculate total execution time.

---

## Step J: compute metrics

```python
compressed_size_bytes = estimate_compressed_size(codes)
original_size_bytes = len(file_bytes)
compression_ratio = original_size_bytes / compressed_size_bytes if compressed_size_bytes else 0
execution_time = end_time - start_time
memory_usage_bytes = estimate_memory_usage(dictionary, codes, steps)
```

### Variables

#### `compressed_size_bytes`

- estimated compressed size based on the code list

#### `original_size_bytes`

- size of original file in bytes

#### `compression_ratio`

- original size divided by compressed size

Higher means stronger compression.

#### `execution_time`

- total time spent in compression

#### `memory_usage_bytes`

- estimated size of the main Python objects used

---

## Step K: build result dictionary

```python
result = {
    ...
}
```

This creates the final structured output returned by the function.

### Main keys

#### `file_type`

- project category of the file

#### `file_path`

- original file path

#### `original_data`

- list of original bytes

#### `codes`

- final compressed LZW code sequence

#### `steps`

- step-by-step trace data

#### `initial_dictionary`

- description of the initial dictionary

#### `final_dictionary_size`

- number of entries after compression

#### `stats`

- metrics dictionary

#### `data_structure_efficiency`

- explanatory notes

---

### Inside `stats`

#### `original_size_bytes`

- file size before compression

#### `compressed_size_bytes`

- estimated size of code stream

#### `number_of_output_codes`

- how many codes were produced

#### `compression_ratio`

- rounded to 4 decimal places

#### `execution_time_seconds`

- rounded to 6 decimal places

#### `compression_speed_bytes_per_second`

- how fast bytes were processed

#### `entropy_bits_per_symbol`

- Shannon entropy of original bytes

#### `memory_usage_bytes`

- estimated memory usage

---

## Step L: save compressed file

```python
result["compressed_file_path"] = save_compressed_file(file_path, result)
```

This writes the `.lzw` file and stores its path in the result.

---

## Step M: measure saved compressed file size

```python
result["stats"]["saved_compressed_file_size_bytes"] = os.path.getsize(result["compressed_file_path"])
```

### Purpose

This gets the real file size of the saved `.lzw` file on disk.

### About `os.path.getsize(path)`

Returns the actual size of the file in bytes.

This is useful because:

- `compressed_size_bytes` is an algorithm estimate
- `saved_compressed_file_size_bytes` is the actual saved file size

These may differ because the file is stored as JSON.

---

## Step N: return final result

```python
return result
```

The function returns the full result dictionary to whoever called it:

- `main.py`
- Flask backend
- tests
- any other module

---

# Final conceptual summary

## What `main.py` does

- imports helper functions
- chooses the correct compression function
- handles direct console execution
- prints result for terminal use

## What `text_compression.py` does

- reads file bytes
- builds the initial dictionary
- performs real LZW compression
- tracks each step
- calculates metrics
- saves `.lzw` file
- returns all output in one structured dictionary

## Most important variables in LZW logic

- `dictionary` = current map from byte sequence to code
- `next_code` = next free code value
- `current` = current known pattern
- `next_symbol` = next byte as a one-byte sequence
- `combined` = current + next symbol
- `codes` = final compressed output
- `steps` = tracing data for explanation

## Most important LZW rule in this file

If `combined` exists in dictionary:

- continue building a longer pattern

If `combined` does not exist:

- output the code for `current`
- add `combined` to the dictionary
- continue from `next_symbol`

