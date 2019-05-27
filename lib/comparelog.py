import logging
import os

formatter = None

name = "compare-properties"

test = False


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


# create logger
getLogger().setLevel(logging.DEBUG)

# Prints only ERROR CRITICAL to stdout
# ch = logging.StreamHandler()
# ch.setLevel(logging.ERROR)

# create formatter
formatter = OptionalArgsFormatter(
    '[[%(levelname)s]\t[%(testName)s]\t[%(checkName)s]\t[%(cardinality)s]\t[%(targetItem)s]\t[%(type)s]\t[%(source)s]]\t%(message)s',
    {'source': '\t[%(source)s]', 'type': '\t[%(type)s]', 'testName': '\t[%(testName)s]',
     'checkName': '\t[%(checkName)s]', 'cardinality': '\t[%(cardinality)s]', 'targetItem': '\t[%(targetItem)s]'})


# add formatter
# ch.setFormatter(formatter)

# add ch to logger
# getLogger().addHandler(ch)


def setOptions(options):
    global test
    for option in options.split(','):
        if option == 'test':
            test = True


logFileSet = False


def setLogFileName(logFileName='automation.log'):
    global fh
    global logFileSet
    if not logFileSet:
        try:
            logFileSet = True
            fh = logging.FileHandler(logFileName, 'w')
            fh.setLevel(logging.DEBUG)

            # add formatter
            fh.setFormatter(formatter)

            # add ch to logger
            getLogger().addHandler(fh)
        except IOError:
            record = getLogger().makeRecord(name, logging.ERROR, os.path.basename(__file__), None,
                                            msg="Path to logFileName '" + logFileName + "' incorrect. Creating default log 'automation.log'",
                                            args=None, exc_info=None,
                                            func="ERROR", extra={})
            getLogger().handle(record)
            print(formatter.format(record))
            fh = logging.FileHandler('automation.log', 'w')
            fh.setLevel(logging.DEBUG)

            # add formatter
            fh.setFormatter(formatter)

            # add ch to logger
            getLogger().addHandler(fh)


# Method to print Error log (prints to log and console)
def print_error(msg, args={}, console=True):
    setLogFileName()
    file_name = os.path.basename(__file__)
    fnName = args['testName'] if 'testName' in args else None
    if 'cardinality' in args and args['cardinality'] == 'one-to-one' and 'targetItem' in args:
        args['targetItem'] = None
        args['cardinality'] = None
    record = getLogger().makeRecord(name, logging.ERROR, file_name, None, msg=msg, args=None,
                                    exc_info=None,
                                    func=fnName, extra=args)
    getLogger().handle(record)
    if not test and console:
        print(formatter.format(record))


# Method to print Info to both log and console
def print_info(msg, args={}, console=True):
    global test
    setLogFileName()
    file_name = os.path.basename(__file__)
    fnName = args['testName'] if 'testName' in args else None
    if 'cardinality' in args and args['cardinality'] == 'one-to-one' and 'targetItem' in args:
        args['targetItem'] = None
        args['cardinality'] = None
    record = getLogger().makeRecord(name, logging.INFO, file_name, None, msg=msg, args=None, exc_info=None,
                                    func=fnName, extra=args)
    getLogger().handle(record)
    if not test and console:
        print(formatter.format(record))
