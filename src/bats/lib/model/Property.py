from bats.lib import comparelog


class Property(object):
    MATCH = "0"  # length and value matches
    NO_MATCH = "1"  # length matches, but values do not match
    ERROR = "-1"  # length do not match
    IGNORE = "2"  # length matches but source value = [] and target value = [], i.e empty array

    def __init__(self, name, value, error=None):
        self.name = name
        self.value = value
        self.error = error

    def __str__(self):
        return str(self.name) + "(" + str(self.value) + ")"

    def compare(self, target):
        if self.value is not None and target is not None and isinstance(target, Property) and target.value is not None:
            if len(self.value) == len(target.value):
                equal = True
                for j in range(len(self.value)):
                    if isinstance(self.value[j], dict):
                        equal = equal and self.value[j] == target.value[j]
                    elif isinstance(self.value[j], list):
                        equal = equal and self.value[j] == target.value[j]
                    else:
                        equal = equal and str(self.value[j]) == str(target.value[j])
                if len(self.value) > 0:
                    if equal:
                        return Property.MATCH
                    else:
                        return Property.NO_MATCH
                else:
                    return Property.IGNORE
            else:
                return Property.ERROR
        else:
            return Property.ERROR

    def isSuccess(self):
        if self.value:
            for i in range(self.value):
                if self.value[i]:
                    return Property.NO_MATCH
        else:
            return Property.ERROR
        return Property.MATCH

    def has_error(self, check, file, target_file=None):
        if self.error:
            comparelog.print_error(
                msg=self.error.message,
                args={"testName": check.testName,
                      "checkName": check.checkName,
                      "cardinality": check.cardinality,
                      "targetItem": target_file,
                      "type": self.error.type,
                      "source": file},
                console=check.failon and self.error.type in check.failon)
            return True
        else:
            return False

    def failed(self, failon):
        return self.error and failon and self.error.type in failon