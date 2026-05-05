# LZW vs Huffman Compression Studio

A complete Information Theory and Data Compression project that implements and compares two lossless compression algorithms from scratch:

- `LZW`
- `Huffman`

The project includes:

- file compression and decompression
- comparison metrics and analysis
- a Flask-based web interface
- side-by-side algorithm comparison
- sample input files for testing

This repository was built for an academic workflow where both correctness and clarity matter.

## Project Overview

The goal of the project is to apply two lossless compression techniques to multiple file types, then evaluate them using the required analytical metrics.

Supported file categories:

- `Text Document`
- `Highly Repetitive Data`
- `Bitmap Image`

Each algorithm supports:

- compression
- decompression
- saving compressed files
- restoring original files
- measuring performance and compression behavior

## Implemented Algorithms

### 1. LZW

LZW is a dictionary-based compression method.

In this project, LZW:

- builds and expands a dictionary during processing
- works on general file input
- supports both compression and decompression
- stores compressed output in `.lzw` files

### 2. Huffman

Huffman coding is a frequency-based compression technique.

In this project, Huffman:

- calculates symbol frequencies
- builds a Huffman tree
- generates binary codes for symbols
- supports both compression and decompression
- stores compressed output in `.huff` files

## Required Comparative Analysis

The project includes the metrics required for the course comparison:

- `Entropy H(X)` of the original file
- `Compression Ratio`
- `Execution Time`
- `Compression Speed`
- `Memory Usage`
- notes about `Data Structure Efficiency`

These results are available through the backend logic and displayed through the web interface.

## Web Interface

The repository includes a modern Flask web application with:

- a landing page
- a main workspace for compression and decompression
- a comparison page for LZW vs Huffman
- automatic comparison generation
- file preview popup after compression or decompression

### Main pages

- `/` -> landing page
- `/app` -> compression/decompression workspace
- `/comparison?id=...` -> side-by-side comparison dashboard

## Project Structure

```text
InfoProject/
│
├── LZW/
│   ├── lzw_compression/
│   │   ├── main.py
│   │   ├── text_compression.py
│   │   ├── bitmap_file.py
│   │   └── compressed_files/
│   └── lzw_decompression/
│       ├── main.py
│       ├── text_decompression.py
│       ├── bitmap_file.py
│       └── decompressed_files/
│
├── Huffman/
│   ├── huffman_compression/
│   │   ├── main.py
│   │   ├── text_compression.py
│   │   ├── bitmap_file.py
│   │   └── compressed_files/
│   └── huffman_decompression/
│       ├── main.py
│       ├── text_decompression.py
│       ├── bitmap_file.py
│       └── decompressed_files/
│
├── webapp/
│   ├── app.py
│   ├── templates/
│   │   ├── index.html
│   │   ├── app.html
│   │   └── comparison.html
│   ├── static/
│   │   ├── styles.css
│   │   ├── app.js
│   │   └── comparison.js
│   ├── uploads/
│   └── runtime/
│
├── sample_text_document.txt
├── repetitive_data.txt
├── sample_bitmap.bmp
└── README.md
```

## Sample Files

The repository includes prepared files for testing:

- [sample_text_document.txt](./sample_text_document.txt)
- [repetitive_data.txt](./repetitive_data.txt)
- [sample_bitmap.bmp](./sample_bitmap.bmp)

These represent the three required file types used in the project.

## Running the Project

### Requirements

- Python 3.14 or compatible Python 3.x installation
- Flask

### Install Flask

```bash
pip install flask
```

### Run the web application

From the project root:

```bash
python webapp/app.py
```

Then open:

```text
http://127.0.0.1:8010
```

## Using the Web App

### In the workspace

1. Choose the operation:
   - `Compression`
   - `Decompression`
2. Select the algorithm:
   - `LZW`
   - `Huffman`
3. Select the file type:
   - `Text Document`
   - `Highly Repetitive Data`
   - `Bitmap Image`
4. Upload a file
5. Click `Process File`

After processing:

- the output metrics appear in the result panel
- the generated output file can be downloaded
- a popup preview shows the generated file content
- a comparison link opens a full side-by-side dashboard

## Output Files

Generated compressed files are stored in algorithm-specific folders:

- `LZW/lzw_compression/compressed_files/`
- `Huffman/huffman_compression/compressed_files/`

Generated decompressed files are stored in:

- `LZW/lzw_decompression/decompressed_files/`
- `Huffman/huffman_decompression/decompressed_files/`

Temporary web runtime files are stored in:

- `webapp/uploads/`
- `webapp/runtime/`

These runtime folders are intentionally excluded from Git except for `.gitkeep`.

## Comparison Workflow

When a user runs one algorithm from the web app:

1. the selected algorithm is executed first
2. the alternative algorithm is executed automatically in the background on the same source context
3. both results are stored
4. the comparison page displays:
   - side-by-side algorithm panels
   - metric graphs
   - detailed comparison metrics

This keeps the comparison fair and based on the same input conditions.

## Notes on File Preview

After each compression or decompression operation, the web app opens a popup preview:

- text-like files are shown as readable text
- binary-like files are shown as a hex preview

This feature was added at the web layer only and does not modify the internal algorithm logic.

## Development Notes

- The algorithms are implemented manually and do not rely on ready-made compression libraries.
- The project separates compression and decompression logic into dedicated folders for clarity.
- The UI is designed to present the project as both a functional tool and a polished academic demo.

## Repository Notes

- `__pycache__` folders are not part of the project logic
- generated runtime files are ignored by Git
- the repository contains both backend logic and frontend presentation

## Future Improvements

Possible future enhancements include:

- richer README screenshots
- deployment instructions
- additional charts or grouped metric sections
- optional bonus features from the course

## Author

Project owner:

- GitHub: [ucseif](https://github.com/ucseif)

