#!/usr/bin/python3
# Copyright (c) IBM 2022 All Rights Reserved.
# This project is licensed under the Apache License version 2.0, see LICENSE.

import sys
from pylatexenc.latexwalker import LatexWalker, LatexMacroNode, LatexGroupNode, LatexCharsNode, LatexEnvironmentNode, LatexMathNode, LatexSpecialsNode
import os
import re
import argparse

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
	description='''
Extract ISA information from LaTeX document, emit JSON
''', epilog='''
$ ''' + sys.argv[0] + ''' --db PowerISAinstructions.txt -o LaTeX2jsonOutput.json PowerISA.tex
''')
parser.add_argument('--debug', action='store_true', help='enable debugging output')
parser.add_argument('--db', metavar='DB', help='instruction database')
parser.add_argument('-o', '--output', help="name of file that json is output to", metavar = 'Output')
parser.add_argument('files',
	nargs=argparse.REMAINDER,
	help="the ISA LaTeX document(s) to process (default: standard input)",
	metavar='ARG',
	default=None)
params = parser.parse_args()

def dprint (out):
    global params
    if params.debug:
        print (out)

class ISADB:
    def __init__ (self, name, operands, fields, level, format):
        self.operands = operands
        self.name = name
        self.fields = fields
        self.level = level
        self.format = format
db = {}

class Field:
    def __init__ (self, name_or_value = '', length = 0):
        self.name_or_value = name_or_value
        self.length = length

if params.db:
    with open (params.db) as f:
        for line in f:
            if not '-+-' in line:
                continue
            else:
                break
        for line in f:
            line = [ x.strip () for x in line.split ('|') ]
            (num, procs, vers, stat, rfc, book, priv, mode, format, prefix, po, suffix, compliance, locat, aocat, mnemonic, operands, name, pfield_defs, field_defs, junk) = line
            if mnemonic == '':
                # ignore reserved opcodes without mnemonics
                continue
            exprs = [mnemonic]
            mnemonics = []
            while len(exprs) > 0:
                exprs_next = []
                for expr in exprs:
                    m = re.match(r'(.*)(\[[\w|.]\])+(.*)',expr)
                    if m != None:
                        exprs_next.append(f"{m.group(1)}{m.group(3)}")
                        exprs_next.append(f"{m.group(1)}{m.group(2)[1:-1]}{m.group(3)}")
                    else:
                        mnemonics.append (expr)
                exprs = exprs_next
            pos = 0
            fields = []
            for item in pfield_defs.split () + field_defs.split ():
                #print (item)
                length = 0
                if item[0] in [ '0', '1' ]:
                    value = 0
                    if len (fields) > 0 and fields[-1].name_or_value.isdecimal ():
                        value = int (fields[-1].name_or_value)
                        length = fields[-1].length
                    else:
                        fields.append (Field ())
                    for bit in item:
                        value = value * 2 + int (bit)
                        pos += 1
                        length += 1
                    fields[-1].name_or_value = str (value)
                    fields[-1].length = length
                elif item[0] == '/':
                    if len (fields) > 0 and fields[-1].name_or_value == 'reserved':
                        length = fields[-1].length
                    else:
                        fields.append (Field ())
                    length += len(item)
                    fields[-1].name_or_value = 'reserved'
                    fields[-1].length = length
                elif item[0] == '?':
                    if len (fields) > 0 and fields[-1].name_or_value == '?':
                        length = fields[-1].length
                    else:
                        fields.append (Field ())
                    length += len(item)
                    fields[-1].name_or_value = '?'
                    fields[-1].length = length
                else:
                    if len (fields) > 0 and fields[-1].name_or_value == item:
                        length = fields[-1].length
                    else:
                        fields.append (Field ())
                    length += 1
                    fields[-1].name_or_value = item
                    fields[-1].length = length
            for m in mnemonics:
                db[m] = ISADB (name, operands, fields, vers, format) 

        for inst in sorted (db.keys ()):
            length = 0
            for field in db[inst].fields:
                length += field.length
            if not length in [ 32, 64 ]:
                print (f"invalid length {length}")

import io
s = io.StringIO()

t = '    '
c = ''

