#!/usr/bin/env python3
"""Base58 encoding — Bitcoin/IPFS style encoding (no 0OIl)."""
import sys
ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
def encode(data):
    if isinstance(data, str): data = data.encode()
    n = int.from_bytes(data, 'big'); result = []
    while n > 0: n, r = divmod(n, 58); result.append(ALPHABET[r])
    for b in data:
        if b == 0: result.append('1')
        else: break
    return "".join(reversed(result))
def decode(s):
    n = 0
    for c in s: n = n * 58 + ALPHABET.index(c)
    result = n.to_bytes((n.bit_length() + 7) // 8, 'big')
    pad = len(s) - len(s.lstrip('1'))
    return b'\x00' * pad + result
if __name__ == "__main__":
    data = sys.argv[1] if len(sys.argv) > 1 else "Hello World"
    enc = encode(data)
    dec = decode(enc)
    print(f"Input:   {data}")
    print(f"Base58:  {enc}")
    print(f"Decoded: {dec.decode()}")
