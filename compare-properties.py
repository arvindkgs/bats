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
                        dynamicProperties = {}
                        if 'dynamic' in compare:
                            # Define dict with key, values for each dynamic object
                            for i, dynamic in enumerate(compare['dynamic']):
                                # compute and store dynamic value
                                dynamicProperty = Property(property=dynamic, check_name=check_name)
                                key = str(i) if dynamicProperty.getKey() == None else dynamicProperty.getKey()
                                dynamicProperties[key] = dynamicProperty.getValue()
                                pass
                        checkPassed = False
                        sourceProperty = Property(property=compare['source'], check_name=check_name)
                        # pdb.set_trace()
                        sourceData = sourceProperty.getValue(dynamicMap=dynamicProperties)
                        targetProperty = Property(property=compare['target'], check_name=check_name)
                        targetData = targetProperty.getValue(dynamicMap=dynamicProperties)
                        for i in range(0, len(sourceData)):
                            if sourceData[i] is not None and targetData[i] is not None:
                                if str(sourceData[i]) != str(targetData[i]):
                                    comparelog.print_error(msg=sourceProperty.property + "(" + str(
                                        sourceData[i]) + ") != " + targetProperty.property + "(" + str(targetData[i]) + ")",
                                                           args={'fnName': check_name, 'type': comparelog.COMPARE})
                                else:
                                    comparelog.print_info_log(msg=sourceProperty.property + "(" + str(
                                        sourceData[i]) + ") == " + targetProperty.property + "(" + str(targetData[i]) + ")",
                                                              args={'fnName': check_name, 'type': "COMPARE"})
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
