COVERAGE_TMPDIR=.coverage-html
PY3_TMPDIR=.py3tmp

default: all

all: test test-py25 test-py3 coverage

test: exttests
	nosetests test_trivialjson.py

test-py25: exttests
	python2.5 test_trivialjson.py
	rm -f trivialjson.pyc

test-py3: exttests
	python3 test_trivialjson.py
	rm -f trivialjson.pyc


coverage:
	python-coverage erase
	@rm -rf '${COVERAGE_TMPDIR}'
	python-coverage run test_trivialjson.py
	@rm -f test_trivialjson.py,cover
	python-coverage html -d '${COVERAGE_TMPDIR}'
	@rm -f trivialjson.py,cover

coverage-display: coverage
	xdg-open '${COVERAGE_TMPDIR}/trivialjson.html'

cd: coverage-display


exttests:
	mkdir exttests && \
		cd exttests && wget 'http://json.org/JSON_checker/test.zip' -c -O test.zip && unzip -o test.zip && mv test json.org-checker

fake-exttests:
	mkdir exttests

clean:
	rm -fr -- '${PYTEST_TMP}' '${COVERAGE_TMPDIR}' .coverage '${PY3_TMPDIR}' trivialjson.pyc exttests trivialjson.py,cover

.PHONY: default all gen-pytest-script test test-py25 test-py3 coverage coverage-display cd clean fake-exttests