class Mnemonic:
	def __init__(self, mnemonic, operands, conditions, name, form):
		self.syntax = ''
		self.mnemonic = mnemonic
		self.operands = operands
		self.conditions = conditions
		self.name = name
		self.form = form
		self.release = ''
	def outputJSON(self,f,line_prefix,line_postfix):
		print(line_prefix + t + t + "{" + line_postfix, file=f)
		print(line_prefix + t + t + t + "\"name\": \"" + self.name + "\"",sep="",end="", file=f)
		print(",", file=f)
		print(line_prefix + t + t + t + "\"form\": \"" + self.form + "\"",sep="",end="", file=f)
		print(",", file=f)
		print(line_prefix + t + t + t + "\"mnemonic\": \"" + self.mnemonic + "\"",sep="",end="", file=f)
		print(",", file=f)
		print(line_prefix + t + t + t + "\"operands\": [ ",sep="",end="", file=f)
		comma = ''
		if self.operands != None:
			for operand in self.operands.split(','):
				print(comma + "\"" + operand + "\"",sep="",end="", file=f)
				comma = ", "
		print(" ]," + line_postfix, file=f)
		if self.conditions != None:
			print(line_prefix + t*3 + "\"conditions\": [ " + line_postfix,sep="", file=f)
			comma = ''
			for condition in self.conditions[1:-1].split():
				(field, value) = condition.split('=')
				print(comma,end="", file=f)
				print(line_prefix + t*4 + "{ \"field\": \"" + field + "\", \"value\": \"" + value + "\" }" + line_postfix,sep="",end="", file=f)
				comma = "," + line_postfix + "\n"
			print(file=f)
			print(line_prefix + t*3 + "]," + line_postfix,sep="", file=f)
		print(line_prefix + t + t + t + "\"release\": \"" + str(self.release) + "\"",sep="", file=f)
		print(line_prefix + t + t + "}",sep="",end="", file=f)

class Instruction:
	def __init__(self):
		self.mnemonics = []
		self.form = ""
		self.code = []
		self.body = []
		self.category = ''
		self.layout = None
		self.book = ''
	def outputJSON(self,f,line_prefix,line_postfix):
		print(line_prefix + "{" + line_postfix, file=f)
		print(line_prefix + t + "\"category\": \"" + self.category + "\"," + line_postfix, file=f)
		print(line_prefix + t + "\"book\": \"" + self.book + "\"," + line_postfix, file=f)
		print(line_prefix + t + "\"mnemonics\": [" + line_postfix, file=f)
		comma = ''
		for mnemonic in self.mnemonics:
			print(comma,sep="",end="", file=f)
			mnemonic.outputJSON(f,line_prefix,line_postfix)
			comma = "," + line_postfix + "\n"
		print(file=f)
		print(line_prefix + t + "]," + line_postfix, file=f)

		print(line_prefix + t + "\"layout\": ",sep="",end="", file=f)
		comma = ''
		print("[" + line_postfix,sep="", file=f)
		if self.layout != None:
			for field in self.layout:
				print (f"{comma}{line_prefix+t}" + t + "{" + f" \"name\": \"{field.name_or_value}\", \"size\": \"{field.length}\"",sep="",end="", file=f)
				print (" }",sep="",end="", file=f)
				comma = "," + line_postfix + "\n"
		else:
			print("\"\"", sep="", end="", file=f)
		print("" + line_postfix, file=f)
		print(line_prefix + t + "]",sep="",end="", file=f)
		print("," + line_postfix, file=f)

		print(line_prefix + t + "\"code\": [" + line_postfix, file=f)
		comma = ''
		for line in self.code:
			print(comma,sep="",end="", file=f)
			print(line_prefix + t + t + "\"" + line + "\"",sep="",end="", file=f)
			comma = "," + line_postfix + "\n"
		print(file=f)
		print(line_prefix + t + "]," + line_postfix, file=f)
		print(line_prefix + t + "\"body\": [" + line_postfix, file=f)
		comma = ''
		for line in self.body:
			print(comma,sep="",end="", file=f)
			print(line_prefix + t + t + "\"" + line.replace ('"', "\\\"") + "\"",sep="",end="", file=f)
			comma = "," + line_postfix + "\n"
		print(file=f)
		print(line_prefix + t + "]" + line_postfix, file=f)
		print(line_prefix + "}" + line_postfix,sep="",end="", file=f)

