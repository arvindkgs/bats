import re
import Constants
from lib import comparelog


class Type(object):
    JSON = "JSON"
    PROPERTY = "PROPERTY"
    XML = "XML"
    SHELL = "SHELL"
    STATIC = "STATIC"
    CONFIG = "CONF"


class Resource(object):
    def __init__(self, property, testName, checkName, handlerFn):
        self.type = None if "type" not in property else property['type']
        self.property = None if "property" not in property else property['property']
        self.file = None if "file" not in property else property['file']
        self.format = None if "format" not in property else property['format']
        self.testName = testName
        self.key = None if "key" not in property else property['key']
        self.checkName = checkName
        self.extractProperties = handlerFn

    def getProperties(self, dynamicMap):
        extrapolated_properties = self.extrapolate(dynamicMap, self.property)
        if extrapolated_properties is None:
            return None
        files = self.extrapolate(dynamicMap, self.file)
        properties = self.extractProperties(self, extrapolated_properties, files)
        if self.format is not None and properties is not None and properties != [None] * len(properties):
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
                for i, property in enumerate(properties):
                    if property is not None and property.value is not None:
                        values = []
                        for val in property.value:
                            m = re.match(regex_format, val)
                            if m:
                                values.append(m.group(1))
                            else:
                                comparelog.print_error(
                                    msg="No pattern '" + self.format + "' in " + property.name,
                                    args={'fnName': self.testName, 'type': comparelog.MISSING_PROPERTY,
                                          'source': self.file,
                                          'checkName': self.checkName})
                                # values.append(None)
                        property.value = values
        return properties

    def toString(self):
        return 'Type: ' + str(self.type) + ', Resource: ' + str(self.file) + ', Property: ' + str(
            self.property) + ', Format: ' + str(self.format)

    def getKey(self):
        return self.key

    def extrapolate(self, dynamicMap, propertyStr):
        properties = [propertyStr]
        dynamic_pattern = Constants.RegularExpression.findIndexExpression
        if dynamicMap is not None and len(dynamicMap) > 0:
            for m in re.finditer(dynamic_pattern, propertyStr):
                if m.group(1) in dynamicMap:
                    values = dynamicMap[m.group(1)]
                    newproperties = []
                    if values is not None and any(values):
                        for property in properties:
                            if isinstance(values, list):
                                for value in values:
                                    newproperties.append(property.replace("${" + str(m.group(1)) + "}", value))
                            else:
                                newproperties.append(property.replace("${" + str(m.group(1)) + "}", values))
                        properties = newproperties
                    else:
                        comparelog.print_error(msg="No dynamic value present for key: '" + m.group(1) + "'",
                                               args={'fnName': self.testName,
                                                     'type': comparelog.MISSING_DYNAMIC_VALUE,
                                                     'source': self.file, 'checkName': self.checkName})
                        return None
                else:
                    comparelog.print_error(msg="No dynamic value present for key: '" + m.group(1) + "'",
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
