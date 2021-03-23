#!/usr/bin/python3
# Copyright (c) IBM 2021 All Rights Reserved.
# This project is licensed under the Apache License version 2.0, see LICENSE.

import sys
import json

f = sys.stdin
if len(sys.argv) > 1:
    f = open (sys.argv[1])
powerisa = json.load (f)

powervipr = powerisa['intrinsics']
for intrinsic in powervipr:
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
print (json.dumps (powerisa, indent=4))
