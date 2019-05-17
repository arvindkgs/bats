from lib import comparelog, ShellHandler
from Property import Property
from os import path


def getProperties(resource, extrapolated_properties, files):
    properties = []
    for fileobj in files:
        if path.isfile(fileobj):
            for property in extrapolated_properties:
                if property:
                    propFrmFile = ShellHandler.runShellCommand(
                        'grep \'^\\s*\'"' + property + '"\'=\' ./"' + fileobj + '"|cut -d\'=\' -f2-')
                    if propFrmFile is None:
                        comparelog.print_error_log(msg="No property: " + property,
                                                   args={'fnName': resource.testName,
                                                         'type': comparelog.MISSING_PROPERTY,
                                                         'source': resource.file, 'checkName': resource.checkName})
                        properties.append(Property(property, None))
                    else:
                        properties.append(Property(property, [propFrmFile]))
        else:
            comparelog.print_error(msg="File not found.",
                                   args={'fnName': resource.testName, 'type': comparelog.FILE_NOT_FOUND,
                                         'source': fileobj, 'checkName': resource.checkName})
    return properties
