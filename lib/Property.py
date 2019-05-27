from lib import Error


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
        return self.name + "(" + str(self.value) + ")"

    def compare(self, target):
        if self.value is not None and target is not None and isinstance(target, Property) and target.value is not None:
            if len(self.value) == len(target.value):
                result = True
                for j in range(0, len(self.value)):
                    result = result and str(self.value[j]) == str(target.value[j])
                if result and len(self.value) > 0:
                    return Property.MATCH
                elif result:
                    return Property.IGNORE
                else:
                    return Property.NO_MATCH
            else:
                return Property.ERROR
        else:
            return Property.ERROR