class InstructionLayout:
	def __init__(self):
		self.fields = {}
	def append(self,field):
		self.fields.append (field)
	def outputJSON(self,f,line_prefix,line_postfix):
		print("[" + line_postfix,sep="", file=f)
		column = 0
		multiword_adjust = 0
		opcode_index = 0
		comma = ''
		while column < len(self.rows[0]):
			col = self.rows[0][column]
			field_start = self.rows[1][column]
			column += 1
			if col.isdecimal():
				field_name = f"opcode"
				field_value = int(col)
			elif col.startswith("/"):
				field_name = "reserved"
				field_value = None
			else:
				field_name = col
				field_value = None

			field_width = 1
			while column < len(self.rows[0]) and len(self.rows[0][column]) == 0:
				field_width += 1
				column += 1
			try:
				field_start = str(int(field_start) + multiword_adjust)
				if column < len(self.rows[0]):
					if self.rows[1][column] == '0' and column > 0:
						multiword_adjust += 32
					field_end = str(int(self.rows[1][column]) + multiword_adjust)
				else:
					field_end = str(multiword_adjust + 32)
				if field_start.isdecimal() and field_end.isdecimal():
					field_width = int(field_end) - int(field_start)
			except: pass
			print (f"{comma}{line_prefix}" + t + "{" + f" \"name\": \"{field_name}\", \"size\": \"{field_width}\"",sep="",end="", file=f)
			if field_value != None:
				print (f", \"value\": \"{field_value}\"",sep="",end="", file=f)
			print (" }",sep="",end="", file=f)
			comma = "," + line_postfix + "\n"
		print("" + line_postfix, file=f)
		print(line_prefix + "]",sep="",end="", file=f)

inst = None
insts = []
book_title = ''
books = {}
title = []
outline = {}
layout = None
layouts = {}

def updateOutline(outline,title):
	if len(title[0]) > 0:
		if title[0] not in outline:
			outline[title[0]] = {}
		if len(title) > 1:
			updateOutline(outline[title[0]],title[1:])

conditions = {}

part = -1
volume = '0'

def process_groupnode_to_chars (nodelist):
    s = ''
    for node in nodelist:
        # TODO: note that this will inadvertently skip over non-strings (macros)
        if node.isNodeType (LatexCharsNode):
            s += node.chars
        elif node.isNodeType (LatexMacroNode):
            if node.macroname in [ '_' ]:
                s += node.macroname
    return s

def process_MathNode_to_chars (nodelist):
    s = ''
    for node in nodelist:
        # TODO: note that this will inadvertently skip over non-strings (macros)
        if node.isNodeType (LatexMacroNode):
            if node.macroname == "leftarrow":
                s += ":="
            elif node.macroname == "neg":
                s += "~"
            elif node.macroname == "not":
                s += "!="
            elif node.macroname == "equiv":
                s += "=="
            elif node.macroname in [ "oplus", "wedge" ]:
                s += "^"
            elif node.macroname == "times":
                s += "*"
            elif node.macroname == "le":
                s += "<="
            elif node.macroname == "ge":
                s += ">="
            elif node.macroname == "div":
                s += "/"
            elif node.macroname in [ "sigma", "Sigma" ]:
                s += node.macroname
            else:
                print (f"Unhandled MathNode MacroNode \"{node.macroname}\"")
        elif node.isNodeType (LatexCharsNode):
            if node.chars == "times":
                # Why have a MathNode/MacroNode AND MathNode/CharsNode for "times" ?
                s += "*"
            else:
                print (f"Unhandled MathNode CharsNode \"{node.chars}\"")
        else:
            print ("Unknown MathNode subnode")
    return s

