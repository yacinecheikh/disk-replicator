# Disk replicator

## What it can do

* Faster backups of physical drives (by only copying useful data)
* Smaller backups of physical drives (by using a dynamic virtual disk to only store what is written)
* "Sparsify" virtual disks, by filling a new empty disk with only the useful data

## Warning

Cloning MBR bootable disks creates non-bootable disks, making them useless in virtual machines.
This is not a problem for non-bootable disks or GPT (UEFI) disks.

## Usage

```
git clone <this repo>
cd <this repo>
```
`sudo python3 main.py /dev/{src} /dev/{dst}` to clone a disk.

To use virtual disks without a virtual machine, use `qemu-nbd`:
`sudo qemu-nbd -c /dev/nbd0 <disk>` to connect a virtual disk
`sudo qemu-nbd -d /dev/nbd0` to disconnect it.

To create an empty virtual disk: `qemu-img create -f qcow2 <name> <size>`
`size` can include a suffix (M, G,...)

If you have a disk without a partition table (just one partition), you can use the scripts in the `clone/` directory to clone your partition.


If the script crashes while copying files, make sure that everything in `mnt/` is unmounted.
The script will not work again until the `mnt/` directory is available.
You can also restart your computer.


## Motivations

I just wanted to be able to make 200To dynamic virtual drives and not have to care about virt-sparsify writing 199To of zeros on my physical disks.

Everything the script does can be made manually by using standard tools like gparted on the disks.
The only "new" part is replicating partitions and files instead of using virt-sparsify (also done with standard partitioning tools).

## How it works

The main script (in python) checks the partition tables and partition list with `sfdisk -d`, replicates the table with `sfdisk`, and then calls executable scripts in `clone/` to copy the contents of partitions.

To handle unexpected partition types, the default behaviour is to use `dd` to just clone everything. This is not a problem for small partitions like EFI (the excess zeros can be stripped by converting the image into itself with `qemu-img convert`, and the size of the deleted files in a EFI partition is negligible).

To replicate the ext4 partitions, the `clone/ext4` script mounts the partitions and calls `cp -a`. Can't do simpler than that.


To compare with `virt-sparsify`:
In exchange for requiring a script for every type of partition (ext4, fat,...), this script is very high level (the main script is under 100 lines, and the replicators can approach 10 lines each) and does not care about unneeded sectors.
From what i saw in the Ocaml source code of `virt-sparsify`, it scans the disk sectors to check which ones are used or not.


I intended to release a compressed minimal debian image with it (only 1.5G when uncompressed). It would have been more fun to say "this image has been recreated by itself", but this would have been overkill.



## Future goals

* Support bootable MBR partitions
* add replicator scripts for more partition formats (btrfs, fat, ext2/3,...)
(currently, the only optimized partition types are `swap` and `ext4`)
* Make this tool better known, and start addressing the crashes when ran incorrectly

## How to help

The easiest way to help is to simply use the tool, and report problems or improvements to do.

If you know your way around formatting and mounting partitions, you can also write your own duplication scripts to support more formats (any language can be used, since they are different programs. It should take under 30m for each one, and under 15m to test in a virtual machine).

If you are really dedicated, you could try to replicate a booting MBR disk and write the steps you followed (the script is just going to do the same automatically). I am not an expert of how low level BIOS boot works, so maybe there is something that is missing when replicating partitions.

I am not a git collaboration expert, so you will have to teach me how to accept pull/push requests if you want me to.


