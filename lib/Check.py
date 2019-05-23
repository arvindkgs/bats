import ResourceBuilder
from Property import Property
from lib import comparelog
from lib.Dynamic import addDynamicProperties


class Check:
    def __init__(self, check, testName, dynamicProperties, failon):
        self.check = check
        self.checkName = check['name']
        self.checkType = check['type']
        self.failon = failon
        self.dynamicProperties = dynamicProperties
        self.testName = testName

    def evaluateCheck(self):
        passed = True
        addDynamicProperties(self.check, self.dynamicProperties, self.testName)
        if self.checkType == 'COMPARE':
            source = ResourceBuilder.build(property=self.check['source'], testName=self.testName,
                                           checkName=self.checkName)
            sourcePropertyList = source.getProperties(dynamicMap=self.dynamicProperties)
            target = ResourceBuilder.build(property=self.check['target'], testName=self.testName,
                                           checkName=self.checkName)
            targetPropertyList = target.getProperties(dynamicMap=self.dynamicProperties)
            cardinality = 'one-to-one' if 'cardinality' not in self.check else self.check['cardinality']
            sourceProperty = sourcePropertyList[0][1]
            if cardinality == 'one-to-one':
                targetProperty = []
                for targetPropertyTuple in targetPropertyList:
                    targetProperty.extend(targetPropertyTuple[1])
                passed = passed and self.compareSourceTargetFile(source, sourceProperty, target, targetProperty)
            elif cardinality == 'one-to-many':
                for targetPropertyTuple in targetPropertyList:
                    targetProperty = targetPropertyTuple[1]
                    passed = passed and self.compareSourceTargetFile(source, sourceProperty, target, targetProperty)
        else:
            comparelog.print_error_log(
                msg="Unsupported check type '" + self.checkType + "'. Only 'COMPARE' and 'SUCCESS' is supported.",
                args={
                    'fnName': self.testName, 'checkName': self.checkName, 'type': comparelog.SYNTAX_ERROR
                })
            # passed = False
        return passed

    def compareSourceTargetFile(self, source, sourceProperty, target, targetProperty):
        passed = True
        if sourceProperty is not None and targetProperty is not None:
            if len(sourceProperty) == len(targetProperty) and any(sourceProperty) and any(targetProperty):
                for i, source_property in enumerate(sourceProperty):
                    compare = source_property.compare(targetProperty[i])
                    if compare == Property.MATCH:
                        comparelog.print_info_log(msg=str(source_property) + " == " + str(targetProperty[i]),
                                                  args={'fnName': self.testName, 'type': self.checkType,
                                                        'checkName': self.checkName})
                        passed = passed and True
                    elif compare == Property.NO_MATCH:
                        comparelog.print_info(msg=str(source_property) + " != " + str(targetProperty[i]),
                                              args={'fnName': self.testName, 'type': self.checkType,
                                                    'checkName': self.checkName})
                        passed = passed and False
                    elif compare == Property.ERROR:
                        comparelog.print_info(
                            "Values mismatch. Source: " + str(source_property) + ", Target: " + str(targetProperty[i]),
                            args={'fnName': self.testName, 'type': comparelog.VALUE_MISMATCH,
                                  'checkName': self.checkName})
                        if self.failon and comparelog.VALUE_MISMATCH in self.failon:
                            passed = passed and False
            else:
                if not any(sourceProperty):
                    comparelog.print_info(
                        msg="Source Properties missing : "+source.property,
                        args={'fnName': self.testName, 'type': comparelog.VALUE_MISMATCH,
                              'checkName': self.checkName, 'source': source.file})
                if not any(targetProperty):
                    comparelog.print_info(
                        msg="Target Properties missing : "+target.property,
                        args={'fnName': self.testName, 'type': comparelog.VALUE_MISMATCH,
                              'checkName': self.checkName, 'source': target.file})
                else:
                    comparelog.print_info(
                        msg="Source and target properties length mismatch. Source Length: " + len(
                            sourceProperty) + ", Target Length: " + len(targetProperty),
                        args={'fnName': self.testName, 'type': comparelog.VALUE_MISMATCH,
                              'checkName': self.checkName})

                if self.failon and comparelog.VALUE_MISMATCH in self.failon:
                    passed = passed and False
        return passed
