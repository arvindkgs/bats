import re

import jsonpath_rw_ext as jp
from apacheconfig import *
from Error import Error
from Property import Property
from Resource import Item


class ConfigHandler(object):
    def getResourceItem(self, extrapolated_properties, *args):
        properties = None
        error = None
        file = args[0]
        try:
            with open(file, 'r') as conf_file:
                dataStr = conf_file.read()
                if dataStr is not None:
                    pattern = re.compile('^include.*', flags=re.MULTILINE)
                    dataStr = pattern.sub('', dataStr)
                    try:
                        with make_loader() as loader:
                            confDict = None
                            if dataStr is not None:
                                confDict = loader.loads(dataStr)
                            for property in extrapolated_properties:
                                if property:
                                    parser = jp.parse(property)
                                    values = []
                                    if confDict is not None:
                                        for match in parser.find(confDict):
                                            values.append(match.value)
                                    if not properties:
                                        properties = []
                                    if values is None:
                                        properties.append(
                                            Property(str(property), values, Error(type=Error.MISSING_PROPERTY,
                                                                                  message="No property: '" + str(
                                                                                      property) + "' found.")))
                                    else:
                                        properties.append(Property(str(property), values))
                    except Error:
                        error = Error(type=Error.PARSER_ERROR, message="Invalid conf file '" + file + "'")
        except IOError as e:
            print e
            error = Error(Error.FILE_NOT_FOUND, "File not found")
        return Item(file, properties, error)

# def getPropertiesExtrapolation(resource, extrapolated_properties, files):
#     properties = []
#     for fileobj in files:
#         dataStr = None
#         try:
#             with open(fileobj, 'r') as conf_file:
#                 dataStr = conf_file.read()
#         except IOError:
#             comparelog.print_error(msg="File '" + fileobj + "' not found", args={'fnName': resource.testName,
#                                                                                  'type': comparelog.FILE_NOT_FOUND,
#                                                                                  'source': resource.file,
#                                                                                  'checkName': resource.checkName})
#         try:
#             with make_loader() as loader:
#                 jsonData = None
#                 if dataStr is not None:
#                     jsonData = loader.loads(dataStr)
#                     properties.extend(JsonHandler.readJsonData(resource, extrapolated_properties, jsonData))
#         except ValueError:
#             comparelog.print_error(msg="Invalid conf file '" + resource.file + "'", args={'fnName': resource.testName,
#                                                                                           'type': comparelog.FILE_NOT_FOUND,
#                                                                                           'source': resource.file,
#                                                                                           'checkName': resource.checkName})
#     return properties
