import ConfigHandler
import PropertiesHandler
import XmlHandler
from Resource import Type, Resource
from lib import comparelog, JsonHandler


def build(property, testName, checkName):
    if property['type'] == Type.JSON:
        return Resource(property, testName, checkName, JsonHandler.getProperties)
    elif property['type'] == Type.XML:
        return Resource(property, testName, checkName, XmlHandler.getProperties)
    elif property['type'] == Type.PROPERTY:
        return Resource(property, testName, checkName, PropertiesHandler.getProperties)
    elif property['type'] == Type.CONFIG:
        return Resource(property, testName, checkName, ConfigHandler.getProperties)
    else:
        comparelog.print_error(
            msg="No type available '" + property['type'] + "' . Available types: JSON, PROPERTY, XML, SHELL, STATIC",
            args={'fnName': testName, 'type': comparelog.SYNTAX_ERROR, 'source': "Metadata.json",
                  'checkName': checkName})
