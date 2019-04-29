import json
import re
import execute_shell_script
from lib import *


class Type(object):
    JSON = "JSON"
    PROPERTY = "PROPERTY"
    XML = "XML"
    SHELL = "SHELL"
    STATIC = "STATIC"


class Resource(object):
    def __init__(self, property, testName, checkName):
        self.type = None if "type" not in property else property['type']
        self.property = None if "property" not in property else property['property']
        self.file = None if "file" not in property else property['file']
        self.format = None if "format" not in property else property['format']
        self.testName = testName
        self.key = None if "key" not in property else property['key']
        self.checkName = checkName


    def getProperties(self, dynamicMap):
        global logger
        properties = self.extrapolate(dynamicMap)
        if properties is None:
            return None
        if self.type == Type.JSON:
            try:
                with open(self.file, 'r') as json_file:
                    data = json.load(json_file)
                    # key : "topology.wlsClusters.[clusterName = 'AdminServer'].Xms"
                    flatListValues = []
                    for property in properties:
                        nodes = property.split('.')
                        jsondata = data
                        for i, node in enumerate(nodes):
                            if not isinstance(jsondata, list):
                                jsondata = [jsondata]
                            newdata = []
                            for j, obj in enumerate(jsondata):
                                index = re.match("\[(.*)\]", node)
                                error = False
                                if obj != None:
                                    if index:
                                        index = index.group(1)
                                        if index.isdigit():
                                            try:
                                                # jsondata[j] = obj[index]
                                                newdata.append(obj[index])
                                            except:
                                                comparelog.print_error(msg="No object at index: " + index + " in property " + property, args={
                                                    'fnName': self.testName,
                                                    'type': comparelog.MISSING_PROPERTY,
                                                    'source': self.file, 'checkName': self.checkName
                                                })
                                                error = True
                                                pass
                                        elif "=" in index:
                                            key, value = index.split("=")
                                            key = key.strip()
                                            value = value.strip()
                                            if value is not None and value != '':
                                                value = value if value[0] != '\'' and value[
                                                    len(value) - 1] != '\'' else value[
                                                                                 1:len(
                                                                                     value) - 1]
                                                if key:
                                                    found = False
                                                    for item in obj:
                                                        if key in item and item[key] == value:
                                                            # jsondata[j] = item
                                                            newdata.append(item)
                                                            found = True
                                                    if not found:
                                                        comparelog.print_error(
                                                            msg="No object with attribute: " + key + " = " + value + " found in : " + str(
                                                                self.file),
                                                            args={'fnName': self.testName,
                                                                  'type': comparelog.MISSING_PROPERTY,
                                                                  'source': self.file, 'checkName': self.checkName})
                                                        error = True
                                            else:
                                                comparelog.print_error(msg="Value expected for '" + node + "' after '='",
                                                                       args={'fnName': self.testName,
                                                                             'type': comparelog.SYNTAX_ERROR,
                                                                             'source': "Metadata.json",
                                                                             'checkName': self.checkName})
                                                error = True
                                        elif index == '':
                                            if not isinstance(obj, list):
                                                comparelog.print_error(
                                                    msg="Property '" + property + "' specified is not an array.",
                                                    args={'fnName': self.testName, 'type': comparelog.MISSING_PROPERTY,
                                                          'source': self.file, 'checkName': self.checkName})
                                                error = True
                                            else:
                                                newdata = obj

                                    elif node in obj:
                                        # jsondata[j] = obj[node]
                                        newdata.append(obj[node])
                                    else:
                                        comparelog.print_error(msg="No attribute: " + str(node) + " in " + property,
                                                               args={'fnName': self.testName,
                                                                     'type': comparelog.MISSING_PROPERTY,
                                                                     'source': self.file, 'checkName': self.checkName})
                                        error = True
                                    if error:
                                        newdata.append(None)
                                else:
                                    newdata.append(None)
                            jsondata = newdata
                        # tupleValue = (str(property), jsondata)
                        flatListValues.append(Property(str(property), jsondata))
                    data = flatListValues
                # data now is array of values to be given to formatter
            except Exception:
                comparelog.print_error(msg="File '" + self.file + "' not found", args={'fnName': self.testName,
                                                              'type': comparelog.FILE_NOT_FOUND,
                                                              'source': self.file, 'checkName': self.checkName})
        elif self.type == Type.PROPERTY:
            data = []
            for property in properties:
                propFrmFile = execute_shell_script.grepProp(property, self.file)
                if propFrmFile is None:
                    comparelog.print_error(msg="Not able to get property: " + property + ", from file:" + self.file,
                                           args={'fnName': self.testName, 'type': comparelog.MISSING_PROPERTY,
                                                 'source': self.file, 'checkName': self.checkName})
                    data.append(Property(property, None))
                else:
                    data.append(Property(property, [propFrmFile]))
        else:
            comparelog.print_error(
                msg="No type available '" + self.type + "' . Available types: JSON, PROPERTY, XML, SHELL, STATIC",
                args={'fnName': self.testName, 'type': comparelog.SYNTAX_ERROR, 'source': "Metadata.json",
                      'checkName': self.checkName})
            return [None]
        if self.format is not None and data is not None and data != [None] * len(data):
            # extract data using self.format
            # meta-chars: {}, ?
            # {} -> return value. {2:} -> return 2 characters
            # ? -> single character
            # Future enhancement : {:4} -> n-4 characters
            # Example:
            # Format='-Xms{}?'
            # Data='-Xms512m -Xmx8192m -Xss102400k'
            # Extract=512
            regex_format = self.getRegexPatternFormat()
            if regex_format is not None:
                for i, property in enumerate(data):
                    if property is not None and property.value is not None:
                        values = []
                        for val in property.value:
                            m = re.match(regex_format, val)
                            if m:
                                values.append(m.group(1))
                            else:
                                comparelog.print_error(
                                    msg="Not able to extract: '" + self.format + "' from " + property.name + ", from file:" + self.file,
                                    args={'fnName': self.testName, 'type': comparelog.MISSING_PROPERTY,
                                          'source': self.file,
                                          'checkName': self.checkName})
                                values.append(None)
                        property.value = values
        return data

    def toString(self):
        return 'Type: ' + str(self.type) + ', Resource: ' + str(self.file) + ', Property: ' + str(
            self.property) + ', Format: ' + str(self.format)

    def getKey(self):
        return self.key

    def extrapolate(self, dynamicMap):
        properties = [self.property]
        dynamic_pattern = "\\${([^}]*)(?=})"
        if dynamicMap:
            for m in re.finditer(dynamic_pattern, self.property):
                if m.group(1) in dynamicMap:
                    values = dynamicMap[m.group(1)]
                    newproperties = []
                    for value in values:
                        for property in properties:
                            newproperties.append(property.replace("${" + str(m.group(1)) + "}", value))
                    properties = newproperties
                else:
                    comparelog.print_error(msg="No dynamic value present for key: '" + m.group(1),
                                           args={'fnName': self.testName,
                                                 'type': comparelog.MISSING_DYNAMIC_VALUE,
                                                 'source': self.file, 'checkName': self.checkName})
                    return None
        return properties

    def getRegexPatternFormat(self):
        pattern = None
        iOpenB = -1
        iCloseB = -1
        for i in range(0, len(self.format)):
            if (i > 0 and self.format[i - 1] != '\\' and self.format[i] == '{') or self.format[i] == '{':
                iOpenB = i
                for j in range(i + 1, len(self.format)):
                    if (self.format[j - 1] == '\\' or self.format[j] == '}'):
                        break;
                iCloseB = j
                # print "I: "+str(i)
                if (j != len(self.format) and self.format[j] == '}'):
                    if (j > (i + 1) and isinstance(self.format[i, j], int)):
                        limit = int(self.format[i, j])
        # i = index of '{' , j = index of '}' , limit = numeral (if exists)
        if (iOpenB != -1 and iOpenB != len(self.format) and self.format[
            iOpenB] == '{' and iCloseB != -1 and iCloseB != len(self.format) and self.format[iCloseB] == '}'):
            prefix = ''
            suffix = ''
            if (iOpenB > 0):
                prefix = self.format[:iOpenB]
            # print "Prefix: "+prefix
            if (iCloseB < (len(self.format) - 1)):
                suffix = self.format[(iCloseB + 1):]
            for patternStr in [prefix, suffix]:
                replacedStr = patternStr
                # print "checking str: "+replacedStr
                for i in range(0, len(patternStr)):
                    if (i > 0 and patternStr[i - 1] != '\\' and patternStr[i] == '?') or patternStr[i] == '?':
                        # print "Found ?, pos: "+str(i)
                        replacedStr = patternStr[:i] + '[^ ]' + patternStr[i + 1:]
                if (patternStr == prefix):
                    prefix = replacedStr
                else:
                    suffix = replacedStr
            pattern = '.*' + prefix + '([^ ]+)' + '(?=' + suffix + '\\b)' + '.*'
        return pattern
