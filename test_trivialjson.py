# -*- coding: utf-8 -*-

from __future__ import with_statement

import unittest
import os
_trivialjson_testing = True
import trivialjson

loadsb = trivialjson.json.loads # Load from bytes
try:
	bytes
	loads = lambda s: loadsb(s.encode('utf-8'))
except NameError:
	loads = loadsb

def assertRaises(err, code, *args, **kwargs):
	try:
		code(*args, **kwargs)
	except err:
		return
	raise AssertionError('Expected ' + str(err))
assertInvalid = lambda jsoni: assertRaises(ValueError, loads, jsoni)

# Prevent contextlib from being by coverage tools
import sys
import contextlib
del sys.modules['contextlib']

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
	assert loadsb('"\u1234"'.encode('UTF-8')) == unichr(0x1234)
	assert loadsb('"\u0000"'.encode('UTF-8')) == unichr(0x0000)
	assert loadsb('"\u1000\u2000"'.encode('UTF-8')) == unichr(0x1000) + unichr(0x2000)

def test_unicode_escapes_bmp():
	assert loadsb('"\\u1234"'.encode('UTF-8')) == unichr(0x1234)
	assert loadsb('"\\u0000"'.encode('UTF-8')) == unichr(0x0000)
	assert loadsb('"\\u1000\\u2000"'.encode('UTF-8')) == unichr(0x1000) + unichr(0x2000)

def test_unicode_escapes_complex():
	assert loadsb('"\\uD834\\uDD1E"'.encode('UTF-8')) == unichr(0x1d11e)

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
	#print('Found json.org-checker tests, testing ...')
	for fn in files:
		if fn in IGNORED:
			continue
		with contextlib.closing(open(os.path.join(exttestdir, fn), 'rb')) as f:
			content = f.read()
		#print('  ' + fn)
		if fn.startswith('fail'):
			assertRaises(ValueError, loadsb, content)
		else:
			assert loadsb(content)

if __name__ == '__main__':
	testfuncs = [f for fname,f in locals().items() if fname.startswith('test_')]
	for tf in testfuncs:
		tf()
