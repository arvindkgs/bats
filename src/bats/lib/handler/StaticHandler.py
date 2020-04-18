from ..model.Item import Item
from ..model.Property import Property


class StaticHandler(object):
    def getResourceItem(self, extrapolated_properties, *args):
        error = None
        if args and len(args) > 0:
            properties = [Property(args[0], extrapolated_properties)]
        else:
            properties = [Property(extrapolated_properties, extrapolated_properties)]
        return Item(file, properties, error)