import copy

import comparelog
from Error import Error
from model import ResourceBuilder
from model.Property import Property


class PropertyMap(object):

    def __init__(self, parentPropertyMap=None):
        if parentPropertyMap is not None and type(parentPropertyMap) is PropertyMap:
            self.properties = copy.deepcopy(parentPropertyMap.properties)
        else:
            self.properties = {}

    def addDynamicPropertiesFromCheck(self, check, testName=None, failon=None):
        if testName is None:
            checkName = "Global"
            testName = check['name'] if 'name' in check else None
        else:
            checkName = check['name'] if 'name' in check else None
        passed = True
        if 'dynamic' in check:
            # Define dict with key, values for each dynamic object
            for i, dynamic in enumerate(check['dynamic']):
                # compute and store dynamic value
                dynamicResource = ResourceBuilder.build(property=dynamic, testName=testName, checkName=checkName,
                                                        dynamicProperties=self)
                key = str(i + 1) if dynamicResource.getKey() is None else dynamicResource.getKey()
                dynamicItems = dynamicResource.items
                self.properties[key] = None
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
                                    self.properties[key] = []
                                    for item in value:
                                        if isinstance(item.value, list):
                                            self.properties[key].extend(item.value)
                                        else:
                                            self.properties[key].append(item.value)
                                elif value is not None:
                                    self.properties[key] = [value]
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

    def addDynamicProperties(self, propertyMap):
        self.properties.update(propertyMap.properties)

    def __getitem__(self, key):
        retValue = None
        error = None
        if key is not None:
            dynamickey = key
            if '.' in key:
                dynamickey = key.split('.')[0]
            if dynamickey in self.properties:
                values = self.properties[dynamickey]
                if not isinstance(values, list):
                    values = [values]
                if dynamickey != key:
                    dynamickeyattributes = key.split('.')[1:]
                    for attribute in dynamickeyattributes:
                        newvalues = None
                        for i, value in enumerate(values):
                            if value:
                                if attribute in value:
                                    if not newvalues:
                                        newvalues = []
                                    newvalues.append(value.get(attribute))
                                else:
                                    error = Error(type=Error.MISSING_DYNAMIC_VALUE,
                                                  message="No key: '" + str(
                                                      attribute) + "' in object: " + dynamickey + " for dynamic key: '" + str(
                                                      key))
                                    break
                        values = newvalues
                retValue = values
        return Property(key, retValue, error)

    def __len__(self):
        return len(self.properties)

    def __contains__(self, item):
        return item in self.properties

    def __setitem__(self, key, value):
        self.properties[key] = value

    def addCommandLineArgs(self, args):
        if args:
            for argument in args:
                key, value = argument.split('=')
                self.properties[key] = value
