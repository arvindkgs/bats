from model import ResourceBuilder
import comparelog
from Error import Error


def addDynamicProperties(check, dynamicProperties, testName='Global', failon=None):
    checkName = check['name'] if 'name' in check else None
    passed = True
    if 'dynamic' in check:
        # Define dict with key, values for each dynamic object
        for i, dynamic in enumerate(check['dynamic']):
            # compute and store dynamic value
            dynamicResource = ResourceBuilder.build(property=dynamic, testName=testName,
                                                    checkName=checkName, dynamicProperties=dynamicProperties)
            key = str(i + 1) if dynamicResource.getKey() is None else dynamicResource.getKey()
            if key not in dynamicProperties:
                dynamicItems = dynamicResource.items
                dynamicProperties[key] = None
                if not dynamicResource.error:
                    if dynamicItems and len(dynamicItems) > 0:
                        for dynamicItem in dynamicItems:
                            if dynamicItem.error:
                                printToConsole = False
                                if failon and dynamicItem.error.type in failon:
                                    passed = False
                                    printToConsole = True
                                comparelog.print_error(
                                    msg=dynamicItem.error.message,
                                    args={"testName": testName,
                                          "checkName": checkName,
                                          "type": dynamicItem.error.type,
                                          "source": dynamicItem.file},
                                    console=printToConsole)
                            else:
                                value = dynamicItem.properties
                                if isinstance(value, list):
                                    dynamicProperties[key] = []
                                    for item in value:
                                        if isinstance(item.value, list):
                                            dynamicProperties[key].extend(item.value)
                                        else:
                                            dynamicProperties[key].append(item.value)
                                elif value is not None:
                                    dynamicProperties[key] = [value]
                                else:
                                    printToConsole = False
                                    if failon and Error.MISSING_DYNAMIC_VALUE in failon:
                                        passed = False
                                        printToConsole = True
                                    comparelog.print_error(
                                        msg="No dynamic properties.",
                                        args={"testName": testName,
                                              "checkName": checkName,
                                              "type": Error.MISSING_DYNAMIC_VALUE,
                                              "source": dynamicItem.file},
                                        console=printToConsole)
                else:
                    printToConsole = False
                    if failon and dynamicResource.error.type in failon:
                        passed = False
                        printToConsole = True
                    comparelog.print_error(
                        msg=dynamicResource.error.message,
                        args={"testName": testName,
                              "type": dynamicResource.error.type,
                              "checkName": checkName,
                              "source": dynamicResource.file},
                        console=printToConsole)
    return passed


def addCommandLineArgs(args, dynamicProperties):
    if args:
        for argument in args:
            key, value = argument.split('=')
            dynamicProperties[key] = value
