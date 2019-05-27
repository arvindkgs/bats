import os
import platform
import subprocess
from Property import Property
import Resource
from Error import Error


class ShellOutput:
    def __init__(self, output, error=None):
        self.output = output
        self.error = error


class ShellHandler(object):

    def getResourceItem(self, extrapolated_properties, *args):
        properties = None
        error = None
        password = username = hostname = None
        if args and len(args) == 3:
            hostname = args[0]
            username = args[1]
            password = args[2]
        for property in extrapolated_properties:
            if property:
                command = property
                if hostname and username and password:
                    command = 'sh ./scripts/runSSHCommand.sh ' + hostname + ' ' + username + ' ' + password + ' "' + command + '"'
                shellOutput = runShellCommand(command)
                commandOutput = shellOutput.output
                error = shellOutput.error
                if commandOutput is not None:
                    lines = commandOutput.split('\n')
                    i = -1
                    if hostname and username and password:
                        for i, line in enumerate(lines):
                            if (line.strip() == username + '@' + hostname + '\'s password:'):
                                break
                    commandOutput = lines[i + 1:]
                else:
                    commandOutput = [None]
                if not properties:
                    properties = []
                properties.append(Property(property, commandOutput, error))
        return Resource.Item("SHELL", properties, error)


def runShellCommand(command):
    returnVal = None
    error = None
    if platform.system() == 'Windows':
        programfiles = ('PROGRAMW6432' if platform.architecture()[0] == '32bit'
                        else 'PROGRAMFILES')
        bash_exe = os.getenv(programfiles) + r'\Git\bin\bash'
        process = subprocess.Popen(
            [bash_exe, '-c', command],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            if stdout.decode('ascii').strip() != "":
                returnVal = stdout.decode('ascii').strip()
            else:
                error = Error(type=Error.SHELL_COMMAND_ERROR,
                              message="Shell command returned empty string.")
        else:
            error = Error(type=Error.SHELL_COMMAND_ERROR,
                          message="Shell command failed with error: '" + stderr.strip() + "'")
    else:
        process = subprocess.Popen(
            [command], stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, shell=True)
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            if stdout.decode('ascii').strip() != "":
                returnVal = stdout.decode('ascii').strip()
            else:
                error = Error(type=Error.SHELL_COMMAND_ERROR,
                              message="Shell command returned empty string.")
        else:
            error = Error(type=Error.SHELL_COMMAND_ERROR,
                          message="Shell command failed with error: '" + stderr.strip() + "'")
    return ShellOutput(returnVal, error)


def getRemoteFile(hostname, username, password, path):
    filename = hostname + "_" + path
    filename = "./tmp/" + filename.replace("/", "_")
    if not os.path.isfile(filename):
        runShellCommand(
            'sh ./scripts/runSCPCommand.sh ' + hostname + ' ' + username + ' ' + password + ' ' + path + ' ' + filename)
    return filename
