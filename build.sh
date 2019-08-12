#!/usr/bin/env bash
if [ -f "bats.tar.gz" ]; then rm "bats.tar.gz"; fi;
if [ -d "dist" ]; then rm -rf dist; fi;
python setup.py sdist bdist_wheel
if [ -d "dist" ]; then cp -f dist/basic-acceptance-test-suite-0.0.1.tar.gz -t dependencies; cp README.md -t dist/; tar czf bats.tar.gz  dependencies README.md -C scripts setup.sh; fi
