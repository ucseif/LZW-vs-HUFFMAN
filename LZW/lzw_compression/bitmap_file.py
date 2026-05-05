import math
import json
import os
import sys
import time


def build_empty_result(file_path):
    return {
        "file_type": "bitmap_image",
        "file_path": file_path,
        "original_data": [],
        "codes": [],
        "steps": [],
        "initial_dictionary": {},
        "final_dictionary_size": 0,
        "stats": {
            "original_size_bytes": 0,
            "compressed_size_bytes": 0,
            "number_of_output_codes": 0,
            "compression_ratio": 0,
            "execution_time_seconds": 0,
        },
    }


def build_initial_dictionary():
    dictionary = {}

    for number in range(256):
        dictionary[bytes([number])] = number

    return dictionary


def estimate_compressed_size(codes):
    if not codes:
        return 0

    max_code = max(codes)
    bits_per_code = max(1, math.ceil(math.log2(max_code + 1)))
    return math.ceil((len(codes) * bits_per_code) / 8)


def calculate_entropy(file_bytes):
    if not file_bytes:
        return 0

    frequencies = {}
    for byte in file_bytes:
        frequencies[byte] = frequencies.get(byte, 0) + 1

    entropy = 0
    total_size = len(file_bytes)

    for count in frequencies.values():
        probability = count / total_size
        entropy -= probability * math.log2(probability)

    return round(entropy, 6)


def estimate_memory_usage(dictionary, codes, steps):
    return (
        sys.getsizeof(dictionary)
        + sys.getsizeof(codes)
        + sys.getsizeof(steps)
    )


def build_data_structure_efficiency(final_dictionary_size):
    return {
        "dictionary": (
            f"Python dictionary is used for fast lookup and insert; "
            f"average time is close to O(1). Final dictionary size = {final_dictionary_size}"
        ),
        "codes_list": "Python list is used for output codes; append is efficient and close to O(1).",
        "steps_list": "Python list stores step-by-step tracing for explanation and debugging.",
    }


def save_compressed_file(file_path, result):
    output_folder = os.path.join(os.path.dirname(__file__), "compressed_files")
    os.makedirs(output_folder, exist_ok=True)

    file_name = os.path.basename(file_path) + ".lzw"
    compressed_file_path = os.path.join(output_folder, file_name)

    compressed_data = {
        "algorithm": "LZW",
        "file_type": result["file_type"],
        "original_file_path": file_path,
        "original_extension": os.path.splitext(file_path)[1],
        "initial_dictionary": "ASCII_0_TO_255",
        "codes": result["codes"],
    }

    with open(compressed_file_path, "w", encoding="utf-8") as file:
        json.dump(compressed_data, file)

    return compressed_file_path


def compress_bitmap_file(file_path):
    with open(file_path, "rb") as file:
        file_bytes = file.read()

    if not file_bytes:
        return build_empty_result(file_path)

    start_time = time.perf_counter()

    dictionary = build_initial_dictionary()
    next_code = 256
    current = bytes([file_bytes[0]])
    codes = []
    steps = []

    for step_number, next_byte in enumerate(file_bytes[1:], start=1):
        next_symbol = bytes([next_byte])
        combined = current + next_symbol

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

        if combined in dictionary:
            current = combined
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

        steps.append(step)

    codes.append(dictionary[current])
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

    end_time = time.perf_counter()

    compressed_size_bytes = estimate_compressed_size(codes)
    original_size_bytes = len(file_bytes)
    compression_ratio = original_size_bytes / compressed_size_bytes if compressed_size_bytes else 0
    execution_time = end_time - start_time
    memory_usage_bytes = estimate_memory_usage(dictionary, codes, steps)

    result = {
        "file_type": "bitmap_image",
        "file_path": file_path,
        "original_data": list(file_bytes),
        "codes": codes,
        "steps": steps,
        "initial_dictionary": "ASCII_0_TO_255",
        "final_dictionary_size": len(dictionary),
        "stats": {
            "original_size_bytes": original_size_bytes,
            "compressed_size_bytes": compressed_size_bytes,
            "number_of_output_codes": len(codes),
            "compression_ratio": round(compression_ratio, 4),
            "execution_time_seconds": round(execution_time, 6),
            "compression_speed_bytes_per_second": round(original_size_bytes / execution_time, 2) if execution_time else 0,
            "entropy_bits_per_symbol": calculate_entropy(file_bytes),
            "memory_usage_bytes": memory_usage_bytes,
        },
        "data_structure_efficiency": build_data_structure_efficiency(len(dictionary)),
    }

    result["compressed_file_path"] = save_compressed_file(file_path, result)
    result["stats"]["saved_compressed_file_size_bytes"] = os.path.getsize(result["compressed_file_path"])

    return result
