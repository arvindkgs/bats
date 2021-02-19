---
id: doc3
title: Build
---

To build an artifact, cd into the root directory and run `sh build.sh`

This creates in root
```
(ROOT)
|- bats.tar.gz (This is file that should be transferred to the POD/vm where *bats* should run)
|- dist
   |- basic_acceptance_test_suite-0.0.1-py2-none-any.whl
   |- basic-acceptance-test-suite-0.0.1.tar.gz (Package that can be installed directly using pip (pip install ...), or  extracting and running python setup.py install)
   |- README.md
```   