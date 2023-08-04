"""
snippets that are reused by multiple programs

imported with sys.path.append()


reject package managers, go back to M-w C-y
"""

from subprocess import Popen, PIPE, STDOUT


def system(cmd, stdin=None, stderr=False):
    "stdout[, stderr], errcode = system(command[, stdin][, stderr=True])"
    # merge stdout and stderr, and return error code instead
    if stdin is not None:
        stdin = stdin.encode()
    process = Popen(cmd, shell=True,
                    stdout=PIPE,
                    stderr=PIPE if stderr else STDOUT)
    out, err = process.communicate(stdin)
    returncode = process.returncode
    if stderr:
        return out.decode(), err.decode(), returncode
    else:
        return out.decode(), returncode


def parseargs(parameters):
    'UUID="..." TYPE="..." -> dict()'
    # args = [arg.split("=") for arg in parameters.split(" ")]
    # return {key: val[1:-1] for key, val in args}
    args = parameters.split(" ")
    fields = {}
    for arg in args:
        key, val = arg.split("=")
        fields[key] = val[1:-1]  # '"ext4"' -> 'ext4'
    return fields