def process_rtl_nodelist (nodelist):
    s = ''
    i = 0
    while i < len (nodelist):
        node = nodelist[i]
        if node.isNodeType (LatexCharsNode):
            #dprint ("Chars")
            #dprint (node)
            s += node.chars
        elif node.isNodeType (LatexMathNode):
            #dprint ("Math")
            #dprint (node)
            s += process_MathNode_to_chars (node.nodelist)
        elif node.isNodeType (LatexMacroNode):
            if node.macroname in [ 'textsubscript', 'textsuperscript' ]:
                if node.macroname == 'textsubscript':
                    tag = 'sub'
                elif node.macroname == 'textsuperscript':
                    tag = 'sup'
                s += f"<{tag}>"
                i += 1
                node = nodelist[i]
                if node.isNodeType (LatexGroupNode):
                    s += process_groupnode_to_chars (node.nodelist)
                else:
                    print (f"Unhandled text{tag}script node")
                s += f"</{tag}>"
            elif node.macroname in [ '_', '&', '%', '#' ]:
                s += node.macroname
            elif node.macroname in [ ',', 'clearpage', 'setlength' ]:
                # ignore "thin" spaces (?), page breaks, setlength
                pass
            elif node.macroname == '\\':
                s += '\\\\'
            else:
                print (f"Unhandled macro \"{node.macroname}\"")
                print (node)
        elif node.isNodeType (LatexGroupNode):
            print ("Unhandled Group")
            print (node)
        elif node.isNodeType (LatexSpecialsNode):
            if node.specials_chars == '~':
                # ignore non-breaking spaces (?)
                pass
            elif node.specials_chars in [ '``', "''" ]:
                s += '\\"'
            else:
                print (f"Unhandled SpecialsNode \"{node.specials_chars}\"")
        else:
            print ("Unhandled node type")
            print (node)
        i += 1
    return s

def process_descr_nodelist (nodelist):
    s = ''
    i = 0
    while i < len (nodelist):
        node = nodelist[i]
        if node.isNodeType (LatexCharsNode):
            s += node.chars
        elif node.isNodeType (LatexGroupNode):
            s += process_groupnode_to_chars (node.nodelist)
        elif node.isNodeType (LatexSpecialsNode):
            if node.specials_chars == '~':
                # ignore non-breaking spaces (?)
                pass
        i += 1
    return s

current_name = ''
current_form = ''

def process_instrunion_nodelist (nodelist):
    global inst, current_name, current_form
    i = 0
    while i < len (nodelist):
        node = nodelist[i]
        if node.isNodeType (LatexMacroNode):
            dprint (f"Macro {node.macroname}")
            if node.macroname == 'instrhead':
                dprint (node.macroname)
                dprint (node)
            elif node.macroname == 'instrsyntax':
                dprint (node.macroname)
                dprint (node)
                i += 1
                node = nodelist[i]
                if node.isNodeType (LatexGroupNode):
                    dprint (process_groupnode_to_chars (node.nodelist))
                    s = process_groupnode_to_chars (node.nodelist)
                    # TODO: This `replace` can be removed if the source LaTeX is cleaned up.
                    # (https://git.openpower.foundation/isa/PowerISA/issues/4)
                    #s = s.replace (', ',',')
                    s = s.split ()
                    mnemonic = s[0]
                    try:
                        operands = s[1]
                    except:
                        operands = None
                    conditions = ' '.join (s[2:])
                    dprint (mnemonic)
                    dprint (operands)
                    dprint (conditions)
                    mnemonic = Mnemonic (mnemonic, operands, conditions, current_name, current_form)
                    inst.mnemonics.append (mnemonic)
                    if mnemonic.mnemonic in db:
                        inst.layout = db[mnemonic.mnemonic].fields

            elif node.macroname == 'instrheading':
                i += 1
                current_name = process_groupnode_to_chars (nodelist[i].nodelist)
                i += 1
                current_form = process_groupnode_to_chars (nodelist[i].nodelist)
                i += 1

            elif node.macroname == 'newlayout':
                dprint ("newlayout!")
                i += 1
                if nodelist[i].isNodeType (LatexCharsNode):
                    args = ''.join(nodelist[i].chars.split())
                    if args[0] != '[' or args[-1] != ']':
                        print ('Poorly formatted arguments for newlayout')
                        continue
                    args = args[1:-1].split(',')
                    form = args[0].split ('=')[1]
                    fields = []
                    n_fields = int (args[1].split ('=')[1])
                    for field in range (n_fields):
                        (arg, field_name) = args[field*2+2].split ('=')
                        (arg, field_len) = args[field*2+3].split ('=')
                        fields.append ([field_name, field_len])
                inst.layout = fields   

        elif node.isNodeType (LatexEnvironmentNode):
            if node.environmentname == 'rtl':
                code = process_rtl_nodelist (node.nodelist)
                for line in code.split("\n"):
                    dprint (f":{line}")
                    inst.code.append (line)
                if len (inst.code) > 0 and inst.code[0] == '':
                    del inst.code[0]
                if len (inst.code) > 0 and inst.code[-1] == '':
                    del inst.code[-1]
            elif node.environmentname == 'instrdescr':
                inst.body = process_descr_nodelist (node.nodelist).split('\n')
        i += 1

