import pkg_resources
import json
import sys
import argparse

from lib.model import ResourceBuilder
from lib.Dynamic import PropertyMap

if __name__ == "__main__" and __package__ is None:
    from sys import path
    from os.path import dirname as dir

    path.append(dir(path[0]))

from lib.handler.ShellHandler import *
from lib import comparelog, Dynamic
from lib.Check import Check

"""
Tool to run post resizing or scaleout (or any other process) validation checks
"""
__author__ = "Arvind Kumar GS(arvind.kumar.gs@oracle.com)"


class CompareProperties(object):
    metadata = ""

    def __init__(self, args):
        self.action = args.action
        # Resize
        self.source = args.source if self.action == "resize" else None
        self.log = args.log if self.action == "resize" else None
        # Metadata
        self.metadata = args.metadataFile if self.action == "metadata" else None
        # Extract
        self.file = args.file if self.action == "extract" else None
        self.type = args.type if self.action == "extract" else None
        self.property = args.property if self.action == "extract" else None
        # Compare
        self.srcFile = args.srcFile if self.action == "compare" else None
        self.srcType = args.srcType if self.action == "compare" else None
        self.srcProperty = args.srcProperty if self.action == "compare" else None
        self.trgFile = args.trgFile if self.action == "compare" else None
        self.trgType= args.trgType if self.action == "compare" else None
        self.trgProperty = args.trgProperty if self.action == "compare" else None
        self.dynamic = args.dynamic
        self.failon = args.failon
        self.tests = args.test
        self.checks = args.check
        runShellCommand("if [-d tmp]; then rm -rf tmp; fi; mkdir tmp")

    def validate(self):
        passed = True
        # Set cmd-line dynamic properties
        globalProperties = PropertyMap(None)
        if self.dynamic:
            for argument in self.dynamic:
                key, value = argument.split('=')
                globalProperties[key] = value
        if self.action == "compare":
            check = dict(name="json compare", type="COMPARE", source=dict(type="JSON", file=self.srcFile),
                         target=dict(type="JSON", file=self.trgFile))
            config = dict(name="Comparing source(" + self.srcFile + ") with target(" + self.trgFile + ")",
                          tests=[dict(name="File Comparision", checks=[check])])
        elif self.action == "extract":
            property = {'file': self.file, 'property': self.property}
            if self.type is not None:
                property['type'] = self.type
            elif self.file.find('.') != -1:
                property['type'] = self.file[self.file.rindex('.')+1:].upper()
            if not (
                'type' in property
                and property['type'] in ['JSON', 'XML', 'PROPERTIES', 'CONFIG']
            ):
                print(
                    "Not able to determine property type. Set cmdline arg '--type' = JSON or XML or PROPERTIES or CONFIG")
                sys.exit(1)
            else:
                resource = ResourceBuilder.build(property, None, None, {})
                if resource.error:
                    print("Error: "+resource.error.type+", Message: "+resource.error.message)
                    sys.exit(1)
                else:
                    print("Extracted properties: ")
                    value_str = ''
                    for item in resource.items:
                        if item and item.properties:
                            for values in item.properties:
                                if values:
                                    value_str += "\t"+str(values.value)+","
                    if len(value_str)>0:
                        value_str = value_str[:len(value_str)-1]
                    print value_str
                sys.exit(0)

        elif self.action == "metadata":
            try:
                with open(self.metadata, 'r') as json_file:
                    config = json.load(json_file)
            except IOError:
                comparelog.print_error(msg="Metadata file '" + self.metadata + "' not found.")
                sys.exit(1)
            except ValueError as e:
                comparelog.print_error(msg="Error parsing metadata file '" + self.metadata + "'.")
                sys.exit(1)
        elif self.action == "resize":
            resource_package = "bats"
            resource_path = '/'.join(('templates', 'resizing_metadata.json'))
            resizing_metadata = pkg_resources.resource_stream(resource_package, resource_path)
            config = json.load(resizing_metadata)
            comparelog.setLogFileName("validation.log") if self.log is None else comparelog.setLogFileName(args.log)
            globalProperties['source'] = args.source
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

        # Add global dynamic properties from config
        globalProperties.addDynamicPropertiesFromCheck(config, failon=self.failon)
        for test in config['tests']:
            if not self.tests or (self.tests and test['name'] in self.tests):
                testName = test['name']
                dynamicProperties = PropertyMap(globalProperties)
                if not dynamicProperties.addDynamicPropertiesFromCheck(test, failon=self.failon):
                    passed = False
                for check in test['checks']:
                    if not self.checks or (self.checks and check['name'] in self.checks):
                        checkPassed = Check(check, testName, dynamicProperties, failon=self.failon).evaluateCheck()
                        passed = checkPassed and passed
        # Return validation result
        return passed

    def __del__(self):
        runShellCommand("if [ -d tmp ]; then rm -rf tmp; fi;")


