from abc import *
from PropertiesHandler import PropertiesHandler
from ShellHandler import ShellHandler
from ConfigHandler import ConfigHandler
from XmlHandler import XmlHandler
from JsonHandler import JsonHandler


class DataHandler(ABCMeta):
    __metaclass__ = ABCMeta

    @abstractmethod
    def getResourceItem(self, properties, *args):
        pass


DataHandler.register(PropertiesHandler)
DataHandler.register(ShellHandler)
DataHandler.register(ConfigHandler)
DataHandler.register(XmlHandler)
DataHandler.register(JsonHandler)
