#!/usr/bin/env bash

runPositiveTest() {
    python bin/validation_suite.py $1/metadata.json
    if [ $? -eq 0 ]; then
        diff $1/$3 $1/$4
        if [ $? -eq 0 ]; then
            echo "$1 : Success!"
        else
            echo "$1: Failure : expected log(metadatas/tests/positive/success.log) not same as generated log(metadatas/tests/positive/positive.log)"
        fi
     else
        echo "$1: Failure, validation should pass"
    fi
}

runNegativeTest() {
    python bin/validation_suite.py $1/metadata.json
    if [ $? -ne 0 ]; then
        diff $1/failure.log $1/negative.log
        if [ $? -eq 0 ]; then
            echo "$1: Success!"
        else
            echo "$1: Failure : expected log(metadatas/tests/negative/failure.log) not same as generated log(metadatas/tests/negative/negative.log)"
        fi
    else
        echo "$1: Failure : validation should fail"
    fi
}

runAllTest(){
    python bin/validation_suite.py metadatas/tests/all/individual.json
    if [ $? -ne 0 ]; then
        python bin/validation_suite.py metadatas/tests/all/dynamic.json
        if [ $? -ne 0 ]; then
            diff metadatas/tests/all/individual.log metadatas/tests/all/dynamic.log
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

runPositiveTest "metadatas/tests/positive/" "success.log" "positive.log"
runPositiveTest "metadatas/tests/jdbc" "success.log" "jdbc.log"
runNegativeTest "metadatas/tests/negative/" "failure.log" "negative.json"
runAllTest "metadatas/tests/all/"

