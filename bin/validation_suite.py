import json
import sys
import argparse

if __name__ == "__main__" and __package__ is None:
    from sys import path
    from os.path import dirname as dir

    path.append(dir(path[0]))

from lib import ShellHandler, comparelog, Dynamic
from lib.Check import Check

"""
Tool to run post resizing or scaleout (or any other process) validation checks
"""
__author__ = "Arvind Kumar GS(arvind.kumar.gs@oracle.com)"


class CompareProperties(object):
    metadata = ""

    def __init__(self, args):
        self.metadata = args.metadataFile
        self.dynamic = args.dynamic
        self.failon = args.failon
        ShellHandler.runShellCommand("if [-d tmp]; then rm -rf tmp; fi; mkdir tmp")

    def validate(self):
        passed = True
        try:
            with open(self.metadata, 'r') as json_file:
                config = json.load(json_file)
                # get options
                if 'options' in config:
                    comparelog.setOptions(config['options'])
                # check for log
                if 'log' in config and config['log'] != '':
                    comparelog.setLogFileName(config['log'])
                # check for description
                if 'name' in config:
                    comparelog.print_info(msg="--------------------------------", args={})
                    comparelog.print_info(config['name'])
                    comparelog.print_info("--------------------------------")
                else:
                    comparelog.print_info("--------------------------------")
                    comparelog.print_info("Running '" + self.metadata + "'")
                    comparelog.print_info("--------------------------------")

                for test in config['tests']:
                    testName = test['name']
                    dynamicProperties = {}
                    Dynamic.addCommandLineArgs(self.dynamic, dynamicProperties)
                    passed = passed and Dynamic.addDynamicProperties(test, dynamicProperties, failon=self.failon)
                    for check in test['checks']:
                        checkPassed = Check(check, testName, dynamicProperties, failon=self.failon).evaluateCheck()
                        passed = passed and checkPassed

        except IOError:
            comparelog.print_error(msg="Metadata file '" + self.metadata + "' not found.")
            sys.exit(1)
        except ValueError as e:
            comparelog.print_error(msg="Error parsing metadata file '" + self.metadata + "'.")
            sys.exit(1)
        return passed

    def __del__(self):
        ShellHandler.runShellCommand("if [ -d tmp ]; then rm -rf tmp; fi;")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compares (static and dynamic) resources defined in the metadata.json")
    parser.add_argument('--metadata', default='metadata.json', dest='metadataFile', required=True, type=str,
                        help="(Required) Metadata file which defines resources that should be compared")
    parser.add_argument('--failon', required=False, dest="failon", nargs="+",
                        help="Fail Validation when this type of message is encountered", type=str)
    parser.add_argument('-D', required=False, dest="dynamic", help="Dynamic values to be passed", action="append")
    args = parser.parse_args()
    if CompareProperties(args).validate():
        comparelog.print_info(msg="--------------------------------", args={})
        comparelog.print_info("Validation Successful.")
        comparelog.print_info("--------------------------------")

    else:
        comparelog.print_info(msg="--------------------------------", args={})
        comparelog.print_info("Validation Failed.")
        comparelog.print_info("--------------------------------")
        sys.exit(1)
