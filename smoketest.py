from compare_properties import CompareProperties

def test_postive_compare():
    assert CompareProperties("metadatas/tests/positive_test.json").validate() == True

def test_negative_compare():
    assert CompareProperties("metadatas/tests/negative_test.json").validate() == False