#!/usr/bin/python3
# Copyright (c) IBM 2020 All Rights Reserved.
# This project is licensed under the Apache License version 2.0, see LICENSE.

import sys
import os
import re
import html

debug = False
next_arg = 1

def dprint (out):
    if debug:
        print (out)

if next_arg < len(sys.argv) and sys.argv[next_arg] == "--debug":
    debug = True
    next_arg += 1

whitespace = re.compile('\s')
wordchar = re.compile('\w')
t = '    '
c = ''

class Mnemonic:
	def __init__(self):
		self.syntax = ''
		self.mnemonic = ''
		self.operands = None
		self.conditions = None
		self.release = ''
	def outputJSON(self,line_prefix,line_postfix):
		print(line_prefix + t + t + "{" + line_postfix)
		print(line_prefix + t + t + t + "\"mnemonic\": \"" + self.mnemonic + "\"",sep="",end="")
		print(",")
		print(line_prefix + t + t + t + "\"operands\": [ ",sep="",end="")
		comma = ''
		if self.operands != None:
			for operand in self.operands.split(','):
				print(comma + "\"" + operand + "\"",sep="",end="")
				comma = ", "
		print(" ]," + line_postfix)
		if self.conditions != None:
			print(line_prefix + t*3 + "\"conditions\": [ " + line_postfix,sep="")
			comma = ''
			for condition in self.conditions[1:-1].split():
				(field, value) = condition.split('=')
				print(comma,end="")
				print(line_prefix + t*4 + "{ \"field\": \"" + field + "\", \"value\": \"" + value + "\" }" + line_postfix,sep="",end="")
				comma = "," + line_postfix + "\n"
			print("")
			print(line_prefix + t*3 + "]," + line_postfix,sep="")
		print(line_prefix + t + t + t + "\"release\": \"" + str(self.release) + "\"",sep="")
		print(line_prefix + t + t + "}",sep="",end="")

class Instruction:
	def __init__(self):
		self.head = []
		self.mnemonics = []
		self.form = ""
		self.code = []
		self.body = []
		self.category = ''
		self.layout = None
		self.book = ''
	def outputJSON(self,line_prefix,line_postfix):
		print(line_prefix + "{" + line_postfix);
		print(line_prefix + t + "\"description\": \"" + self.head + "\"," + line_postfix)
		print(line_prefix + t + "\"form\": \"" + self.form + "\"," + line_postfix)
		print(line_prefix + t + "\"category\": \"" + self.category + "\"," + line_postfix)
		print(line_prefix + t + "\"book\": \"" + self.book + "\"," + line_postfix)
		print(line_prefix + t + "\"mnemonics\": [" + line_postfix)
		comma = ''
		for mnemonic in self.mnemonics:
			print(comma,sep="",end="")
			mnemonic.outputJSON(line_prefix,line_postfix)
			comma = "," + line_postfix + "\n"
		print("")
		print(line_prefix + t + "]," + line_postfix)

		print(line_prefix + t + "\"layout\": ",sep="",end="")
		self.layout.outputJSON(line_prefix+t,line_postfix)
		print("," + line_postfix)

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
	def append(self,layout):
		self.rows[0] += layout.rows[0]
		self.rows[1] += layout.rows[1]
	def outputJSON(self,line_prefix,line_postfix):
		print("[" + line_postfix,sep="");
		column = 0
		opcode_index = 0
		comma = ''
		while column < len(self.rows[0]):
			col = self.rows[0][column]
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
			print (f"{comma}{line_prefix}" + t + "{" + f" \"name\": \"{field_name}\", \"size\": \"{field_width}\"",sep="",end="")
			if field_value != None:
				print (f", \"value\": \"{field_value}\"",sep="",end="")
			print (" }",sep="",end="")
			comma = "," + line_postfix + "\n"
		print("" + line_postfix);
		print(line_prefix + "]",sep="",end="");

inst = None
insts = []
book_title = ''
books = {}
title = []
outline = {}
layout = None
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

