#!/usr/bin/env python3
import argparse
import numpy as np


poly = np.dtype([
    ('v1', '<i4'),
    ('v2', '<i4'),
    ('v3', '<i4'),
])
vertex = np.dtype([
    ('x', np.float32),
    ('y', np.float32),
    ('z', np.float32),
    ('i0', np.float32),
    ('i1', np.float32),
    ('wx', np.float32),
    ('wy', np.float32),
    ('wz', np.float32),
])
uv = np.dtype([
    ('u', np.float32),
    ('v', np.float32)
])

parser = argparse.ArgumentParser(
    description='Convert a .ucm to Wavefront .obj file.')
parser.add_argument('src', type=str,
                    help='source file, .ucm')
parser.add_argument('dest', type=str,
                    help='destination file, .obj')
parser.add_argument('dest_mtl', type=str,
                    help='generated material, .mtl')
parser.add_argument('map', type=str, default='texture.png',
                    help='texture map')
args = parser.parse_args()

with open(args.src, 'rb') as f_src:
    print('Reading', args.src, '...')
    b = f_src.read()

    model_name = b[0x08:0x08+16]
    num_polygons = np.frombuffer(b,
                                 offset=0x4c,
                                 count=1,
                                 dtype='<i4')[0]
    num_vertices = np.frombuffer(b,
                                 offset=0x50,
                                 count=1,
                                 dtype='<i4')[0]
    num_submodels = np.frombuffer(b,
                                  offset=0x54,
                                  count=1,
                                  dtype='<i4')[0]
    print(f'Model "{model_name.decode()}" loaded.')
    print('Submodels:\t', num_submodels)
    print('Polygons:\t', num_polygons)
    print('Vertices:\t', num_vertices)

    offset = 0x5c
    print('I\toffset:', hex(offset))

    i_buffer = np.frombuffer(b,
                             offset=offset,
                             count=num_polygons,
                             dtype=poly)
    offset += num_polygons * 4 * 3
    print('V\toffset:', hex(offset))

    v_buffer = np.frombuffer(b,
                             offset=offset,
                             count=num_vertices,
                             dtype=vertex
                             )
    offset += num_vertices * 32
    print('subm\toffset:', hex(offset))

    try:
        submodels = [b[offset + 16*i:offset + 16*i +
                   16].split(b'\x00')[0].decode() for i in range(num_submodels)]
        offset += num_submodels * 16
        print('Submodels:', submodels)
    except Exception as e:
        # TODO: Exception handling
        print(e)

with open(args.dest, 'w') as f_dest:
    f_dest.write(f'mttlib {args.dest_mtl}\n')

    for v in v_buffer:
        #for field in vertex.names:
        #    v[field] = round(v1[field], 2)
        f_dest.write(f"v {v['x']} {v['y']} {v['z']}\n")

    for v in v_buffer:
        #for field in vertex.names:
        #    v[field] = round(v1[field], 2)
        f_dest.write(f"vt {v['wy']} {v['wz'] * -1}\n")

    f_dest.write(f'usemtl mtl\n')

    for i in i_buffer:
        f_dest.write(
            f"f {i['v1'] + 1}/{i['v1'] + 1} {i['v2'] + 1}/{i['v2'] + 1} {i['v3'] + 1}/{i['v3'] + 1}\n")

print(f'Saved to "{args.dest}"!')

# TODO: Proper materials
with open(args.dest_mtl, 'w') as f_mtl:
    f_mtl.write(f'''newmtl mtl
    Ka 1.000000 1.000000 1.000000
Kd 0.640000 0.640000 0.640000
Ks 0.500000 0.500000 0.500000
Ns 96.078431
Ni 1.000000
d 1.000000
illum 0
map_Kd {args.map}
    ''')
