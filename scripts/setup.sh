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


install "dependencies/six-1.12.0.tar.gz" "six"
install "dependencies/pbr-5.2.0.tar.gz" "pbr"
install "dependencies/decorator-4.4.0.tar.gz" "decorator"
install "dependencies/ply-3.11.tar.gz" "ply"
install "dependencies/apacheconfig-0.2.8.tar.gz" "apacheconfig"
install "dependencies/jsonpath-rw-1.4.0.tar.gz" "jsonpath_rw"
install "dependencies/jsonpath-rw-ext-1.2.0.tar.gz" "jsonpath_rw_ext"
install "dependencies/argparse-1.4.0.tar.gz" "argparse"
install "dependencies/basic-acceptance-test-suite-0.0.1.tar.gz" "bats"