def getVariable(name):
    global variables,volume
    value = variables[name]
    value = value.replace ("<$volnum\>",volume)
    dprint (f"getVariable(\"{name}\") = \"{value}\"")
    return value

def updateOutline(outline,title):
	if len(title[0]) > 0:
		if title[0] not in outline:
			outline[title[0]] = {}
		if len(title) > 1:
			updateOutline(outline[title[0]],title[1:])

suppress = False
possibly_in_instruction = False
def ParaLine(f,tag):
	global c,inst,title,outline,suppress,possibly_in_instruction,volume,book_title
	FTag = ''
	if tag == "code_example" and possibly_in_instruction:
		try:
			inst.code.append("")
		except: return
	if tag == "Body" and possibly_in_instruction:
		try:
			if len(inst.head) > 0:
				inst.body.append("")
		except: pass
	if tag == "Instruction Form" and possibly_in_instruction:
		if len(inst.mnemonics[-1].syntax) != 0:
			inst.mnemonics.append(Mnemonic())
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
				inst.book = volume
				updateOutline(outline,title)
				possibly_in_instruction = True
			elif tag == "Instruction Form" and possibly_in_instruction:
				c = f.read(1)
				s = getString(f)
				inst.mnemonics[-1].syntax += s.strip()
			elif tag == "code_example" and possibly_in_instruction:
				c = f.read(1)
				# translate FrameMaker special characters with ASCII equivalents
				s = getString(f)
				if FTag == "Wingding_3":
					s = s.replace('f',':=')
				elif FTag == "symbol":
					s = s.replace(b'\xc2\xac'.decode(),':=')
				s = s.replace(b'\xc2\xac'.decode(),'~').replace(b'\xc2\xa3'.decode(),'<=').replace(b'\xc2\xba'.decode(),'==').replace(b'\xc3\x85'.decode(),'^').replace('\>','>').replace(b'\xc2\xb9'.decode(),'!=').replace(b'\xc2\xb4'.decode(),'*')
				s = html.escape(s)
				if FTag == "subscript":
					s = "<sub>" + s + "</sub>"
				elif FTag == "superscript":
					s = "<sup>" + s + "</sup>"
				inst.code[len(inst.code)-1] += s
			elif tag == "Body" and possibly_in_instruction:
				try:
					c = f.read(1)
					s = getString(f).replace('\>','>').replace('\q','')
					s = html.escape(s)
					if FTag == "subscript":
						s = "<sub>" + s + "</sub>"
					elif FTag == "superscript":
						s = "<sup>" + s + "</sup>"
					inst.body[len(inst.body)-1] += s
				except: pass
			elif tag == "Book Title":
				c = f.read(1)
				book_title += getString (f)
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
			elif tag == "Head_2":
				c = f.read(1)
				h = getString(f)
				dprint (f"{tag} \"{h}\"")
		elif token == "Char" and not suppress and possibly_in_instruction:
			c = f.read(1)
			token = getToken(f)
			if token == "HardHyphen":
				if tag == "Instruction Head":
					inst.head.append('-')
			elif token == "Tab":
				if tag == "Instruction Form":
					#inst.mnemonics[-1].rest.append(' ')
					inst.mnemonics[-1].syntax += ' '
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
			c = f.read(1)
			TblID = getToken(f)
			if inst != None and (tag == "Instruction Form" or TblID in layouts):
				if inst.layout == None:
					inst.layout = layouts[TblID]
				else:
					inst.layout.append(layouts[TblID])
		elif token == "Font" and possibly_in_instruction:
			if tag == "code_example" or tag == "Body":
				while True:
					try:
						FindElementStart(f)
					except: break
					token = getToken(f)
					if token == "FTag":
						c = f.read(1)
						s = getString(f)
						if s == "Wingding_3":
							FTag = "Wingding_3"
						elif s == "Sub" or s == "Sub - compressed":
							FTag = "subscript"
						elif s == "Super" or s == "Super - compressed":
							FTag = "superscript"
						elif s == "":
							FTag = "normal"
					elif token == "FFamily":
						c = f.read(1)
						s = getString(f)
						if s == "Symbol":
							FTag = "symbol"
					elif token == "FPosition":
						c = f.read(1)
						token = getToken(f)
						if token == "FSubscript":
							FTag = "subscript"
					FindElementEnd(f)
		elif token == "Variable":
			if tag == "Book Title":
				while True:
					try:
						FindElementStart(f)
					except: break
					token = getToken(f)
					if token == "VariableName":
						c = f.read(1)
						s = getString(f)
						book_title += getVariable (s)
					FindElementEnd(f)
		FindElementEnd(f)

