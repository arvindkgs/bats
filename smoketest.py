from bin.validation_suite import CompareProperties
import subprocess


def test_postive_compare():
    passed = CompareProperties("positive.json").validate()
    process = subprocess.Popen(
        ['diff metadatas/tests/positive/positive.log metadatas/tests/positive/success.log'], stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, shell=True)
    process.communicate()
    assert passed is True and process.returncode == 0


def later_test_negative_compare():
    assert CompareProperties("metadatas/tests/negative_test.json").validate() is False
