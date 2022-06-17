#!/usr/bin/env python3
import argparse
import numpy as np


KEY_FSC = '930%&g/2ANUBIS=!s?p$'
KEY_VSC = 'tz023416'


def rearranged(data, len_op):
    return np.append(np.flip(data[:len_op]), data[len_op:])


def shifted(mode, offset, data, len_op):
    ar = np.arange(offset + len_op, offset + len_op + len(data), dtype='u1')
    return data + ar if mode else data - ar


def diffed(mode, data):
    return np.cumsum(data, dtype='u1') if mode else np.append(data[0], np.diff(data))


def crypt(mode, data, key):
    data = np.frombuffer(data, dtype='u1')
    key = np.frombuffer(key.encode(), dtype='u1')
    if mode == 0:
        key = rearranged(key, len(key))
        combined = diffed(0, data)
        len_op = len(data)
    else:
        combined = np.append(key, data)
        len_op = len(combined)

    for i in range(0, len(key), 2):
        modulo = key[i + mode] % 3
        if modulo == 0:
            combined = rearranged(combined, len_op)
        elif modulo == 1:
            combined = shifted(mode, key[i + 1 - mode], combined, len_op)
        elif modulo == 2:
            combined = diffed(mode, combined)

    if mode:
        return diffed(mode, combined).tobytes()
    else:
        return combined[len(key):].tobytes()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Decrypt or encrypt .fsc and .vsc files.')
    parser.add_argument('src', type=str,
                        help='source file')
    parser.add_argument('dest', type=str,
                        help='destination file')
    parser.add_argument('--encrypt', '-e', action='store_true',
                        default=False,
                        help='encrypt the file')
    parser.add_argument('--fsc', '-f', action='store_true',
                        default=True,
                        help='use .fsc default key')
    parser.add_argument('--vsc', '-v', action='store_true',
                        default=False,
                        help='use .vsc default key')
    parser.add_argument('--key', '-k', type=str,
                        help='specify custom key')
    args = parser.parse_args()

    if args.fsc:
        key = KEY_FSC
    elif args.vsc:
        key = KEY_VSC
    else:
        key = args.key

    with open(args.src, 'rb') as f_src:
        with open(args.dest, 'wb') as f_dest:
            f_dest.write(crypt(args.encrypt, f_src.read(), key))