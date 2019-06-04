#!/usr/bin/env bash

runPositiveTest() {
    path=$1
    metadatafile=$2
    generatedlog=$3
    expectedlog=$4
    python bin/validation_suite.py metadata $path/$metadatafile
    if [ $? -eq 0 ]; then
        diff $path/$generatedlog $path/$expectedlog > /dev/null
        if [ $? -eq 0 ]; then
            echo "$1 : Success!"
        else
            echo "$1: Failure : generated log($path/$generatedlog) not same as expected log($path/$expectedlog)"
        fi
     else
        echo "$1: Failure, validation should pass"
    fi
}

runNegativeTest() {
    path=$1
    metadatafile=$2
    generatedlog=$3
    expectedlog=$4
    python bin/validation_suite.py metadata $path/$metadatafile
    if [ $? -ne 0 ]; then
        diff $path/$generatedlog $path/$expectedlog > /dev/null
        if [ $? -eq 0 ]; then
            echo "$1: Success!"
        else
            echo "$1: Failure : generated log($path/$generatedlog) not same as expected log($path/$expectedlog)"
        fi
    else
        echo "$1: Failure : validation should fail"
    fi
}

runAllTest(){
    python bin/validation_suite.py metadatas/tests/all/individual.json
    if [ $? -ne 0 ]; then
        python bin/validation_suite.py metadata metadatas/tests/all/dynamic.json
        if [ $? -ne 0 ]; then
            diff metadatas/tests/all/individual.log metadatas/tests/all/dynamic.log > /dev/null
            if [ $? -eq 0 ]; then
                echo "metadatas/tests/all: Success!"
            else
                echo "metadatas/tests/all: Failure : generated individual log(metadatas/tests/all/individual.log) not same as dynamic generated log(metadatas/tests/all/dynamic.log)"
            fi
        else
          echo "metadatas/tests/all: Failed, dynamic json validation should pass"
        fi
    else
        echo "metadatas/tests/all: Failed, individual json validation should pass"
    fi
}

runPositiveTest "metadatas/tests/jvm" "metadata.json" "jvm.log" "success.log"
runPositiveTest "metadatas/tests/jdbc" "metadata.json" "jdbc.log" "success.log"
runNegativeTest "metadatas/tests/ohs" "metadata.json" "ohs.log" "failure.log"
runNegativeTest "metadatas/tests/shell-dynamic" "metadata.json" "ohs.log" "failure.log"
runNegativeTest "metadatas/tests/negative" "metadata.json" "negative.log" "failure.log"
runNegativeTest "metadatas/tests/individual" "metadata.json" "individual.log" "failure.log"
runNegativeTest "metadatas/tests/dynamic" "metadata.json" "dynamic.log" "failure.log"
runPositiveTest "metadatas/tests/one-to-many" "metadata.json" "jvm.log" "success.log"
runNegativeTest "metadatas/tests/elasticsearch" "metadata.json" "elasticsearch.log" "failure.log"
runPositiveTest "metadatas/tests/current-pod-size" "metadata.json" "podsize.log" "success.log"
