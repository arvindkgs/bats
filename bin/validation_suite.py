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
        self.action = args.action
        self.metadata = args.metadataFile if self.action == "metadata" else None
        self.source = args.source if self.action == "compare" else None
        self.target = args.target if self.action == "compare" else None
        self.type = args.type if self.action == "compare" else None
        self.dynamic = args.dynamic
        self.failon = args.failon
        ShellHandler.runShellCommand("if [-d tmp]; then rm -rf tmp; fi; mkdir tmp")

    def validate(self):
        passed = True
        if self.action == "metadata":
            try:
                with open(self.metadata, 'r') as json_file:
                    config = json.load(json_file)
            except IOError:
                comparelog.print_error(msg="Metadata file '" + self.metadata + "' not found.")
                sys.exit(1)
            except ValueError as e:
                comparelog.print_error(msg="Error parsing metadata file '" + self.metadata + "'.")
                sys.exit(1)
        elif self.action == "compare":
            check = dict(name="json compare", type="COMPARE", source=dict(type="JSON", file=self.source),
                         target=dict(type="JSON", file=self.target))
            config = dict(name="Comparing source(" + self.source + ") with target(" + self.target + ")",
                          tests=[dict(name="File Comparision", checks=[check])])
        else:
            comparelog.print_error(msg="Only 'metadata' and 'compare' are allowed actions.")
            sys.exit(1)
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
            if not Dynamic.addDynamicProperties(test, dynamicProperties, failon=self.failon):
                passed = False
            for check in test['checks']:
                checkPassed = Check(check, testName, dynamicProperties, failon=self.failon).evaluateCheck()
                passed = passed and checkPassed

        return passed

    def __del__(self):
        ShellHandler.runShellCommand("if [ -d tmp ]; then rm -rf tmp; fi;")


if __name__ == "__main__":
    parent_parser = argparse.ArgumentParser(add_help=False,
                                            description="Compares (static and dynamic) resources defined in the metadata.json")
    parent_parser.add_argument('-D', required=False, dest="dynamic", help="Dynamic values to be passed",
                               action="append", metavar="KEY=VALUE")
    parent_parser.add_argument('--failon', required=False, dest="failon", nargs="+", metavar="ERROR-TYPE",
                               help="Fail validation when this type of message is encountered", type=str)

    parser = argparse.ArgumentParser(description="Compares (static and dynamic) resources defined in the metadata.json")

    subparsers = parser.add_subparsers(help="allowed actions", dest="action")
    parser_metadata = subparsers.add_parser("metadata",
                                            help="Takes metadata file and runs tests and checks defined in it.",
                                            parents=[parent_parser])
    parser_metadata.add_argument('metadataFile', default='metadata.json', type=str,
                                 help="(Required) Metadata file which defines resources that should be compared")
    parser_compare = subparsers.add_parser("compare", help="Compares source and target file", parents=[parent_parser])
    parser_compare.add_argument('--source', required=True, dest="source", help="Source Resource")
    parser_compare.add_argument('--target', required=True, dest="target", help="Target Resource")
    parser_compare.add_argument('--type', required=True, dest="type", help="Source and Target type")
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
