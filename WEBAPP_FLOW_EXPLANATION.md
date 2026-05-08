# Web Application Flow Explanation

This file explains exactly how the web application works, especially during `decompression`, and also explains what the `codes` field means in compressed LZW files.

## 1. What are these LZW `codes`?

Example:

```json
{
  "algorithm": "LZW",
  "file_type": "text_document",
  "original_file_path": "E:\\InfoProject\\webapp\\uploads\\fa93d957_repetitive_data.txt",
  "original_extension": ".txt",
  "initial_dictionary": "ASCII_0_TO_255",
  "codes": [68, 65, 84, 65, 95, 67, 79, 77, 80, 82, 69, 83, 83, 73, 79, 78, 95, 256, 258, ...]
}
```

### What do these codes mean?

These are the actual compressed output of the LZW algorithm.

They are not random numbers and not dummy data.

Each number represents one dictionary entry during compression.

### How does that happen?

At the beginning of LZW compression:

- the initial dictionary contains all byte values from `0` to `255`
- this means:
  - `65` = byte for `A`
  - `66` = byte for `B`
  - `68` = byte for `D`
  - `95` = byte for `_`
  - and so on

So the first values in the codes list:

```text
68, 65, 84, 65
```

mean:

```text
D A T A
```

because those byte values already exist in the initial dictionary.

### Why do values larger than 255 appear?

Because LZW keeps building new dictionary entries while reading the file.

For example:

- `256` is the first newly created dictionary entry
- `257` is the second new entry
- `258` is the third
- and so on

So when you see:

```text
..., 95, 256, 258, 260, ...
```

this means the algorithm is no longer outputting only single bytes.
It is now outputting codes that represent repeated patterns or longer sequences that were added to the dictionary during compression.

### Very important summary

In LZW:

- `0..255` = original single-byte symbols from the ASCII/byte dictionary
- `256+` = new repeated patterns discovered and stored by the algorithm

So the `codes` array is the real compressed representation of the original file.

## 2. General Web Flow

The web application is handled mainly by:

- `webapp/app.py`
- `webapp/templates/app.html`
- `webapp/static/app.js`
- `webapp/templates/comparison.html`
- `webapp/static/comparison.js`

The user interacts with the frontend, but the actual algorithm execution happens in the Flask backend.

## 3. Main workflow from the UI

When the user opens the workspace page:

- page: `/app`
- file: `webapp/templates/app.html`

The page lets the user choose:

1. operation
   - `compress`
   - `decompress`
2. algorithm
   - `lzw`
   - `huffman`
3. file type
   - `text`
   - `repetitive`
   - `bitmap`
4. file upload

When the user clicks `Process File`, the frontend sends a request to:

```text
POST /api/process
```

This request is handled in:

- `webapp/app.py`

## 4. What happens inside `/api/process`

Inside `process_file()`:

### Step 1: Validate input

The backend checks:

- that a file was uploaded
- the chosen operation
- the chosen file type
- the chosen algorithm

### Step 2: Save the uploaded file

The uploaded file is stored in:

- `webapp/uploads/`

The function used:

- `save_upload(file_storage)`

It generates a unique prefix so files do not overwrite each other.

Example:

```text
fa93d957_repetitive_data.txt
```

### Step 3: Run the selected algorithm

The route calls:

- `run_operation(algorithm, operation, saved_upload_path, file_type)`

This does not execute dummy logic.
It dispatches to the real LZW or Huffman module.

Examples:

- `lzw_compress_dispatch(...)`
- `lzw_decompress_dispatch(...)`
- `huffman_compress_dispatch(...)`
- `huffman_decompress_dispatch(...)`

So the selected algorithm is truly executed.

## 5. Exact flow in Compression mode

Suppose the user chooses:

- operation = `compress`
- algorithm = `lzw`
- file type = `text`

Then the flow is:

1. file is uploaded and saved in `webapp/uploads/`
2. Flask runs `lzw_compress_dispatch(...)`
3. That calls the real LZW compression function from:
   - `LZW/lzw_compression/text_compression.py`
4. LZW reads the uploaded file as bytes
5. LZW builds its dictionary
6. LZW creates the compressed `codes`
7. LZW saves the compressed file in:
   - `LZW/lzw_compression/compressed_files/`
8. LZW returns:
   - `codes`
   - `stats`
   - `data_structure_efficiency`
   - `compressed_file_path`

Then Flask prepares a response for the frontend.

## 6. Exact flow in Decompression mode

This is the most important part for discussion.

Suppose the user chooses:

- operation = `decompress`
- algorithm = `lzw`
- file type = `text`

and uploads a compressed `.lzw` file.

Then the flow is:

### Step 1: Upload the compressed file

The compressed file is saved in:

- `webapp/uploads/`

Example:

```text
fa93d957_repetitive_data.txt.lzw
```

### Step 2: Run the selected decompression algorithm

Flask calls:

```python
run_operation("lzw", "decompress", saved_upload_path, file_type)
```

which dispatches to:

- `lzw_decompress_dispatch(...)`

then to:

- `LZW/lzw_decompression/text_decompression.py`

### Step 3: Read the compressed file

The LZW decompressor opens the `.lzw` file and reads JSON data like:

