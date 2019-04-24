import json
import sys
import comparelog
from Property import Property

"""
Application that compares two resources defined in a metadata.json file
"""
__author__ = "Arvind Kumar GS(arvind.kumar.gs@oracle.com)"


class CompareProperties(object):
    metadata = ""

    def __init__(self, metadataFile):
        self.metadata = metadataFile

    def validate(self):
        # read metadata.json
        passed = True
        try:
            with open(self.metadata, 'r') as json_file:
                config = json.load(json_file)
                # get options
                if 'options' in config:
                    comparelog.setOptions(config['options'])
                # check for logDir
                if 'logDir' in config and config['logDir'] != '':
                    comparelog.setLogDir(config['logDir'])
                # check for description
                if 'name' in config:
                    comparelog.print_info(msg="--------------------------------", args={})
                    comparelog.print_info(config['name'])
                    comparelog.print_info("--------------------------------")
                else:
                    comparelog.print_info("--------------------------------")
                    comparelog.print_info("Comparing checks defined in '" + self.metadata + "'")
                    comparelog.print_info("--------------------------------")

                for check in config['checks']:
                    check_name = check['name']
                    for compare in check['compare']:
                        # get dynamic variables if any
                        compare_name = compare['name'] if 'name' in compare else None
                        dynamicProperties = {}
                        if 'dynamic' in compare:
                            # Define dict with key, values for each dynamic object
                            for i, dynamic in enumerate(compare['dynamic']):
                                # compute and store dynamic value
                                dynamicProperty = Property(property=dynamic, check_name=check_name,
                                                           compare_name=compare_name)
                                key = str(i + 1) if dynamicProperty.getKey() == None else dynamicProperty.getKey()
                                value = dynamicProperty.getValue({})
                                dynamicProperties[key] = None if value is None else value[0][1]
                                pass
                        sourceProperty = Property(property=compare['source'], check_name=check_name,
                                                  compare_name=compare_name)
                        sourceData = sourceProperty.getValue(dynamicMap=dynamicProperties)
                        targetProperty = Property(property=compare['target'], check_name=check_name,
                                                  compare_name=compare_name)
                        targetData = targetProperty.getValue(dynamicMap=dynamicProperties)
                        if len(sourceData) == len(targetData):
                            for i in range(0, len(sourceData)):
                                checkPassed = False
                                if sourceData[i] is not None and sourceData[i][1] is not None and targetData[
                                    i] is not None and targetData[i][1] is not None and len(sourceData[i][1]) == len(targetData[i][1]):
                                    for j in range(0, len(sourceData[i][1])):
                                        if str(sourceData[i][1][j]) != str(targetData[i][1][j]):
                                            comparelog.print_info(msg=sourceData[i][0] + "(" + str(
                                                sourceData[i][1][j]) + ") != " + targetData[i][0] + "(" + str(
                                                targetData[i][1][j]) + ")",
                                                                  args={'fnName': check_name, 'type': comparelog.COMPARE,
                                                                        'compareName': compare_name})
                                            checkPassed = False
                                        else:
                                            comparelog.print_info_log(msg=sourceData[i][0] + "(" + str(
                                                sourceData[i][1][j]) + ") == " + targetData[i][0] + "(" + str(
                                                targetData[i][1][j]) + ")",
                                                                  args={'fnName': check_name, 'type': "COMPARE",
                                                                        'compareName': compare_name})
                                            checkPassed = True
                                else:
                                    checkPassed = False
                                passed = passed and checkPassed
        except IOError:
            comparelog.print_error(msg="Metadata file '" + self.metadata + "' not found.")
            passed = False
        return passed


if __name__ == "__main__":
    global metadata_file
    if len(sys.argv) < 2:
        print "Missing Metadata.json argument."
        print "Usage: compare_properties.py <metadata.json>"
        sys.exit(1)
    if CompareProperties(sys.argv[1]).validate():
        comparelog.print_info(msg="--------------------------------", args={})
        comparelog.print_info("Validation Successful.")
        comparelog.print_info("--------------------------------")

    else:
        comparelog.print_info(msg="--------------------------------", args={})
        comparelog.print_info("Validation Failed.")
        comparelog.print_info("--------------------------------")
        sys.exit(1)
