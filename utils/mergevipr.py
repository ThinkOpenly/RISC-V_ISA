#!/usr/bin/python3
# Copyright (c) IBM 2021 All Rights Reserved.
# This project is licensed under the Apache License version 2.0, see LICENSE.

import sys
import json

f = sys.stdin
if len(sys.argv) > 1:
    f = open (sys.argv[1])
powervipr = json.load (f)

powerisa = json.load (open ('src/ISA.json'))
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
