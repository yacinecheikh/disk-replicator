import sys

args = sys.argv[1:]
args = [arg.split("=") for arg in args]
print(args)
