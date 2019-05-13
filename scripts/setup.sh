#!/usr/bin/env bash

# Script: setup
# installs python module dependencies

install() {
    pushd . &&  if [ -d "temp" ]; then rm -Rf temp; fi && mkdir temp && tar zxf $1 -C temp && cd temp && cd * && python setup.py install --user && popd && rm -rf temp
}

if [ ! -d "dependencies" ]; then
    echo "'dependencies' folder does not exist. Run script from root directory of validation tool source";
fi


install "dependencies/six-1.12.0.tar.gz"
install "dependencies/pbr-5.2.0.tar.gz"
install "dependencies/decorator-4.4.0.tar.gz"
install "dependencies/ply-3.11.tar.gz"
install "dependencies/jsonpath-rw-1.4.0.tar.gz"
install "dependencies/jsonpath-rw-ext-1.2.0.tar.gz"
