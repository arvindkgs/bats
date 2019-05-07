import json
import sys

if __name__ == "__main__" and __package__ is None:
    from sys import path
    from os.path import dirname as dir

    path.append(dir(path[0]))

from lib import *

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
                # check for logFileName
                if 'logFileName' in config and config['logFileName'] != '':
                    comparelog.setLogFileName(config['logFileName'])
                # check for description
                if 'name' in config:
                    comparelog.print_info(msg="--------------------------------", args={})
                    comparelog.print_info(config['name'])
                    comparelog.print_info("--------------------------------")
                else:
                    comparelog.print_info("--------------------------------")
                    comparelog.print_info("Running tests defined in '" + self.metadata + "'")
                    comparelog.print_info("--------------------------------")

                for test in config['tests']:
                    testName = test['name']
                    for check in test['checks']:
                        checkPassed = Check.evaluateCheck(check, testName)
                        passed = passed and checkPassed

        except IOError:
            comparelog.print_error(msg="Metadata file '" + self.metadata + "' not found.")
            sys.exit(1)
        except ValueError as e:
            comparelog.print_error(msg="Error parsing metadata file '" + self.metadata + "'.")
            sys.exit(1)
        return passed


if __name__ == "__main__":
    global metadata_file
    if len(sys.argv) < 2:
        print "Missing Metadata.json argument."
        print "Usage: validation_suite.py <metadata.json>"
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
