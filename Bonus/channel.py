import random

def simulate_noisy_channel(bit_list, error_probability=0.01):
    
    noisy_bits = []
    flips_count = 0
    
    for bit in bit_list:
        if random.random() < error_probability:
            noisy_bits.append(1 - bit)
            flips_count += 1
        else:
            noisy_bits.append(bit)
            
    return noisy_bits, flips_count
