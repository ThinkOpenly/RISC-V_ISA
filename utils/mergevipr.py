#!/usr/bin/python3
# Copyright (c) IBM 2022 All Rights Reserved.
# This project is licensed under the Apache License version 2.0, see LICENSE.

import sys
import json
import argparse

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
	description='''
Merge Power Vector Intrinsics Programming Reference JSON data info
PowerISA JSON data.
''', epilog='''
$ ''' + sys.argv[0] + ''' --pvipr PowerVIPR.json -o VIPRmergedjsonOutput.json LaTeX2jsonOutput.json
''')
parser.add_argument('--debug', action='store_true', help='enable debugging output')
parser.add_argument('--pvipr', metavar='PVIPR', required=True, help='Power VIPR JSON database')
parser.add_argument('-o', '--output', help="name of file that result is output to", metavar = 'Output')
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

powervipr = json.load (open (params.pvipr, encoding='utf-8'))
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
            for intrinsic in map[mnemonic['mnemonic']]:
                if intrinsic not in intrinsics:
                    intrinsics.append(intrinsic)
    instruction['intrinsics'] = intrinsics

for intrinsic in powerisa['intrinsics']:
    headerData = intrinsic['type_signatures']['var_heads']
    newheaders = []
    for header in headerData:
        newheaderData = {}
        key = header
        if 'implementation' in key.lower():
            key = "implementation"
        newheaderData['key'] = key
        newheaderData['header'] = header
        newheaders.append(newheaderData)
    intrinsic['type_signatures']['var_heads'] = newheaders
    list = intrinsic['type_signatures']['list']
    id = 0
    newlist = []
    for sig in list:
        newsig = {}
        newsig['id'] = str(id)
        index = 0
        for field in sig:
            newsig[newheaders[index]['key']] = field
            index += 1
        newlist.append (newsig)
        id += 1
    intrinsic['type_signatures']['list'] = newlist

if(params.output):
    jsonFileOutput = open(params.output, 'w')
    jsonFileOutput.write(json.dumps (powerisa, indent=4))
    jsonFileOutput.write('\n')
    jsonFileOutput.close()

else:
    print(json.dumps (powerisa, indent=4))

