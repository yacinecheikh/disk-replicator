from subprocess import Popen, PIPE, STDOUT
import sys
import os

from snippets import system, parseargs


src_disk, dst_disk = sys.argv[1:]
system("mkdir mnt mnt/src mnt/dst")


def list_partitions():
    info, _ = system("cat part_table0")
    # string parsing code, don't try to understand it
    lines = info.split("\n")
    partitions = []
    lines.pop()
    while lines[-1] != "":
        line = lines.pop()
        # TODO: the partition description could be useful for debugging
        name, desc = line.split(" : ")
        partitions.append(name)
    return partitions


def duplicate(src):
    dst = src.replace(src_disk, dst_disk)
    # scan the partition to get its layout type
    out, err = system(f"/usr/sbin/blkid {src}")
    assert err == 0
    fields = parseargs(out.split(": ")[1])

    cloner = fields["TYPE"]
    if not os.path.exists(f"clone/{cloner}"):
        print(f"unrecognized partition type: {cloner}")
        raise NotImplementedError

    print(f"recognized {src} to be of type {cloner}")
    # system() would block until the cloning completes
    os.system(f"clone/{cloner} {src} {dst}")


table, err = system(f"sfdisk -d {src_disk}")
assert err == 0
if table.startswith("label: dos"):
    print("found MBR partition table")
elif table.startswith("label: gpt"):
    print("found GPT partition table")
else:
    print("unknown partition table")
    raise NotImplementedError

# clone partition table
with open("part_table0", "w") as f:
    f.write(table)
out, err = system(f"cat part_table0 | sfdisk {dst_disk}")
assert err == 0

# basic check, probably useless
with open("part_table1", "w") as f:
    f.write(table.replace(dst_disk, src_disk))
out, _ = system("diff part_table0 part_table1")
assert out == ""
system("rm part_table1")

# clone individual partitions
partitions = list_partitions()
for partition in partitions:
    duplicate(partition)

