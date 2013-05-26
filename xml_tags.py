# -*- coding: utf-8 -*- 
# Author: Paweł Parafiński
# You can contact me: ppablo28@gmail.com
# Tags and attributes of the XML file

class Tags(object):
	ROOT = "ucd"
	BLOCK_HEADER = "block_header"
	BLOCK_SUBHEADER = "block_subheader"
	FILE_COMMENT = "file_comment"
	TITLE = "title"
	SUBTITLE = "subtitle"
	NOTICE_LINE = "notice_line"
	CHAR_ENTRY = "char_entry"
	ALIAS_LINE = "alias_line"
	CROSS_REF = "cross_ref"
	VARIATION_LINE = "variation_line"
	COMMENT_LINE = "comment_line"
	DECOMPOSITION = "decomposition"
	COMPAT_MAPPING = "compat_mapping"
	FORMALALIAS_LINE = "formalalias_line"

class Attributes(object):
	BLOCK_START = "block_start"
	BLOCK_END = "block_end"
	CODE_POINT = "code_point"
	COMPAT = "compat"
	CONTENT = "content"
	DECOMP = "decomp"
	NAME = "name"
	REF = "ref"
	TYPE = "type"
	VARIATION = "variation"
	WITH_ASTERISK = "with_asterisk"

class YesNo(object):
	YES = "Y"
	NO = "N"
