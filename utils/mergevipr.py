#!/usr/bin/python3
# Copyright (c) IBM 2021 All Rights Reserved.
# This project is licensed under the Apache License version 2.0, see LICENSE.

import sys
import json
import argparse

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
	description='''
Merge Power Vector Intrinsics Programming Reference JSON data info
PowerISA JSON data.
''', epilog='''
$ ''' + sys.argv[0] + ''' --pvipr PowerVIPR.json src/ISA.json > ISA-vipr.json
''')
parser.add_argument('--debug', action='store_true', help='enable debugging output')
parser.add_argument('--pvipr', metavar='PVIPR', required=True, help='Power VIPR JSON database')
parser.add_argument('file',
	nargs='?',
	help="the ISA LaTeX document(s) to process (default: standard input)",
	default=None)
params = parser.parse_args()

f = sys.stdin
if params.file != None:
    f = open (params.file)
powerisa = json.load (f)
f.close ()

powervipr = json.load (open (params.pvipr))
powerisa['intrinsics'] = powervipr
map = {}
for intrinsic in powervipr:
    for instruction in intrinsic['instructions']:
        if instruction in map:
            map[instruction].append (intrinsic['mnemonic'])
        else:
            map[instruction] = [ intrinsic['mnemonic'] ]
for instruction in powerisa['instructions']:
    intrinsics = []
    for mnemonic in instruction['mnemonics']:
        if mnemonic['mnemonic'] in map:
            intrinsics += map[mnemonic['mnemonic']]
    instruction['intrinsics'] = intrinsics
print (json.dumps (powerisa, indent=4))
