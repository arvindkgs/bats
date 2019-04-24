import logging
import os

formatter = None
MISSING_PROPERTY = "MISSING PROPERTY"
SYNTAX_ERROR = "SYNTAX ERROR"
COMPARE = "COMPARE"
INFO = "MESSAGE"
MISSING_DYNAMIC_VALUE = "MISSING DYNAMIC VALUE"

name = "compare-properties"


class OptionalArgsFormatter(logging.Formatter, object):
    def __init__(self, formatStr, optional_args=None):
        super(OptionalArgsFormatter, self).__init__(formatStr)
        self.optional_args = optional_args
        self.formatStr = formatStr

    def format(self, record):
        self._fmt = self.formatStr
        for k, v in self.optional_args.items():
            if record.__dict__ is not None and (k not in record.__dict__ or record.__dict__[k] is None):
                # Remove optional v
                self._fmt = self._fmt.replace(v, "")
        return super(OptionalArgsFormatter, self).format(record)


def getLogger():
    return logging.getLogger(name)


# dir_path = os.path.dirname(os.path.realpath(__file__))
# current_date = datetime.now()
# current_date_formatted = current_date.strftime('%Y_%m_%d_%H%M')

# create logger
getLogger().setLevel(logging.DEBUG)

# Prints only ERROR CRITICAL to stdout
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)

# Prints ALL log levels to file
fh = logging.FileHandler(os.path.join(os.getcwd(), 'automation.log'), 'w')
fh.setLevel(logging.DEBUG)

# create formatter
formatter = OptionalArgsFormatter(
    '[[%(asctime)s]\t[%(levelname)s]\t[%(funcName)s]\t[%(compareName)s]\t[%(type)s]\t[%(source)s]]\t%(message)s',
    {'source': '\t[%(source)s]', 'type': '\t[%(type)s]', 'fnName': '\t[%(funcName)s]',
     'compareName': '\t[%(compareName)s]'})

# add formatter
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# add ch to logger
getLogger().addHandler(fh)
getLogger().addHandler(ch)


def setLogDir(logDir):
    global fh
    getLogger().removeHandler(fh)
    fh = logging.FileHandler(os.path.join(os.getcwd(), logDir + '/automation.log'), 'w')
    fh.setLevel(logging.DEBUG)

    # add formatter
    fh.setFormatter(formatter)

    # add ch to logger
    getLogger().addHandler(fh)


# Method to print Error log (prints to log and console)
def print_error(msg, args={}):
    file_name = os.path.basename(__file__)
    fnName = args['fnName'] if 'fnName' in args else None
    record = getLogger().makeRecord(name, logging.ERROR, file_name, None, msg=msg, args=None,
                                    exc_info=None,
                                    func=fnName, extra=args)
    getLogger().handle(record)


# Method to print Info to both log and console
def print_info(msg, args={}):
    file_name = os.path.basename(__file__)
    fnName = args['fnName'] if 'fnName' in args else None
    record = getLogger().makeRecord(name, logging.INFO, file_name, None, msg=msg, args=None, exc_info=None,
                                    func=fnName, extra=args)
    getLogger().handle(record)
    print(formatter.format(record))


# Method to print Info to log
def print_info_log(msg, args={}):
    file_name = os.path.basename(__file__)
    fnName = args['fnName'] if 'fnName' in args else None
    record = getLogger().makeRecord(name, logging.INFO, file_name, None, msg=msg, args=None,
                                    exc_info=None,
                                    func=fnName, extra=args)
    getLogger().handle(record)
