import os
import platform
import subprocess
from ..model.Property import Property
from ..Error import Error
from ..model.Item import Item


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
                shellOutput = runShellCommand(get_ssh_command(hostname, username, property, password))
                commandOutput = shellOutput.output
                error = shellOutput.error
                if commandOutput is not None:
                    lines = commandOutput.split('\n')
                    i = -1
                    if password:
                        for i, line in enumerate(lines):
                            if (line.strip() == username + '@' + hostname + '\'s password:'):
                                break
                    commandOutput = lines[i + 1:]
                else:
                    commandOutput = [None]
                if not properties:
                    properties = []
                properties.append(Property(property, commandOutput, error))
        return Item("SHELL", properties, error)


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
    else:
        process = subprocess.Popen(
            [command], stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    if process.returncode == 0:
        if stdout.decode('ascii').strip() != "":
            returnVal = stdout.decode('ascii').strip()
        else:
            error = Error(type=Error.MISSING_PROPERTY,
                          message="No output for shell command: " + command)
    else:
        error = Error(type=Error.SHELL_COMMAND_ERROR,
                      message="Shell command '" + command + "' failed with error: " + stderr.strip())
    return ShellOutput(returnVal, error)


def get_scp_command(hostname, username, password, path, filename):
    if hostname:
        if username:
            if password:
                return "expect -c \"spawn scp -q -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no {0}@{1}:{2} " \
                       "{3}; expect password: {{ send {4}\\r }}; set timeout 50; expect eof;\"| tr -d \"\\r\" ".format(username, hostname, path, filename, password)
            else:
                return "scp -q -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no {0}@{1}:{2} {3}".format(username, hostname, path, filename)
        elif password:
            return "expect -c \"spawn scp -q -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no {0}:{1} {2}; " \
                   "expect password: {{ send {3}\\r }}; set timeout 50; expect eof;\"| tr -d \"\\r\" ".format(hostname, path, filename, password)
        else:
            return "scp -q -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no {0}:{1} {2}".format(hostname, path, filename)

def get_ssh_command(hostname, username, command, password):
    if hostname:
        if username:
            if password:
                return "expect -c \"spawn ssh -q -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no {0}@{1} {2}; " \
                 "expect password: {{ send {3}\\r }}; set timeout 50; expect eof;\"| tr -d \"\\r\"".format(username, hostname, command, password)
            else:
                return "ssh -q -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no {0}@{1} {2}".format(username, hostname, command)
        elif password:
            return "expect -c \"spawn ssh -q -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no {0} {1}; " \
                 "expect password: {{ send {2}\\r }}; set timeout 50; expect eof;\"| tr -d \"\\r\"".format(hostname, command, password)
        else:
            return "ssh -q -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no {0} {1}".format(hostname, command)
    else:
        return command


def getRemoteFile(hostname, username, password, path):
    filename = hostname + "_" + path
    filename = "./tmp/" + filename.replace("/", "_")
    if not os.path.isfile(filename):
        shell_output = runShellCommand(get_scp_command(hostname, username, password, path, filename))
        if shell_output.error and shell_output.error.type == Error.SHELL_COMMAND_ERROR:
            raise IOError(shell_output.error.message)
    return filename
