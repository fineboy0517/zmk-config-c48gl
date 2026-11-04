#!/usr/bin/env python3
"""Read KiCad 5 PCB S-expressions without third-party dependencies."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def parse(text):
    stack = [[]]
    for token in re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', text):
        if token == '(':
            node = []
            stack[-1].append(node)
            stack.append(node)
        elif token == ')':
            stack.pop()
        else:
            stack[-1].append(json.loads(token) if token.startswith('"') else token)
    assert len(stack) == 1
    return stack[0][0]

def children(node, name):
    return [x for x in node if isinstance(x, list) and x and x[0] == name]

def footprints():
    pcb = parse((ROOT / 'research/hardware/C48GL.kicad_pcb').read_text())
    result = {}
    for module in children(pcb, 'module'):
        ref = next(x[2] for x in children(module, 'fp_text') if x[1] == 'reference')
        pads = {}
        for pad in children(module, 'pad'):
            nets = children(pad, 'net')
            if nets:
                assert pad[1] not in pads or pads[pad[1]] == nets[0][2]
                pads[pad[1]] = nets[0][2]
        result[ref] = {'at': [float(v) for v in children(module, 'at')[0][1:]], 'pads': pads}
    return result

if __name__ == '__main__':
    parts = footprints()
    print('U1 pads:', json.dumps(parts['U1'], indent=2))
    for i in [1, 5, 21, 25, 29, 45]:
        print(i, parts[f'SW{i}'], parts[f'D{i}'])
