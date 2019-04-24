import json
import sys
from Property import Property
import comparelog
import pdb

"""
Application that compares two resources defined in a metadata.json file
"""
__author__ = "Arvind Kumar GS(arvind.kumar.gs@oracle.com)"


class Compare_FusionApps_properties(object):
    metadata = ""

    def __init__(self, metadataFile):
        self.metadata = metadataFile

    def validate(self):
        # read metadata.json
        passed = True
        try:
            with open(self.metadata, 'r') as json_file:
                config = json.load(json_file)
                # check for logDir
                if 'logDir' in config and config['logDir'] != '':
                    comparelog.setLogDir(config['logDir'])
                # check for description
                if 'description' in config:
                    comparelog.print_info(msg="--------------------------------", args={})
                    comparelog.print_info(config['description'])
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
                                # pdb.set_trace()
                                value = dynamicProperty.getValue({})
                                dynamicProperties[key] = None if value is None else value[0][1]
                                pass
                        checkPassed = False
                        sourceProperty = Property(property=compare['source'], check_name=check_name,
                                                  compare_name=compare_name)
                        # pdb.set_trace()
                        sourceData = sourceProperty.getValue(dynamicMap=dynamicProperties)
                        # print "Source Data" + str(sourceData)
                        targetProperty = Property(property=compare['target'], check_name=check_name,
                                                  compare_name=compare_name)
                        targetData = targetProperty.getValue(dynamicMap=dynamicProperties)
                        # print "Target Data" + str(targetData)
                        for i in range(0, len(sourceData)):
                            if sourceData[i] is not None and sourceData[i][1] is not None and targetData[
                                i] is not None and targetData[i][1] is not None:
                                if str(sourceData[i][1]) != str(targetData[i][1]):
                                    comparelog.print_error(msg=sourceData[i][0] + "(" + str(
                                        sourceData[i][1]) + ") != " + targetData[i][0] + "(" + str(
                                        targetData[i][1]) + ")",
                                                           args={'fnName': check_name, 'type': comparelog.COMPARE,
                                                                 'compareName': compare_name})
                                else:
                                    comparelog.print_info_log(msg=sourceData[i][0] + "(" + str(
                                        sourceData[i][1]) + ") == " + targetData[i][0] + "(" + str(
                                        targetData[i][1]) + ")",
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
        print "Usage: compare-properties.py <metadata.json>"
        sys.exit(1)
    if Compare_FusionApps_properties(sys.argv[1]).validate():
        print("Validation Successful.")
    else:
        print("Validation failed.")
        sys.exit(1)