def assign_version (mnemonic, version):
    dprint (f"assign_version (\"{mnemonic}\", \"{version}\"")
    global insts
    # Unfortunately, the "dot" ('.') character will match any character in
    # re.match (), below.  So, use a character without special meaning instead.
    # '/' seems to work...
    # pattern = '^' + re.sub (r"\[([\w\.])\]", '\\1{0,1}', mnemonic) + '$'
    encoded_mnemonic = mnemonic.replace ('.', '/')
    pattern = '^' + re.sub (r"\[([\w/])\]", '\\1{0,1}', encoded_mnemonic) + '$'
    for inst in insts:
        for m in inst.mnemonics:
            if re.match (pattern, m.mnemonic):
                if m.release == '':
                    m.release = version
                elif m.release != version:
                    print (f"multiple Versions for \"{mnemonic}\": \"{m.release}\" and \"{version}\"")

def process_longtable (nodelist):
    global insts
    i = 0
    while i < len (nodelist):
        node = nodelist[i]
        if node.isNodeType (LatexMacroNode) and node.macroname in [ 'isetwordinstr', 'isetdwordinstr' ]:
            #print (f"*{node.macroname}")
            i += 1
            for column in range (5):
                while not (nodelist[i].isNodeType (LatexSpecialsNode) and nodelist[i].specials_chars == '&'):
                    i += 1
                i += 1
            while not nodelist[i].isNodeType (LatexGroupNode):
                if nodelist[i].isNodeType (LatexMacroNode) and nodelist[i].macroname == 'scalebox':
                    i += 2
                i += 1
            mnemonic = nodelist[i].nodelist[0].chars
            for column in range (5,6):
                while not (nodelist[i].isNodeType (LatexSpecialsNode) and nodelist[i].specials_chars == '&'):
                    i += 1
                i += 1
            while not nodelist[i].isNodeType (LatexGroupNode):
                if nodelist[i].isNodeType (LatexMacroNode) and nodelist[i].macroname == 'scalebox':
                    i += 2
                i += 1
            version = nodelist[i].nodelist[0].chars
            assign_version (mnemonic, version)
        i += 1

def process_nodelist (nodelist):
    global insts, inst, part, volume, book_title, books, outline, dir
    i = 0
    while i < len (nodelist):
        node = nodelist[i]
        if node.isNodeType (LatexMacroNode):
            if node.macroname in ['input', 'include']:
                dprint (node)
                filename = process_groupnode_to_chars (node.nodeargd.argnlist[0].nodelist)
                try:
                    f = open (dir + filename)
                except:
                    filename += '.tex'
                    f = open (dir + filename)
                dprint (f"Processing \"{filename}\"...")
                process_file (f)
                dprint (f"Completed  \"{filename}\".")
                f.close ()
            elif node.macroname == 'part':
                dprint (node)
                part += 1
                dprint (f"part {part}")
                i += 1
                node = nodelist[i]
                if node.isNodeType (LatexGroupNode):
                    s = process_groupnode_to_chars (node.nodelist)
                    dprint (s)
                    book_title = s
                    # hack to make Book I be part 1
                    if book_title == "Preface":
                        part = 0
                    dprint (book_title)
                    # TODO: Should volume be converted to roman numeral?
                    if part == 1:
                        volume = 'I'
                    elif part == 2:
                        volume = 'II'
                    elif part == 3:
                        volume = 'III'
                    if volume not in books:
                        dprint (f"TITLE {book_title}")
                        books[volume] = book_title
            elif node.macroname == 'chapter':
                dprint (f"chapter ...")
                try:
                    dprint (node)
                    dprint (node.nodeargd.argnlist[2].nodelist)
                    dprint (f"TITLE: {node.nodeargd.argnlist[2].nodelist[0].chars}")
                    book_title = node.nodeargd.argnlist[2].nodelist[0].chars
                except: pass
            #elif node.macroname in [ 'isetwordinstr', 'isetdwordinstr' ]:
            #    print (f"{node.macroname}!")
        elif node.isNodeType (LatexEnvironmentNode):
            if node.environmentname == 'instrunion':
                dprint ("instrunion!")
                inst = Instruction ()
                insts.append (inst)
                inst.book = volume
                try:
                    inst.category = book_title
                except:
                    inst.category = '0'
                process_instrunion_nodelist (node.nodelist)
                #inst.outputJSON (sys.stdout, '  ', '')
                updateOutline(outline,[book_title])
            elif node.environmentname == 'longtable':
                #print ('longtable!')
                process_longtable (node.nodelist)
            elif node.environmentname == 'document':
                dprint ('begin{document}')
                process_nodelist (node.nodelist)
        i += 1

