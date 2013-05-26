# -*- coding: utf-8 -*- 
# Author: Paweł Parafiński
# You can contact me: ppablo28@gmail.com
# Some useful constants for *.txt parsing

class FileSplit(object):
	INTRO = 0;
	BLOCKS = 1;
	
class BlockSplit(object):
	HEADER = 0;
	CONTENT = 1;	

class BlockHeader(object):
	BLOCK_START = 1
	HEADER = 2
	BLOCK_END = 3
	
class CodesBlock(object):
	NOTICE_LINE = 1
	SUBHEADER = 1
	CODE_POINT = 0
	CHAR_NAME = 1
	CHAR_ENTRY_INFO_SIGN = 0
	CHAR_ENTRY_INFO = 0
	
class Titles(object):
	TITLE = 1
	SUBTITLE = 1
	
class FileSyntax(object):
	TITLE = "@@@"
	SUBTITLE = "@@@+"
	SUBHEADER = "@"
	NOTICE_LINE = "@+"
	BLOCK_HEADER = "@@"
	ALIAS_LINE = "="
	CROSS_REF = "x"
	VARIATION_LINE = "~"
	COMMENT_LINE = "*"
	DECOMPOSITION = ":"
	COMPAT_MAPPING = "#"
	FORMALALIAS_LINE = "%"
	CHAR_ENTRY_INFO = [
		ALIAS_LINE, CROSS_REF, VARIATION_LINE, COMMENT_LINE, DECOMPOSITION, 
		COMPAT_MAPPING, FORMALALIAS_LINE
	]
	CHAR_NAME_TYPES = ["control", "not a character"]
	
class Whitespace(object):
	TAB = "\t"
	SPACE = " "
	
class Controls(object):
	LT = "<"
	GT = ">"
	LPAR = "("
	RPAR = ")"
	ASTERISK = "*"
