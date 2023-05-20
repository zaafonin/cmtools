#!/usr/bin/env python3
'''cmworkspace.py

Script for converting a game ./data directory into a workspace (editable
unencrypted scripts that can be batch encrypted back for the game to use)
'''

import argparse
from pathlib import Path

from faktcrypt import crypt


KEY_FSC_1 = '930%&g/2ANUBIS=!s?p$'
KEY_FSC_2 = '1234ghji45%3245?)(2!'
KEY_VSC = 'tz023416'
no_crypt = (
    'scripts/elements/_menu_pipes.fsc',
    'scripts/config/labs.vsc'
) # TODO: Implement no_crypt for other game versions or abolish it altogether 

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Decrypt or encrypt a Crazy Machines game directory.')
    parser.add_argument('game', type=str,
                        help='directory with game files')
    parser.add_argument('workspace', type=str,
                        help='workspace directory')
    parser.add_argument('--encrypt', '-e', action='store_true',
                        default=False,
                        help='encrypt the file')
    args = parser.parse_args()

    path_game = Path(args.game)
    path_workspace = Path(args.workspace)

    if args.encrypt:
        path_dest, path_src = Path(args.game), Path(args.workspace)
    else:
        path_src, path_dest = Path(args.game), Path(args.workspace)

    print('\nProcessing fsc...\n')

    for p in path_src.rglob('*.fsc'):
        fsc_path = p.relative_to(path_src)
        result_path = Path(path_dest / fsc_path)
        result_path.parent.mkdir(parents=True, exist_ok=True)
        if str(fsc_path.as_posix()) in no_crypt:
            result_path.write_bytes(p.read_bytes())
        else:
            result_path.write_bytes(
                crypt(
                    args.encrypt,
                    p.read_bytes(),
                    KEY_FSC_1
                    )
                )
        print("Copying" if str(fsc_path.as_posix()) in no_crypt else (("En" if args.encrypt else "De") + "crypting"),
            fsc_path, '->', result_path)

    print('\nProcessing vsc...\n')

    for p in path_src.rglob('*.vsc'):
        vsc_path = p.relative_to(path_src)
        result_path = Path(path_dest / vsc_path)
        result_path.parent.mkdir(parents=True, exist_ok=True)
        if str(vsc_path.as_posix()) in no_crypt:
            result_path.write_bytes(p.read_bytes())
        else:
            result_path.write_bytes(
                crypt(
                    args.encrypt,
                    p.read_bytes(),
                    KEY_VSC
                    )
                )
        print("Copying" if str(vsc_path.as_posix()) in no_crypt else (("En" if args.encrypt else "De") + "crypting"),
            vsc_path, '->', result_path)
    
    print('\nProcessing shd...\n')
    
    for p in path_src.rglob('*.shd'):
        shd_path = p.relative_to(path_src)
        result_path = Path(path_dest / shd_path)
        result_path.parent.mkdir(parents=True, exist_ok=True)
        result_path.write_bytes(p.read_bytes())
        print("Copying", shd_path, '->', result_path)
        
    print(path_game)