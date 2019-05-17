import libxml2
import re
from lib import comparelog
from Property import Property


def getProperties(resource, extrapolated_properties, files):
    properties = []
    if files is not None:
        for fileobj in files:
            try:
                if fileobj:
                    with open(fileobj, 'r') as f:
                        doc = libxml2.parseDoc(remove_namespace(f.read()))
                        root = doc.xpathNewContext()
                        for property in extrapolated_properties:
                            if property:
                                try:
                                    nodes = property.split(".")
                                    xPath = '/'
                                    for ele in nodes:
                                        ele = ele.replace(' == ', '=')
                                        ele = ele.replace('==', '=')
                                        xPath += ele + '/'
                                    xPath = xPath[:len(xPath) - 1]
                                    if xPath != '':
                                        # xPath = xPath[:len(xPath) - 1]
                                        nodes = root.xpathEval(xPath)
                                        for node in nodes:
                                            properties.append(Property(property, [node.content]))
                                except Exception as e:
                                    comparelog.print_error_log(
                                        msg="XPath error for property: " + property,
                                        args={'fnName': resource.testName, 'type': comparelog.MISSING_PROPERTY,
                                              'source': fileobj, 'checkName': resource.checkName})
            except EnvironmentError:
                comparelog.print_error(msg="File not found.",
                                       args={'fnName': resource.testName, 'type': comparelog.FILE_NOT_FOUND,
                                             'source': fileobj, 'checkName': resource.checkName})
    return properties


def remove_namespace(data):
    data = re.sub('xmlns="[^"]*"\s*', '', data)
    return data
