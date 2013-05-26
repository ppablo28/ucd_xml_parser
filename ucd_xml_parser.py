# -*- coding: utf-8 -*- 
# Author: Paweł Parafiński
# You can contact me: ppablo28@gmail.com
# This python script parses the text file containing UCD data available here:
# http://www.unicode.org/Public/UNIDATA/NamesList.txt

import argparse
import sys
import re
import logging
from lxml import etree
from itertools import groupby
from xml.dom import minidom

from xml_tags import *
from parser_constants import *

# The default name of the file containing UCD data
_NAME_LISTS_FILE = "NamesList.txt"

# The root of XML
root = etree.Element(Tags.ROOT)

# Logging file
logging.basicConfig(format='%(asctime)s: %(message)s', filename='parser.log',
	level=logging.DEBUG, datefmt='%m/%d/%Y %I:%M:%S %p')

# The parser for script arguments
parser = argparse.ArgumentParser(description='Parse the UCD data.')
parser.add_argument('-n', metavar='Name', type=str,
                   	help='the name of the file with UCD data, default ' + _NAME_LISTS_FILE,
                   	required=False)
parser.add_argument('-o', metavar='output', type=str, help='output name, default NamesList.xml', 
				  	required=False)
parser.add_argument('-C', default=False, action='store_true', required=False, dest='C',
                    help='Whether generate C structure with XML tags and attributes')

# =============================== EXCEPTIONS ====================================== #

