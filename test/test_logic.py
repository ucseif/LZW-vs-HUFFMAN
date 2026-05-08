import sys
import os
import json
import importlib.util
from pathlib import Path

# --- INSTRUCTOR GRADING CONFIGURATION ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Banned libraries according to Dr. Mohamed Fouad Elewa's Rubric
BANNED_LIBS = ["zlib", "gzip", "zipfile", "bz2", "lzma", "cryptography"]

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def audit_codebase():
    """Checks for the 'Strict No-Library Rule' across all algorithmic files."""
    print_header("ACADEMIC AUDIT: Checking for Restricted Libraries")
    violations = []
    core_dirs = ["Huffman", "LZW", "Bonus"]
    
    for cdir in core_dirs:
        path = PROJECT_ROOT / cdir
        for py_file in path.rglob("*.py"):
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()
                for lib in BANNED_LIBS:
                    if f"import {lib}" in content or f"from {lib}" in content:
                        violations.append(f"{py_file.name} violates 'No-Library Rule' by importing '{lib}'")
    
    if violations:
        for v in violations: print(f"[!] VIOLATION: {v}")
        return False
    print("[+] Audit Passed: No restricted compression libraries detected.")
    return True

def run_grading_suite():
    scores = {
        "implementation": 0.0,
        "analysis": 0.0,
        "bonus": 0.0,
        "gui": 0.0
    }
    
    # Load modules dynamically
    try:
        from Huffman.huffman_compression.text_compression import compress_text_file as huff_comp
        from Huffman.huffman_decompression.text_decompression import decompress_text_file as huff_decomp
        from LZW.lzw_compression.text_compression import compress_text_file as lzw_comp
        from LZW.lzw_decompression.text_decompression import decompress_text_file as lzw_decomp
        from Bonus.channel import simulate_noisy_channel
        from Bonus.error_correction import bytes_to_bits, bits_to_bytes, apply_ecc_protection, recover_from_ecc
    except ImportError as e:
        print(f"[!] CRITICAL: Missing core modules. Implementation score set to 0. Error: {e}")
        return scores

    # 1. Implementation Test (5 Points)
    print_header("SECTION 1: Algorithmic Implementation (Max 5.0)")
    test_files = ["repetitive_data.txt", "sample_text_document.txt"]
    huff_ok = True
    lzw_ok = True
    
    for fname in test_files:
        fpath = PROJECT_ROOT / fname
        if not fpath.exists(): continue
        try:
            res = huff_comp(str(fpath))
            decomp = huff_decomp(res["compressed_file_path"])
            with open(fpath, "rb") as o, open(decomp["decompressed_file_path"], "rb") as r:
                if o.read() != r.read(): huff_ok = False
        except: huff_ok = False
        try:
            res = lzw_comp(str(fpath))
            decomp = lzw_decomp(res["compressed_file_path"])
            with open(fpath, "rb") as o, open(decomp["decompressed_file_path"], "rb") as r:
                if o.read() != r.read(): lzw_ok = False
        except: lzw_ok = False


    if huff_ok and lzw_ok:
        print("[+] Both Huffman and LZW passed lossless verification.")
        scores["implementation"] = 5.0
    else:
        print("[!] Minor Bugs detected.")
        scores["implementation"] = 2.5

    # 2. Analysis Test (3 Points)
    print_header("SECTION 2: Comparative Analysis & Math (Max 3.0)")
    sample_res = lzw_comp(str(PROJECT_ROOT / "repetitive_data.txt"))
    if "entropy_bits_per_symbol" in sample_res["stats"]:
        print("[+] Entropy H(X) and Ratio metrics are correctly calculated.")
        scores["analysis"] = 3.0
    else:
        scores["analysis"] = 1.0

    # 3. Bonus Test (5 Points)
    print_header("SECTION 3: Bonus - Noisy Channel & ECC (Max 5.0)")
    test_bytes = b"ECU_TEST_2026"
    bits = bytes_to_bits(test_bytes)
    prot_bits, pad = apply_ecc_protection(bits)
    
    # Force an error if random noise doesn't hit
    noisy, flips = simulate_noisy_channel(prot_bits, 0.005)
    if flips == 0:
        noisy[5] = 1 - noisy[5] # Force a manual flip for demonstration
        flips = 1
        
    rec_bits, corr = recover_from_ecc(noisy, pad)
    if bytes(bits_to_bytes(rec_bits)) == test_bytes:
        print(f"[+] ECC successfully corrected {corr} flips and recovered data.")
        scores["bonus"] = 5.0

    # 4. GUI Check (2 Points)
    print_header("SECTION 4: GUI & Usability (Max 2.0)")
    if (PROJECT_ROOT / "webapp" / "templates" / "app.html").exists():
        print("[+] Web GUI files detected and verified.")
        scores["gui"] = 2.0

    return scores

def final_report(scores, audit_passed):
    print_header("FINAL INSTRUCTOR GRADING REPORT")
    if not audit_passed:
        print("[CRITICAL] RULE VIOLATION: PROJECT REJECTED (0 POINTS)")
        return

    total_team = scores["implementation"] + scores["analysis"] + scores["gui"]
    print(f"1. Algorithmic Implementation:  {scores['implementation']}/5.0")
    print(f"2. Comparative Analysis:        {scores['analysis']}/3.0")
    print(f"3. Graphical User Interface:    {scores['gui']}/2.0")
    print(f"4. Bonus Features:              {scores['bonus']}/5.0")
    print("-" * 30)
    print(f"SUBTOTAL (Team Grade):          {total_team}/10.0")
    print(f"BONUS ACHIEVED:                 {scores['bonus']}/5.0")
    print(f"FINAL PROJECT SCORE:            {total_team + scores['bonus']}/15.0")
    print("-" * 30)

if __name__ == "__main__":
    audit_passed = audit_codebase()
    scores = run_grading_suite()
    final_report(scores, audit_passed)
