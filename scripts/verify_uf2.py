#!/usr/bin/env python3
"""Validate nRF52840 UF2 family, block structure and nice!nano application range."""
import hashlib
import struct
import sys
from pathlib import Path

def verify(path):
    data = path.read_bytes()
    assert data and len(data) % 512 == 0, 'Not a whole UF2 block stream'
    blocks = len(data) // 512
    addresses = []
    for index in range(blocks):
        block = data[index*512:(index+1)*512]
        magic0, magic1, flags, addr, size, number, total, family = struct.unpack_from('<8I', block)
        assert (magic0, magic1) == (0x0A324655, 0x9E5D5157)
        assert struct.unpack_from('<I', block, 508)[0] == 0x0AB16F30
        assert flags & 0x2000 and not flags & 0x1
        assert family == 0xADA52840, 'Wrong MCU family'
        assert number == index and total == blocks
        assert 0 < size <= 476
        assert 0x26000 <= addr and addr + size <= 0xEC000, 'Outside application partition'
        addresses.append((addr, size))
    assert min(addr for addr, _ in addresses) == 0x26000
    for (addr, size), (following, _) in zip(addresses, addresses[1:]):
        assert addr + size <= following, 'Overlapping UF2 writes'
    print(f'{path.name}: PASS, {blocks} blocks, {len(data)} bytes, SHA256 {hashlib.sha256(data).hexdigest()}')

if __name__ == '__main__':
    for value in sys.argv[1:]:
        verify(Path(value))
