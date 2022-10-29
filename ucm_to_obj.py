#!/usr/bin/env python3
import argparse
from multiprocessing.sharedctypes import Value
import numpy as np


# decimals to round coordinates to
r = 5

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
        f'vtx_buf:\t{num_verts}\n'
        f'Tags:\t{num_tags}\n'
    )
    idx_buf = np.fromfile(f_src,
                          count=num_tris,
                          dtype=tri)
    vtx_buf = np.fromfile(f_src,
                        count=num_verts,
                        dtype=vertex)
    v_dd, vn_dd, vt_dd = [], [], []
    idx_buf_dd = []

    for tri in idx_buf:
        i_dd = []
        for i in range(3):
            x, y, z, nx, ny, nz, tx, ty = vtx_buf[tri[i]]
            v = (round(x, 4), round(y, 4), round(z, 4))
            vn = (round(nx, 4), round(ny, 4), round(nz, 4))
            vt = (round(tx, 4), round(ty, 4))
            # print(v, vn, vt)
            try:
                i_v = v_dd.index(v)
            except:
                i_v = len(v_dd)
                v_dd.append(v)

            try:
                i_vt = vt_dd.index(vt)
            except:
                i_vt = len(vt_dd)
                vt_dd.append(vt)

            try:
                i_vn = vn_dd.index(vn)
            except:
                i_vn = len(vn_dd)
                vn_dd.append(vn)
            i_dd.append((i_v, i_vt, i_vn))
        idx_buf_dd.append(i_dd)

with open(args.dest, 'w') as f_dest:
    f_dest.write(f"o {model_name}\n")

    for v in v_dd:
        f_dest.write(f"v {v[0]} {v[1]} {v[2]}\n")
    for v in vt_dd:
        f_dest.write(f"vt {v[0]} {v[1] * -1}\n")
    for v in vn_dd:
        f_dest.write(f"vn {v[0]} {v[1]} {v[2]}\n")
    for i in idx_buf_dd:
        print(i)
        f_dest.write(
            f"f {i[0][0] + 1}/{i[0][1] + 1}/{i[0][2] + 1} {i[1][0] + 1}/{i[1][1] + 1}/{i[1][2] + 1} {i[2][0] + 1}/{i[2][1] + 1}/{i[2][2] + 1}\n")
print(f'Complete!')
