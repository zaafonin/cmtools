#!/usr/bin/env python3
import argparse
import numpy as np


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Create a .ucm model from Wavefront .obj file.')
    parser.add_argument('obj', type=str,
                        help='source model')
    parser.add_argument('ucm', type=str,
                        help='conversion result')
    parser.add_argument('name', type=str,
                        help='model name')
    args = parser.parse_args()

    with open(args.obj, 'r') as f:
        lines = f.readlines()

    indices = np.ndarray((0, 3), np.uint32)
    vs = np.ndarray((0, 3), np.float32)
    vts = np.ndarray((0, 2), np.float32)
    vns = np.ndarray((0, 3), np.float32)
    kostyl = []
    vertices = np.ndarray((0, 8), np.float32)

    for line in lines:
        if line.startswith('v '):
            vs = np.vstack([vs, np.asarray(line.split()[1:], dtype=np.float32)])
        elif line.startswith('vt '):
            vts = np.vstack([vts, np.asarray(line.split()[1:], dtype=np.float32)])
        elif line.startswith('vn '):
            vns = np.vstack([vns, np.asarray(line.split()[1:], dtype=np.float32)])
        elif line.startswith('f '):
            verts = line.split()[1:]
            ind = np.ndarray((1, 3), np.uint32)
            for i in range(3):
                v, vt, vn = map(lambda x: int(x) - 1, verts[i].split('/'))
                try:
                    idx = kostyl.index((v, vt, vn))
                except ValueError:
                    kostyl.append((v, vt, vn))
                    idx = len(kostyl) - 1
                ind[0][i] = idx
            indices = np.vstack([indices, ind])
    
    for vert in kostyl:
        vertex = np.concatenate((vs[vert[0]], vns[vert[2]], vts[vert[1]]))
        print(vertex)
        vertices = np.vstack([vertices, vertex])

    final = b''.join((
        b'UCM1\x02\x00\x00\x00',
        args.name.encode().ljust(0x48 - 0x08, b'\x00'),
        b'\x01\x00\x00\x00',
        (indices.size // 3).to_bytes(4, byteorder='little'),
        (vertices.size // 8).to_bytes(4, byteorder='little'),
        b'\x00' * 8,
        indices.tobytes(),
        vertices.tobytes(),
    ))
    with open(args.ucm, 'wb') as f:
        f.write(final)