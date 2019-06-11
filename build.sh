#!/usr/bin/env bash
if [ -d "dist" ]; then rm -rf dist; fi;
python setup.py sdist bdist_wheel
if [ -d "dist" ]; then cp -f dist/basic-acceptance-test-suite-0.0.1.tar.gz dependencies/py_modules; tar czf bats.tar.gz  dependencies -C scripts setup.sh; fi
