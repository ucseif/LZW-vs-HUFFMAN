import importlib.util
import json
from pathlib import Path
from uuid import uuid4

from flask import Flask, jsonify, render_template, request, send_file, url_for
from werkzeug.utils import secure_filename


BASE_DIR = Path(__file__).resolve().parent.parent
WEBAPP_DIR = BASE_DIR / "webapp"
UPLOAD_DIR = WEBAPP_DIR / "uploads"
RUNTIME_DIR = WEBAPP_DIR / "runtime"
COMPARISON_DIR = RUNTIME_DIR / "comparisons"

for directory in [UPLOAD_DIR, RUNTIME_DIR, COMPARISON_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


def load_module(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, str(file_path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


lzw_text_compress_module = load_module(
    "lzw_text_compress_module",
    BASE_DIR / "LZW" / "lzw_compression" / "text_compression.py",
)
lzw_bitmap_compress_module = load_module(
    "lzw_bitmap_compress_module",
    BASE_DIR / "LZW" / "lzw_compression" / "bitmap_file.py",
)
lzw_text_decompress_module = load_module(
    "lzw_text_decompress_module",
    BASE_DIR / "LZW" / "lzw_decompression" / "text_decompression.py",
)
lzw_bitmap_decompress_module = load_module(
    "lzw_bitmap_decompress_module",
    BASE_DIR / "LZW" / "lzw_decompression" / "bitmap_file.py",
)
huffman_text_compress_module = load_module(
    "huffman_text_compress_module",
    BASE_DIR / "Huffman" / "huffman_compression" / "text_compression.py",
)
huffman_bitmap_compress_module = load_module(
    "huffman_bitmap_compress_module",
    BASE_DIR / "Huffman" / "huffman_compression" / "bitmap_file.py",
)
huffman_text_decompress_module = load_module(
    "huffman_text_decompress_module",
    BASE_DIR / "Huffman" / "huffman_decompression" / "text_decompression.py",
)
huffman_bitmap_decompress_module = load_module(
    "huffman_bitmap_decompress_module",
    BASE_DIR / "Huffman" / "huffman_decompression" / "bitmap_file.py",
)
channel_module = load_module(
    "channel_module",
    BASE_DIR / "Bonus" / "channel.py",
)
ecc_module = load_module(
    "ecc_module",
    BASE_DIR / "Bonus" / "error_correction.py",
)


def lzw_compress_dispatch(file_path, file_type):
    if file_type == "bitmap":
        return lzw_bitmap_compress_module.compress_bitmap_file(str(file_path))
    if file_type == "repetitive":
        return lzw_text_compress_module.compress_text_file(str(file_path), "highly_repetitive_data_file")
    return lzw_text_compress_module.compress_text_file(str(file_path), "text_document")


def lzw_decompress_dispatch(file_path, file_type):
    if file_type == "bitmap":
        return lzw_bitmap_decompress_module.decompress_bitmap_file(str(file_path))
    if file_type == "repetitive":
        return lzw_text_decompress_module.decompress_text_file(str(file_path), "highly_repetitive_data_file")
    return lzw_text_decompress_module.decompress_text_file(str(file_path), "text_document")


def huffman_compress_dispatch(file_path, file_type):
    if file_type == "bitmap":
        return huffman_bitmap_compress_module.compress_bitmap_file(str(file_path))
    if file_type == "repetitive":
        return huffman_text_compress_module.compress_text_file(str(file_path), "highly_repetitive_data_file")
    return huffman_text_compress_module.compress_text_file(str(file_path), "text_document")


def huffman_decompress_dispatch(file_path, file_type):
    if file_type == "bitmap":
        return huffman_bitmap_decompress_module.decompress_bitmap_file(str(file_path))
    if file_type == "repetitive":
        return huffman_text_decompress_module.decompress_text_file(str(file_path), "highly_repetitive_data_file")
    return huffman_text_decompress_module.decompress_text_file(str(file_path), "text_document")


ALGORITHMS = {
    "lzw": {
        "label": "LZW",
        "compress": lzw_compress_dispatch,
        "decompress": lzw_decompress_dispatch,
    },
    "huffman": {
        "label": "Huffman",
        "compress": huffman_compress_dispatch,
        "decompress": huffman_decompress_dispatch,
    },
}


app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024 * 1024


def save_upload(file_storage):
    safe_name = secure_filename(file_storage.filename or "uploaded_file")
    saved_name = f"{uuid4().hex[:8]}_{safe_name}"
    saved_path = UPLOAD_DIR / saved_name
    file_storage.save(saved_path)
    return saved_path


def relative_path(path_value):
    path_obj = Path(path_value)
    try:
        return str(path_obj.resolve().relative_to(BASE_DIR.resolve()))
    except Exception:
        return str(path_obj)


def build_download_info(result, operation):
    output_path = result.get("compressed_file_path") if operation == "compress" else result.get("decompressed_file_path")
    output_path = Path(output_path) if output_path else None

    return {
        "path": str(output_path) if output_path else "",
        "relative_path": relative_path(output_path) if output_path else "",
        "filename": output_path.name if output_path else "",
    }


def summarize_result(result, operation, algorithm_key):
    summary = {
        "algorithm": ALGORITHMS[algorithm_key]["label"],
        "operation": operation,
        "file_type": result.get("file_type", ""),
        "stats": result.get("stats", {}),
        "data_structure_efficiency": result.get("data_structure_efficiency", {}),
        "download": build_download_info(result, operation),
    }

    if operation == "compress":
        summary["preview"] = {
            "codes": result.get("codes", [])[:50],
            "code_table": result.get("code_table", [])[:10],
            "final_low": result.get("final_low"),
            "final_high": result.get("final_high"),
            "compressed_code": result.get("compressed_code"),
        }
    else:
        summary["preview"] = {
            "decompressed_file_path": result.get("decompressed_file_path", ""),
        }

    return summary


def run_operation(algorithm_key, operation, file_path, file_type):
    dispatcher = ALGORITHMS[algorithm_key][operation]
    return dispatcher(file_path, file_type)


def comparison_source_file(primary_result, operation, original_upload_path):
    if operation == "compress":
        return original_upload_path
    return Path(primary_result["decompressed_file_path"])


def create_comparison_payload(operation, file_type, selected_algorithm, original_upload_path, primary_result):
    comparison_id = uuid4().hex
    other_algorithm = "huffman" if selected_algorithm == "lzw" else "lzw"
    source_path = comparison_source_file(primary_result, operation, original_upload_path)

    if operation == "compress":
        primary_compare_result = primary_result
    else:
        primary_compare_result = run_operation(selected_algorithm, "compress", source_path, file_type)

    secondary_result = run_operation(other_algorithm, "compress", source_path, file_type)

    payload = {
        "comparison_id": comparison_id,
        "operation": operation,
        "file_type": file_type,
        "source_file": relative_path(source_path),
        "selected_algorithm": selected_algorithm,
        "primary": summarize_result(primary_compare_result, "compress", selected_algorithm),
        "secondary": summarize_result(secondary_result, "compress", other_algorithm),
    }

    with open(COMPARISON_DIR / f"{comparison_id}.json", "w", encoding="utf-8") as file:
        json.dump(payload, file)

    return payload


@app.route("/")
def landing_page():
    return render_template("index.html")


@app.route("/app")
def workspace_page():
    return render_template("app.html")


@app.route("/comparison")
def comparison_page():
    return render_template("comparison.html")


@app.route("/api/process", methods=["POST"])
def process_file():
    uploaded_file = request.files.get("file")
    if not uploaded_file or not uploaded_file.filename:
        return jsonify({"error": "A file is required"}), 400

    operation = request.form.get("operation", "compress")
    file_type = request.form.get("file_type", "text")
    algorithm = request.form.get("algorithm", "lzw")

    if algorithm not in ALGORITHMS:
        return jsonify({"error": "Invalid algorithm"}), 400

    saved_upload_path = save_upload(uploaded_file)
    primary_result = run_operation(algorithm, operation, saved_upload_path, file_type)
    comparison_payload = create_comparison_payload(
        operation=operation,
        file_type=file_type,
        selected_algorithm=algorithm,
        original_upload_path=saved_upload_path,
        primary_result=primary_result,
    )

    return jsonify({
        "success": True,
        "primary": summarize_result(primary_result, operation, algorithm),
        "comparison_id": comparison_payload["comparison_id"],
        "comparison_url": url_for("comparison_page") + f"?id={comparison_payload['comparison_id']}",
    })


@app.route("/api/comparison")
def get_comparison():
    comparison_id = request.args.get("id", "")
    comparison_path = COMPARISON_DIR / f"{comparison_id}.json"

    if not comparison_path.exists():
        return jsonify({"error": "Comparison not found"}), 404

    with open(comparison_path, "r", encoding="utf-8") as file:
        return jsonify(json.load(file))


@app.route("/download")
def download_file():
    requested_path = request.args.get("path", "")
    target_path = Path(requested_path)

    if not target_path.exists():
        return jsonify({"error": "File not found"}), 404

    return send_file(target_path, as_attachment=True, download_name=target_path.name)


@app.route("/api/simulate_channel", methods=["POST"])
def simulate_channel():
    data = request.json
    file_path = Path(data.get("file_path", ""))
    error_prob = float(data.get("error_probability", 0.01))
    
    if not file_path.exists():
        return jsonify({"error": "Compressed file not found"}), 404
        
    with open(file_path, "rb") as f:
        # For simplicity in the demo, we read the JSON-based compressed file
        # and extract the 'packed_bytes' (for Huffman) or 'codes' (for LZW)
        comp_data = json.load(f)
    
    # We'll treat the entire compressed JSON string as the data to be protected
    # to demonstrate end-to-end recovery of the archive itself
    with open(file_path, "rb") as f:
        raw_bytes = f.read()
    
    bits = ecc_module.bytes_to_bits(raw_bytes)
    
    # 1. Protect with ECC
    encoded_bits, padding = ecc_module.apply_ecc_protection(bits)
    
    # 2. Pass through Noisy Channel
    noisy_bits, actual_flips = channel_module.simulate_noisy_channel(encoded_bits, error_prob)
    
    # 3. Recover with ECC
    recovered_bits, corrected_errors = ecc_module.recover_from_ecc(noisy_bits, padding)
    
    # 4. Check integrity
    success = recovered_bits == bits
    recovered_bytes = ecc_module.bits_to_bytes(recovered_bits)
    
    # We don't save the recovered file here, just report stats
    return jsonify({
        "success": success,
        "stats": {
            "original_bits": len(bits),
            "encoded_bits": len(encoded_bits),
            "actual_flips": actual_flips,
            "corrected_errors": corrected_errors,
            "integrity_maintained": success
        }
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8011, debug=True)
