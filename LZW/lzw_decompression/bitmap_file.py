import json
import os
import sys
import time


def build_empty_result(file_path):
    return {
        "file_type": "bitmap_image",
        "compressed_file_path": file_path,
        "decompressed_file_path": "",
        "output_data": [],
        "steps": [],
        "final_dictionary_size": 0,
        "stats": {
            "compressed_file_size_bytes": 0,
            "decompressed_file_size_bytes": 0,
            "execution_time_seconds": 0,
        },
    }


def build_initial_dictionary():
    dictionary = {}

    for number in range(256):
        dictionary[number] = bytes([number])

    return dictionary


def save_decompressed_file(compressed_file_path, file_bytes, original_extension):
    output_folder = os.path.join(os.path.dirname(__file__), "decompressed_files")
    os.makedirs(output_folder, exist_ok=True)

    original_name = os.path.basename(compressed_file_path)
    if original_name.endswith(".lzw"):
        original_name = original_name[:-4]

    output_name = original_name + "_decompressed" + original_extension
    output_path = os.path.join(output_folder, output_name)

    with open(output_path, "wb") as file:
        file.write(file_bytes)

    return output_path


def estimate_memory_usage(dictionary, output_bytes, steps):
    return (
        sys.getsizeof(dictionary)
        + sys.getsizeof(output_bytes)
        + sys.getsizeof(steps)
    )


def build_data_structure_efficiency(final_dictionary_size):
    return {
        "dictionary": (
            f"Python dictionary is used for reverse translation during decompression; "
            f"average time is close to O(1). Final dictionary size = {final_dictionary_size}"
        ),
        "bytearray": "bytearray is used to rebuild the file efficiently while appending bytes.",
        "steps_list": "Python list stores step-by-step tracing for explanation and debugging.",
    }


def decompress_bitmap_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        compressed_data = json.load(file)

    codes = compressed_data.get("codes", [])
    original_extension = compressed_data.get("original_extension", ".bmp")

    if not codes:
        return build_empty_result(file_path)

    start_time = time.perf_counter()

    dictionary = build_initial_dictionary()
    next_code = 256

    previous = dictionary[codes[0]]
    output_bytes = bytearray(previous)
    steps = [{
        "step": 1,
        "read": codes[0],
        "output": list(previous),
        "entry": "(Nothing to build yet)",
        "new_code": "-",
        "edge_case": False,
    }]

    for step_number, code in enumerate(codes[1:], start=2):
        edge_case = code not in dictionary

        if edge_case:
            current = previous + previous[:1]
        else:
            current = dictionary[code]

        new_entry = previous + current[:1]
        dictionary[next_code] = new_entry
        output_bytes.extend(current)

        steps.append({
            "step": step_number,
            "read": code,
            "output": list(current),
            "entry": {
                "previous": list(previous),
                "first_char_of_current": current[0],
                "new_entry": list(new_entry),
            },
            "new_code": next_code,
            "edge_case": edge_case,
        })

        next_code += 1
        previous = current

    end_time = time.perf_counter()
    execution_time = end_time - start_time

    decompressed_file_path = save_decompressed_file(file_path, bytes(output_bytes), original_extension)
    memory_usage_bytes = estimate_memory_usage(dictionary, output_bytes, steps)

    return {
        "file_type": "bitmap_image",
        "compressed_file_path": file_path,
        "decompressed_file_path": decompressed_file_path,
        "output_data": list(output_bytes),
        "steps": steps,
        "final_dictionary_size": len(dictionary),
        "stats": {
            "compressed_file_size_bytes": os.path.getsize(file_path),
            "decompressed_file_size_bytes": len(output_bytes),
            "execution_time_seconds": round(execution_time, 6),
            "decompression_speed_bytes_per_second": round(len(output_bytes) / execution_time, 2) if execution_time else 0,
            "memory_usage_bytes": memory_usage_bytes,
        },
        "data_structure_efficiency": build_data_structure_efficiency(len(dictionary)),
    }
