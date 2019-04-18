#!/usr/bin/python
# Copyright (c) IBM 2019 All Rights Reserved.
# This project is licensed under the Apache License version 2.0, see LICENSE.

from __future__ import print_function
import sys
import re

if len(sys.argv) < 2:
        f = sys.stdin
else:
        f = open(sys.argv[1])

c = f.read(1)

whitespace = re.compile('\s')
wordchar = re.compile('\w')

class Instruction:
	def __init__(self):
		self.head = []
		self.index = 0
		self.forms = []
	def output(self):
		print("Instruction:")
		print("\tDesc:\t",sep="",end="")
		form = ''
		n_head = len(self.head)
		if n_head > 1:
			form = self.head[n_head-1]
		else:
			n_head += 1
		heads = ''
		for head in self.head[0:n_head-1]:
			heads = (heads + ' ' + head).strip()
		print(heads)
		print("\tForm:\t" + form)
		for form in self.forms:
			if len(form) > 0:
				print("\tMnem:\t" + str(form))
		print("--")
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
		print(line_prefix + "\t\"description\":\"" + heads + "\"," + line_postfix)
		print(line_prefix + "\t\"form\":\"" + form + "\"," + line_postfix)
		print(line_prefix + "\t\"mnemonics\":[" + line_postfix)
		comma = ''
		for form in self.forms:
			print(comma,sep="",end="")
			print(line_prefix + "\t\t{" + line_postfix)
			if len(form) > 0:
				print(line_prefix + "\t\t\t\"mnemonic\": \"" + form[0] + "\"",sep="",end="")
			if len(form) > 1:
				print(",")
				print(line_prefix + "\t\t\t\"regs\": \"" + str(form[1:]) + "\"",sep="",end="")
			print("")
			print(line_prefix + "\t\t}",sep="",end="")
			comma = "," + line_postfix + "\n"
		print("")
		print(line_prefix + "\t]" + line_postfix)
		print(line_prefix + "}" + line_postfix,sep="",end="");

inst = ''
insts = []

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

ignored = [ "MIFFile", "Units", "CharUnits", "ColorCatalog", "ConditionCatalog", "BoolCondCatalog", "DefAttrValuesCatalog", "AttrCondExprCatalog", "DictionaryPreferences", "CombinedFontCatalog", "PgfCatalog", "FontCatalog", "RulingCatalog", "TblCatalog", "StyleCatalog", "KumihanCatalog", "Views", "VariableFormats", "MarkerTypeCatalog", "XRefFormats", "Document", "BookComponent", "InitialAutoNums", "Dictionary", "AFrames", "Tbls", "Page", "InlineComponentsInfo" ]

def ParaLine(f,tag):
	global c,inst
	while True:
		try:
			FindElementStart(f)
		except: return
		token = getToken(f)
		if token == "String":
			if tag == "Instruction Head":
				c = f.read(1)
				h = getString(f)
				inst.head.append(h)
			elif tag == "Instruction Form":
				c = f.read(1)
				s = getString(f).strip()
				if len(s) > 0:
					inst.forms[len(inst.forms)-1].append(s.strip())
		FindElementEnd(f)

def PgfTag(f):
	global c,inst,insts
	tag = ''
	c = f.read(1)
	s = getString(f)
	if s == "Instruction Head":
		tag = s
		try:
			# implicit exception on first invocation
			# excplicit exception if last instruction was OK
			# if last instruction was a dud, reuse the object
			if len(inst.head) > 0:
				raise
		except:
			inst = Instruction();
		insts.append(inst)
	elif s in ["Instruction Form", ":p1.inst-syntax", ":p1.inst-syntax-compact"]:
		tag = "Instruction Form"
		inst.forms.append([])
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
			tag = PgfTag(f)
		elif token == "Pgf":
			while True:
				try:
					FindElementStart(f)
				except: break
				token = getToken(f)
				if token == "PgfTag":
					tag = PgfTag(f)
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

while c:
	FindElementStart(f)

	token = getToken(f)
	if token in ignored:
		FindElementEnd(f)
		continue
	if token == "TextFlow":
		TextFlow(f)
	FindElementEnd(f)

for inst in insts:
	inst.head = [x.strip() for x in inst.head]

print("[")
comma=''
for inst in insts:
	print(comma,sep="",end="")
	inst.outputJSON('\t','')
	comma=',\n'
print("\n]")