- algorithm
- file_type
- original_extension
- codes

### Step 4: Rebuild the initial dictionary

For decompression, the initial dictionary is reversed:

- `0 -> byte 0`
- `1 -> byte 1`
- ...
- `255 -> byte 255`

### Step 5: Decode codes back to bytes

The decompressor:

1. reads the first code
2. translates it to bytes using the dictionary
3. appends it to output
4. for each next code:
   - finds the corresponding byte sequence
   - handles edge case if needed
   - creates a new dictionary entry
   - appends decoded bytes to the output

### Step 6: Save the decompressed file

The rebuilt bytes are saved in:

- `LZW/lzw_decompression/decompressed_files/`

Example output:

```text
repetitive_data_decompressed.txt
```

### Step 7: Return decompression result

The result includes:

- `decompressed_file_path`
- `stats`
- `steps`
- `data_structure_efficiency`

So in decompression mode, the main algorithm the user selected is actually run in full and produces a restored file.

## 7. How comparison works in the web app

This is the key question:

### How can the web app compare two algorithms if I only selected one?

Answer:

Because the backend runs the second algorithm automatically in the background.

This happens in:

- `create_comparison_payload(...)`

inside:

- `webapp/app.py`

## 8. Comparison logic in Compression mode

If the user selected:

- operation = `compress`
- algorithm = `lzw`

then:

1. Flask runs `LZW compress` first
2. that result becomes the primary result
3. then Flask runs `Huffman compress` on the same original uploaded file
4. that result becomes the secondary result
5. both results are written into a comparison JSON file

So the second algorithm is absolutely executed.
It is simply not triggered manually by the user.

It is triggered automatically by the backend.

## 9. Comparison logic in Decompression mode

This is more subtle and very important.

If the user selected:

- operation = `decompress`
- algorithm = `lzw`

then this happens:

### First: actual decompression

1. Flask runs `LZW decompress`
2. this restores the original file
3. now we have a real decompressed output file

### Second: choose the comparison source

The function:

- `comparison_source_file(primary_result, operation, original_upload_path)`

returns:

- original uploaded file if operation was `compress`
- decompressed output file if operation was `decompress`

So in decompression mode, the source file for comparison becomes:

- the restored decompressed file

### Third: run both algorithms on the restored file

Inside `create_comparison_payload(...)`:

- the selected algorithm is run again in `compress` mode on the restored file
- the other algorithm is also run in `compress` mode on the same restored file

This is done because compression metrics like:

- compression ratio
- compressed size
- entropy
- memory usage during compression

must be compared on the same original-like source file.

### So why is this correct?

Because after decompression, we want a fair comparison of the algorithms on the recovered data itself.

That means:

1. user decompresses with one algorithm
2. web app restores the original file
3. web app then compresses that restored file using both algorithms
4. comparison page shows those two compression results

So the comparison page after decompression is not comparing:

- decompression result vs compression result

Instead, it compares:

- `selected algorithm compress on restored file`
- `other algorithm compress on restored file`

That is why the comparison remains meaningful.

## 10. What is saved for comparison?

The comparison result is stored in:

- `webapp/runtime/comparisons/`

Each comparison gets a unique id:

```text
0e4687de393e4793a857ed50c5c4529b
```

The comparison page opens with:

```text
/comparison?id=0e4687de393e4793a857ed50c5c4529b
```

Then the frontend calls:

```text
GET /api/comparison?id=...
```

and loads the saved comparison payload.

## 11. Are the comparison numbers real or dummy?

They are real.

They come from actual execution of:

- LZW compression
- LZW decompression
- Huffman compression
- Huffman decompression

The web interface does not invent fake numbers.

However, some metrics are academic estimates rather than industrial profilers.

### Real metrics

- `original_size_bytes`
- `compressed_size_bytes`
- `compression_ratio`
- `execution_time_seconds`
- `compression_speed_bytes_per_second`
- `entropy_bits_per_symbol`

### Estimated / educational metrics

- `memory_usage_bytes`
  - estimated using Python object sizes
  - not a full OS-level profiler

- `data_structure_efficiency`
  - explanatory notes
  - not measured by a system benchmark tool

So the numbers are not dummy, but some of them are educational estimates rather than production benchmarking values.

## 12. Why does the comparison page show only compression metrics?

Because the comparison page is designed to compare algorithm performance on a common source file in a consistent way.

Compression metrics are easier to compare side by side because both algorithms can operate on the same source data under the same conditions.

If the current user action is `decompress`, the system first restores the file, then performs a fresh comparison using compression mode on that restored file.

## 13. Short discussion answer

If you need a short answer in the discussion, you can say:

> In the web application, the algorithm selected by the user is executed first. Then the backend automatically runs the other algorithm in the background on the same source context to generate a fair comparison. In compression mode, both algorithms are run on the original uploaded file. In decompression mode, the selected algorithm first restores the file, then both algorithms are run in compression mode on the restored file so that the comparison metrics remain consistent and meaningful.

## 14. Short answer about LZW codes

You can also say:

> The `codes` field in an LZW compressed file is the actual compressed output of the algorithm. Values from `0` to `255` correspond to the initial ASCII/byte dictionary, while values greater than `255` represent new dictionary entries created dynamically during compression for repeated patterns.

