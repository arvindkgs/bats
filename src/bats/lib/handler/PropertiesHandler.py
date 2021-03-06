from os import path
from ..Error import Error
from ..model.Property import Property
from ..model.Item import Item
import ShellHandler


class PropertiesHandler(object):

    def getResourceItem(self, extrapolated_properties, *args):
        error = None
        properties = None
        file = args[0]
        if file:
            if path.isfile(file):
                for property in extrapolated_properties:
                    if property:
                        propFrmFile = ShellHandler.runShellCommand(
                            'grep \'^\\s*\'"' + property + '"\'=\' "' + file + '"|cut -d\'=\' -f2-')
                        if not properties:
                            properties = []
                        if propFrmFile is None or propFrmFile.error:
                            errorMessage = "No property: " + property if propFrmFile.error.type == Error.MISSING_PROPERTY else propFrmFile.error.message
                            properties.append(Property(property, None, Error(type=Error.MISSING_PROPERTY,
                                                                             message=errorMessage)))
                        else:
                            properties.append(Property(property, [propFrmFile.output]))
            else:
                error = Error(Error.FILE_NOT_FOUND, "File not found")

        return Item(file, properties, error)
