import json
import re
from subprocess import Popen, PIPE
import comparelog

class Type(object):
    JSON = "JSON"
    PROPERTY = "PROPERTY"
    XML = "XML"
    SHELL = "SHELL"
    STATIC = "STATIC"

class Property(object):
    def __init__(self, property, check_name):
        self.type = None if "type" not in property else property['type']
        self.property = None if "property" not in property else property['property']
        self.file = None if "file" not in property else property['file']
        self.format = None if "format" not in property else property['format']
        self.check_name = check_name
        self.key = None if "key" not in property else property['key']

    def getValue(self, dynamicMap):
        global logger
        data = None
        if self.type == Type.JSON:
            with open(self.file, 'r') as json_file:
                data = json.load(json_file)
                # key : "topology.wlsClusters.[clusterName = 'AdminServer'].Xms"
                nodes = self.property.split('.')
                for i, node in enumerate(nodes):
                    if not isinstance(data, list):
                        data = [data]
                    newdata = []
                    for j, obj in enumerate(data):
                        index = re.match("\[(.*)\]", node)
                        error = False
                        if obj != None:
                            if index:
                                index = index.group(1)
                                if index.isdigit():
                                    try:
                                        # data[j] = obj[index]
                                        newdata.append(obj[index])
                                    except:
                                        error = True
                                        pass
                                elif "=" in index:
                                    key, value = index.split("=")
                                    key = key.strip()
                                    value = value.strip()
                                    if value is not None and value != '':
                                        value = value if value[0] != '\'' and value[len(value) - 1] != '\'' else value[1:len(value) - 1]
                                        if key:
                                            found = False
                                            for item in obj:
                                                if key in item and item[key] == value:
                                                    # data[j] = item
                                                    newdata.append(item)
                                                    found = True
                                            if not found:
                                                comparelog.print_error(
                                                    msg="No object with attribute: " + key + " = " + value + " found in : " + str(
                                                        self.file),
                                                    args={'fnName': self.check_name, 'type': comparelog.MISSING_PROPERTY,
                                                          'source': self.file})
                                                error = True
                                    else:
                                        comparelog.print_error(msg="Value expected for '" + node + "' after '='",
                                                               args={'fnName': self.check_name,
                                                                     'type': comparelog.SYNTAX_ERROR,
                                                                     'source': "Metadata.json"})
                                        error = True
                                elif index == '':
                                    if not isinstance(obj, list):
                                        comparelog.print_error(
                                            msg="Property '" + self.property + "' specified is not an array.",
                                            args={'fnName': self.check_name, 'type': comparelog.MISSING_PROPERTY,
                                                  'source': self.file})
                                        # return None
                                        error = True
                                    else:
                                        newdata = obj
                                    pass
                            elif node in obj:
                                # data[j] = obj[node]
                                newdata.append(obj[node])
                            else:
                                comparelog.print_error(msg="No attribute: " + str(node) + " in " + self.property,
                                                       args={'fnName': self.check_name, 'type': comparelog.MISSING_PROPERTY,
                                                             'source': self.file})
                                error = True
                            if error:
                                newdata.append(None)
                        else:
                            newdata.append(None)
                    data = newdata
                # data now is array of values to be given to formatter
                pass
        elif self.type == Type.PROPERTY:
            # extrapolate properties based on dynamicMap
            for (k, v) in dynamicMap:
                pass
            data = []
            properties = [self.property]
            for property in properties:
                process = Popen(
                    ['./grepProp.sh', property,
                     self.file], stdout=PIPE, stderr=PIPE)
                stdout, stderr = process.communicate()
                error = True
                if process.returncode == 0:
                    if stdout.decode('ascii').strip() != "":
                        data.append(stdout.decode('ascii').strip())
                        error = False
                if error:
                    data.append(None)
                    comparelog.print_error(msg="Not able to get property: " + property + ", from file:" + self.file,
                                           args={'fnName': self.check_name, 'type': comparelog.MISSING_PROPERTY,
                                                 'source': self.file})
                    # return None
        else:
            comparelog.print_error(
                msg="No type available '" + self.type + "' . Available types: JSON, PROPERTY, XML, SHELL, STATIC",
                args={'fnName': self.check_name, 'type': comparelog.SYNTAX_ERROR, 'source': "Metadata.json"})
            return [None]
        if self.format is not None and data is not None and data != [None] * len(data):
            # extract data using self.format
            # meta-chars: {}, ?
            # {} -> return value. {2} -> return 2 characters
            # ? -> single character
            # Future enhancement : ?[n] -> n characters
            # Example:
            # Format='-Xms{}?'
            # Data='-Xms512m -Xmx8192m -Xss102400k'
            # Extract=512
            newdata = []
            for j, obj in enumerate(data):
                limit = -1
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
                    # print "Regex Pattern: "+pattern
                    # pdb.set_trace()
                    m = re.match(pattern, obj)
                    if m:
                        newdata.append(m.group(1))
            data = newdata
        return data

    def toString(self):
        return 'Type: ' + str(self.type) + ', Source: ' + str(self.file) + ', Property: ' + str(
            self.property) + ', Format: ' + str(self.format)

    def getKey(self):
        return self.key