from model import ResourceBuilder
from model.Property import Property
import comparelog
from Dynamic import PropertyMap
from model.Item import Item
from Error import Error


class Check:

    def __init__(self, check, testName, dynamicProperties, failon):
        self.check = check
        self.checkName = check['name']
        self.checkType = check['type'] if 'type' in check else "COMPARE"
        self.testName = testName
        self.failon = failon
        self.dynamicProperties = PropertyMap(dynamicProperties)
        self.cardinality = 'one-to-one' if 'cardinality' not in self.check else self.check['cardinality']


    def evaluateCheck(self):
        passed = self.dynamicProperties.addDynamicPropertiesFromCheck(self.check, self.testName, self.failon)
        if Check.Type.getType(self) == Check.Type.COMPARE_PROPERTY:
            source_resource = ResourceBuilder.build(property=self.check['source'], testName=self.testName,
                                           checkName=self.checkName, dynamicProperties=self.dynamicProperties)
            target_resource = ResourceBuilder.build(property=self.check['target'], testName=self.testName,
                                           checkName=self.checkName, dynamicProperties=self.dynamicProperties)

            if source_resource.has_error(self.failon) or target_resource.has_error(self.failon):
                passed = False if source_resource.failed(self.failon) or target_resource.failed(self.failon) else passed
            else:
                source_item = source_resource.items[0]
                if source_item.has_error(self):
                    passed = False if source_item.failed(self.failon) else passed
                elif self.cardinality == 'one-to-one':
                        fromPropertiesIndex = 0
                        for target_item in target_resource.items:
                            if target_item.has_error(self):
                                passed = False if target_item.failed(self.failon) else passed
                            else:
                                toPropertiesIndex = fromPropertiesIndex + len(target_item.properties)
                                if toPropertiesIndex <= len(source_item.properties):
                                    sourceProperties = source_item.properties[
                                                       fromPropertiesIndex:toPropertiesIndex]
                                    fromPropertiesIndex += len(target_item.properties)
                                    passed = self.compareItem(
                                        Item(source_item.file, sourceProperties, source_item.error), target_item) and passed
                                else:
                                    passed = False
                                    comparelog.print_error(
                                        msg="Number of source properties from (" + source_resource.file + ") != Number of target properties from (" + target_resource.file + ")",
                                        args={"testName": self.testName,
                                              "type": Error.VALUE_MISMATCH,
                                              "checkName": self.checkName})
                                    break
                elif self.cardinality == 'one-to-many':
                    for target_item in target_resource.items:
                        if target_item.has_error(self):
                            passed = False if target_item.failed(self.failon) else passed
                        else:
                            passed = self.compareItem(source_item, target_item, True) and passed

        elif Check.Type.getType(self) == Check.Type.COMPARE_FILES:
            source_resource = ResourceBuilder.build(property=self.check['source'], testName=self.testName,
                                           checkName=self.checkName, dynamicProperties=self.dynamicProperties)
            target_resource = self.check['target']
            if source_resource.has_error(self.failon):
                passed = False if source_resource.failed(self.failon) else passed
            else:
                targetProperties = []
                if source_resource.items[0].properties:
                    for property in source_resource.items[0].properties:
                        targetProperties.append(property.name)
                target_resource['property'] = targetProperties
                target_resource = ResourceBuilder.build(property=self.check['target'], testName=self.testName,
                                               checkName=self.checkName, dynamicProperties=self.dynamicProperties)
                passed = self.compareItem(source_resource.items[0], target_resource.items[0]) and passed

        elif Check.Type.getType(self) == Check.Type.SUCCESS:
            if 'target' not in self.check:
                passed = False
                comparelog.print_error(msg="'target' not defined in check: "+self.checkName, args={'testName': self.testName, 'type': Error.SYNTAX_ERROR,'checkName': self.checkName})
            else:
                target_resource = ResourceBuilder.build(property=self.check['target'], testName=self.testName,
                                               checkName=self.checkName, dynamicProperties=self.dynamicProperties)
                if target_resource.type == ResourceBuilder.Type.SHELL:
                    if target_resource.error and target_resource.error.type == Error.SHELL_COMMAND_ERROR:
                        passed = False
                        comparelog.print_info(
                            msg=str(target_resource.property),
                            args={"testName": self.testName,
                                  "checkName": self.checkName,
                                  "type": "FAILED"})
                    elif target_resource.error and target_resource.error.type == Error.MISSING_PROPERTY:
                        comparelog.print_info(
                            msg=str(target_resource.property),
                            args={"testName": self.testName,
                                  "checkName": self.checkName,
                                  "type": "PASSED"},
                        console=False)
                    else:
                        for item in target_resource.items:
                            passed = self.isSuccessShell(item) and passed
                else:
                    if not target_resource.has_error(self.failon):
                        for item in target_resource.items:
                            passed = self.isSuccess(item) and passed
                    else:
                        passed = False if target_resource.failed(self.failon) else passed
                            
        else:
            comparelog.print_error(
                msg="Unsupported check type '" + self.checkType + "'. Only 'COMPARE' and 'SUCCESS' is supported.",
                args={"testName": self.testName, "checkName": self.checkName, "type": Error.SYNTAX_ERROR})
        return passed

    def compareItem(self, source_item, target_item, onetomany=False):
        passed = True
        if source_item.has_error(self, target_item.file) and target_item.has_error(self):
            passed = False if source_item.failed(self.failon) or target_item.failed(self.failon) else passed
        else:
            cardinality = "one-to-one" if not onetomany else "one-to-many"
            if len(source_item.properties) != len(target_item.properties):
                passed = False
                comparelog.print_error(
                    msg="Number of source properties from (" + source_item.file + ") != Number of target properties from (" + target_item.file + ")",
                    args={"testName": self.testName,
                          "checkName": self.checkName,
                          "cardinality": cardinality,
                          "targetItem": target_item.file,
                          "type": Error.VALUE_MISMATCH})
            else:
                for i, source_property in enumerate(source_item.properties):
                    target_property = target_item.properties[i]
                    if source_property.has_error(self, source_item.file, target_item.file) or target_property.has_error(self, target_item.file):
                        passed = False if source_property.failed(self.failon) or target_property.failed(self.failon) else passed
                    else:
                        compare = source_property.compare(target_property)
                        if compare == Property.MATCH:
                            comparelog.print_info(
                                msg=str(source_property) + " == " + str(target_property),
                                args={"testName": self.testName,
                                      "checkName": self.checkName,
                                      "cardinality": cardinality,
                                      "targetItem": target_item.file,
                                      "type": "PASSED"},
                                console=False)
                        elif compare == Property.NO_MATCH:
                            comparelog.print_info(
                                msg=str(source_property) + " != " + str(target_property),
                                args={"testName": self.testName,
                                      "checkName": self.checkName,
                                      "cardinality": cardinality,
                                      "targetItem": target_item.file,
                                      "type": "FAILED"})
                            passed = False
                        elif compare == Property.ERROR:
                            comparelog.print_info(
                                msg="Values mismatch. Source: " + str(source_property) + ", Target: " + str(
                                    target_property),
                                args={"testName": self.testName,
                                      "checkName": self.checkName,
                                      "cardinality": cardinality,
                                      "targetItem": target_item.file,
                                      "type": Error.VALUE_MISMATCH})
                            passed = False
        return passed

    def isSuccessShell(self, item):
        passed = True
        if item.error and item.error.type == Error.SHELL_COMMAND_ERROR:
            passed = False
            comparelog.print_info(
                msg=str(item),
                args={"testName": self.testName,
                      "checkName": self.checkName,
                      "type": "FAILED"})
        elif item.error and item.error.type == Error.MISSING_PROPERTY:
            comparelog.print_info(
                msg=str(item),
                args={"testName": self.testName,
                      "checkName": self.checkName,
                      "type": "PASSED"},
                console=False)
        else:
            for i, property in enumerate(item.properties):
                if property.error and property.error.type == Error.MISSING_PROPERTY:
                    comparelog.print_info(
                        msg=str(property),
                        args={"testName": self.testName,
                              "checkName": self.checkName,
                              "type": "PASSED"},
                        console=False)
                else:
                    passed = False
                    comparelog.print_info(
                        msg=str(property),
                        args={"testName": self.testName,
                              "checkName": self.checkName,
                              "type": "FAILED"})
        return passed
    
    def isSuccess(self, item):
        passed = True
        if item.has_error(self):
            passed = False if item.failed(self.failon) else passed
        else:
            for i, property in enumerate(item.properties):
                if property.has_error(self, item.file):
                    passed = False if property.failed(self.failon) else passed
                else:
                    success = property.isSuccess()
                    if success == Property.MATCH:
                        comparelog.print_info(
                            msg=str(property),
                            args={"testName": self.testName,
                                  "checkName": self.checkName,
                                  "targetItem": item.file,
                                  "type": "PASSED"},
                            console=False)
                    elif success == Property.NO_MATCH:
                        comparelog.print_info(
                            msg=str(property),
                            args={"testName": self.testName,
                                  "checkName": self.checkName,
                                  "targetItem": item.file,
                                  "type": "FAILED"})
                        passed = False
                    elif success == Property.ERROR:
                        comparelog.print_info(
                            msg="No values for item: " + str(property),
                            args={"testName": self.testName,
                                  "checkName": self.checkName,
                                  "targetItem": item.file,
                                  "type": Error.VALUE_MISMATCH})
                        passed = False
        return passed

    class Type:
        COMPARE_PROPERTY = "COMPARE_PROPERTY"
        COMPARE_FILES = "COMPARE_FILES"
        SUCCESS = "SUCCESS"

        @classmethod
        def getType(self, checkObj):
            retType = None
            if checkObj.checkType == 'COMPARE' and 'source' in checkObj.check:
                if (
                    'property' in checkObj.check['source']
                    and 'target' in checkObj.check
                    and 'property' in checkObj.check['target']
                ):
                    retType = Check.Type.COMPARE_PROPERTY
                elif (
                    'property' not in checkObj.check['source']
                    and 'target' in checkObj.check
                    and 'property' not in checkObj.check['target']
                ):
                    retType = Check.Type.COMPARE_FILES
            elif checkObj.checkType == 'SUCCESS':
                retType = Check.Type.SUCCESS
            return retType
