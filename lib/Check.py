import ResourceBuilder
from Property import Property
from lib import comparelog
from lib.Dynamic import addDynamicProperties
from lib.Resource import Item
from lib.Error import Error


class Check:
    def __init__(self, check, testName, dynamicProperties, failon):
        self.check = check
        self.checkName = check['name']
        self.checkType = check['type']
        self.testName = testName
        self.failon = failon
        self.dynamicProperties = dynamicProperties

    def evaluateCheck(self):
        passed = True
        addDynamicProperties(self.check, self.dynamicProperties, self.testName)
        if self.checkType == 'COMPARE':
            source = ResourceBuilder.build(property=self.check['source'], testName=self.testName,
                                           checkName=self.checkName, dynamicProperties=self.dynamicProperties)
            target = ResourceBuilder.build(property=self.check['target'], testName=self.testName,
                                           checkName=self.checkName, dynamicProperties=self.dynamicProperties)
            if source and target:
                if not source.error and not target.error:
                    cardinality = 'one-to-one' if 'cardinality' not in self.check else self.check['cardinality']
                    sourceItems = source.items
                    targetItems = target.items
                    if sourceItems and len(sourceItems) > 0:
                        sourceItem = sourceItems[0]
                        if cardinality == 'one-to-one':
                            fromPropertiesIndex = 0
                            if targetItems:
                                for targetItem in targetItems:
                                    if targetItem.properties and not targetItem.error:
                                        targetProperties = targetItem.properties
                                        toPropertiesIndex = fromPropertiesIndex + len(targetProperties)
                                        if toPropertiesIndex <= len(sourceItem.properties):
                                            sourceProperties = sourceItem.properties[
                                                               fromPropertiesIndex:toPropertiesIndex]
                                            fromPropertiesIndex = fromPropertiesIndex + len(targetProperties)
                                            passed = passed and self.compareItem(
                                                Item(sourceItem.file, sourceProperties, sourceItem.error), targetItem)
                                        else:
                                            passed = False
                                            comparelog.print_error(
                                                msg="Number of source properties from (" + source.file + ") != Number of target properties from (" + target.file + ")",
                                                args={"testName": self.testName,
                                                      "type": Error.VALUE_MISMATCH,
                                                      "checkName": self.checkName})
                                            break
                                    elif targetItem.error:
                                        printToConsole = False
                                        if self.failon and targetItem.error.type in self.failon:
                                            passed = False
                                            printToConsole = True
                                        comparelog.print_error(msg=targetItem.error.message,
                                                               args={"testName": self.testName,
                                                                     "type": targetItem.error.type,
                                                                     "checkName": self.checkName,
                                                                     "source": targetItem.file},
                                                               console=printToConsole)
                                    else:
                                        passed = False
                                        comparelog.print_error(msg="No target properties.",
                                                               args={"testName": self.testName,
                                                                     "type": Error.VALUE_MISMATCH,
                                                                     "checkName": self.checkName,
                                                                     "source": targetItem.file})
                            else:
                                passed = False
                                comparelog.print_error(
                                    msg="No target items retrieved.",
                                    args={"testName": self.testName,
                                          "type": Error.VALUE_MISMATCH,
                                          "checkName": self.checkName,
                                          "source": target.file})
                        elif cardinality == 'one-to-many':
                            for targetItem in targetItems:
                                if targetItem.error:
                                    printToConsole = False
                                    if self.failon and targetItem.error.type in self.failon:
                                        passed = False
                                        printToConsole = True
                                    comparelog.print_error(msg=targetItem.error.message,
                                                           args={"testName": self.testName,
                                                                 "type": targetItem.error.type,
                                                                 "checkName": self.checkName,
                                                                 "source": targetItem.file},
                                                           console=printToConsole)
                                else:
                                    passed = passed and self.compareItem(sourceItem, targetItem, True)
                    else:
                        passed = False
                        comparelog.print_error(
                            msg="No source items retrieved.",
                            args={"testName": self.testName,
                                  "type": Error.VALUE_MISMATCH,
                                  "checkName": self.checkName,
                                  "source": source.file})
                elif source.error:
                    printToConsole = False
                    if self.failon and source.error.type in self.failon:
                        passed = False
                        printToConsole = True
                    comparelog.print_error(msg=source.error.message,
                                           args={'testName': self.testName, 'type': source.error.type,
                                                 "checkName": self.checkName, "source": source.file},
                                           console=printToConsole)
                else:
                    printToConsole = False
                    if self.failon and target.error.type in self.failon:
                        passed = False
                        printToConsole = True
                    comparelog.print_error(msg=target.error.message,
                                           args={'testName': self.testName, 'type': target.error.type,
                                                 "checkName": self.checkName, "source": target.file},
                                           console=printToConsole)
            elif not source:
                passed = False
                comparelog.print_error(
                    msg="No source type available '" + self.check['source'][
                        'type'] + "' . Available types: JSON, PROPERTY, CONF, XML, SHELL",
                    args={"testName": self.testName,
                          "type": comparelog.SYNTAX_ERROR,
                          "checkName": self.checkName})
            elif not target:
                passed = False
                comparelog.print_error(
                    msg="No target type available '" + self.check['target'][
                        'type'] + "' . Available types: JSON, PROPERTY, CONF, XML, SHELL",
                    args={"testName": self.testName,
                          "type": comparelog.SYNTAX_ERROR,
                          "checkName": self.checkName})

        else:
            passed = False
            comparelog.print_error(
                msg="Unsupported check type '" + self.checkType + "'. Only 'COMPARE' and 'SUCCESS' is supported.",
                args={"testName": self.testName, "checkName": self.checkName, "type": comparelog.SYNTAX_ERROR})
        return passed

    def compareItem(self, source, target, onetomany=False):
        passed = True
        cardinality = "one-to-one" if not onetomany else "one-to-many"
        if source.error:
            printToConsole = False
            if self.failon and source.error.type in self.failon:
                passed = False
                printToConsole = True
            comparelog.print_error(
                msg=source.error.message,
                args={"testName": self.testName,
                      "checkName": self.checkName,
                      "cardinality": cardinality,
                      "targetItem": target.file,
                      "type": source.error.type,
                      "source": source.file},
                console=printToConsole)
        elif target.error:
            printToConsole = False
            if self.failon and target.error.type in self.failon:
                passed = False
                printToConsole = True
            comparelog.print_error(
                msg=target.error.message,
                args={"testName": self.testName,
                      "checkName": self.checkName,
                      "cardinality": cardinality,
                      "targetItem": target.file,
                      "type": target.error.type,
                      "source": target.file},
                console=printToConsole)
        elif len(source.properties) != len(target.properties):
            passed = False
            comparelog.print_error(
                msg="Number of source properties from (" + source.file + ") != Number of target properties from (" + target.file + ")",
                args={"testName": self.testName,
                      "checkName": self.checkName,
                      "cardinality": cardinality,
                      "targetItem": target.file,
                      "type": Error.VALUE_MISMATCH})
        elif not any(source.properties):
            passed = False
            comparelog.print_error(
                msg="No source properties",
                args={"testName": self.testName,
                      "checkName": self.checkName,
                      "cardinality": cardinality,
                      "targetItem": target.file,
                      "type": Error.VALUE_MISMATCH,
                      "source": source.file})
        elif not any(target.properties):
            passed = False
            comparelog.print_error(
                msg="No target properties",
                args={"testName": self.testName,
                      "checkName": self.checkName,
                      "cardinality": cardinality,
                      "targetItem": target.file,
                      "type": Error.VALUE_MISMATCH,
                      "source": target.file})
        else:
            for i, source_property in enumerate(source.properties):
                target_property = target.properties[i]
                if source_property.error:
                    printToConsole = False
                    if self.failon and source_property.error.type in self.failon:
                        passed = False
                        printToConsole = True
                    comparelog.print_error(
                        msg=source_property.error.message,
                        args={
                            "testName": self.testName,
                            "checkName": self.checkName,
                            "cardinality": cardinality,
                            "targetItem": target.file,
                            "type": source_property.error.type,
                            "source": source.file},
                        console=printToConsole)
                elif target_property.error:
                    printToConsole = False
                    if self.failon and target_property.error.type in self.failon:
                        passed = False
                        printToConsole = True
                    comparelog.print_error(
                        msg=target_property.error.message,
                        args={"testName": self.testName,
                              "checkName": self.checkName,
                              "cardinality": cardinality,
                              "targetItem": target.file,
                              "type": target_property.error.type,
                              "source": target.file},
                        console=printToConsole)
                else:
                    compare = source_property.compare(target_property)
                    if compare == Property.MATCH:
                        comparelog.print_info(
                            msg="PASSED : " + str(source_property) + " == " + str(target_property),
                            args={"testName": self.testName,
                                  "checkName": self.checkName,
                                  "cardinality": cardinality,
                                  "targetItem": target.file,
                                  "type": self.checkType},
                            console=False)
                    elif compare == Property.NO_MATCH:
                        comparelog.print_info(
                            msg="FAILED : " + str(source_property) + " != " + str(target_property),
                            args={"testName": self.testName,
                                  "checkName": self.checkName,
                                  "cardinality": cardinality,
                                  "targetItem": target.file,
                                  "type": self.checkType})
                        passed = False
                    elif compare == Property.ERROR:
                        comparelog.print_info(
                            msg="Values mismatch. Source: " + str(source_property) + ", Target: " + str(
                                target_property),
                            args={"testName": self.testName,
                                  "checkName": self.checkName,
                                  "cardinality": cardinality,
                                  "targetItem": target.file,
                                  "type": comparelog.VALUE_MISMATCH})
                        passed = False
        return passed