def process_file (f):
    data = f.read ()

    l = LatexWalker (data)

    (nodelist, pos, length) = l.get_latex_nodes ()

    process_nodelist (nodelist)

dir = './'
if len (params.files) == 0:
    process_file (sys.stdin)
else:
    for file in params.files:
        dir = os.path.dirname (file) + '/'
        f = open (file)
        dprint (f"Processing \"{file}\"...")
        process_file (f)
        dprint (f"Completed  \"{file}\".")
        f.close ()

# post-processing...

forms = []
books_with_insts = set()
for inst in insts:
	#inst.head = [x.strip() for x in inst.head]
	# hack to get HardHyphen properly inline in Instruction Head
	#if len(inst.head) > 2 and inst.head[-2] == '-' and inst.head[-1] == 'form':
	#	inst.head = inst.head[0:-3] + [ f"{inst.head[-3]}-form" ]
	# hack to combine long form types across minor font changes
	#if len(inst.head) > 1 and inst.head[-2].endswith(':'):
	#	inst.head = inst.head[0:-2] + [ f"{inst.head[-2]}{inst.head[-1]}" ]

	#heads = ''
	#for head in inst.head:
	#	heads = (heads + ' ' + head).strip()
	#(inst.head, space, inst.form) = heads.rpartition(' ')
	#if inst.form not in forms and len(inst.form) > 0:
	#if inst.form not in forms:
	#	forms.append(inst.form)
	for mnemonic in inst.mnemonics:
		if mnemonic.form not in forms:
			forms.append (mnemonic.form)

	books_with_insts.add (inst.book)

forms.sort()

print ("{", file=s)

print (t + "\"instructions\": [", file=s)
comma=''
for inst in insts:
	# hack because some empty instructions are sneaking through, because of ATbls not being suppressed, I think
	if True:
		print (comma,sep="",end="", file=s)
		inst.outputJSON(s,t+t,'')
		comma=',\n'
print (file=s)
print (t + "]",sep="",end="", file=s)

print (",", file=s)
print (t + "\"forms\": [", file=s)
comma=''
for form in forms:
	print (f"{comma}{t*2}\"{form}\"",sep="",end="", file=s)
	comma=',\n'
print (file=s)
print (t + "]",sep="",end="", file=s)

def printOutline(f,outline,line_prefix):
	print (",", file=f)
	print (line_prefix + "\"chapters\": [",sep="",end="", file=f)
	if len(outline) > 0:
		print (file=f)
		comma=''
		for c in outline:
			print (comma + line_prefix + t + "{", file=f)
			print (line_prefix + t + t + "\"name\": \"" + c + "\"",sep="",end="", file=f)
			printOutline(f,outline[c],line_prefix+t+t)
			print (file=f)
			comma=',\n'
			print (line_prefix + t + "}",sep="",end="", file=f)
		print ("\n" + line_prefix,sep="",end="", file=f)
	print ("]",sep="",end="", file=f)

printOutline(s,outline,t)

print (",", file=s)
print (t + "\"books\": [",sep="",end="", file=s)
comma=''
for book in books:
    if book in books_with_insts:
        print (comma, sep="", file=s)
        print (t*2 + "{", sep="", file=s)
        print (t*3 + "\"shortname\": \"" + book + "\",", sep="", file=s)
        print (t*3 + "\"title\": \"" + books[book] + "\"", sep="", file=s)
        print (t*2 + "}", sep="", end="", file=s)
        comma = ','
print (file=s)
print (t + "]", sep="",end="", file=s)
print (file=s)

print ("}", end="", file=s)

dprint (s.getvalue ())

import json
j = json.loads (s.getvalue ())

if(params.output):
    jsonFileOutput = open(params.output, 'w')
    jsonFileOutput.write(json.dumps (j, indent=4))
    jsonFileOutput.close()
else:
    print(json.dumps (j, indent=4))
