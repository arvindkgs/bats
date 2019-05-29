from lib.ConfigHandler import ConfigHandler
from lib.PropertiesHandler import PropertiesHandler
from lib.JsonHandler import JsonHandler
from lib.XmlHandler import XmlHandler
from ShellHandler import ShellHandler
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
    else:
        return None
