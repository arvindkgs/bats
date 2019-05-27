import re
from os import path
import Constants
from Property import Property
from lib import ShellHandler
from lib.Error import Error


class Type(object):
    JSON = "JSON"
    PROPERTY = "PROPERTY"
    XML = "XML"
    SHELL = "SHELL"
    STATIC = "STATIC"
    CONFIG = "CONF"


class Item(object):
    def __init__(self, file, properties, error=None):
        self.file = file
        self.properties = properties
        self.error = error


class Resource(object):
    def __init__(self, property, testName, checkName, handler, dynamicProperties=None):
        self.type = None if "type" not in property else property['type']
        self.property = None if "property" not in property else property['property']
        self.hostname = None if "hostname" not in property else property['hostname']
        self.username = None if "username" not in property else property['username']
        self.password = None if "password" not in property else property['password']
        self.file = None if "file" not in property else property['file']
        self.format = None if "format" not in property else property['format']
        self.testName = testName
        self.key = None if "key" not in property else property['key']
        self.checkName = checkName
        self.handler = handler
        self.dynamicMap = dynamicProperties
        self.items = self.fetch()
        self.error = None

    def fetch(self):
        extrapolatedProp = self.extrapolate(self.dynamicMap, self.property)
        extrapolated_properties = extrapolatedProp.value
        if extrapolatedProp.error:
            self.error = extrapolatedProp.error
            return None
        fileProp = self.extrapolate(self.dynamicMap, self.file)
        if fileProp.error:
            self.error = fileProp.error
            return None
        files = fileProp.value
        hostProp = self.extrapolate(self.dynamicMap, self.hostname)
        if hostProp.error:
            self.error = hostProp.error
            return None
        hostname = hostProp.value[0]
        userProp = self.extrapolate(self.dynamicMap, self.username)
        if userProp.error:
            self.error = userProp.error
            return None
        username = userProp.value[0]
        passwordProp = self.extrapolate(self.dynamicMap, self.password)
        if passwordProp.error:
            self.error = passwordProp.error
            return None
        password = passwordProp.value[0]
        if hostname and username and password and files and any(files):
            for i, file in enumerate(files):
                if file:
                    files[i] = ShellHandler.getRemoteFile(hostname, username, password, file)
        resourceItems = None
        if files and any(files):
            for file in files:
                if not resourceItems:
                    resourceItems = []
                if file and path.isfile(file):
                    resourceItems.append(self.handler.getResourceItem(extrapolated_properties, file))
                else:
                    resourceItems.append(Item(file, None, Error(Error.FILE_NOT_FOUND, "File not found")))
        elif self.type == Type.SHELL:
            if not resourceItems:
                resourceItems = []
            resourceItems.append(self.handler.getResourceItem(extrapolated_properties, self.hostname,
                                                              self.username, self.password))
        else:
            self.error = Error(type=Error.EXTRAPOLATION_ERROR, message="Error in extrapolation of 'file'")
        if self.format is not None and resourceItems and any(resourceItems):
            # extract data using self.format
            # meta-chars: {}, ?
            # {} -> return value. {2:} -> return 2 characters
            # ? -> single character
            # Future enhancement : {:4} -> n-4 characters
            # Example:
            # Format='-Xms{}?'
            # Data='-Xms512m -Xmx8192m -Xss102400k'
            # Extract=512
            for resourceItem in resourceItems:
                properties = resourceItem.properties
                if not resourceItem.error and properties and any(properties) and properties != [None] * len(properties):
                    regex_format = self.getRegexPatternFormat()
                    if regex_format is not None:
                        for i, property in enumerate(properties):
                            if property is not None and property.value is not None and property.error is None:
                                values = None
                                for val in property.value:
                                    m = re.match(regex_format, val)
                                    if m:
                                        if values is None:
                                            values = []
                                        values.append(m.group(1))
                                    else:
                                        values = None
                                        break
                                if values is None and any(property.value):
                                    property.error = Error(Error.MISSING_FORMAT,
                                                           "No format '" + self.format + "' in " + property.name)
                                property.value = values
        return resourceItems

    def toString(self):
        return 'Type: ' + str(self.type) + ', Resource: ' + str(self.file) + ', Property: ' + str(
            self.property) + ', Format: ' + str(self.format)

    def getKey(self):
        return self.key

    def extrapolate(self, dynamicMap, propertyStr):
        properties = [propertyStr]
        error = None
        if any(properties):
            if dynamicMap is not None and len(dynamicMap) > 0:
                for m in re.finditer(Constants.RegularExpression.findIndexExpression, propertyStr):
                    dynamickey = m.group(1)
                    if dynamickey is not None and '.' in dynamickey:
                        dynamickey = dynamickey.split('.')[0]
                    if dynamickey in dynamicMap:
                        valuesProp = self.fetchValueFromDynamicMap(m.group(1), dynamicMap)
                        if not valuesProp.error:
                            values = valuesProp.value
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
                                error = Error(type=Error.MISSING_DYNAMIC_VALUE,
                                              message="No dynamic value present for key: '" + m.group(
                                                  1) + "'")
                                break
                        else:
                            error = valuesProp.error
                            break
                    else:
                        error = Error(type=Error.MISSING_DYNAMIC_VALUE,
                                      message="No dynamic value present for key: '" + m.group(
                                          1) + "'")
                        break
        properties = None if error is not None else properties
        return Property(propertyStr, properties, error)

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

    def fetchValueFromDynamicMap(self, key, dynamicMap):
        retValue = None
        error = None
        if key is not None and dynamicMap is not None:
            dynamickey = key
            if '.' in key:
                dynamickey = key.split('.')[0]
            if dynamickey in dynamicMap:
                values = dynamicMap[dynamickey]
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
