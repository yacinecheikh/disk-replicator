from subprocess import Popen, PIPE, STDOUT
import sys
import os


# copy pasted useful snippets
# package management is bloat, go back to M-w C-y

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


src_disk, dst_disk = sys.argv[1:]
system("mkdir mnt mnt/src mnt/dst")


def save_mbr():
    out, err = system(f"sfdisk -d {src_disk} > part_table0")
    assert err == 0
    print(f"wrote partition table of {src_disk} to part_table0")

def restore_mbr():
    out, err = system(f"cat part_table0 | sfdisk {dst_disk}")
    assert err == 0
    print(f"applied partition table to {dst_disk}")

def check_mbr():
    out, ret = system(f"sfdisk -d {dst_disk} > part_table1")
    assert ret == 0
    print(f"wrote partition table of {dst_disk} to part_table1")

    # dirty patch
    # may remove if useless, but it's a security against myself
    # replace name of {dst_drive} by {src_drive} before diffing
    with open("part_table1") as f:
        with open("part_table2", "w") as g:
            g.write(f.read().replace(dst_disk, src_disk))
    out, ret = system("diff part_table0 part_table2")
    assert out == ""
    system("rm part_table2")

    print("checked cloned partition table against original")


def list_partitions():
    # TODO: make GPT-compatible
    # can probably be done with sfdisk on a GPT table
    info, _ = system("cat part_table0")
    # string parsing code, don't try to understand it
    lines = info.split("\n")
    partitions = []
    lines.pop()
    while lines[-1] != "":
        line = lines.pop()
        name, desc = line.split(" : ")
        partitions.append(name)
        # TODO: partition flags
        # should not be needed to duplicate a partition, but keep it in mind in case it's needed
        #print(desc.replace(" ", "").split(","))
        #partitions[name]["bootable"] = "bootable" in desc

    return partitions

def duplicate(dev, args):
    match partition_info[dev]["TYPE"]:
        case "ext4":
            system(f"./clone/ext4 {dev} {dest_device}")
            #clone_ext4(dev, dest_device, args)
        case _:
            print("error")

def duplicate(src):
    dst = src.replace(src_disk, dst_disk)
    # scan the partition to check its layout type
    # the cloning program should also scan the partition/partition table
    out, err = system(f"/usr/sbin/blkid {src}")
    assert err == 0
    args = out.split(": ")[1].split(" ")
    args = [field.split("=") for field in args]
    fields = {}
    for key, value in args:
        fields[key] = value[1:-1]

    match fields["TYPE"]:
        case "ext4":
            print(f"recognized {src} to be of type ext4")
            os.system(f"clone/ext4 {src} {dst}")
            #print(out)
            #print(err)

    #uuid = fields["UUID"]
    #cloner = fields["TYPE"]

    #print(f"clone/{cloner} {src} {dst}")


# TODO: breaking news: sfdisk supports gpt tables
# parse output of sfdisk instead
out, err = system(f"sgdisk --backup=part_table0 {src_disk}")
assert err == 0
if "Found invalid GPT and valid MBR" in out:
    print("found MBR partition table")
    save_mbr()
    restore_mbr()
    check_mbr()
else:
    print("found GPT partition table")
    raise NotImplemented

# TODO: find something to do with partition info (currently not even used nor useable)
# TODO: better: stop scanning everything ?
partitions = list_partitions()
for partition in partitions:
    duplicate(partition)


"""
échec -> tester en réécrivant la table de partitions par dessus
!!!tester aussi de vérifier le flag bootable (pas mis pendant mkfs.ext4)
->tune2fs ?


(si besoin de recharger la table de partitions: partprobe (/dev/vdX))
"""
