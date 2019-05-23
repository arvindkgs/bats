from lib import ResourceBuilder


def addDynamicProperties(check, dynamicProperties, testName='Global'):
    checkName = check['name'] if 'name' in check else None
    if 'dynamic' in check:
        # Define dict with key, values for each dynamic object
        for i, dynamic in enumerate(check['dynamic']):
            # compute and store dynamic value
            dynamicProperty = ResourceBuilder.build(property=dynamic, testName=testName,
                                                    checkName=checkName)
            key = str(i + 1) if dynamicProperty.getKey() is None else dynamicProperty.getKey()
            if key not in dynamicProperties:
                propertiesTupleList = dynamicProperty.getProperties(dynamicProperties)
                dynamicProperties[key] = []
                if propertiesTupleList:
                    for propertiesTuple in propertiesTupleList:
                        value = propertiesTuple[1]
                        if isinstance(value, list):
                            for item in value:
                                if isinstance(item.value, list):
                                    dynamicProperties[key].extend(item.value)
                                else:
                                    dynamicProperties[key].append(item.value)
                        elif value is not None:
                            dynamicProperties[key] = [value]


def addCommandLineArgs(args, dynamicProperties):
    if args:
        for argument in args:
            key, value = argument.split('=')
            dynamicProperties[key] = value
