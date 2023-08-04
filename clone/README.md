# Disk replicator

## Motivations

The main use is actually virtualization. This is just a better alternative to virt-sparsify

## How it works

The main script scans the partition table and partitions, and replicates them
The cloning scripts are used to clone specific partition layouts (ext4,...)

## Usage

`sudo python main.py /dev/{src} /dev/{dst}`
