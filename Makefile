COVERAGE_TMPDIR=.coverage-html
PY3_TMPDIR=.py3tmp

default: all

all: test test-py25 test-py2to3 test-py3-parsing

test: exttests
	nosetests --with-coverage --cover-erase --cover-html "--cover-html-dir=${COVERAGE_TMPDIR}" test_trivialjson.py
	@rm -f test_trivialjson.py,cover

test-py25: exttests
	python2.5 test_trivialjson.py
	rm -f trivialjson.pyc

test-py2to3: exttests
	mkdir -p '${PY3_TMPDIR}'
	cp trivialjson.py test_trivialjson.py '${PY3_TMPDIR}'
	2to3 -w -n --no-diffs '${PY3_TMPDIR}/trivialjson.py' '${PY3_TMPDIR}/test_trivialjson.py'
	python3 '${PY3_TMPDIR}/test_trivialjson.py'
	rm -rf '${PY3_TMPDIR}'

test-py3-parsing: exttests
	python3 trivialjson.py
	@echo 'No syntax error when interpreted in Python 3.'

coverage-display: test
	xdg-open '${COVERAGE_TMPDIR}/trivialjson.html'

cd: coverage-display


exttests:
	mkdir exttests && \
		cd exttests && wget 'http://json.org/JSON_checker/test.zip' -c -O test.zip && unzip -o test.zip && mv test json.org-checker

fake-exttests:
	mkdir exttests

clean:
	rm -fr -- '${PYTEST_TMP}' '${COVERAGE_TMPDIR}' .coverage '${PY3_TMPDIR}' trivialjson.pyc exttests trivialjson.py,cover

.PHONY: default all gen-pytest-script test test-py25 test-py2to3 test-py3-parsing coverage coverage-display cd clean fake-exttests
