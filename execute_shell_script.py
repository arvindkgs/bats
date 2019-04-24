import platform, os, subprocess


def grepProp(property, file):
    returnVal = None
    if platform.system() == 'Windows':
        programfiles = ('PROGRAMW6432' if platform.architecture()[0] == '32bit'
                        else 'PROGRAMFILES')
        bash_exe = os.getenv(programfiles) + r'\Git\bin\bash'
        process = subprocess.Popen(
            [bash_exe, '-c', 'grep \'^\\s*\'"' + property + '"\'=\' ./"' + file + '"|cut -d\'=\' -f2-'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            if stdout.decode('ascii').strip() != "":
                returnVal = stdout.decode('ascii').strip()
    else:
        process = subprocess.Popen(
            ['./grepProp.sh', property,
             file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            if stdout.decode('ascii').strip() != "":
                returnVal = stdout.decode('ascii').strip()
    return returnVal

