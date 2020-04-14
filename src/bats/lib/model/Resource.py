from os import path

from ..Constants import *
from ..handler.ShellHandler import *


class Resource(object):
    def __init__(self, property, testName, checkName, handler, dynamicProperties=None):
        self.type = None if "type" not in property else property['type']
        self.property = None if "property" not in property else property['property']
        self.hostname = None if "hostname" not in property else property['hostname']
        self.username = None if "username" not in property else property['username']
        self.password = None if "password" not in property else property['password']
        self.cardinality = None if "cardinality" not in property else property['cardinality']
        self.file = None if "file" not in property else property['file']
        self.format = None if "format" not in property else property['format']
        self.key = None if "key" not in property else property['key']
        self.join = None if "join" not in property else property['join']
        self.testName = testName
        self.checkName = checkName
        self.handler = handler
        self.dynamicProperties = dynamicProperties
        self.error = None
        self.items = self.fetch()

    def fetch(self):
        if isinstance(self.property, list):
            extrapolated_properties = self.property
        else:
            extrapolatedProp = self.extrapolate(self.property)
            extrapolated_properties = extrapolatedProp.value
            if extrapolatedProp.error:
                self.error = extrapolatedProp.error
                return None
        fileProp = self.extrapolate(self.file)
        if fileProp.error:
            self.error = fileProp.error
            return None
        files = fileProp.value
        hostProp = self.extrapolate(self.hostname)
        if hostProp.error:
            self.error = hostProp.error
            return None
        hostnames = hostProp.value
        userProp = self.extrapolate(self.username)
        if userProp.error:
            self.error = userProp.error
            return None
        username = userProp.value[0]
        passwordProp = self.extrapolate(self.password)
        if passwordProp.error:
            self.error = passwordProp.error
            return None
        password = passwordProp.value[0]
        resourceItems = None
        if files and any(files):
            if hostnames and any(hostnames):
                origFiles = files[:]
                files = []
                for i, hostname in enumerate(hostnames):
                    if hostname:
                        if self.cardinality == 'one-to-one':
                            try:
                                files.append((getRemoteFile(hostname, username, password, origFiles[i]),
                                              str(origFiles[i]), str(hostname), None))
                            except IOError, err:
                                files.append((origFiles[i], origFiles[i], str(hostname), str(err)))
                        else:
                            # default to one-to-many
                            for j, file in enumerate(origFiles):
                                if file:
                                    try:
                                        files.append((getRemoteFile(hostname, username, password, file), str(file),
                                                      str(hostname), None))
                                    except IOError, err:
                                        files.append((file, file, str(hostname), str(err)))
            else:
                for i, file in enumerate(files):
                    files[i] = (file, None, None, None)
            for j, file in enumerate(files):
                if not resourceItems:
                    resourceItems = []
                if not file[3]:
                    if file[0] and path.isfile(file[0]):
                        resourceItems.append(self.handler.getResourceItem(extrapolated_properties, file[0]))
                    else:
                        resourceItems.append(Item(file[2] + ":" + file[1] if file[1] else file[0], None,
                                                  Error(Error.FILE_NOT_FOUND, "File not found")))
                else:
                    resourceItems.append(Item(file[2] + ":" + file[1], None, Error(Error.FILE_NOT_FOUND, file[3])))
        elif self.type == Type.SHELL:
            if not resourceItems:
                resourceItems = []
            if hostnames:
                for hostname in hostnames:
                    resourceItems.append(self.handler.getResourceItem(extrapolated_properties, hostname,
                                                                  username, password))
            else:
                resourceItems.append(self.handler.getResourceItem(extrapolated_properties))
        elif self.type == Type.STATIC:
            if not resourceItems:
                resourceItems = []
            resourceItems.append(self.handler.getResourceItem(extrapolated_properties, self.key))
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
        if self.join is not None and resourceItems and any(resourceItems):
            joinedResourceItem = ""
            error = None
            for resourceItem in resourceItems:
                if resourceItem.error is not None:
                    error = Error(type=resourceItem.error.type, message=resourceItem.error.message)
                    joinedResourceItem = ""
                    break
                for property in resourceItem.properties:
                    joinedResourceItem += self.join.join(property.value) + self.join
            if len(joinedResourceItem) > 0:
                joinedResourceItem = joinedResourceItem[:len(joinedResourceItem)-len(self.join)]
            resourceItems = [Item(self.key, [Property(self.key, joinedResourceItem, error)], error)]
        return resourceItems

    def __str__(self):
        return 'Type: ' + str(self.type) + ', Resource: ' + str(self.file) + ', Property: ' + str(
            self.property) + ', Format: ' + str(self.format)

    def getKey(self):
        return self.key

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
                    prefix = '.*' + replacedStr if prefix else ''
                else:
                    suffix = replacedStr
            pattern = prefix + '([^ ]+)' + '(?=' + suffix + '\\b)' + '.*'
        return pattern

    def extrapolate(self, propertyStr):
        properties = [propertyStr]
        error = None
        if (
                any(properties)
                and self.dynamicProperties is not None
                and len(self.dynamicProperties) > 0
        ):
            for m in re.finditer(RegularExpression.findIndexExpression, propertyStr):
                dynamickey = m.group(1)
                if dynamickey is not None and '.' in dynamickey:
                    dynamickey = dynamickey.split('.')[0]
                if dynamickey in self.dynamicProperties:
                    valuesProp = self.dynamicProperties[m.group(1)]
                    if not valuesProp.error:
                        values = valuesProp.value
                        if values is not None and any(values):
                            newproperties = []
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


class Type(object):
    JSON = "JSON"
    PROPERTIES = "PROPERTIES"
    XML = "XML"
    SHELL = "SHELL"
    STATIC = "STATIC"
    CONFIG = "CONF"
