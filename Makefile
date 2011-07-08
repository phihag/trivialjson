COVERAGE_TMPDIR=.coverage-html

default: all

all: test

test:
	nosetests --with-coverage --cover-erase --cover-html "--cover-html-dir=${COVERAGE_TMPDIR}" test_trivialjson.py

coverage-display: test
	xdg-open '${COVERAGE_TMPDIR}/trivialjson.html'

cd: coverage-display

clean:
	rm -fr -- '${PYTEST_TMP}' '${COVERAGE_TMPDIR}' .coverage

.PHONY: default all gen-pytest-script test coverage coverage-display cd clean
