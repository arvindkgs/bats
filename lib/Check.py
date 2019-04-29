from lib import comparelog
from Resource import Resource
from Property import Property


def evaluateCheck(check, testName):
    checkType = check['type']
    # get dynamic variables if any
    checkName = check['name'] if 'name' in check else None
    dynamicProperties = {}
    passed = True
    if 'dynamic' in check:
        # Define dict with key, values for each dynamic object
        for i, dynamic in enumerate(check['dynamic']):
            # compute and store dynamic value
            dynamicProperty = Resource(property=dynamic, testName=testName,
                                       checkName=checkName)
            key = str(i + 1) if dynamicProperty.getKey() is None else dynamicProperty.getKey()
            value = dynamicProperty.getProperties(dynamicProperties)
            dynamicProperties[key] = None if value is None else value[0].value
            pass
    if checkType == 'COMPARE':
        source = Resource(property=check['source'], testName=testName,
                          checkName=checkName)
        sourceProperty = source.getProperties(dynamicMap=dynamicProperties)
        target = Resource(property=check['target'], testName=testName,
                          checkName=checkName)
        targetProperty = target.getProperties(dynamicMap=dynamicProperties)
        if len(sourceProperty) == len(targetProperty):
            for i, source_property in enumerate(sourceProperty):
                compare = source_property.compare(targetProperty[i])
                if compare == Property.MATCH:
                    comparelog.print_info_log(msg=source_property.name + "(" + str(
                        source_property.value) + ") == " + targetProperty[
                                                      i].name + "(" + str(
                        targetProperty[i].value) + ")",
                                              args={'fnName': testName, 'type': checkType,
                                                    'checkName': checkName})
                    passed = passed and True
                elif compare == Property.NO_MATCH:
                    comparelog.print_info_log(msg=source_property.name + "(" + str(
                        source_property.value) + ") != " + targetProperty[
                                                      i].name + "(" + str(
                        targetProperty[i].value) + ")",
                                              args={'fnName': testName, 'type': checkType,
                                                    'checkName': checkName})
                    passed = passed and False
        else:
            comparelog.print_info_log(
                msg="Mismatch in extrapolation on properties in Source resource: (File: '" + source.file + "', Property: '" + str(
                    source.property) + "') and  Target resource: (File: '" + target.file + "', Property: '" + str(
                    target.property) + "')",
                args={'fnName': testName, 'type': "COMPARE",
                      'compareName': checkName})
            passed = False
    else:
        comparelog.print_error(
            msg="Unsupported check type '" + checkType + "'. Only 'COMPARE' and 'SUCCESS' is supported.", args={
                'fnName': testName, 'compareName': checkName
            })
        passed = False
    return passed
