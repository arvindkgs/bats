from lib import execute_shell_script, comparelog, Property


def getProperties(resource, extrapolated_properties, files):
    properties = []
    for fileobj in files:
        for property in extrapolated_properties:
            propFrmFile = execute_shell_script.grepProp(property, fileobj)
            if propFrmFile is None:
                comparelog.print_error_log(msg="No property: " + property,
                                       args={'fnName': resource.testName, 'type': comparelog.MISSING_PROPERTY,
                                             'source': resource.file, 'checkName': resource.checkName})
                properties.append(Property(property, None))
            else:
                properties.append(Property(property, [propFrmFile]))
    return properties
