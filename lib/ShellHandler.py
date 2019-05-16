import os
import platform
import subprocess

from Property import Property


def getProperties(resource, extrapolated_properties, files):
    properties = []
    for property in extrapolated_properties:
        command = property
        if resource.hostname and resource.username and resource.password:
            command = 'sh ./scripts/runSSHCommand.sh ' + resource.hostname + ' ' + resource.username + ' ' + resource.password + ' "' + command + '"'
        commandOutput = runShellCommand(command)
        if commandOutput is not None:
            lines = commandOutput.split('\n')
            commandOutput = lines[len(lines)-1]
        else:
            commandOutput = [None]
        properties.append(Property(property, commandOutput))
    return properties


def runShellCommand(command):
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
    return returnVal


def getRemoteFile(hostname, username, password, path):
    filename = hostname + "_" + path
    filename = "./tmp/" + filename.replace("/", "_")
    if not os.path.isfile(filename):
        runShellCommand(
            'sh ./scripts/runSCPCommand.sh ' + hostname + ' ' + username + ' ' + password + ' ' + path + ' ' + filename)
    return filename
