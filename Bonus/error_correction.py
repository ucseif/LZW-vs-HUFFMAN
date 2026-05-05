def encode_hamming_7_4(data_bits):
    """
    Encodes 4 bits of data into a 7-bit Hamming codeword.
    Parity bits are at positions 1, 2, 4 (1-indexed).
    
    Args:
        data_bits (list of int): 4 bits of data [d1, d2, d3, d4].
        
    Returns:
        list of int: 7-bit codeword [p1, p2, d1, p4, d2, d3, d4].
    """
    d1, d2, d3, d4 = data_bits
    
    p1 = d1 ^ d2 ^ d4
    p2 = d1 ^ d3 ^ d4
    p4 = d2 ^ d3 ^ d4
    
    return [p1, p2, d1, p4, d2, d3, d4]

def decode_hamming_7_4(codeword):
    """
    Decodes a 7-bit Hamming codeword, correcting up to 1 bit error.
    
    Args:
        codeword (list of int): 7 bits [c1, c2, c3, c4, c5, c6, c7].
        
    Returns:
        tuple: (data_bits, error_detected, error_index)
            data_bits: Corrected 4 data bits.
            error_detected: Boolean, true if an error was found and corrected.
            error_index: The 1-based index of the corrected bit, or 0 if none.
    """
    c1, c2, c3, c4, c5, c6, c7 = codeword
    
    # Calculate syndromes
    s1 = c1 ^ c3 ^ c5 ^ c7
    s2 = c2 ^ c3 ^ c6 ^ c7
    s3 = c4 ^ c5 ^ c6 ^ c7
    
    error_index = s1 + (s2 * 2) + (s3 * 4)
    error_detected = error_index != 0
    
    corrected_codeword = list(codeword)
    if error_detected:
        # Flip the bit at the error index (1-based)
        corrected_codeword[error_index - 1] = 1 - corrected_codeword[error_index - 1]
        
    # Extract data bits from corrected codeword
    # Positions: p1(1), p2(2), d1(3), p4(4), d2(5), d3(6), d4(7)
    d1_corr = corrected_codeword[2]
    d2_corr = corrected_codeword[4]
    d3_corr = corrected_codeword[6]
    d4_corr = corrected_codeword[5] 
    # Wait, let me re-check my mapping.
    # Standard mapping for Hamming(7,4):
    # p1 = b1, covers 1, 3, 5, 7
    # p2 = b2, covers 2, 3, 6, 7
    # p4 = b4, covers 4, 5, 6, 7
    # Data: b3, b5, b6, b7
    
    return [corrected_codeword[2], corrected_codeword[4], corrected_codeword[5], corrected_codeword[6]], error_detected, error_index

def bytes_to_bits(byte_list):
    bits = []
    for byte in byte_list:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return bits

def bits_to_bytes(bit_list):
    bytes_out = []
    for i in range(0, len(bit_list), 8):
        byte = 0
        chunk = bit_list[i:i+8]
        for bit in chunk:
            byte = (byte << 1) | bit
        bytes_out.append(byte)
    return bytes_out

def apply_ecc_protection(bits):
    """Protects a bitstream using Hamming(7,4). Pads if necessary."""
    # Pad to multiple of 4
    padding = (4 - (len(bits) % 4)) % 4
    padded_bits = bits + [0] * padding
    
    encoded_bits = []
    for i in range(0, len(padded_bits), 4):
        chunk = padded_bits[i:i+4]
        encoded_bits.extend(encode_hamming_7_4(chunk))
        
    return encoded_bits, padding

def recover_from_ecc(encoded_bits, padding):
    """Corrects errors and recovers original bitstream."""
    decoded_bits = []
    total_errors = 0
    
    for i in range(0, len(encoded_bits), 7):
        chunk = encoded_bits[i:i+7]
        if len(chunk) < 7: break # Should not happen if correctly protected
        data, detected, _ = decode_hamming_7_4(chunk)
        decoded_bits.extend(data)
        if detected:
            total_errors += 1
            
    # Remove padding
    if padding > 0:
        decoded_bits = decoded_bits[:-padding]
        
    return decoded_bits, total_errors
