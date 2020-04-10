from ..handler.ConfigHandler import ConfigHandler
from ..handler.PropertiesHandler import PropertiesHandler
from ..handler.JsonHandler import JsonHandler
from ..handler.XmlHandler import XmlHandler
from ..handler.ShellHandler import ShellHandler
from ..handler.StaticHandler import StaticHandler
from Resource import Type, Resource

def build(property, testName, checkName, dynamicProperties):
    if property['type'] == Type.JSON:
        return Resource(property, testName, checkName, JsonHandler(), dynamicProperties)
    elif property['type'] == Type.XML:
        return Resource(property, testName, checkName, XmlHandler(), dynamicProperties)
    elif property['type'] == Type.PROPERTIES:
        return Resource(property, testName, checkName, PropertiesHandler(), dynamicProperties)
    elif property['type'] == Type.CONFIG:
        return Resource(property, testName, checkName, ConfigHandler(), dynamicProperties)
    elif property['type'] == Type.SHELL:
        return Resource(property, testName, checkName, ShellHandler(), dynamicProperties)
    elif property['type'] == Type.STATIC:
        return Resource(property, testName, checkName, StaticHandler(), dynamicProperties)
    else:
        return None