if __name__ == "__main__":
    parent_parser = argparse.ArgumentParser(add_help=False,
                                            description="Compares (static and dynamic) resources defined in the metadata.json")
    parent_parser.add_argument('-D', required=False, dest="dynamic", help="Dynamic values to be passed",
                               action="append", metavar="KEY=VALUE")
    parent_parser.add_argument('--failon', required=False, dest="failon", nargs="+", metavar="ERROR-TYPE",
                               help="Fail validation when this type of message is encountered", type=str)

    parser = argparse.ArgumentParser(description="Compares (static and dynamic) resources defined in the metadata.json")

    subparsers = parser.add_subparsers(help="allowed actions", dest="action")
    # Metadata action
    parser_metadata = subparsers.add_parser("metadata",
                                            help="Takes metadata file and runs tests and checks defined in it.",
                                            parents=[parent_parser])
    parser_metadata.add_argument('metadataFile', default='metadata.json', type=str,
                                 help="(Required) Metadata file which defines resources that should be compared")
    parser_metadata.add_argument('--test', required=False, dest="test", nargs="+", metavar="TEST_NAME",
                               help="Specify test names of tests to run, separated by space.")
    parser_metadata.add_argument('--check', required=False, dest="check", nargs="+", metavar="CHECK_NAME",
                               help="Specify test names of tests to run, separated by space.")
    # Compare Action
    parser_compare = subparsers.add_parser("compare", help="Compares source and target file", parents=[parent_parser])
    parser_compare.add_argument('--srcFile', required=True, dest="srcFile", help="Source File")
    parser_compare.add_argument('--srcType', required=True, dest="srcType", help="Source type")
    parser_compare.add_argument('--srcProperty', required=False, dest="srcProperty", help="Source property")
    parser_compare.add_argument('--trgFile', required=True, dest="trgFile", help="Target File")
    parser_compare.add_argument('--trgType', required=True, dest="trgType", help="Target type")
    parser_compare.add_argument('--trgProperty', required=False, dest="trgProperty", help="Target property")
    # Resize Action
    parser_resize = subparsers.add_parser("resize",
                                          help="Runs resize OCI checks. Refer https://confluence.oraclecorp.com/confluence/display/FALCM/Resize+OCI+Checks for details.",
                                          parents=[parent_parser])
    parser_resize.add_argument('source', type=str, help="(Required) Path of size profile json to validate against. For example:"
                                                                       " '/podscratch/lcm-artifacts/size-profiles-factory-default/facs/size-profile-overrides/11.13.19.10.0/s-post-factory-override.json'")
    parser_resize.add_argument('--log', required=False, dest="log", help="Log - defaults to 'validation.log' in pwd")
    parser_resize.add_argument('--test', required=False, dest="test", nargs="+", metavar="TEST_NAME",
                               help="Limits tests to run, specify test names separated by space.")
    parser_resize.add_argument('--check', required=False, dest="check", nargs="+", metavar="CHECK_NAME",
                               help="Limits checks to run, specify check names separated by space.")
    # Extract Action
    parser_extract = subparsers.add_parser("extract", help="Extracts a property from file", parents=[parent_parser])
    parser_extract.add_argument('file', help='(Required) File to extract property from')
    parser_extract.add_argument('property', help='(Required) Property to extract')
    parser_extract.add_argument('--type', dest='type', required=False, help='Optional file type, if file extension is not correct. Supported file types = JSON, XML, PROPERTIES, CONFIG')
    args = parser.parse_args()

    if args.action == "compare" and not args.srcProperty and args.trgProperty:
        comparelog.print_error(msg="If target property is given, source property is necessary")
        sys.exit(1)

    if args.action == "compare" and args.srcProperty and not args.trgProperty:
        comparelog.print_error(msg="If source property is given, target property is necessary")
        sys.exit(1)

    if args.action == "compare" and not args.srcProperty and not args.trgProperty and args.srcType != args.trgType:
        comparelog.print_error(msg="If properties are not specified, type should match.")
        sys.exit(1)

    if CompareProperties(args).validate():
        comparelog.print_info(msg="--------------------------------", args={})
        comparelog.print_info("Validation Successful.")
        comparelog.print_info("--------------------------------")

    else:
        comparelog.print_info(msg="--------------------------------", args={})
        comparelog.print_info("Validation Failed.")
        comparelog.print_info("--------------------------------")
        sys.exit(1)
