import re

import jsonpath_rw_ext as jp
from apacheconfig import *

from lib import comparelog, JsonHandler
from Property import Property


def getProperties(resource, extrapolated_properties, file):
    properties = []
    dataStr = None
    try:
        with open(file, 'r') as conf_file:
            dataStr = conf_file.read()
    except IOError:
        comparelog.print_error(msg="File '" + file + "' not found", args={'fnName': resource.testName,
                                                                             'type': comparelog.FILE_NOT_FOUND,
                                                                             'source': resource.file,
                                                                             'checkName': resource.checkName})
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
                        properties.append(Property(str(property), values))
        except ValueError:
            comparelog.print_error(msg="Invalid conf file '" + resource.file + "'",
                                   args={'fnName': resource.testName,
                                         'type': comparelog.FILE_NOT_FOUND,
                                         'source': resource.file,
                                         'checkName': resource.checkName})
    return properties


def getPropertiesExtrapolation(resource, extrapolated_properties, files):
    properties = []
    for fileobj in files:
        dataStr = None
        try:
            with open(fileobj, 'r') as conf_file:
                dataStr = conf_file.read()
        except IOError:
            comparelog.print_error(msg="File '" + fileobj + "' not found", args={'fnName': resource.testName,
                                                                                 'type': comparelog.FILE_NOT_FOUND,
                                                                                 'source': resource.file,
                                                                                 'checkName': resource.checkName})
        try:
            with make_loader() as loader:
                jsonData = None
                if dataStr is not None:
                    jsonData = loader.loads(dataStr)
                    properties.extend(JsonHandler.readJsonData(resource, extrapolated_properties, jsonData))
        except ValueError:
            comparelog.print_error(msg="Invalid conf file '" + resource.file + "'", args={'fnName': resource.testName,
                                                                                          'type': comparelog.FILE_NOT_FOUND,
                                                                                          'source': resource.file,
                                                                                          'checkName': resource.checkName})
    return properties
