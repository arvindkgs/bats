try:
    import libxml2
except ImportError:
    from lxml import etree
import imp
import re
from Property import Property
from Error import Error
from Resource import Item


class XmlHandler(object):

    def getResourceItem(self, extrapolated_properties, *args):
        error = None
        properties = []
        file = args[0]
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
                                properties.append(Property(property, None, Error(Error.MISSING_PROPERTY,
                                                                                 "XPath error for property: " + property)))
        except Error as e:
            print e
            error = Error(Error.PARSER_ERROR, "XML parsing error")
            properties = None

        return Item(file, properties, error)


def remove_namespace(data):
    data = re.sub('xmlns="[^"]*"\s*', '', data)
    return data
