#!/usr/bin/python3
# Copyright (c) IBM 2020 All Rights Reserved.
# This project is licensed under the Apache License version 2.0, see LICENSE.

import sys
import re

if len(sys.argv) < 2:
        f = sys.stdin
else:
        f = open(sys.argv[1])

c = f.read(1)

whitespace = re.compile('\s')
wordchar = re.compile('\w')
t = '    '

class Mnemonic:
	def __init__(self):
		self.mnemonic = ''
		self.rest = []
		self.release = ''
	def outputJSON(self,line_prefix,line_postfix):
		print(line_prefix + t + t + "{" + line_postfix)
		print(line_prefix + t + t + t + "\"mnemonic\": \"" + self.mnemonic + "\"",sep="",end="")
		print(",")
		print(line_prefix + t + t + t + "\"regs\": [ ",sep="",end="")
		comma = ''
		for reg in self.rest:
			print(comma + "\"" + reg + "\"",sep="",end="")
			comma = ", "
		print(" ],")
		print(line_prefix + t + t + t + "\"release\": \"" + str(self.release) + "\"",sep="",end="")
		print("")
		print(line_prefix + t + t + "}",sep="",end="")

class Instruction:
	def __init__(self):
		self.head = []
		self.index = 0
		self.forms = []
		self.code = []
		self.body = []
		self.category = ''
		self.layout = []
	def outputJSON(self,line_prefix,line_postfix):
		print(line_prefix + "{" + line_postfix);
		form = ''
		n_head = len(self.head)
		if n_head > 1:
			form = self.head[n_head-1]
		else:
			n_head += 1
		heads = ''
		for head in self.head[0:n_head-1]:
			heads = (heads + ' ' + head).strip()
		print(line_prefix + t + "\"description\": \"" + heads + "\"," + line_postfix)
		print(line_prefix + t + "\"form\": \"" + form + "\"," + line_postfix)
		print(line_prefix + t + "\"category\": \"" + self.category + "\"," + line_postfix)
		print(line_prefix + t + "\"mnemonics\": [" + line_postfix)
		comma = ''
		for form in self.forms:
			print(comma,sep="",end="")
			form.outputJSON(line_prefix,line_postfix)
			comma = "," + line_postfix + "\n"
		print("")
		print(line_prefix + t + "]," + line_postfix)

		print(line_prefix + t + "\"layout\": [" + line_postfix)
		comma = ''
		for row in self.layout:
			print(comma + line_prefix + t + t + "[ ",sep="",end="")
			sep=''
			for col in row:
				print(sep + "\"" + col + "\"",sep="",end="")
				sep = ", "
			print(" ]",sep="",end="")
			comma = "," + line_postfix + "\n"
		print("")
		print(line_prefix + t + "]," + line_postfix)

		print(line_prefix + t + "\"code\": [" + line_postfix)
		comma = ''
		for line in self.code:
			print(comma,sep="",end="")
			print(line_prefix + t + t + "\"" + line + "\"",sep="",end="")
			comma = "," + line_postfix + "\n"
		print("")
		print(line_prefix + t + "]," + line_postfix)
		print(line_prefix + t + "\"body\": [" + line_postfix)
		comma = ''
		for line in self.body:
			print(comma,sep="",end="")
			print(line_prefix + t + t + "\"" + line + "\"",sep="",end="")
			comma = "," + line_postfix + "\n"
		print("")
		print(line_prefix + t + "]" + line_postfix)
		print(line_prefix + "}" + line_postfix,sep="",end="");

class InstructionLayout:
	def __init__(self):
		self.rows = []

inst = ''
insts = []
title = []
outline = {}
layout = ''
layouts = {}

def FindElementStart(f):
	global c
	while c:
		while whitespace.match(c) != None:
			c = f.read(1)
		if c == '`':
			s = c
			while c != "'":
				c = f.read(1)
				s += c
			continue
		if c == '\\':
			c = f.read(1)
			c = f.read(1)
			continue
		if c == '#':
			f.readline()
			c = f.read(1)
			continue
		if c == '<':
			c = f.read(1)
			return
		# failed to find start if MIF element
		raise

def FindElementEnd(f):
	global c
	depth = 0
	while c and (c != '>' or depth != 0):
		if c == '`':
			while c != "'":
				c = f.read(1)
			continue
		if c == '<':
			depth += 1
		elif c == '>':
			depth -= 1
		c = f.read(1)
		if c == '\\':
			c = f.read(1)
			c = f.read(1)
	c = f.read(1)

def getToken(f):
	global c
	token = ''
	while c and wordchar.match(c):
		token += c
		c = f.read(1)
	return token

def getString(f):
	global c
	s = ''
	c = f.read(1)
	while c != "'":
		s += c
		c = f.read(1)
	return s

def updateOutline(outline,title):
	if len(title[0]) > 0:
		if title[0] not in outline:
			outline[title[0]] = {}
		if len(title) > 1:
			updateOutline(outline[title[0]],title[1:])

