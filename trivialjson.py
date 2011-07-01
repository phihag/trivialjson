# -*- coding: utf-8 -*-

try:
	import json__
except ImportError: # Python <2.5, use trivialjson:
	import re
	class json(object):
		@staticmethod
		def loads(s):
			def raiseError(msg, i):
				raise ValueError(msg + ' at position ' + str(i) + ' of ' + repr(s) + ': ' + repr(s[i:]))
			def skipSpace(i):
				while i < len(s) and s[i] in ' \t\r\n':
					i += 1
				return i
			def decodeEscape(match):
				esc = match.group(1)
				_STATIC = {
					u'"': u'"',
					u'\\': u'\\',
					u'/': u'/',
					u'b': unichr(0x8),
					u'f': unichr(0xc),
					u'n': u'\n',
					u'r': u'\r',
					u't': u'\t',
				}
				if esc in _STATIC:
					return _STATIC[esc]
				if esc[0] == 'u':
					if len(esc) == 1+4:
						return unichr(int(esc[1:5], 16))
					if len(esc) == 5+6 and esc[5:7] == '\\u':
						hi = int(esc[1:5], 16)
						low = int(esc[7:11], 16)
						return unichr((hi - 0xd800) * 0x400 + low - 0xdc00 + 0x10000)
				raise ValueError('Unknown escape ' + str(esc))
			def parseString(i):
				if s[i] != '"':
					raise ValueError('Expected a string at char ' + str(i) + ' of ' + repr(s))
				i += 1
				e = i
				while True:
					e = s.index('"', e)
					bslashes = 0
					while s[e-bslashes-1] == '\\':
						bslashes += 1
					if bslashes % 2 == 1:
						e += 1
						continue
					break

				stri = s[i:e].decode('UTF-8')
				rexp = re.compile(r'\\(u[dD][89aAbB][0-9a-fA-F]{2}\\u[0-9a-fA-F]{4}|u[0-9a-fA-F]{4}|.|$)')
				stri = rexp.sub(decodeEscape, stri)
				return (e+1,stri)
			def parseObj(i):
				if s[i] != '{':
					raise ValueError('Expected an object at char ' + str(i))
				i += 1
				res = {}
				while True:
					i = skipSpace(i)
					if i >= len(s):
						raise ValueError('Premature end of dictionary at position ' + str(i) + ' of ' + repr(s))
					if s[i] == '}': # Empty dictionary
						return (i+1,res)
					i,key = parseString(i)
					i = skipSpace(i)
					if i >= len(s) or s[i] != ':':
						raise ValueError('Expected a colon at position ' + str(i))
					i,val = parse(i+1)
					res[key] = val
					if i >= len(s):
						raise ValueError('Premature end of dictionary at position ' + str(i) + ' of ' + repr(s))
					if s[i] == '}':
						return (i+1, res)
					if s[i] != ',':
						raise ValueError('Expected comma or closing curly brace at position ' + str(i))
					i += 1
			def parseArray(i):
				if s[i] != '[':
					raise ValueError('Expected an array at char ' + str(i) + ' of ' + repr(s))
				res = []
				while True:
					i = skipSpace(i+1)
					if i >= len(s):
						raise ValueError('Premature end of array')
					if s[i] == ']':
						return (i+1,res)
					i,val = parse(i)
					res.append(val)
					if i >= len(s):
						raise ValueError('Premature end of array')
					if s[i] == ']':
						return (i+1, res)
					if s[i] != ',':
						raise ValueError('Expected a comma or closing bracket at position ' + str(i))
			def parseDiscrete(i):
				for k,v in {'true': True, 'false': False, 'null': None}.items():
					if s.startswith(k, i):
						return (i+len(s), v)
				raise ValueError('Not a boolean (or null) at char ' + str(i) + ' of ' + repr(s))
			def parseNumber(i):
				mobj = re.match('^([0-9.eE]+)([^0-9.eE]|$)', s[i:])
				if mobj is None:
					raise ValueError('Not a number at char ' + str(i) + ' of ' + repr(s[i]))
				nums = mobj.group(1)
				if '.' in nums or 'e' in nums or 'E' in nums:
					return (i+len(nums), float(nums))
				return (i+len(nums), int(nums))
			CHARMAP = {'{': parseObj, '[': parseArray, '"': parseString, 't': parseDiscrete, 'f': parseDiscrete, 'n': parseDiscrete}
			def parse(i):
				i = skipSpace(i)
				i,res = CHARMAP.get(s[i], parseNumber)(i)
				i = skipSpace(i)
				return (i,res)

			i,res = parse(0)
			if i < len(s):
				raise ValueError('Extra data at end of input (index ' + str(i) + ' of ' + repr(s) + ': ' + repr(s[i:]) + ')')
			return res
