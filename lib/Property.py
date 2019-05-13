
class Property(object):
    MATCH = "0"
    NO_MATCH = "1"
    ERROR = "-1"
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return self.name + "(" + str(self.value) + ")"

    def compare(self, target):
        if self.value is not None and target is not None and target.value is not None:
            if len(self.value) == len(
                target.value):
                for j in range(0, len(self.value)):
                    if self.value[j] is not None and target.value[j] is not None:
                        if str(self.value[j]) != str(target.value[j]):
                            return Property.NO_MATCH
                        else:
                            return Property.MATCH
            else:
                return Property.NO_MATCH
        else:
            return Property.ERROR
