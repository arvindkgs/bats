---
id: doc5
title: Folder structure
---

```
.
├── build.sh
├── dependencies
│   ├── apacheconfig-0.2.8.tar.gz
│   ├── argparse-1.4.0.tar.gz
│   ├── basic-acceptance-test-suite-0.0.1.tar.gz
│   ├── decorator-4.4.0.tar.gz
│   ├── jsonpath-rw-1.4.0.tar.gz
│   ├── jsonpath-rw-ext-1.2.0.tar.gz
│   ├── pbr-5.2.0.tar.gz
│   ├── ply-3.11.tar.gz
│   └── six-1.12.0.tar.gz
├── Enhancements.txt
├── MANIFEST.in (Resource to be added to python module) 
├── metadatas
│   ├── fa_host
│   ├── ohs-shell-dynamic
│   ├── resizing
│   └── tests
├── README.md
├── scripts
│   ├── runSCPCommand.sh (Test scp command)
│   ├── runSSHCommand.sh (Test ssh command)
│   ├── runTests.sh (Call this after any code modifications, to run unit tests)
│   └── setup.sh (Call this for installing in local vm/laptop, when using virtual environment pass 'dev' argument)
├── setup.py (Install script for artifact, that is bundled with artifact)
├── src
│   └── bats
├── struct
├── tmp
│   ├── dependencies
│   ├── README.md
│   └── setup.sh
└── Validation\ Suite.png (Flow diagram)

```

