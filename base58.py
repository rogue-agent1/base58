#!/usr/bin/env python3
"""Base58 and Base58Check encoder/decoder (Bitcoin-style).

Encodes/decodes bytes using the Bitcoin Base58 alphabet (no 0OIl).
Base58Check adds a 4-byte SHA-256d checksum.

Usage:
    python base58.py encode "Hello World"
    python base58.py decode "JxF12TrwUP45BMd"
    python base58.py check_encode "00f54a5851e9372b87810a8e60cdd2e7cfd80b6e31"
    python base58.py --test
"""

import hashlib
import sys

ALPHABET = b'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
BASE = 58
ALPHA_MAP = {c: i for i, c in enumerate(ALPHABET)}


def encode(data: bytes) -> str:
    """Encode bytes to Base58."""
    # Count leading zeros
    n_pad = 0
    for b in data:
        if b == 0:
            n_pad += 1
        else:
            break

    # Convert to big integer
    n = int.from_bytes(data, 'big')
    result = []
    while n > 0:
        n, r = divmod(n, BASE)
        result.append(ALPHABET[r:r+1])
    result.reverse()

    return (b'1' * n_pad + b''.join(result)).decode('ascii')


def decode(s: str) -> bytes:
    """Decode Base58 string to bytes."""
    # Count leading 1s
    n_pad = 0
    for c in s:
        if c == '1':
            n_pad += 1
        else:
            break

    n = 0
    for c in s.encode('ascii'):
        if c not in ALPHA_MAP:
            raise ValueError(f"Invalid Base58 character: {chr(c)}")
        n = n * BASE + ALPHA_MAP[c]

    # Convert to bytes
    if n == 0:
        result = b''
    else:
        result = n.to_bytes((n.bit_length() + 7) // 8, 'big')

    return b'\x00' * n_pad + result


def sha256d(data: bytes) -> bytes:
    """Double SHA-256."""
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def check_encode(data: bytes) -> str:
    """Base58Check encode (adds 4-byte checksum)."""
    checksum = sha256d(data)[:4]
    return encode(data + checksum)


def check_decode(s: str) -> bytes:
    """Base58Check decode (verifies checksum)."""
    data = decode(s)
    payload, checksum = data[:-4], data[-4:]
    expected = sha256d(payload)[:4]
    if checksum != expected:
        raise ValueError(f"Checksum mismatch: {checksum.hex()} != {expected.hex()}")
    return payload


def test():
    print("=== Base58 Tests ===\n")

    # Basic encode/decode roundtrip
    for text in [b"Hello World", b"", b"\x00\x00\x01", b"\xff" * 32]:
        encoded = encode(text)
        decoded = decode(encoded)
        assert decoded == text, f"Roundtrip failed for {text.hex()}: {decoded.hex()}"
    print("✓ Encode/decode roundtrip")

    # Known test vectors
    assert encode(b"Hello World") == "JxF12TrwUP45BMd"
    print(f"✓ 'Hello World' → {encode(b'Hello World')}")

    # Leading zeros preserved
    assert encode(b"\x00\x00\x01") == "112"
    assert decode("112") == b"\x00\x00\x01"
    print("✓ Leading zero preservation")

    # Base58Check
    payload = bytes.fromhex("00f54a5851e9372b87810a8e60cdd2e7cfd80b6e31")
    checked = check_encode(payload)
    decoded_payload = check_decode(checked)
    assert decoded_payload == payload
    print(f"✓ Base58Check roundtrip: {checked[:20]}...")

    # Bad checksum
    try:
        check_decode(checked[:-1] + ("2" if checked[-1] != "2" else "3"))
        assert False, "Should have raised"
    except ValueError:
        pass
    print("✓ Bad checksum detected")

    # Invalid character
    try:
        decode("0OIl")
        assert False, "Should have raised"
    except ValueError:
        pass
    print("✓ Invalid characters rejected")

    # Empty
    assert encode(b"") == ""
    assert decode("") == b""
    print("✓ Empty input")

    print("\nAll tests passed! ✓")


def main():
    args = sys.argv[1:]
    if not args or args[0] == "--test":
        test()
    elif args[0] == "encode":
        print(encode(args[1].encode()))
    elif args[0] == "decode":
        print(decode(args[1]))
    elif args[0] == "check_encode":
        print(check_encode(bytes.fromhex(args[1])))
    elif args[0] == "check_decode":
        print(check_decode(args[1]).hex())


if __name__ == "__main__":
    main()
