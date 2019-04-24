#!/usr/bin/env bash

runPositiveTest() {
    python compare_properties.py $1
    if [ $? -eq 0 ]; then
        echo "Success : $1"
    else
        echo "Failure : $1"
    fi
}

runNegativeTest() {
    python compare_properties.py $1
    if [ $? -ne 0 ]; then
        echo "Success : $1"
    else
        echo "Failure : $1"
    fi
}

runPositiveTest "metadatas/tests/positive_test.json"
runNegativeTest "metadatas/tests/negative_test.json"

