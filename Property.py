MATCH = "0"
NO_MATCH = "1"
ERROR = "-1"

class Property(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def compare(self, target):
        if self.value is not None and target is not None and target.value is not None and len(self.value) == len(
                target.value):
            for j in range(0, len(self.value)):
                if self.value[j] is not None and target.value[j] is not None:
                    if str(self.value[j]) != str(target.value[j]):
                        return NO_MATCH
                    else:
                        return MATCH
        else:
            return ERROR
