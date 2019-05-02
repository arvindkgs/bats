#!/usr/bin/env bash

runPositiveTest() {
    python bin/validation_suite.py $1
    if [ $? -eq 0 ]; then
        diff metadatas/tests/positive/success.log metadatas/tests/positive/positive.log
        if [ $? -eq 0 ]; then
            echo "PositiveTest: Success!"
        else
            echo "PositiveTest: Failure : expected log(metadatas/tests/positive/success.log) not same as generated log(metadatas/tests/positive/positive.log)"
        fi
     else
        echo "PositiveTest: Failure, validation should pass"
    fi
}

runNegativeTest() {
    python bin/validation_suite.py $1
    if [ $? -ne 0 ]; then
        diff metadatas/tests/negative/failure.log metadatas/tests/negative/negative.log
        if [ $? -eq 0 ]; then
            echo "NegativeTest: Success!"
        else
            echo "NegativeTest: Failure : expected log(metadatas/tests/negative/failure.log) not same as generated log(metadatas/tests/negative/negative.log)"
        fi
    else
        echo "NegativeTest: Failure : validation should fail"
    fi
}

runAllTest(){
    python bin/validation_suite.py metadatas/tests/all/individual.json
    if [ $? -ne 0 ]; then
        python bin/validation_suite.py metadatas/tests/all/dynamic.json
        if [ $? -ne 0 ]; then
            diff metadatas/tests/all/individual.log metadatas/tests/all/dynamic.log
            if [ $? -eq 0 ]; then
                echo "AllTest: Success"
            else
                echo "AllTest: Failure : generated individual log(metadatas/tests/all/individual.log) not same as dynamic generated log(metadatas/tests/all/dynamic.log)"
            fi
        else
          echo "AllTest: Failed, dynamic json validation should pass"
        fi
    else
        echo "AllTest: Failed, individual json validation should pass"
    fi
}
runPositiveTest "metadatas/tests/positive/positive.json"
runNegativeTest "metadatas/tests/negative/negative.json"
runAllTest