class UnknownInput(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return "\nUnknown input: " + repr(self.value)

# ============================ SOME STRING OPERATIONS ============================= #

# Get the first word of the line (use the given delimiter)
def firstWord(line, delimiter=Whitespace.TAB):
	return line[:line.find(delimiter)]

# Check if the character ordinal is valid for XML
def valid_XML_char_ordinal(i):
    return (
        0x20 <= i <= 0xD7FF
        or i in (0x9, 0xA, 0xD)
        or 0xE000 <= i <= 0xFFFD
        or 0x10000 <= i <= 0x10FFFF
    )

# Remove invalid characters and encode the given string with UTF-8
def validateTextForXml(text):
	cleanedText = ''.join([c for c in text if valid_XML_char_ordinal(ord(c))])
 	return unicode(cleanedText, 'UTF-8')

# Split the string with the given delimiter (take care of multiple occurrences)
def splitMultiple(line, delimiter=Whitespace.TAB):
	return [elem for elem in line.split(delimiter) if elem != '']

# Strip the text with the given characters
def stripWithChars(text, chars=Controls.LT + Controls.GT):
	return text.strip(chars)

# Performs all operations needed for saving this text properly in an XML file
def prepareForXml(text):
	return validateTextForXml(text).strip()

# ================================ PARSING ====================================== #

# Parses the first block of the file (title, subtitle, etc.)
def parseIntro(intro):
	for line in intro:
		firstW = firstWord(line)
		if (firstW == FileSyntax.TITLE):
			title = etree.Element(Tags.TITLE)
			title.text = prepareForXml(splitMultiple(line)[Titles.TITLE])
			root.append(title)
		elif (firstW == FileSyntax.SUBTITLE):
			subtitle = etree.Element(Tags.SUBTITLE)
			subtitle.text = prepareForXml(splitMultiple(line)[Titles.SUBTITLE])
			root.append(subtitle)

# Extract the header content from iterator object
def getHeaderFromIterator(header):
	for headerContent in header:
		return headerContent

# Parse the header of the block of chars
def parseBlockHeader(header):
	blockHead = etree.Element(Tags.BLOCK_HEADER)
   	blockSplit = splitMultiple(header)
  	blockHead.attrib[Attributes.NAME] = prepareForXml(blockSplit[BlockHeader.HEADER])
  	blockHead.attrib[Attributes.BLOCK_START] = prepareForXml(blockSplit[BlockHeader.BLOCK_START])
  	blockHead.attrib[Attributes.BLOCK_END] = prepareForXml(blockSplit[BlockHeader.BLOCK_END])
  	return blockHead

def parseCharEntryInfo(info):
	infoType = info[0]
	infoContent = splitMultiple(info[2:])[CodesBlock.CHAR_ENTRY_INFO]
	if infoType == FileSyntax.ALIAS_LINE:
		aliasLine = etree.Element(Tags.ALIAS_LINE)
		aliasLine.attrib[Attributes.NAME] = prepareForXml(infoContent)
		return aliasLine
	elif infoType == FileSyntax.CROSS_REF:
		crossRef = etree.Element(Tags.CROSS_REF)
		crossRef.attrib[Attributes.REF] = stripWithChars(prepareForXml(infoContent),
														chars=Controls.LPAR + Controls.RPAR)
		return crossRef
	elif infoType == FileSyntax.VARIATION_LINE:
		variationLine = etree.Element(Tags.VARIATION_LINE)
		variationLine.attrib[Attributes.VARIATION] = prepareForXml(infoContent)
		return variationLine
	elif infoType == FileSyntax.COMMENT_LINE:
		commentLine = etree.Element(Tags.COMMENT_LINE)
		commentLine.attrib[Attributes.CONTENT] = prepareForXml(infoContent)
		return commentLine
	elif infoType == FileSyntax.DECOMPOSITION:
		decomposition = etree.Element(Tags.DECOMPOSITION)
		decomposition.attrib[Attributes.DECOMP] = prepareForXml(infoContent)
		return decomposition
 	elif infoType == FileSyntax.COMPAT_MAPPING:
 		compat_mapping = etree.Element(Tags.COMPAT_MAPPING)
 		compat_mapping.attrib[Attributes.COMPAT] = prepareForXml(infoContent)
 		return compat_mapping
 	elif infoType == FileSyntax.FORMALALIAS_LINE:
 		formalalias_line = etree.Element(Tags.FORMALALIAS_LINE)
 		formalalias_line.attrib[Attributes.NAME] = prepareForXml(infoContent)
 		return formalalias_line
	else:
		raise UnknownInput(info)

# Parse the whole block of chars
def parseBlock(header, content):
	# Create the head and add it to the root node
	blockHead = parseBlockHeader(header)
  	root.append(blockHead)

  	# Parse block content. It's a simple pattern-matching. Depending on the availability
  	# of the last char entry decide what to do with new nodes. Every new subheader is
  	# treated like a parent for following char entries
  	headerNodes = [blockHead]
  	lastCharEntry = None
  	for elem in content:
  		firstW = firstWord(elem)
  		elem = elem.strip()  # Remove trailing whitespaces
		if (isCodePoint(firstW)):
			charEntry = etree.Element(Tags.CHAR_ENTRY)
			charEntry.attrib[Attributes.CODE_POINT] = prepareForXml(splitMultiple(elem)[CodesBlock.CODE_POINT])
			charName = stripWithChars(prepareForXml(splitMultiple(elem)[CodesBlock.CHAR_NAME]))

			# What type of category should be assigned
			if charName in FileSyntax.CHAR_NAME_TYPES:
				charEntry.attrib[Attributes.TYPE] = charName
			else:
				charEntry.attrib[Attributes.NAME] = charName

			# Always take the last node
			headerNodes[-1:][0].append(charEntry)
			lastCharEntry = charEntry
		elif elem[CodesBlock.CHAR_ENTRY_INFO_SIGN] in FileSyntax.CHAR_ENTRY_INFO:
			# Take care of availability of char entries, it may be None at beginning of the subheader
			if lastCharEntry == None:
				headerNodes[-1:][0].append(parseCharEntryInfo(elem))
			else:
				lastCharEntry.append(parseCharEntryInfo(elem))
		elif (firstW == FileSyntax.SUBHEADER):
			subHeader = etree.Element(Tags.BLOCK_SUBHEADER)
			subHeader.attrib[Attributes.NAME] = prepareForXml(splitMultiple(elem)[CodesBlock.SUBHEADER])
			lastCharEntry = None
			headerNodes.append(subHeader)
		elif (firstW == FileSyntax.NOTICE_LINE):
			notice_line = etree.Element(Tags.NOTICE_LINE)

			# If there is an asterisk sign at the beginning of the notice line, add
			# an additional attribute to indicate that fact
			line = prepareForXml(splitMultiple(elem)[CodesBlock.NOTICE_LINE])
			if line[0] == Controls.ASTERISK:
				notice_line.attrib[Attributes.WITH_ASTERISK] = YesNo.YES
				line = stripWithChars(line, Controls.ASTERISK + Whitespace.SPACE)
			notice_line.text = line

			# Add the notice line to the proper element
			if lastCharEntry == None:
				headerNodes[-1:][0].append(notice_line)
			else:
				lastCharEntry.append(notice_line)
		else:
			logging.info("Ignoring line: " + elem)

	# Add all children to the head of the block (omit the first one - header)
	for node in headerNodes[1:]:
		blockHead.append(node)

# Whether the line contains the block header
def isBlockHeader(line):
  	return firstWord(line) == FileSyntax.BLOCK_HEADER

# Whether the text represents a code point
def isCodePoint(text):
	return (re.match(r'^[0-9,A-F]{4,6}$', text, re.IGNORECASE) != None)

# The main function of this parser. Splits the file into blocks (using block headers), parses
# the introduction (title, subtitle, etc.) and block, eventually creates an XML with these data
def runParser():
	try:
		# Open the file (default one if no files provided)
		fileName = _NAME_LISTS_FILE
		if args.n:
			fileName = args.n
		file = open(fileName, 'r')

 		# Split the file into blocks (blocks of Unicode data)
		splitFile = groupby(file, isBlockHeader)

 		# Parse title, subtitle, etc.
		(dummy, intro) = next(splitFile)
 		parseIntro(intro)

 		# Parse codes blocks, when a header is found wait for the content
 		header = []
		for isHeader, blockContent in splitFile:
			if isHeader:
				header = getHeaderFromIterator(blockContent)
			else:
				parseBlock(header, blockContent)

		file.close()

		# Save the XML
		f = None
		if args.o:
			if args.o.endswith('.xml'):
				f = open(args.o, 'w')
			else:
				f = open(args.o + '.xml', 'w')
		else:
			f = open('NamesList.xml', 'w')
		f.write(minidom.parseString(etree.tostring(root)).toprettyxml(encoding="UTF-8"))
		f.close()

	except IOError:
		print "No such file:", fileName
		print "You can find the required file on: http://www.unicode.org/Public/UNIDATA/NamesList.txt"


# Parse arguments (if any) and run the parser
args = parser.parse_args()
runParser()

# Generate a C structure with XML tag and attributes
if args.C:
	# Create the structure with tags
	d = dict((name, getattr(Tags, name)) for name in dir(Tags) if not name.startswith('__'))

	sH, sI = [], []
	for field, value in d.iteritems():
		sH.append("  const char *" + field + ";")
		sI.append("\"" + value + "\"")

	# Create the structure with attributes
	d = dict((name, getattr(Attributes, name)) for name in dir(Attributes) if not name.startswith('__'))

	sA, sV = [], []
	for field, value in d.iteritems():
		sA.append("  const char *" + field + ";")
		sV.append("\"" + value + "\"")

	# Create the structure with YES/NO values
	d = dict((name, getattr(YesNo, name)) for name in dir(YesNo) if not name.startswith('__'))

	sYN, sYN_V = [], []
	for field, value in d.iteritems():
		sYN.append("  const char *" + field + ";")
		sYN_V.append("\"" + value + "\"")

	# Print the whole C code to the standard output
	print "\n/* Constants containing XML tags */"
	print "struct XmlTag {\n" + '\n'.join(sH) + "\n};"
	print "\n/* Constants containing XML attributes */"
	print "struct XmlAttr {\n" + '\n'.join(sA) + "\n};"
	print "\n/* Constants containing Yes/No values */"
	print "struct YesNo {\n" + '\n'.join(sYN) + "\n};"
	print "\nextern const struct XmlTag xmlTags;"
	print "extern const struct XmlAttr xmlAttrs;"
	print "extern const struct YesNo yesNoValues;"
	print "\nconst struct XmlTag xmlTags = {\n  " + ', '.join(sI) + "\n};"
	print "\nconst struct XmlAttr xmlAttrs = {\n  " + ', '.join(sV) + "\n};"
	print "\nconst struct YesNo yesNoValues = {\n  " + ', '.join(sYN_V) + "\n};"