def xTag(f):
	global c,inst,insts,title,possibly_in_instruction
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
	elif s in [ "Instruction Form", ":p1.inst-syntax", ":p1.inst-syntax-compact", ":p1.inst-syntax.wide", ":p1.inst-syntax compact", ":inst-syntax." ]:
		tag = "Instruction Form"
		if possibly_in_instruction:
			inst.mnemonics.append(Mnemonic())

	# This is a weird one, which sometimes appears as the tag for
	# where the ATbl for the Instruction Layout is found, AND
	# for more things as well, including pseudocode.
	# TODO: figure this out in the general case (or reformat
	# the source data!)
	#
	# elif s in [ ":table.column" ]:
	#	tag = "Instruction Form"

	elif s in [ "code_example", ":xmp.", ":xmp.compact", "code_example first" ]:
		tag = "code_example"
	elif s in [ "Body", ":p1." ]:
		tag = "Body"
	elif s in [ "instruction index" ]:
		tag = s
	elif s in [ "Instruction Layout", "Instruction Layout - compressed", ":inst-encoding." ]:
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
	 	inst = None
	 	tag = ""
	# 	tag = "sub-sub-title"
	# 	title = title[0:2]
	# 	title.append("")
	elif s in [ "Head_3_span" ]:
	 	tag = ""
	# 	tag = "sub-sub-sub-title"
	# 	title = title[0:3]
	# 	title.append("")
	elif s in [ "Title" ]:
		tag = "Book Title"
	return tag

PgfTag = ''
def Para(f):
	global c,inst,insts,PgfTag,outline,book_title
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
			PgfTag = xTag(f)
		elif token == "Pgf":
			while True:
				try:
					FindElementStart(f)
				except: break
				token = getToken(f)
				if token == "PgfTag":
					PgfTag = xTag(f)
				FindElementEnd(f)
		elif token == "ParaLine":
			ParaLine(f,PgfTag)
		else:
			pass
		FindElementEnd(f)

	if PgfTag == "Book Title":
		#updateOutline(outline,book_title)
		# only the first title, please
		if volume not in books:
			books[volume] = book_title
		book_title = ''
		PgfTag = ''
         
	# some silly cleaning...
	try:
		if inst.mnemonics[len(inst.mnemonics)-1] == []:
			del inst.mnemonics[len(inst.mnemonics)-1]
	except: pass

def TextFlow(f):
	global c,possibly_in_instruction
	while True:
		try:
			FindElementStart(f)
		except: break
		token = getToken(f)
		if token == "Para":
			Para(f)
		elif token == "TFTag":
			c = f.read(1)
			s = getString(f)
			if s == "HIDDEN":
				FindElementEnd(f)
				return

		FindElementEnd(f)
	possibly_in_instruction = False

def cell_ParaLine(f):
	global c,suppress
	s = ''
	while True:
		try:
			FindElementStart(f)
		except: break
		token = getToken(f)
		if token == "String" and not suppress:
			c = f.read(1)
			s += getString(f)
		elif token == "Conditional":
			suppress = False
			while True:
				try:
					FindElementStart(f)
				except: break
				token = getToken(f)
				if token == "InCondition":
					c = f.read(1)
					if getString(f) == "tags_both":
						suppress = True
				FindElementEnd(f)
		elif token == "Unconditional":
			suppress = False
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

