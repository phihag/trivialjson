#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement

import codecs
import contextlib
import unittest
import os
try:
	from io import StringIO
except ImportError:
	from StringIO import StringIO

import imp
file,pathname,description = imp.find_module('trivialjson')
trivialjson = imp.load_module('trivialjson_testing', file, pathname, description)

loads = trivialjson.json.loads # Load from bytes

try:
	chr(256)
	_compat_chr = chr
except ValueError: # Python 2
	_compat_chr = unichr

load = trivialjson.json.load


def assertRaises(err, code, *args, **kwargs):
	try:
		code(*args, **kwargs)
	except err:
		return
	raise AssertionError('Expected ' + str(err))
assertInvalid = lambda jsoni: assertRaises(ValueError, loads, jsoni)

def _compat_StringIO(s):
	""" In Python 2.7, io.StringIO expects a string (i.e. unicode), not bytes (i.e. str)"""
	try:
		bytes
	except NameError:
		pass
	else:
		if isinstance(s, bytes):
			s = s.decode('UTF-8')
	return StringIO(s)


def test_basic():
	assert loads('1') == 1
	assert loads('""') == ''
	assert loads('"a"') == 'a'
	assert loads('true') == True
	assert loads('false') == False
	assert loads('null') == None
	assertInvalid('True')
	assertInvalid('_')
	assertInvalid('tfalse')

def test_object():
	assert loads('{}') == {}
	assert loads('{  }') == {}
	assert loads('{"a":"b"}') == {"a":"b"}
	assert loads('{"a":"b","c":"d"}') == {"a":"b","c":"d"}
	assert loads('{"a":{}, "b": {"c": {"d" : "e"}}}') == {"a": {}, "b": {"c": {"d" : "e"}}}
	assertInvalid('{')
	assertInvalid('{"')
	assertInvalid('{"a')
	assertInvalid('{"a"')
	assertInvalid('{"a":')
	assertInvalid('{"a":"')
	assertInvalid('{"a":"b')
	assertInvalid('{"a":"b"')
	assertInvalid('{"a":"b" ,')
	assertInvalid('{"a":"b", "c"')
	assertInvalid('{"a":"b", 2')
	assertInvalid('{"a":"b", "c":')
	assertInvalid('{"a":"b", "c":"e"')
	assertInvalid('{"a" : "b"')
	assertInvalid('{"a" : 2 1')
	assertInvalid('{"a"= "b"}')
	assert loads('{"a" : "b"}') == {'a':'b'}
	assertInvalid('{1:2}')
	assertInvalid('{"a":2,}')
	assertInvalid(' {"x" \n  : "a b c" \t\n\t,\t"y": "z"\t')

def test_array():
	assert loads('[]') == []
	assert loads('[1]') == [1]
	assert loads('[ 1 ]') == [1]
	assert loads(' [  1 , 2 ] ') == [1,2]
	assert loads(' [  1 , 2 , 3,4 ] ') == [1,2,3,4]
	assert loads('[true,false, null]') == [True, False, None]
	assertInvalid(' [ ')
	assertInvalid(' [1,')
	assertInvalid(' [1, ')
	assertInvalid(' [1 ')
	assertInvalid(' [,1] ')
	assertInvalid('[,]')
	assertInvalid('[1,]')
	assertInvalid('[1 2]')

def test_number():
	assert loads('1') == 1
	assert loads('1.0') == 1.0
	assert loads('1e200') == 1e200
	assert loads('-42') == -42
	assert loads('-23E-200') == -23e-200
	assertInvalid('1.2.3')

def test_backslashes():
	assert loads(r'"\""') == '"'
	assertInvalid(r'"\"')
	assert loads(r'"\\\""') == r'\"'
	assertInvalid(r'"\\\"')
	assert loads(r'"\\\\"') == r'\\'

def test_escapes():
	assert loads('"\\' + chr(0x22) + '"') == chr(0x22)
	assert loads('"\\' + chr(0x5C) + '"') == chr(0x5C)
	assert loads('"\\' + chr(0x2F) + '"') == chr(0x2F)
	assert loads('"\\' + chr(0x62) + '"') == chr(0x08)
	assert loads('"\\' + chr(0x66) + '"') == chr(0x0C)
	assert loads('"\\' + chr(0x6E) + '"') == chr(0x0A)
	assert loads('"\\' + chr(0x72) + '"') == chr(0x0D)
	assert loads('"\\' + chr(0x74) + '"') == chr(0x09)

	assertInvalid('"\\' + chr(0x21) + '"')
	assertInvalid('"\\' + chr(0x63) + '"')
	assertInvalid('"\\\'"')

def test_unicode():
	assert loads('"\u1234"') == _compat_chr(0x1234)
	assert loads('"\u00AA"') == _compat_chr(0x00AA)
	assert loads('"\u1000\u2000"') == _compat_chr(0x1000) + _compat_chr(0x2000)

def test_unicode_escapes_bmp():
	assert loads('"\\u1234"') == _compat_chr(0x1234)
	assert loads('"\\u0000"') == _compat_chr(0x0000)
	assert loads('"\\u1000\\u2000"') == _compat_chr(0x1000) + _compat_chr(0x2000)

def test_unicode_escapes_complex():
	assert loads('"\\uD834\\uDD1E"') == _compat_chr(0x1d11e)

def test_skipspace():
	assert loads('1 ') == 1
	assert loads(' { } ') == {}
	assert loads(' \t{ \n} \r \r\n') == {}
	assert loads(' {"x" \n  : "a b c" \t\n\t,\t"y": "z"\t}') == {'x': 'a b c', 'y': 'z'}
	assert loads(' {"x": [   1 , 2  ,3, 4\t]   }') == {'x': [1,2,3,4]}

def test_multiple_roots():
	assertInvalid('')
	assertInvalid('1 2')
	assertInvalid('{} {}')
	assertInvalid('"a" ,[]')

# This test is a nop if external tests are not present
def test_external():
	IGNORED = [
		'fail1.json', # Allow strings as root
		'fail18.json', # Maximum array depth
		'fail25.json', # Allow tab in strings
		'fail27.json', # Allow newlines in strings
		'fail28.json', # Allow newlines in strings
	]
	exttestdir = os.path.join(os.path.dirname(__file__), 'exttests', 'json.org-checker')
	try:
		files = os.listdir(exttestdir)
	except OSError: # json.org tests not downloaded
		return # Skip this test

	for fn in files:
		if fn in IGNORED:
			continue
		with contextlib.closing(codecs.open(os.path.join(exttestdir, fn), 'r', 'UTF-8')) as f:
			content = f.read()
		if fn.startswith('fail'):
			assertRaises(ValueError, loads, content)
		else:
			assert loads(content)

def test_load():
	stream = _compat_StringIO('{"a":"b", "c": 42}')
	assert load(stream) == {
		'a': 'b',
		'c': 42,
	}

if __name__ == '__main__':
	testfuncs = [f for fname,f in locals().items() if fname.startswith('test_')]
	for tf in testfuncs:
		tf()
