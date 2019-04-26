import json
import sys
import comparelog
from Resource import Resource
import Property

"""
Tool to run post resizing or scaleout (or any other process) validation checks
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

                for test in config['tests']:
                    testName = test['name']
                    testPassed = True
                    for check in test['checks']:
                        checkPassed = True
                        checkType = check['type']
                        # get dynamic variables if any
                        checkName = check['name'] if 'name' in check else None
                        dynamicProperties = {}
                        if 'dynamic' in check:
                            # Define dict with key, values for each dynamic object
                            for i, dynamic in enumerate(check['dynamic']):
                                # compute and store dynamic value
                                dynamicProperty = Resource(property=dynamic, testName=testName,
                                                           checkName=checkName)
                                key = str(i + 1) if dynamicProperty.getKey() == None else dynamicProperty.getKey()
                                value = dynamicProperty.getValue(dynamicProperties)
                                dynamicProperties[key] = None if value is None else value[0].value
                                pass
                        if checkType == 'COMPARE':
                            source = Resource(property=check['source'], testName=testName,
                                              checkName=checkName)
                            sourceProperty = source.getValue(dynamicMap=dynamicProperties)
                            target = Resource(property=check['target'], testName=testName,
                                              checkName=checkName)
                            targetProperty = target.getValue(dynamicMap=dynamicProperties)
                            propertiesPassed = True
                            if len(sourceProperty) == len(targetProperty):
                                for i, source_property in enumerate(sourceProperty):
                                    compare = source_property.compare(targetProperty[i])
                                    if compare == Property.MATCH:
                                        comparelog.print_info_log(msg=source_property.name + "(" + str(
                                            source_property.value) + ") == " + targetProperty[
                                                                          i].name + "(" + str(
                                            targetProperty[i].value) + ")",
                                                                  args={'fnName': testName, 'type': checkType,
                                                                        'checkName': checkName})
                                        propertiesPassed = propertiesPassed and True
                                    elif compare == Property.NO_MATCH:
                                        comparelog.print_info_log(msg=source_property.name + "(" + str(
                                            source_property.value) + ") != " + targetProperty[
                                                                          i].name + "(" + str(
                                            targetProperty[i].value) + ")",
                                                                  args={'fnName': testName, 'type': checkType,
                                                                        'checkName': checkName})
                                        propertiesPassed = propertiesPassed and False
                            else:
                                comparelog.print_info_log(
                                    msg="Mismatch in extrapolation on properties in Source resource: (File: '" + source.file + "', Property: '" + str(
                                        source.property) + "') and  Target resource: (File: '" + target.file + "', Property: '" + str(
                                        target.property) + "')",
                                    args={'fnName': testName, 'type': "COMPARE",
                                          'compareName': checkName})
                                propertiesPassed = False
                            checkPassed = checkPassed and propertiesPassed
                        testPassed = testPassed and checkPassed
                    passed = passed and testPassed
        except IOError:
            comparelog.print_error(msg="Metadata file '" + self.metadata + "' not found.")
            sys.exit(1)
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
