try:
    from .bitmap_file import compress_bitmap_file
    from .text_compression import compress_text_file
except ImportError:
    from bitmap_file import compress_bitmap_file
    from text_compression import compress_text_file


def compress_file(file_path, file_type):
    if file_type == "text":
        return compress_text_file(file_path, "text_document")

    if file_type == "repetitive":
        return compress_text_file(file_path, "highly_repetitive_data_file")

    if file_type == "bitmap":
        return compress_bitmap_file(file_path)

    raise ValueError("file_type must be: text, repetitive, or bitmap")


def print_result(result):
    print("\nFile Type:")
    print(result["file_type"])

    print("\nCode Table Preview:")
    preview = result["code_table"][:10]
    for row in preview:
        print(row)
    if len(result["code_table"]) > 10:
        print("...")

    print("\nStatistics:")
    for key, value in result["stats"].items():
        print(f"{key}: {value}")

    print("\nData Structure Efficiency:")
    for key, value in result["data_structure_efficiency"].items():
        print(f"{key}: {value}")

    print("\nCompressed File Path:")
    print(result["compressed_file_path"])


if __name__ == "__main__":
    file_path = input("Enter file path: ").strip()
    file_type = input("Enter file type (text / repetitive / bitmap): ").strip().lower()

    result = compress_file(file_path, file_type)
    print_result(result)
