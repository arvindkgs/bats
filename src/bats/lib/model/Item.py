from bats.lib import comparelog
from bats.lib.Error import Error


class Item(object):
    def __init__(self, file, properties, error=None):
        self.file = file
        self.properties = properties
        self.error = error

    def has_error(self, check, target_item_file=None):
        if self.error:
            comparelog.print_error(
                msg=self.error.message,
                args={"testName": check.testName,
                      "checkName": check.checkName,
                      "cardinality": check.cardinality,
                      "targetItem": target_item_file,
                      "type": self.error.type,
                      "source": self.file},
                console=check.failon and self.error.type in check.failon)
            return True
        elif not (self.properties and any(self.properties)):
            comparelog.print_error(
                msg="No properties",
                args={"testName": check.testName,
                      "checkName": check.checkName,
                      "cardinality": check.cardinality,
                      "targetItem": target_item_file,
                      "type": Error.VALUE_MISMATCH,
                      "source": self.file})
            return True
        else:
            return False

    def __str__(self):
        s = "[" + str(self.file) + "] " if self.file else ''
        if self.properties:
            for property in self.properties:
                s += str(property)
        return s

    def failed(self, failon):
        return (
            (self.error and failon and self.error.type in failon)
            or not self.properties
            or not any(self.properties)
        )