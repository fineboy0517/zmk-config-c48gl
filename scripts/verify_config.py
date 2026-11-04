#!/usr/bin/env python3
"""Cross-check the shield against independent public QMK and KiCad PCB evidence."""
import hashlib
import json
import re
from generate_layout import generated_layout
from inspect_pcb import ROOT, footprints

def main():
    for source in json.loads((ROOT / 'research/sources.json').read_text())['files']:
        path = ROOT / source['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == source['sha256'], path

    config = (ROOT / 'research/qmk/config.h').read_text()
    row_names = re.search(r'MATRIX_ROW_PINS\s+\{([^}]+)', config)[1].replace(' ', '').split(',')
    col_names = re.search(r'MATRIX_COL_PINS\s+\{([^}]+)', config)[1].replace(' ', '').split(',')
    # ATmega32u4 pad names -> Pro Micro connector numbers (not nRF GPIO numbers).
    connector = {'D1': 2, 'D0': 3, 'D4': 4, 'C6': 5,
                 'F4': 21, 'F5': 20, 'F6': 19, 'F7': 18, 'B1': 15, 'B3': 14}
    overlay = (ROOT / 'boards/shields/c48gl/c48gl.overlay').read_text()
    actual = [int(n) for n in re.findall(r'<&pro_micro (\d+) GPIO_ACTIVE_LOW>', overlay)]
    assert actual == [connector[name] for name in row_names + col_names]

    parts = footprints()
    for row in range(4):
        assert parts['U1']['pads'][str(5 + row)] == f'Row{row}'
    for col in range(6):
        assert parts['U1']['pads'][str(20 - col)] == f'Col{col}'

    keys = json.loads((ROOT / 'research/qmk/info.json').read_text())['layouts']['LAYOUT']['layout']
    assert len(keys) == 48
    assert len({tuple(key['matrix']) for key in keys}) == 48
    for key in keys:
        row, col = key['matrix']
        index = 1 + 4 * col + row % 4 + (24 if row >= 4 else 0)
        sw, diode = parts[f'SW{index}']['pads'], parts[f'D{index}']['pads']
        assert sw['1'] == f'Col{col}'
        # KiCad diode pad 1 = cathode, pad 2 = anode.
        cathode, anode = ('1', '2') if row < 4 else ('2', '1')
        assert diode[cathode] == f'Row{row % 4}'
        assert diode[anode] == sw['2']

    assert (ROOT / 'boards/shields/c48gl/c48gl-layout.dtsi').read_text() == generated_layout()
    # A malformed binding count otherwise causes keys to shift in a layer.
    keymap = (ROOT / 'config/c48gl.keymap').read_text()
    groups = re.findall(r'bindings\s*=\s*<(.*?)>;', keymap, re.S)
    assert len(groups) == 4
    for group in groups:
        assert group.count('&') + group.count('STUDIO_BINDING') == 48
    print('PASS: source hashes, 10 pin mappings, 48 PCB switch/diode paths, transform, Studio geometry, and 4 x 48 bindings.')

if __name__ == '__main__':
    main()
