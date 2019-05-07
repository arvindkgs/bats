import json
import re
from lib import Property
from lib import comparelog, execute_shell_script
import xml.etree.ElementTree as ET
import Constants
from StringIO import StringIO


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
        extrapolated_properties = self.extrapolate(dynamicMap, self.property)
        if extrapolated_properties is None:
            return None
        files = self.extrapolate(dynamicMap, self.file)
        if self.type == Type.JSON:
            try:
                properties = []
                for fileobj in files:
                    with open(fileobj, 'r') as json_file:
                        data = json.load(json_file)
                        for property in extrapolated_properties:

                            nodes = self.splitNodes(property)
                            jsondata = data
                            for i, node in enumerate(nodes):
                                if not isinstance(jsondata, list):
                                    jsondata = [jsondata]
                                newdata = []
                                for obj in jsondata:
                                    index = re.match("\[(.*)\]", node)
                                    error = False
                                    if obj != None:
                                        if index:
                                            index = index.group(1)
                                            if index.isdigit():
                                                try:
                                                    newdata.append(obj[index])
                                                except:
                                                    comparelog.print_error(
                                                        msg="No object at index: " + index + " in property " + property,
                                                        args={
                                                            'fnName': self.testName,
                                                            'type': comparelog.MISSING_PROPERTY,
                                                            'source': self.file, 'checkName': self.checkName
                                                        })
                                                    error = True
                                                    pass
                                            elif index == '':
                                                if not isinstance(obj, list):
                                                    comparelog.print_error(
                                                        msg="Property '" + property + "' specified is not an array.",
                                                        args={'fnName': self.testName,
                                                              'type': comparelog.MISSING_PROPERTY,
                                                              'source': self.file, 'checkName': self.checkName})
                                                    error = True
                                                else:
                                                    newdata = obj
                                            else:
                                                if "&&" in index:
                                                    expressions = index.split("&&")
                                                else:
                                                    expressions = [index]
                                                filters = []
                                                for expression in expressions:
                                                    if "==" in expression or "!=" in expression:
                                                        if "==" in expression:
                                                            key, value = expression.split("==")
                                                        else:
                                                            key, value = expression.split("!=")
                                                        key = key.strip()
                                                        value = value.strip()
                                                        if value is not None and value != '' and key:
                                                            value = value if value[0] != '\'' and value[
                                                                len(value) - 1] != '\'' else value[
                                                                                             1:len(
                                                                                                 value) - 1]
                                                            if "==" in expression:
                                                                filters.append((key, value, "EQUAL"))
                                                            else:
                                                                filters.append((key, value, "UNEQUAL"))
                                                        else:
                                                            comparelog.print_error(
                                                                msg="Syntax of '" + node + "' expected as 'key == value'",
                                                                args={'fnName': self.testName,
                                                                      'type': comparelog.SYNTAX_ERROR,
                                                                      'source': "Metadata.json",
                                                                      'checkName': self.checkName})
                                                            error = True
                                                if not error:
                                                    found = False
                                                    for item in obj:
                                                        matches = True
                                                        for filterObj in filters:
                                                            key, value, type = filterObj
                                                            if key not in item:
                                                                matches = False
                                                            else:
                                                                pattern = re.compile('^' + str(value) + '$')
                                                                rematch = pattern.match(str(item[key]))
                                                                if not rematch and type == "EQUAL":
                                                                    matches = False
                                                                    break
                                                                elif rematch and type == "UNEQUAL":
                                                                    matches = False
                                                                    break
                                                        if matches and len(filters) > 0:
                                                            found = True
                                                            newdata.append(item)
                                                    if not found:
                                                        comparelog.print_error(
                                                            msg="No object with attribute: " + index + " found in : " + str(
                                                                self.file),
                                                            args={'fnName': self.testName,
                                                                  'type': comparelog.MISSING_PROPERTY,
                                                                  'source': self.file, 'checkName': self.checkName})
                                                        error = True
                                        elif node in obj:
                                            newdata.append(obj[node])
                                        else:
                                            comparelog.print_error(msg="No attribute: " + str(node) + " in " + property,
                                                                   args={'fnName': self.testName,
                                                                         'type': comparelog.MISSING_PROPERTY,
                                                                         'source': self.file,
                                                                         'checkName': self.checkName})
                                            error = True
                                        if error:
                                            newdata.append(None)
                                    else:
                                        newdata.append(None)
                                jsondata = newdata
                            properties.append(Property(str(property), jsondata))
                    # data now is array of values to be given to formatter
            except Exception as e:
                print str(e)
                comparelog.print_error(msg="File '" + self.file + "' not found", args={'fnName': self.testName,
                                                                                       'type': comparelog.FILE_NOT_FOUND,
                                                                                       'source': self.file,
                                                                                       'checkName': self.checkName})
                return [None]
        elif self.type == Type.PROPERTY:
            properties = []
            for fileobj in files:
                for property in extrapolated_properties:
                    propFrmFile = execute_shell_script.grepProp(property, fileobj)
                    if propFrmFile is None:
                        comparelog.print_error(msg="Not able to get property: " + property + ", from file:" + self.file,
                                               args={'fnName': self.testName, 'type': comparelog.MISSING_PROPERTY,
                                                     'source': self.file, 'checkName': self.checkName})
                        properties.append(Property(property, None))
                    else:
                        properties.append(Property(property, [propFrmFile]))
        elif self.type == Type.XML:
            properties = []
            if files is not None:
                for fileobj in files:
                    it = None
                    try:
                        it = ET.iterparse(StringIO(open(fileobj).read()))
                    except Exception as e:
                        comparelog.print_error(msg="File: " + self.file + ", does not exist.",
                                               args={'fnName': self.testName, 'type': comparelog.FILE_NOT_FOUND,
                                                     'source': fileobj, 'checkName': self.checkName})
                    if it is not None:
                        for _, el in it:
                            if '}' in el.tag:
                                el.tag = el.tag.split('}', 1)[1]  # strip all namespaces
                        root = it.root
                        topelement = root.find(".")
                        if topelement is not None and len(topelement) > 0:
                            for property in extrapolated_properties:
                                try:
                                    split = property.split(".")
                                    if topelement.tag == split[0]:
                                        xPath = ''
                                        for ele in split[1:]:
                                            ele = ele.replace(' == ', '=')
                                            ele = ele.replace('==', '=')
                                            xPath += ele + '/'
                                        if xPath != '':
                                            xPath = xPath[:len(xPath) - 1]
                                            nodes = root.findall(xPath)
                                            for node in nodes:
                                                properties.append(Property(property, [node.text]))
                                except Exception as e:
                                    comparelog.print_error(msg="XPath error for property: "+property+" from xml file: " + self.file,
                                                   args={'fnName': self.testName, 'type': comparelog.MISSING_PROPERTY,
                                                         'source': fileobj, 'checkName': self.checkName})
        else:
            comparelog.print_error(
                msg="No type available '" + self.type + "' . Available types: JSON, PROPERTY, XML, SHELL, STATIC",
                args={'fnName': self.testName, 'type': comparelog.SYNTAX_ERROR, 'source': "Metadata.json",
                      'checkName': self.checkName})
            return [None]
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
                                    msg="Not able to extract: '" + self.format + "' from " + property.name + ", from file:" + self.file,
                                    args={'fnName': self.testName, 'type': comparelog.MISSING_PROPERTY,
                                          'source': self.file,
                                          'checkName': self.checkName})
                                values.append(None)
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
                        comparelog.print_error(msg="No dynamic value present for key: '" + m.group(1)+"'",
                                               args={'fnName': self.testName,
                                                     'type': comparelog.MISSING_DYNAMIC_VALUE,
                                                     'source': self.file, 'checkName': self.checkName})
                        return None
                else:
                    comparelog.print_error(msg="No dynamic value present for key: '" + m.group(1)+"'",
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

    def splitNodes(self, str):
        pattern = re.compile('(\'.*\')')
        nodesEsc = pattern.split(str)
        nodes = []
        joinWithPrev = False
        for node in nodesEsc:
            quotesPattern = re.compile("^'.*'$")
            matcher = quotesPattern.match(node)
            if matcher:
                if len(nodes) > 1:
                    nodes[len(nodes)-1] = nodes[len(nodes)-1]+''+node
                else:
                    nodes.append(node)
                joinWithPrev = True
            else:
                nodesDelim = node.split('.')
                if joinWithPrev:
                    nodes[len(nodes)-1] = nodes[len(nodes)-1]+''+nodesDelim[0]
                else:
                    nodes.append(nodesDelim[0])
                nodes.extend(nodesDelim[1:])
                joinWithPrev = False
        return nodes