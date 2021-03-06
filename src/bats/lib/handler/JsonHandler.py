import json
import jsonpath_rw_ext as jp
from ..Error import Error
from ..model.Property import Property
from ..model.Item import Item


class JsonHandler(object):

    def getResourceItem(self, extrapolated_properties, *args):
        error = None
        properties = None
        file = args[0]
        try:
            with open(file, 'r') as conf_file:
                dataStr = conf_file.read()
                try:
                    jsObj = None
                    if dataStr is not None:
                        jsObj = json.loads(dataStr)
                    if not any(extrapolated_properties):
                        properties = self.generateProperties(jsObj)
                    else:
                        for property in extrapolated_properties:
                            if property:
                                values = None
                                try:
                                    parser = jp.parse(property)
                                    if jsObj is not None:
                                        for match in parser.find(jsObj):
                                            if match.value is not None:
                                                if values is None:
                                                    values = []
                                                values.append(match.value)
                                    if not properties:
                                        properties = []
                                    if values is None:
                                        properties.append(
                                            Property(str(property), values, Error(type=Error.MISSING_PROPERTY,
                                                                                  message="No property: " + str(
                                                                                      property))))
                                    else:
                                        properties.append(Property(str(property), values))
                                except Exception as e:
                                    print e
                                    if not properties:
                                        properties = []
                                    properties.append(Property(str(property), values, Error(type=Error.SYNTAX_ERROR,
                                                                                            message="Parser error, check jsonpath for property '" + str(
                                                                                                property))))
                except Error:
                    error = Error(type=Error.PARSER_ERROR, message="Invalid json file '" + file + "'")
        except IOError as e:
            print e
            error = Error(Error.FILE_NOT_FOUND, "File not found")
        return Item(file, properties, error)

    def generateProperties(self, jsObj):
        properties = []
        self.visitDict(properties=properties, prefix="$", dictionary=jsObj)
        return properties

    def visitDict(self, properties, prefix, dictionary):
        if isinstance(dictionary, dict):
            for key in dictionary:
                self.visitDict(properties, prefix + ".'" + key + "'", dictionary[key])
        elif isinstance(dictionary, list):
            for i, item in enumerate(dictionary):
                self.visitDict(properties, prefix + "[" + str(i) + "]", item)
        else:
            properties.append(Property(prefix, [dictionary]))

    # def getPropertiesExtrapolation(resource, extrapolated_properties, files):
    #     properties = []
    #     for fileobj in files:
    #         try:
    #             with open(fileobj, 'r') as json_file:
    #                 data = json.load(json_file)
    #                 properties.extend(readJsonData(data, extrapolated_properties, resource))
    #         except IOError:
    #             comparelog.print_error(msg="File '" + resource.file + "' not found", args={'fnName': resource.testName,
    #                                                                                        'type': comparelog.FILE_NOT_FOUND,
    #                                                                                        'source': resource.file,
    #                                                                                        'checkName': resource.checkName})
    #         except ValueError:
    #             comparelog.print_error(msg="Invalid json '" + resource.file + "'", args={'fnName': resource.testName,
    #                                                                                      'type': comparelog.FILE_NOT_FOUND,
    #                                                                                      'source': resource.file,
    #                                                                                      'checkName': resource.checkName})
    #     return properties
    #
    # def readJsonData(data, extrapolated_properties, resource):
    #     properties = []
    #     for property in extrapolated_properties:
    #         nodes = splitNodes(property)
    #         jsondata = data
    #         for i, node in enumerate(nodes):
    #             if not isinstance(jsondata, list):
    #                 jsondata = [jsondata]
    #             newdata = []
    #             for obj in jsondata:
    #                 index = re.match("\[(.*)\]", node)
    #                 error = False
    #                 if obj != None:
    #                     if index:
    #                         index = index.group(1)
    #                         if index.isdigit():
    #                             try:
    #                                 newdata.append(obj[index])
    #                             except:
    #                                 comparelog.print_error(
    #                                     msg="No object at index: " + index + " in property " + property,
    #                                     args={
    #                                         'fnName': resource.testName,
    #                                         'type': comparelog.MISSING_PROPERTY,
    #                                         'source': resource.file, 'checkName': resource.checkName
    #                                     })
    #                                 error = True
    #                                 pass
    #                         elif index == '':
    #                             if not isinstance(obj, list):
    #                                 comparelog.print_error(
    #                                     msg="Property '" + property + "' specified is not an array.",
    #                                     args={'fnName': resource.testName,
    #                                           'type': comparelog.MISSING_PROPERTY,
    #                                           'source': resource.file, 'checkName': resource.checkName})
    #                                 error = True
    #                             else:
    #                                 newdata = obj
    #                         else:
    #                             if "&&" in index:
    #                                 expressions = index.split("&&")
    #                             else:
    #                                 expressions = [index]
    #                             filters = []
    #                             for expression in expressions:
    #                                 if "==" in expression or "!=" in expression:
    #                                     if "==" in expression:
    #                                         key, value = expression.split("==")
    #                                     else:
    #                                         key, value = expression.split("!=")
    #                                     key = key.strip()
    #                                     value = value.strip()
    #                                     if value is not None and value != '' and key:
    #                                         value = value if value[0] != '\'' and value[
    #                                             len(value) - 1] != '\'' else value[
    #                                                                          1:len(
    #                                                                              value) - 1]
    #                                         if "==" in expression:
    #                                             filters.append((key, value, "EQUAL"))
    #                                         else:
    #                                             filters.append((key, value, "UNEQUAL"))
    #                                     else:
    #                                         comparelog.print_error(
    #                                             msg="Syntax of '" + node + "' expected as 'key == value'",
    #                                             args={'fnName': resource.testName,
    #                                                   'type': comparelog.SYNTAX_ERROR,
    #                                                   'source': "Metadata.json",
    #                                                   'checkName': resource.checkName})
    #                                         error = True
    #                             if not error:
    #                                 found = False
    #                                 for item in obj:
    #                                     matches = True
    #                                     for filterObj in filters:
    #                                         key, value, type = filterObj
    #                                         if key not in item:
    #                                             matches = False
    #                                         else:
    #                                             pattern = re.compile('^' + str(value) + '$')
    #                                             rematch = pattern.match(str(item[key]))
    #                                             if not rematch and type == "EQUAL":
    #                                                 matches = False
    #                                                 break
    #                                             elif rematch and type == "UNEQUAL":
    #                                                 matches = False
    #                                                 break
    #                                     if matches and len(filters) > 0:
    #                                         found = True
    #                                         newdata.append(item)
    #                                 if not found:
    #                                     comparelog.print_error(
    #                                         msg="No object with attribute: " + index + " found in : " + str(
    #                                             resource.file),
    #                                         args={'fnName': resource.testName,
    #                                               'type': comparelog.MISSING_PROPERTY,
    #                                               'source': resource.file, 'checkName': resource.checkName})
    #                                     error = True
    #                     elif node in obj:
    #                         newdata.append(obj[node])
    #                     else:
    #                         comparelog.print_error(msg="No attribute: " + str(node) + " in " + property,
    #                                                args={'fnName': resource.testName,
    #                                                      'type': comparelog.MISSING_PROPERTY,
    #                                                      'source': resource.file,
    #                                                      'checkName': resource.checkName})
    #                         error = True
    #                     if error:
    #                         newdata.append(None)
    #                 else:
    #                     newdata.append(None)
    #             jsondata = newdata
    #         properties.append(Property(str(property), jsondata))
    #     return properties
    #
    # def splitNodes(str):
    #     pattern = re.compile('(\'.*\')')
    #     nodesEsc = pattern.split(str)
    #     nodes = []
    #     joinWithPrev = False
    #     for node in nodesEsc:
    #         quotesPattern = re.compile("^'.*'$")
    #         matcher = quotesPattern.match(node)
    #         if matcher:
    #             if len(nodes) > 1:
    #                 nodes[len(nodes) - 1] = nodes[len(nodes) - 1] + '' + node
    #             else:
    #                 nodes.append(node)
    #             joinWithPrev = True
    #         else:
    #             nodesDelim = node.split('.')
    #             if joinWithPrev:
    #                 nodes[len(nodes) - 1] = nodes[len(nodes) - 1] + '' + nodesDelim[0]
    #             else:
    #                 nodes.append(nodesDelim[0])
    #             nodes.extend(nodesDelim[1:])
    #             joinWithPrev = False
    #     return nodes
