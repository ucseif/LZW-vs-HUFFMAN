import sys
import os
import json
from pathlib import Path

# Automatically determine project root relative to this script
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Import logic modules
try:
    from Huffman.huffman_compression.text_compression import compress_text_file as huff_compress
    from Huffman.huffman_decompression.text_decompression import decompress_text_file as huff_decompress
    from LZW.lzw_compression.text_compression import compress_text_file as lzw_compress
    from LZW.lzw_decompression.text_decompression import decompress_text_file as lzw_decompress
    from Bonus.channel import simulate_noisy_channel
    from Bonus.error_correction import bytes_to_bits, bits_to_bytes, apply_ecc_protection, recover_from_ecc
except ImportError as e:
    print(f"Import Error: {e}")
    print("Ensure you are running the script from the project root or the test folder.")
    sys.exit(1)

def test_huffman():
    print("\n--- Testing Huffman Logic ---")
    source = PROJECT_ROOT / "repetitive_data.txt"
    
    if not source.exists():
        print(f"Error: {source} not found.")
        return

    # Compress
    print(f"Compressing: {source.name}")
    comp_result = huff_compress(str(source))
    comp_path = comp_result["compressed_file_path"]
    print(f"Ratio: {comp_result['stats']['compression_ratio']}")
    
    # Decompress
    print(f"Decompressing: {os.path.basename(comp_path)}")
    decomp_result = huff_decompress(comp_path)
    decomp_path = decomp_result["decompressed_file_path"]
    
    # Verify
    with open(source, "rb") as f1, open(decomp_path, "rb") as f2:
        original = f1.read()
        recovered = f2.read()
        if original == recovered:
            print("SUCCESS: Data matches exactly.")
        else:
            print("FAILURE: Data mismatch!")

def test_lzw():
    print("\n--- Testing LZW Logic ---")
    source = PROJECT_ROOT / "repetitive_data.txt"
    
    if not source.exists():
        print(f"Error: {source} not found.")
        return

    # Compress
    print(f"Compressing: {source.name}")
    comp_result = lzw_compress(str(source))
    comp_path = comp_result["compressed_file_path"]
    print(f"Ratio: {comp_result['stats']['compression_ratio']}")
    
    # Decompress
    print(f"Decompressing: {os.path.basename(comp_path)}")
    decomp_result = lzw_decompress(comp_path)
    decomp_path = decomp_result["decompressed_file_path"]
    
    # Verify
    with open(source, "rb") as f1, open(decomp_path, "rb") as f2:
        original = f1.read()
        recovered = f2.read()
        if original == recovered:
            print("SUCCESS: Data matches exactly.")
        else:
            print("FAILURE: Data mismatch!")

def test_bonus():
    print("\n--- Testing Bonus (ECC + Noise) Logic ---")
    test_data = b"Information Theory Bonus Test Data"
    print(f"Original Data: {test_data}")
    
    bits = bytes_to_bits(test_data)
    
    # 1. Protect
    print("Applying Hamming(7,4) protection...")
    encoded_bits, padding = apply_ecc_protection(bits)
    
    # 2. Add Noise
    error_prob = 0.005 # 0.5% bit flips
    print(f"Passing through Noisy Channel (p={error_prob})...")
    noisy_bits, actual_flips = simulate_noisy_channel(encoded_bits, error_prob)
    print(f"Bit flips occurred: {actual_flips}")
    
    # 3. Recover
    print("Recovering data using ECC...")
    recovered_bits, corrected_errors = recover_from_ecc(noisy_bits, padding)
    print(f"Errors corrected: {corrected_errors}")
    
    # 4. Verify
    recovered_data = bytes(bits_to_bytes(recovered_bits))
    print(f"Recovered Data: {recovered_data}")
    
    if test_data == recovered_data:
        print("SUCCESS: ECC successfully corrected all channel noise.")
    else:
        print("FAILURE: Noise exceeded ECC correction capacity or logic error.")

if __name__ == "__main__":
    try:
        test_huffman()
        test_lzw()
        test_bonus()
        print("\nAll logical tests completed.")
    except Exception as e:
        print(f"\nAn error occurred during testing: {e}")
        import traceback
        traceback.print_exc()
