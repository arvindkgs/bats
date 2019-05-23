import os
import platform
import subprocess
from Property import Property
from lib import comparelog


def getProperties(resource, extrapolated_properties, file):
    properties = []
    for property in extrapolated_properties:
        if property:
            command = property
            if resource.hostname and resource.username and resource.password:
                command = 'sh ./scripts/runSSHCommand.sh ' + resource.hostname + ' ' + resource.username + ' ' + resource.password + ' "' + command + '"'
            commandOutput = runShellCommand(command, resource)
            if commandOutput is not None:
                lines = commandOutput.split('\n')
                i = -1
                if resource.hostname and resource.username and resource.password:
                    for i, line in enumerate(lines):
                        if (line.strip() == resource.username + '@' + resource.hostname + '\'s password:'):
                            break
                commandOutput = lines[i + 1:]
            else:
                commandOutput = [None]
            properties.append(Property(property, commandOutput))
    return properties


def runShellCommand(command, resource=None):
    returnVal = None
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
        process = subprocess.Popen(
            [command], stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, shell=True)
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            if stdout.decode('ascii').strip() != "":
                returnVal = stdout.decode('ascii').strip()
        else:
            if resource:
                comparelog.print_error(msg="Shell command failed with error: '" + stderr.strip() + "'",
                                   args={'fnName': resource.testName, 'type': comparelog.SHELL_COMMAND_ERROR,
                                         'source': command, 'checkName': resource.checkName})
            else:
                comparelog.print_error(msg="Shell command failed with error: '" + stderr.strip() + "'",
                                       args={'type': comparelog.SHELL_COMMAND_ERROR,
                                             'source': command})
    return returnVal


def getRemoteFile(hostname, username, password, path, resource=None):
    filename = hostname + "_" + path
    filename = "./tmp/" + filename.replace("/", "_")
    if not os.path.isfile(filename):
        runShellCommand(
            'sh ./scripts/runSCPCommand.sh ' + hostname + ' ' + username + ' ' + password + ' ' + path + ' ' + filename,
            resource)
    return filename