def setISA(m,ISA):
	for inst in insts:
		for mnemonic in inst.mnemonics:
			if len(mnemonic.syntax) > 0 and mnemonic.syntax.split()[0] == m:
				mnemonic.release = ISA

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
		exprs = [row[6]]
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
		for mnemonic in mnemonics:
			setISA(mnemonic,row[7])
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
					if tag in [ "Instruction Layout", ":inst-encoding." ]:
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

conditions = {}

def Condition (f):
    global c, conditions
    while True:
        try:
            FindElementStart (f)
        except: break
        token = getToken (f)
        if token == "CTag":
            c = f.read(1)
            ctag = getString (f)
        elif token == "CState":
            c = f.read(1)
            conditions[ctag] = getToken (f)
        FindElementEnd (f)

def ConditionCatalog (f):
    while True:
        try:
            FindElementStart(f)
        except: break
        token = getToken(f)
        if token == "Condition":
            Condition(f)
        FindElementEnd(f)

volume = '0'

def BookComponent (f):
    global c, dir, volume
    filename = None
    exclude = False
    volume_style = None
    while True:
        try:
            FindElementStart(f)
        except: break
        token = getToken(f)
        if token == "FileName":
            c = f.read(1)
            filename = getString (f)
        elif token == "ExcludeComponent":
            c = f.read(1)
            token = getToken (f)
            if token == "Yes":
                exclude = True
            elif token == "No":
                exclude = False
            else: print (f"Unrecognized \"ExcludeComponent\" value \"{token}\"")
        elif token == "VolumeNumStart":
            c = f.read(1)
            volume = getToken (f)
        elif token == "VolumeNumStyle":
            c = f.read(1)
            volume_style = getToken (f)
        elif token == "VolumeNumText":
            c = f.read(1)
            volume_text = getString (f)
        FindElementEnd(f)
    if volume_style == 'UCRoman':
        # One could `pip install roman`, but adds a dependency
        # (for little value here)
        if volume == '1':
            volume = 'I'
        elif volume == '2':
            volume = 'II'
        elif volume == '3':
            volume = 'III'
    elif volume_style == 'TextStyle':
        volume = volume_text
    if filename != None and not exclude:
        if filename.startswith ("<c\>"):
            filename = filename.replace ("<c\>",dir + "/",1)
        filename = filename.replace ("<c\>","/")
        if filename.endswith (".fm"):
            filename = filename[0:-3] + ".mif"
        try:
            fr = open (filename)
        except:
            print (f"Warning: failed to open \"{filename}\". Ignoring.",file=sys.stderr)
            return
        dprint (f"Processing \"{filename}\"...")
        process_file (fr)

variables = {}

def VariableFormat (f):
    global c,variables
    while True:
        try:
            FindElementStart (f)
        except: break
        token = getToken (f)
        if token == "VariableName":
            c = f.read(1)
            name = getString (f)
        elif token == "VariableDef":
            c = f.read(1)
            value = getString (f)
        FindElementEnd (f)
    variables[name] = value

def VariableFormats (f):
    global c
    while True:
        try:
            FindElementStart (f)
        except: break
        token = getToken (f)
        if token == "VariableFormat":
            VariableFormat (f)
        FindElementEnd (f)

def process_file (f):
    global c,layout,layouts,suppress,PgfTag,possibly_in_instruction
    possibly_in_instruction = False
    layout = None
    layouts = {}
    suppress = False
    PgfTag = ''

    c = f.read(1)

    while c:
        FindElementStart(f)

        token = getToken(f)
        if token == "TextFlow":
            TextFlow(f)
        elif token == "Tbls":
            Tbls(f)
        elif token == "MIFFile":
            inst = None
        elif token == "ConditionCatalog":
            ConditionCatalog (f)
        elif token == "BookComponent":
            BookComponent (f)
        elif token == "VariableFormats":
            VariableFormats (f)
        FindElementEnd(f)

dir = '.'
if next_arg == len(sys.argv):
    process_file (sys.stdin)
else:
    while next_arg < len(sys.argv):
        dir = os.path.dirname (sys.argv[next_arg])
        f = open(sys.argv[next_arg])
        dprint (f"Processing \"{sys.argv[next_arg]}\"...")
        process_file (f)
        f.close ()
        next_arg += 1

