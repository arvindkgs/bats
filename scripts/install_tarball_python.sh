#!/usr/bin/env bash

# Script: install_tarball_python
# takes the tar.gz dependency as arg
# creates a temp directory and extracts the archive in it.
# 'cd's into the extracted archive and runs 'python setup.py install'
# 'cd's back to the current directory and removes the temp containing the decompressed archive

if [ $# -lt 1 ]; then
    echo "Usage: install_tarball_python <package.tar.gz>"
    exit 1
fi
pushd . && mkdir temp && tar zxf $1 -C temp && cd temp && cd * && python setup.py install --user&& popd && rm -rf temp