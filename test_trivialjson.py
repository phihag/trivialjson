# -*- coding: utf-8 -*-

import unittest
import trivialjson
loads = trivialjson.json.loads

def assertRaises(err, code, *args, **kwargs):
	try:
		code(*args, **kwargs)
	except err:
		return
	raise AssertionError('Expected ' + str(err))
assertInvalid = lambda jsoni: assertRaises(ValueError, loads, jsoni)

def test_basic():
	assert loads('1') == 1
	assert loads('""') == ''
	assert loads('"a"') == 'a'
	assert loads('true') == True
	assert loads('false') == False
	assert loads('null') == None
	assertInvalid('True')

def test_object():
	assert loads('{}') == {}
	assert loads('{"a":"b"}') == {"a":"b"}
	assert loads('{"a":"b","c":"d"}') == {"a":"b","c":"d"}
	assertInvalid('{')
	assertInvalid('{"a" : "b"')
	assert loads('{"a" : "b"}') == {'a':'b'}
	assertInvalid('{1:2}')
	assertInvalid(' {"x" \n  : "a b c" \t\n\t,\t"y": "z"\t')

def test_array():
	assert loads('[]') == []
	assert loads('[1]') == [1]
	assert loads('[ 1 ]') == [1]
	assert loads(' [  1 , 2 ] ') == [1,2]
	assert loads(' [  1 , 2 , 3,4 ] ') == [1,2,3,4]
	assertInvalid(' [ ')
	assertInvalid(' [1, ')
	assertInvalid(' [1 ')
	assertInvalid(' [,1] ')
	assertInvalid('[,]')

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
	assert loads('"\u1234"'.encode('UTF-8')) == unichr(0x1234)
	assert loads('"\u0000"'.encode('UTF-8')) == unichr(0x0000)
	assert loads('"\u1000\u2000"'.encode('UTF-8')) == unichr(0x1000) + unichr(0x2000)

def test_unicode_escapes_bmp():
	assert loads('"\\u1234"'.encode('UTF-8')) == unichr(0x1234)
	assert loads('"\\u0000"'.encode('UTF-8')) == unichr(0x0000)
	assert loads('"\\u1000\\u2000"'.encode('UTF-8')) == unichr(0x1000) + unichr(0x2000)

def test_unicode_escapes_complex():
	assert loads('"\\uD834\\uDD1E"'.encode('UTF-8')) == unichr(0x1d11e)

def test_skipspace():
	assert loads('1 ') == 1
	assert loads(' { } ') == {}
	assert loads(' \t{ \n} \r \r\n') == {}
	assert loads(' {"x" \n  : "a b c" \t\n\t,\t"y": "z"\t}') == {'x': 'a b c', 'y': 'z'}
	assert loads(' {"x": [   1 , 2  ,3, 4\t]}') == {'x': [1,2,3,4]}

