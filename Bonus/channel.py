import random

def simulate_noisy_channel(bit_list, error_probability=0.01):
    """
    Simulates a Binary Symmetric Channel (BSC).
    Flips each bit in the bit_list with a given probability.
    
    Args:
        bit_list (list of int): List of bits (0 or 1).
        error_probability (float): Probability of a bit flip (0.0 to 1.0).
        
    Returns:
        list of int: The bit list after passing through the noisy channel.
    """
    noisy_bits = []
    flips_count = 0
    
    for bit in bit_list:
        if random.random() < error_probability:
            noisy_bits.append(1 - bit)
            flips_count += 1
        else:
            noisy_bits.append(bit)
            
    return noisy_bits, flips_count