forms = []
books_with_insts = set()
for inst in insts:
	inst.head = [x.strip() for x in inst.head]
	# hack to get HardHyphen properly inline in Instruction Head
	if len(inst.head) > 2 and inst.head[-2] == '-' and inst.head[-1] == 'form':
		inst.head = inst.head[0:-3] + [ f"{inst.head[-3]}-form" ]
	# hack to combine long form types across minor font changes
	if len(inst.head) > 1 and inst.head[-2].endswith(':'):
		inst.head = inst.head[0:-2] + [ f"{inst.head[-2]}{inst.head[-1]}" ]

	heads = ''
	for head in inst.head:
		heads = (heads + ' ' + head).strip()
	(inst.head, space, inst.form) = heads.rpartition(' ')
	if inst.form not in forms and len(inst.form) > 0:
		forms.append(inst.form)

	mnemonics = []
	for mnemonic in inst.mnemonics:
		if mnemonic.syntax != "":
			m = re.fullmatch("^((?P<mnemonic>\w+(\.){,1}))(\s+(?P<operands>[\w,\s\(\)]*)( (?P<conditions>\(.*\))){,1}){,1}\s*",mnemonic.syntax)
			# ISA BUG: some instructions have a period instead of a comma
			if m == None:
				m = re.fullmatch("^((?P<mnemonic>\w+(\.){,1}))(\s+(?P<operands>[\w,\.\s\(\)]*)( (?P<conditions>\(.*\))){,1}){,1}\s*",mnemonic.syntax)
			mnemonic.mnemonic = m.group('mnemonic')
			mnemonic.operands = m.group('operands')
			if mnemonic.operands != None:
				mnemonic.operands = mnemonic.operands.replace(' ','')
				# ISA BUG: some instructions have a period instead of a comma
				mnemonic.operands = mnemonic.operands.replace('.',',')
			mnemonic.conditions = m.group('conditions')
			mnemonics.append(mnemonic)
	inst.mnemonics = mnemonics
	if len(inst.mnemonics) == 0:
		inst.mnemonics.append(Mnemonic())

	books_with_insts.add (inst.book)

forms.sort()

# share code and body from prefix instructions to non-prefix sibling
for i in range(len(insts)-1):
	a = "Prefix " + insts[i].head
	if insts[i+1].head == "Prefixed " + insts[i].head:
		if len(insts[i].code) == 0:
			insts[i].code = insts[i+1].code
		if len(insts[i].body) == 0:
			insts[i].body = insts[i+1].body

#insts.sort(key=lambda inst: inst.head.removeprefix("Prefixed "))
insts.sort(key=lambda inst: inst.head.replace("Prefixed ","",1))

print("{")
print(t + "\"instructions\": [")
comma=''
for inst in insts:
	# hack because some empty instructions are sneaking through, because of ATbls not being suppressed, I think
	if inst.head != "":
		print(comma,sep="",end="")
		inst.outputJSON(t+t,'')
		comma=',\n'
print("")
print(t + "]",sep="",end="")

print(",")
print(t + "\"forms\": [")
comma=''
for form in forms:
	print(f"{comma}{t*2}\"{form}\"",sep="",end="")
	comma=',\n'
print()
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
			print("")
			comma=',\n'
			print(line_prefix + t + "}",sep="",end="")
		print("\n" + line_prefix,sep="",end="")
	print("]",sep="",end="");

printOutline(outline,t)

print(",")
print(t + "\"books\": [",sep="",end="")
comma=''
for book in books:
    if book in books_with_insts:
        print (comma, sep="")
        print (t*2 + "{", sep="")
        print (t*3 + "\"shortname\": \"" + book + "\",", sep="")
        print (t*3 + "\"title\": \"" + books[book] + "\"", sep="")
        print (t*2 + "}", sep="", end="")
        comma = ','
print()
print(t + "]", sep="",end="");
print()

print("}")

