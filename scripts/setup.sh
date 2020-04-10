#!/usr/bin/env bash

# Script: setup
# installs python module dependencies
if [[ $# -gt 0 ]] && [[ $1 == 'dev' ]]; then
  install_flag=""
else
  install_flag="--user"
fi

install() {
    module=$2
    if [[ "$module" == "bats" && $install_flag == "" ]]; then
      python -c "import bats; import shutil; shutil.rmtree(bats.__path__[0])"
    fi
    python -c "import $module"
    if [[ $? == 1 ]]; then
        if [[ "$module" == "bats" && ! -f "dependencies/basic-acceptance-test-suite-0.0.1.tar.gz" && -f "build.sh" ]]; then
          sh ./build.sh
        elif [[ "$module" == "bats" && ! -f "dependencies/basic-acceptance-test-suite-0.0.1.tar.gz"  &&  -f "../build.sh" ]]; then
            cd .. && buid.sh
        fi
        pushd . &&  if [ -d "temp" ]; then rm -Rf temp; fi && mkdir temp && tar zxf $1 -C temp && cd temp && cd * && python setup.py install $install_flag && popd && rm -rf temp
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
