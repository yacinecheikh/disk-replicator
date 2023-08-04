# Disk replicator

## Status

Very WIP, don't expect *anything* to work correctly.
Currently supported:
* MBR and GPT partition tables
* ext4 and swap partitions

I haven't found a way to make the cloned disk bootable
(I just know it can be done because i succeeded once by pure coincidence)

## Motivations

The main use is actually virtualization. This is just a better alternative to virt-sparsify

## How it works

The main script scans the partition table and partitions, and replicates them
The cloning scripts are used to clone specific partition layouts (ext4,...)

## Usage

`sudo python main.py /dev/{src} /dev/{dst}`


