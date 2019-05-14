from StringIO import StringIO
import xml.etree.ElementTree as ET
from lib import Property, comparelog


def getProperties(resource, extrapolated_properties, files):
    properties = []
    if files is not None:
        for fileobj in files:
            it = None
            try:
                it = ET.iterparse(StringIO(open(fileobj).read()))
            except Exception as e:
                comparelog.print_error(msg="File: " + resource.file + ", does not exist.",
                                       args={'fnName': resource.testName, 'type': comparelog.FILE_NOT_FOUND,
                                             'source': fileobj, 'checkName': resource.checkName})
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
                            comparelog.print_error(
                                msg="XPath error for property: " + property + " from xml file: " + resource.file,
                                args={'fnName': resource.testName, 'type': comparelog.MISSING_PROPERTY,
                                      'source': fileobj, 'checkName': resource.checkName})
    return properties
