#!/usr/bin/env python3
import argparse
from multiprocessing.sharedctypes import Value
import numpy as np


tri = np.dtype([
    ('v1', '<i4'),
    ('v2', '<i4'),
    ('v3', '<i4'),
])
vertex = np.dtype([
    ('x', np.float32),
    ('y', np.float32),
    ('z', np.float32),
    ('nx', np.float32),
    ('ny', np.float32),
    ('nz', np.float32),
    ('u', np.float32),
    ('v', np.float32),
])

parser = argparse.ArgumentParser(
    description='Convert a .ucm model to Wavefront .obj file.')
parser.add_argument('src', type=str,
                    help='source file, .ucm')
parser.add_argument('dest', type=str,
                    help='destination file, .obj')
args = parser.parse_args()

with open(args.src, 'rb') as f_src:
    print(f'Reading {args.src} ...')
    model_name = f_src.read(0x48)[0x08:].split(b'\x00')[0].decode()
    num_frames, num_tris, num_verts, num_tags, idk = np.fromfile(f_src,
                                                                 count=5,
                                                                 dtype='<i4')
    print(f'Model "{model_name}" loaded.')
    print(
        f'Frames:\t{num_frames}\n'
        f'Tris:\t{num_tris}\n'
        f'Verts:\t{num_verts}\n'
        f'Tags:\t{num_tags}\n'
    )
    idx_buf = np.fromfile(f_src,
                          count=num_tris,
                          dtype=tri)
    frames = []
    ddframes = []
    ddframes_ids = []

    for i in range(num_frames):
        f_dd = []
        f_dd_table = []
        verts = np.fromfile(f_src,
                            count=num_verts,
                            dtype=vertex)
        for i, v in enumerate(verts):
            try:
                ddframes_ids.append(ddframes.index((v['x'], v['y'], v['z'])))
            except ValueError:
                f_dd_table.append(i)
                f_dd.append((v['x'], v['y'], v['z']))
        frames.append(verts)

    try:
        tags = [f_src.read(0x16).split(b'\x00')[0].decode()
                for i in range(num_tags)]
        print(f'Tag names: \n{tags}\n')
    except Exception as e:
        # TODO: Exception handling
        print(e)

with open(args.dest, 'w') as f_dest:
    for i, vtx_buf in enumerate(frames):
        if len(frames) > 1:
            f_dest.write(f"o {model_name}.{i + 1}\n")
        else:
            f_dest.write(f"o {model_name}\n")

        for v in vtx_buf:
            f_dest.write(f"v {v[0]} {v[1]} {v[2]}\n")
        for v in vtx_buf:
            f_dest.write(f"vt {v['u']} {v['v'] * -1}\n")
        for v in vtx_buf:
            f_dest.write(f"vn {v['nx']} {v['ny']} {v['nz']}\n")
        for i in idx_buf:
            f_dest.write(
                f"f {i['v1'] + 1}/{i['v1'] + 1}/{i['v1'] + 1} {i['v2'] + 1}/{i['v2'] + 1}/{i['v2'] + 1} {i['v3'] + 1}/{i['v3'] + 1}/{i['v3'] + 1}\n")
print(f'Complete!')