def ParaLine(f,tag):
	global c,inst,title,outline
	suppress = False
	if tag == "code_example":
		try:
			inst.code.append("")
		except: return
	if tag == "Body":
		try:
			if len(inst.head) > 0:
				inst.body.append("")
		except: pass
	while True:
		try:
			FindElementStart(f)
		except: return
		token = getToken(f)
		if token == "String" and not suppress:
			if tag == "Instruction Head":
				c = f.read(1)
				h = getString(f)
				inst.head.append(h)
				inst.category = title[len(title)-1]
				updateOutline(outline,title)
			elif tag == "Instruction Form":
				c = f.read(1)
				s = getString(f).strip()
				if len(s) > 0:
					if len(inst.forms[len(inst.forms)-1].mnemonic) == 0:
						s = s.strip().split()
						if len(s) > 0:
							inst.forms[len(inst.forms)-1].mnemonic = s[0]
							del s[0]
						if len(s) > 0:
							for r in s:
								if len(r) > 0:
									inst.forms[len(inst.forms)-1].rest.append(r)
					else:
						inst.forms[len(inst.forms)-1].rest.append(s.strip())
			elif tag == "code_example":
				c = f.read(1)
				# translate FrameMaker special characters with ASCII equivalents
				s = getString(f).replace(b'\xc2\xac',':=').replace(b'\xc2\xa3','<=').replace(b'\xc2\xba','not xor').replace(b'\xc3\x85','/').replace('\>','>')
				inst.code[len(inst.code)-1] += s
			elif tag == "Body":
				try:
					c = f.read(1)
					s = getString(f).replace('\>','>')
					inst.body[len(inst.body)-1] += s
				except: pass
			elif tag == "title":
				c = f.read(1)
				title[0] += getString(f)
			elif tag == "sub-title":
				c = f.read(1)
				title[1] += getString(f)
			elif tag == "sub-sub-title":
				c = f.read(1)
				title[2] += getString(f)
			elif tag == "sub-sub-sub-title":
				c = f.read(1)
				title[3] += getString(f)
		elif token == "Conditional":
			suppress = False
			while True:
				try:
					FindElementStart(f)
				except: break
				token = getToken(f)
				if token == "InCondition":
					c = f.read(1)
					s = getString(f)
					if s == "tags_both":
						suppress = True
				FindElementEnd(f)
		elif token == "Unconditional":
			suppress = False
		elif token == "ATbl":
			if tag == "Instruction Form":
				c = f.read(1)
				TblID = getToken(f)
				inst.layout = layouts[TblID].rows
		FindElementEnd(f)

def xTag(f):
	global c,inst,insts,title
	tag = ''
	c = f.read(1)
	s = getString(f)
	if s == "Instruction Head":
		tag = s
		try:
			# implicit exception on first invocation
			# excplicit exception if last instruction was OK
			# if last instruction was a dud, delete it
			if len(inst.head) > 0:
				raise
			del insts[len(insts)-1]
			del inst
		except: pass
		inst = Instruction();
		insts.append(inst)
	elif s in [ "Instruction Form", ":p1.inst-syntax", ":p1.inst-syntax-compact" ]:
		tag = "Instruction Form"
		inst.forms.append(Mnemonic())

	# This is a weird one, which sometimes appears as the tag for
	# where the ATbl for the Instruction Layout is found, AND
	# for more things as well, including pseudocode.
	# TODO: figure this out in the general case (or reformat
	# the source data!)
	#
	# elif s in [ ":table.column" ]:
	#	tag = "Instruction Form"

	elif s in [ "code_example", ":xmp." ]:
		tag = "code_example"
	elif s in [ "Body", ":p1." ]:
		tag = "Body"
	elif s in [ "instruction index" ]:
		tag = s
	elif s in [ "Instruction Layout", "InstructionFormat", "Instruction Layout - compressed", ":inst-encoding." ]:
		tag = "Instruction Layout"
	elif s in [ "Title (Chapter)" ]:
		tag = "title"
		title = [""]
	# May support these later if nested Accordions work...
	elif s in [ "Head_1_span" ]:
	 	tag = ""
	# 	tag = "sub-title"
	# 	title = title[0:1]
	# 	title.append("")
	elif s in [ "Head_2", "Head_2_span" ]:
	 	inst = ''
	 	tag = ""
	# 	tag = "sub-sub-title"
	# 	title = title[0:2]
	# 	title.append("")
	elif s in [ "Head_3_span" ]:
	 	tag = ""
	# 	tag = "sub-sub-sub-title"
	# 	title = title[0:3]
	# 	title.append("")
	return tag

def Para(f):
	global c,inst,insts
	tag = ''
	while True:
		try:
			FindElementStart(f)
		except: break
		token = getToken(f)
		if token == "Unique":
			while whitespace.match(c) != None:
				c = f.read(1)
			token = getToken(f)
		elif token == "PgfTag":
			tag = xTag(f)
		elif token == "Pgf":
			while True:
				try:
					FindElementStart(f)
				except: break
				token = getToken(f)
				if token == "PgfTag":
					tag = xTag(f)
				FindElementEnd(f)
		elif token == "ParaLine":
			ParaLine(f,tag)
		else:
			pass
		FindElementEnd(f)
	# some silly cleaning...
	try:
		if inst.forms[len(inst.forms)-1] == []:
			del inst.forms[len(inst.forms)-1]
	except: pass

