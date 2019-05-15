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
            value = dynamicProperty.getProperties(dynamicProperties)
            dynamicProperties[key] = []
            if isinstance(value, list):
                for item in value:
                    dynamicProperties[key].extend(item.value)
            elif value is not None:
                dynamicProperties[key] = [value]
