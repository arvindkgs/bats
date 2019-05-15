import ResourceBuilder
from Property import Property
from lib import comparelog
from lib.Dynamic import addDynamicProperties


def evaluateCheck(check, testName, dynamicProperties):
    checkType = check['type']
    # get dynamic variables if any
    checkName = check['name'] if 'name' in check else None
    passed = True
    addDynamicProperties(check, dynamicProperties, testName)
    if checkType == 'COMPARE':
        source = ResourceBuilder.build(property=check['source'], testName=testName,
                                       checkName=checkName)
        sourceProperty = source.getProperties(dynamicMap=dynamicProperties)
        target = ResourceBuilder.build(property=check['target'], testName=testName,
                                       checkName=checkName)
        targetProperty = target.getProperties(dynamicMap=dynamicProperties)
        if sourceProperty is not None and targetProperty is not None:
            if len(sourceProperty) == len(targetProperty):
                for i, source_property in enumerate(sourceProperty):
                    compare = source_property.compare(targetProperty[i])
                    if compare == Property.MATCH:
                        comparelog.print_info_log(msg=str(source_property) + " == " + str(targetProperty[i]),
                                                  args={'fnName': testName, 'type': checkType,
                                                        'checkName': checkName})
                        passed = passed and True
                    elif compare == Property.NO_MATCH:
                        comparelog.print_info(msg=str(source_property) + " != " + str(targetProperty[i]),
                                              args={'fnName': testName, 'type': checkType,
                                                    'checkName': checkName})
                        passed = passed and False
            else:
                comparelog.print_info(
                    msg="Mismatch in number of properties in Source: (File: '" + source.file + "', Property: '" + str(
                        source.property) + "') and  Target: (File: '" + target.file + "', Property: '" + str(
                        target.property) + "')",
                    args={'fnName': testName, 'type': checkType,
                          'checkName': checkName})
                passed = False
        else:
            passed = False
    else:
        comparelog.print_error_log(
            msg="Unsupported check type '" + checkType + "'. Only 'COMPARE' and 'SUCCESS' is supported.", args={
                'fnName': testName, 'checkName': checkName
            })
        passed = False
    return passed
