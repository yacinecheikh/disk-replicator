from subprocess import Popen, PIPE, STDOUT


def system(cmd, stdin=None, stderr=False):
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
