class Error:
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    PARSER_ERROR = "PARSER_ERROR"

    MISSING_PROPERTY = "MISSING_PROPERTY"
    MISSING_FORMAT = "MISSING_FORMAT"
    MISSING_DYNAMIC_VALUE = "MISSING_DYNAMIC_VALUE"

    SHELL_COMMAND_ERROR = "SHELL_COMMAND_ERROR"
    SYNTAX_ERROR = "SYNTAX_ERROR"
    VALUE_MISMATCH = "VALUE_MISMATCH"
    EXTRAPOLATION_ERROR = "EXTRAPOLATION_ERROR"

    def __init__(self, type, message):
        self.type = type
        self.message = message
