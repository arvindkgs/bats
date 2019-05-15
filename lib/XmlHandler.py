import xml.etree.ElementTree as ET
from StringIO import StringIO

from lib import comparelog
from Property import Property


def getProperties(resource, extrapolated_properties, files):
    properties = []
    if files is not None:
        for fileobj in files:
            try:
                with open(fileobj, 'r') as f:
                    it = ET.iterparse(StringIO(f.read()))
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
                                    comparelog.print_error_log(
                                        msg="XPath error for property: " + property,
                                        args={'fnName': resource.testName, 'type': comparelog.MISSING_PROPERTY,
                                              'source': fileobj, 'checkName': resource.checkName})
            except Exception:
                comparelog.print_error(msg="File not found: " + resource.file,
                                       args={'fnName': resource.testName, 'type': comparelog.FILE_NOT_FOUND,
                                             'source': fileobj, 'checkName': resource.checkName})
    return properties
