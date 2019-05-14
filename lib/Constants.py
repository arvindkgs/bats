import re
import re


class RegularExpression:
    findDefaultXMLNamespace = '^{([^}]*)(?=})'
    findIndexExpression = '{([^}]*)(?=})'


def getDefaultXMLNamespace(str):
    pattern = re.compile(RegularExpression.findDefaultXMLNamespace)
    matcher = pattern.match(str)
    if not matcher:
        return ''
    return matcher.group(0)
