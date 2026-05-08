import heapq
import json
import math
import os
import sys
import time


class HuffmanNode:
    def __init__(self, symbol=None, left=None, right=None):
        self.symbol = symbol
        self.left = left
        self.right = right


def build_empty_result(file_path):
    return {
        "file_type": "bitmap_image",
        "file_path": file_path,
        "frequency_table": [],
        "code_table": [],
        "stats": {
            "original_size_bytes": 0,
            "compressed_size_bytes": 0,
            "compression_ratio": 0,
            "execution_time_seconds": 0,
            "compression_speed_bytes_per_second": 0,
            "entropy_bits_per_symbol": 0,
            "memory_usage_bytes": 0,
        },
        "data_structure_efficiency": {},
        "compressed_file_path": "",
    }


def calculate_entropy(file_bytes):
    if not file_bytes:
        return 0

    frequencies = {}
    for byte in file_bytes:
        frequencies[byte] = frequencies.get(byte, 0) + 1

    entropy = 0
    total = len(file_bytes)

    for count in frequencies.values():
        probability = count / total
        entropy -= probability * math.log2(probability)

    return round(entropy, 6)


def build_frequency_table(file_bytes):
    frequencies = {}

    for byte in file_bytes:
        frequencies[byte] = frequencies.get(byte, 0) + 1

    return frequencies


def build_huffman_tree(frequencies):
    heap = []
    order = 0

    for symbol in sorted(frequencies):
        heapq.heappush(heap, (frequencies[symbol], order, HuffmanNode(symbol=symbol)))
        order += 1

    if len(heap) == 1:
        return heap[0][2]

    while len(heap) > 1:
        left_frequency, _, left_node = heapq.heappop(heap)
        right_frequency, _, right_node = heapq.heappop(heap)

        merged_node = HuffmanNode(left=left_node, right=right_node)
        heapq.heappush(heap, (left_frequency + right_frequency, order, merged_node))
        order += 1

    return heap[0][2]


def build_codes(node, current_code="", codes=None):
    if codes is None:
        codes = {}

    if node.left is None and node.right is None:
        codes[node.symbol] = current_code or "0"
        return codes

    if node.left is not None:
        build_codes(node.left, current_code + "0", codes)

    if node.right is not None:
        build_codes(node.right, current_code + "1", codes)

    return codes


def pack_bits(bit_string):
    if not bit_string:
        return [], 0

    padding_bits = (8 - (len(bit_string) % 8)) % 8
    bit_string += "0" * padding_bits
    packed_bytes = []

    for index in range(0, len(bit_string), 8):
        packed_bytes.append(int(bit_string[index:index + 8], 2))

    return packed_bytes, padding_bits


def estimate_memory_usage(frequencies, codes, packed_bytes):
    return (
        sys.getsizeof(frequencies)
        + sys.getsizeof(codes)
        + sys.getsizeof(packed_bytes)
    )


def build_data_structure_efficiency(symbol_count):
    return {
        "frequency_dictionary": (
            f"Python dictionary stores frequencies with average lookup/update close to O(1). "
            f"Number of used symbols = {symbol_count}"
        ),
        "heap_priority_queue": "heapq is used to repeatedly extract the two minimum-frequency nodes efficiently.",
        "code_dictionary": "Python dictionary stores the final Huffman codes for direct encoding lookup.",
    }


import struct

def save_compressed_file(file_path, result, frequencies, packed_bytes, padding_bits):
    output_folder = os.path.join(os.path.dirname(__file__), "compressed_files")
    os.makedirs(output_folder, exist_ok=True)

    file_base = os.path.splitext(os.path.basename(file_path))[0]
    file_name = file_base + ".huff"
    compressed_file_path = os.path.join(output_folder, file_name)

    magic = b"HF"
    ext = os.path.splitext(file_path)[1].encode("utf-8")
    ext_len = len(ext)
    
    with open(compressed_file_path, "wb") as file:
        file.write(magic)
        file.write(struct.pack("=B", padding_bits))
        file.write(struct.pack("=H", len(frequencies)))
        
        for symbol, count in frequencies.items():
            file.write(struct.pack("=BI", symbol, count))
            
        file.write(struct.pack("=B", ext_len))
        file.write(ext)
        file.write(bytes(packed_bytes))

    return compressed_file_path



def compress_bitmap_file(file_path):
    with open(file_path, "rb") as file:
        file_bytes = file.read()

    if not file_bytes:
        return build_empty_result(file_path)

    start_time = time.perf_counter()

    frequencies = build_frequency_table(file_bytes)
    tree = build_huffman_tree(frequencies)
    codes = build_codes(tree)
    bit_string = "".join(codes[byte] for byte in file_bytes)
    packed_bytes, padding_bits = pack_bits(bit_string)

    end_time = time.perf_counter()
    execution_time = end_time - start_time

    original_size_bytes = len(file_bytes)
    memory_usage_bytes = estimate_memory_usage(frequencies, codes, packed_bytes)

    result = {
        "file_type": "bitmap_image",
        "file_path": file_path,
        "frequency_table": [
            {"symbol": symbol, "count": count}
            for symbol, count in sorted(frequencies.items())
        ],
        "code_table": [
            {"symbol": symbol, "code": code}
            for symbol, code in sorted(codes.items())
        ],
        "stats": {
            "original_size_bytes": original_size_bytes,
            "compressed_size_bytes": 0,
            "compression_ratio": 0,
            "execution_time_seconds": round(execution_time, 6),
            "compression_speed_bytes_per_second": round(original_size_bytes / execution_time, 2) if execution_time else 0,
            "entropy_bits_per_symbol": calculate_entropy(file_bytes),
            "memory_usage_bytes": memory_usage_bytes,
            "padding_bits": padding_bits,
            "packed_data_size_bytes": len(packed_bytes),
        },
        "data_structure_efficiency": build_data_structure_efficiency(len(frequencies)),
    }

    result["compressed_file_path"] = save_compressed_file(
        file_path=file_path,
        result=result,
        frequencies=frequencies,
        packed_bytes=packed_bytes,
        padding_bits=padding_bits,
    )
    saved_file_size = os.path.getsize(result["compressed_file_path"])
    result["stats"]["saved_compressed_file_size_bytes"] = saved_file_size
    result["stats"]["compressed_size_bytes"] = saved_file_size
    result["stats"]["compression_ratio"] = round(
        original_size_bytes / saved_file_size, 4
    ) if saved_file_size else 0

    return result
