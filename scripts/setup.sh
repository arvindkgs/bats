#!/usr/bin/env bash

# Script: setup
# installs python module dependencies

install() {
    module=$2
    python -c "import $module"
    if [ $? == 1 ]; then
        pushd . &&  if [ -d "temp" ]; then rm -Rf temp; fi && mkdir temp && tar zxf $1 -C temp && cd temp && cd * && python setup.py install --user && popd && rm -rf temp
    fi
}

if [ ! -d "dependencies" ]; then
    echo "'dependencies' folder does not exist. Run script from root directory of validation tool source";
fi


install "dependencies/py_modules/six-1.12.0.tar.gz" "six"
install "dependencies/py_modules/pbr-5.2.0.tar.gz" "pbr"
install "dependencies/py_modules/decorator-4.4.0.tar.gz" "decorator"
install "dependencies/py_modules/ply-3.11.tar.gz" "ply"
install "dependencies/py_modules/jsonpath-rw-1.4.0.tar.gz" "jsonpath-rw"
install "dependencies/py_modules/jsonpath-rw-ext-1.2.0.tar.gz" "jsonpath-rw-ext"
