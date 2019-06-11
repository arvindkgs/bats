class Item(object):
    def __init__(self, file, properties, error=None):
        self.file = file
        self.properties = properties
        self.error = error