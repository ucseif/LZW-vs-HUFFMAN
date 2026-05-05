import heapq
import json
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
        "compressed_file_path": file_path,
        "decompressed_file_path": "",
        "stats": {
            "compressed_file_size_bytes": 0,
            "decompressed_file_size_bytes": 0,
            "execution_time_seconds": 0,
            "decompression_speed_bytes_per_second": 0,
            "memory_usage_bytes": 0,
        },
        "data_structure_efficiency": {},
    }


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


def unpack_bits(packed_bytes, padding_bits):
    bit_string = "".join(format(byte, "08b") for byte in packed_bytes)

    if padding_bits:
        bit_string = bit_string[:-padding_bits]

    return bit_string


def save_decompressed_file(compressed_file_path, file_bytes, original_extension):
    output_folder = os.path.join(os.path.dirname(__file__), "decompressed_files")
    os.makedirs(output_folder, exist_ok=True)

    original_name = os.path.basename(compressed_file_path)
    if original_name.endswith(".huff"):
        original_name = original_name[:-5]

    output_name = original_name + "_decompressed" + original_extension
    output_path = os.path.join(output_folder, output_name)

    with open(output_path, "wb") as file:
        file.write(file_bytes)

    return output_path


def estimate_memory_usage(frequencies, packed_bytes, output_bytes):
    return (
        sys.getsizeof(frequencies)
        + sys.getsizeof(packed_bytes)
        + sys.getsizeof(output_bytes)
    )


def build_data_structure_efficiency(symbol_count):
    return {
        "frequency_dictionary": (
            f"Python dictionary stores frequencies used to rebuild the Huffman tree. "
            f"Number of used symbols = {symbol_count}"
        ),
        "heap_priority_queue": "heapq rebuilds the Huffman tree by combining the smallest frequencies first.",
        "bytearray": "bytearray is used to rebuild the output file efficiently while appending decoded bytes.",
    }


def decompress_bitmap_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        compressed_data = json.load(file)

    frequencies = {int(symbol): count for symbol, count in compressed_data.get("frequencies", {}).items()}
    packed_bytes = compressed_data.get("packed_bytes", [])
    padding_bits = compressed_data.get("padding_bits", 0)
    original_extension = compressed_data.get("original_extension", ".bmp")
    original_length = compressed_data.get("original_length", 0)

    if not packed_bytes and not frequencies:
        return build_empty_result(file_path)

    start_time = time.perf_counter()

    tree = build_huffman_tree(frequencies)
    output_bytes = bytearray()

    if tree.left is None and tree.right is None:
        output_bytes.extend([tree.symbol] * original_length)
    else:
        bit_string = unpack_bits(packed_bytes, padding_bits)
        current = tree

        for bit in bit_string:
            if bit == "0":
                current = current.left
            else:
                current = current.right

            if current.left is None and current.right is None:
                output_bytes.append(current.symbol)
                current = tree

    end_time = time.perf_counter()
    execution_time = end_time - start_time

    decompressed_file_path = save_decompressed_file(file_path, bytes(output_bytes), original_extension)
    memory_usage_bytes = estimate_memory_usage(frequencies, packed_bytes, output_bytes)

    return {
        "file_type": "bitmap_image",
        "compressed_file_path": file_path,
        "decompressed_file_path": decompressed_file_path,
        "stats": {
            "compressed_file_size_bytes": os.path.getsize(file_path),
            "decompressed_file_size_bytes": len(output_bytes),
            "execution_time_seconds": round(execution_time, 6),
            "decompression_speed_bytes_per_second": round(len(output_bytes) / execution_time, 2) if execution_time else 0,
            "memory_usage_bytes": memory_usage_bytes,
        },
        "data_structure_efficiency": build_data_structure_efficiency(len(frequencies)),
    }
