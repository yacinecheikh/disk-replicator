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
    "parse commandline arguments (used for the results of blkid and sfdisk -d)"
    out, _ = system(f"./parseargs {parameters}")
    args = eval(out)
    fields = {}
    for key, val in args:
        fields[key] = val

    return fields