def TextFlow(f):
	global c
	while True:
		try:
			FindElementStart(f)
		except: break
		token = getToken(f)
		if token == "Para":
			Para(f)
		FindElementEnd(f)

def cell_ParaLine(f):
	global c
	s = ''
	while True:
		try:
			FindElementStart(f)
		except: break
		token = getToken(f)
		if token == "String":
			c = f.read(1)
			s += getString(f)
		FindElementEnd(f)
	return s
	
def cell_Para(f):
	global c
	s = ''
	while True:
		try:
			FindElementStart(f)
		except: break
		token = getToken(f)
		if token == "ParaLine":
			s += cell_ParaLine(f)
		FindElementEnd(f)
	return s

def CellContent(f):
	global c
	s = ''
	while True:
		try:
			FindElementStart(f)
		except: break
		token = getToken(f)
		if token == "Para":
			s += cell_Para(f)
		FindElementEnd(f)
	return s
	
def Cell(f):
	global c
	s = ''
	while True:
		try:
			FindElementStart(f)
		except: break
		token = getToken(f)
		if token == "CellContent":
			s += CellContent(f)
		FindElementEnd(f)
	return s

def setISA(mnemonic,ISA):
	for inst in insts:
		for form in inst.forms:
			if form.mnemonic == mnemonic:
				form.release = ISA

def Row(f,tag):
	global c,layout
	row = []
	while True:
		try:
			FindElementStart(f)
		except: break
		token = getToken(f)
		if token == "Cell":
			row.append(Cell(f))
		FindElementEnd(f)
	if tag == "instruction index":
		mnemonics = [row[9]]
		for n in re.finditer(r'\[(\w|\.)*\]',row[9]):
			mnemonics_preexpand_list = []
			for s in mnemonics:
				mnemonics_preexpand_list.append(s)
			mnemonics = []
			for s in mnemonics_preexpand_list:
				mnemonics.append(s.replace(n.group(0),'')) 
				mnemonics.append(s.replace(n.group(0),n.group(1))) 
		for mnemonic in mnemonics:
			setISA(mnemonic,row[10])
	elif tag == "Instruction Layout":
		layout.rows.append(row)

def TblBody(f,tag):
	global c
	while True:
		try:
			FindElementStart(f)
		except: break
		token = getToken(f)
		if token == "Row":
			Row(f,tag)
		FindElementEnd(f)

def Tbl(f):
	global c,layout,layouts
	tag = ''
	TblID = ''
	while True:
		try:
			FindElementStart(f)
		except: break
		token = getToken(f)
		if token == "TblTag":
			tag = xTag(f)
			if tag == "Instruction Layout":
				layout = InstructionLayout()
		elif token == "TblID":
			c = f.read(1)
			TblID = getToken(f)
		elif token == "TblBody":
			if tag in [ "instruction index", "Instruction Layout" ]:
				TblBody(f,tag)
		elif token == "TblFormat":
			while True:
				try:
					FindElementStart(f)
				except: break
				token = getToken(f)
				if token == "TblTag":
					tag = xTag(f)
					if tag == "Instruction Layout":
						layout = InstructionLayout()
				FindElementEnd(f)
		FindElementEnd(f)
	if tag == "Instruction Layout":
		layouts[TblID] = layout

def Tbls(f):
	global c
	while True:
		try:
			FindElementStart(f)
		except: break
		token = getToken(f)
		if token == "Tbl":
			Tbl(f)
		FindElementEnd(f)

while c:
	FindElementStart(f)

	token = getToken(f)
	if token == "TextFlow":
		TextFlow(f)
	elif token == "Tbls":
		Tbls(f)
	elif token == "MIFFile":
		inst = ''
	FindElementEnd(f)

for inst in insts:
	inst.head = [x.strip() for x in inst.head]
	forms = []
	for form in inst.forms:
		if form.mnemonic != "":
			forms.append(form)
	inst.forms = forms
	if len(inst.forms) == 0:
		inst.forms.append(Mnemonic())

print("{")
print(t + "\"instructions\": [")
comma=''
for inst in insts:
	print(comma,sep="",end="")
	inst.outputJSON(t+t,'')
	comma=',\n'
print("")
print(t + "]",sep="",end="")

def printOutline(outline,line_prefix):
	print(",")
	print(line_prefix + "\"chapters\": [",sep="",end="")
	if len(outline) > 0:
		print("")
		comma=''
		for c in outline:
			print(comma + line_prefix + t + "{")
			print(line_prefix + t + t + "\"name\": \"" + c + "\"",sep="",end="")
			printOutline(outline[c],line_prefix+t+t)
			comma=',\n'
			print(line_prefix + t + "}",sep="",end="")
		print("\n" + line_prefix,sep="",end="")
	print("]");

printOutline(outline,t)

print("}")
