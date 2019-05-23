try:
    import libxml2
except ImportError:
    from lxml import etree
import imp
import re
from lib import comparelog
from Property import Property


def getProperties(resource, extrapolated_properties, file):
    properties = []
    try:
        if file:
            with open(file, 'r') as f:
                try:
                    imp.find_module('libxml2')
                    doc = libxml2.parseDoc(remove_namespace(f.read()))
                    root = doc.xpathNewContext()
                    xpath = root.xpathEval
                except ImportError:
                    parser = etree.XMLParser(remove_blank_text=True)
                    root = etree.fromstring(remove_namespace(f.read()), parser)
                    xpath = root.xpath

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
                                nodes = xpath(xPath)
                                for node in nodes:
                                    try:
                                        properties.append(Property(property, [node.content]))
                                    except AttributeError:
                                        properties.append(Property(property, [node.text]))
                        except Exception as e:
                            comparelog.print_error_log(
                                msg="XPath error for property: " + property,
                                args={'fnName': resource.testName, 'type': comparelog.MISSING_PROPERTY,
                                      'source': file, 'checkName': resource.checkName})
    except EnvironmentError:
        comparelog.print_error(msg="File not found.",
                               args={'fnName': resource.testName, 'type': comparelog.FILE_NOT_FOUND,
                                     'source': file, 'checkName': resource.checkName})
    return properties


def remove_namespace(data):
    data = re.sub('xmlns="[^"]*"\s*', '', data)
    return data
