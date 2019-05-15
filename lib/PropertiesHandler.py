from lib import comparelog, ShellHandler
from Property import Property


def getProperties(resource, extrapolated_properties, files):
    properties = []
    for fileobj in files:
        for property in extrapolated_properties:
            propFrmFile = ShellHandler.runShellCommand(
                'grep \'^\\s*\'"' + property + '"\'=\' ./"' + fileobj + '"|cut -d\'=\' -f2-')
            if propFrmFile is None:
                comparelog.print_error_log(msg="No property: " + property,
                                           args={'fnName': resource.testName, 'type': comparelog.MISSING_PROPERTY,
                                                 'source': resource.file, 'checkName': resource.checkName})
                properties.append(Property(property, None))
            else:
                properties.append(Property(property, [propFrmFile]))
    return properties
