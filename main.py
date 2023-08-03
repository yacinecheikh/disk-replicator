from subprocess import Popen, PIPE, STDOUT
import sys


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


src_disk, dst_disk = system.argv[1:]


def save_mbr():
    out, err = system(f"sfdisk -d {src_disk} > part_table0")
    print(err)
    assert err == 0
    print(out)

def restore_mbr():
    out, err = system(f"cat part_table0 | sfdisk {dst_disk}")
    print(0)
    assert err == 0
    print(out)

def check_mbr():
    out, ret = system(f"sfdisk -d {dst_disk} > part_table1")
    assert ret == 0

    out, err, ret = system("diff part_table0 part_table1", stdout=True)
    print(err.encode(), out.encode(), ret)

def scan_partitions():
    info, _ = system("cat part_table0")
    # TODO: use scan_partitions() instead of bloating list_partitions

    # parse the partition table (output of sfdisk -d)
    lines = info.split("\n")
    partitions = {}
    lines.pop()
    while lines[-1] != "":
        # TODO: lire le reste de la ligne, si c'est utile
        dev, desc = lines.pop().split(" : ")
        partitions[dev] = {}

    # parse description of each partition
    # blkid /dev/vdX (alt: lsblk -f)
    for dev in partitions:
        out, err = system(f"/usr/sbin/blkid {dev}")
        assert err == 0
        print(out)

        _, args = out.split(":")
        args = args.split(" ")
        for arg in args:
            key, val = args.split("=")
            partitions[dev][key] = val[1:-1]

    return partitions

def duplicate(dev, args):
    # /dev/vdX in VM
    dev_id = dev[8:]
    dest_device = f"{dest_disk}{dev_id}"
    match partition_info[dev]["TYPE"]:
        case "ext4":
            system(f"./clone/ext4 {dev} {dest_device}")
            #clone_ext4(dev, dest_device, args)
        case _:
            print("error")



out, err = system(f"sgdisk --backup=part_table0 {src_disk}")
print(out)
assert err == 0
if "Found invalid GPT and valid MBR" in out:
    print("found MBR")
    save_mbr()
    restore_mbr()
    check_mbr()
else:
    print("found GPT partition table")
    raise NotImplemented

# TODO: find something to do with partition info (currently not even used nor useable)
# TODO: better: stop scanning everything ?
partition_info = scan_partitions()
for partition, data in partition_info.items():
    duplicate(partition, data)


échec -> tester en réécrivant la table de partitions par dessus
!!!tester aussi de vérifier le flag bootable (pas mis pendant mkfs.ext4)
->tune2fs ?


(si besoin de recharger la table de partitions: partprobe (/dev/vdX))
