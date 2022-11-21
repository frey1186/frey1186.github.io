

## live linux Install ntfsprogs

```bash
# for RHEL 6
yum install ftp://ftp.pbone.net/mirror/ftp5.gwdg.de/pub/opensuse/repositories/Virtualization:/Appliances/RedHat_RHEL-6/x86_64/libx86emu1-1.5-1.1.x86_64.rpm

yum install ftp://ftp.pbone.net/mirror/ftp.pramberger.at/systems/linux/contrib/rhel6/x86_64/libhd-20.1-1.el6.pp.x86_64.rpm

yum install ftp://ftp.pbone.net/mirror/ftp.pramberger.at/systems/linux/contrib/rhel6/x86_64/ntfs-3g-libs-2017.3.23-1.el6.pp.x86_64.rpm

yum install ftp://ftp.icm.edu.pl/vol/rzm8/linux-fedora/linux/epel/6/x86_64/Packages/n/ntfsprogs-2017.3.23-1.el6.x86_64.rpm


# for rhel 7 
ntfs-3g-2017.3.23-1.el7.x86_64.rpm  
ntfsprogs-2017.3.23-1.el7.x86_64.rpm
```



Here's how we transfer or clone Windows from one hard disk to another. This process should work for transferring any NTFS based filesystem, bootable or not.

## Preparation

The following equipment and tools are necessary to perform this task.

- Existing Windows System/NTFS File System
- Intermediate Storage Location
- New Hard Disk, same or larger size
- A copy of [SystemRescueCd](http://www.sysresccd.org/) or other suitable Live Linux

## Prepare the Windows System

Not much here, make sure the machine is stable and does have any updates pending. Run a Windows disk check (`chkdsk /f`) and reboot the system twice. When the boot process is verified clean reboot and start up from the SystemRescueCd.

## Backup the Partition Information

Using `sfdisk` we can dump to a reasonable format that we can feed back to sfdisk when restoring.

```
# sfdisk -d /dev/sda > /mnt/storage/sda.ptab
```

## Backup the BootSector/MBR

Some guides show only taking the first 512 bytes ([MBR](http://en.wikipedia.org/wiki/Master_boot_record)), others show the first 63 blocks (MBR + Bootloader).

```
# dd if=/dev/sda of=/mnt/storage/sda.mbr bs=512 count=1
# dd if=/dev/sda of=/mnt/storage/sda.vbr bs=512 count=63
```

查看MBR

```bash
[root@networkerserver ~]# which hexdump
/usr/bin/hexdump
[root@networkerserver ~]# rpm -qf /usr/bin/hexdump 
util-linux-ng-2.17.2-12.28.el6.x86_64
[root@networkerserver ~]# hexdump -C mbr.hex 
00000000  eb 48 90 10 8e d0 bc 00  b0 b8 00 00 8e d8 8e c0  |.H..............|
00000010  fb be 00 7c bf 00 06 b9  00 02 f3 a4 ea 21 06 00  |...|.........!..|
00000020  00 be be 07 38 04 75 0b  83 c6 10 81 fe fe 07 75  |....8.u........u|
00000030  f3 eb 16 b4 02 b0 01 bb  00 7c b2 80 8a 74 03 02  |.........|...t..|
00000040  80 00 00 80 fe 49 08 00  00 08 fa 90 90 f6 c2 80  |.....I..........|
00000050  75 02 b2 80 ea 59 7c 00  00 31 c0 8e d8 8e d0 bc  |u....Y|..1......|
00000060  00 20 fb a0 40 7c 3c ff  74 02 88 c2 52 f6 c2 80  |. ..@|<.t...R...|
00000070  74 54 b4 41 bb aa 55 cd  13 5a 52 72 49 81 fb 55  |tT.A..U..ZRrI..U|
00000080  aa 75 43 a0 41 7c 84 c0  75 05 83 e1 01 74 37 66  |.uC.A|..u....t7f|
00000090  8b 4c 10 be 05 7c c6 44  ff 01 66 8b 1e 44 7c c7  |.L...|.D..f..D|.|
000000a0  04 10 00 c7 44 02 01 00  66 89 5c 08 c7 44 06 00  |....D...f.\..D..|
000000b0  70 66 31 c0 89 44 04 66  89 44 0c b4 42 cd 13 72  |pf1..D.f.D..B..r|
000000c0  05 bb 00 70 eb 7d b4 08  cd 13 73 0a f6 c2 80 0f  |...p.}....s.....|
000000d0  84 f0 00 e9 8d 00 be 05  7c c6 44 ff 00 66 31 c0  |........|.D..f1.|
000000e0  88 f0 40 66 89 44 04 31  d2 88 ca c1 e2 02 88 e8  |..@f.D.1........|
000000f0  88 f4 40 89 44 08 31 c0  88 d0 c0 e8 02 66 89 04  |..@.D.1......f..|
00000100  66 a1 44 7c 66 31 d2 66  f7 34 88 54 0a 66 31 d2  |f.D|f1.f.4.T.f1.|
00000110  66 f7 74 04 88 54 0b 89  44 0c 3b 44 08 7d 3c 8a  |f.t..T..D.;D.}<.|
00000120  54 0d c0 e2 06 8a 4c 0a  fe c1 08 d1 8a 6c 0c 5a  |T.....L......l.Z|
00000130  8a 74 0b bb 00 70 8e c3  31 db b8 01 02 cd 13 72  |.t...p..1......r|
00000140  2a 8c c3 8e 06 48 7c 60  1e b9 00 01 8e db 31 f6  |*....H|`......1.|
00000150  31 ff fc f3 a5 1f 61 ff  26 42 7c be 7f 7d e8 40  |1.....a.&B|..}.@|
00000160  00 eb 0e be 84 7d e8 38  00 eb 06 be 8e 7d e8 30  |.....}.8.....}.0|
00000170  00 be 93 7d e8 2a 00 eb  fe 47 52 55 42 20 00 47  |...}.*...GRUB .G|
00000180  65 6f 6d 00 48 61 72 64  20 44 69 73 6b 00 52 65  |eom.Hard Disk.Re|
00000190  61 64 00 20 45 72 72 6f  72 00 bb 01 00 b4 0e cd  |ad. Error.......|
000001a0  10 ac 3c 00 75 f4 c3 00  00 00 00 00 00 00 00 00  |..<.u...........|
000001b0  00 00 00 00 00 00 00 00  11 e6 02 00 00 00 80 20  |............... |  # 80 20 开始分区表
000001c0  21 00 83 dd 1e 3f 00 08  00 00 00 a0 0f 00 00 dd  |!....?..........|
000001d0  1f 3f 8e fe ff ff 00 a8  0f 00 00 58 70 0c 00 00  |.?.........Xp...|
000001e0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
000001f0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 55 aa  |..............U.| # 55 aa 结束标志
00000200
```



## Create FileSystem Copy

SystemRescueCd should boot directly to a shell, we will dump the file system and power off.

There are many ways to store the file system image, not covered here. The `ntfsclone` tool does not care. We have sucessfully created images on external USB drives (ext3), over Samba shares (to NTFS & Samba 3), GlusterFS (reiser,ext4) and others. Just ensure capacity is available and the FS supports large files.

In the example the Windows system is installed to */dev/sda1*. The image storage location is mounted, through whatever means necessary, at */mnt/storage*. Adjust parameters as necessary for the environment.

Examine the disk before starting, take note of the *Space in use* value. The image created by `ntfsclone` will be slightly larger ( ~2%).

```
# ntfsresize --info /dev/sda1
ntfsresize v2.0.0 (libntfs 10:0:0)
Device name        : /dev/sda1
NTFS volume version: 3.1
Cluster size       : 4096 bytes
Current volume size: 25802666496 bytes (25803 MB)
Current device size: 25802671104 bytes (25803 MB)
Checking filesystem consistency ...
100.00 percent completed
Accounting clusters ...
Space in use       : 10949 MB (42.4%)
Collecting resizing constraints ...
You might resize at 10948591616 bytes or 10949 MB (freeing 14854 MB).
Please make a test run using both the -n and -s options before real resizing!
```

If `ntfsresize` complains follow it's request to run `chkdsk /f` and try again. The clone should only be created from a dirty file system in emergencies.

```
# ntfsclone --save-image --output /mnt/storage/windows.ntfsclone /dev/sda1
ntfsclone v2.0.0 (libntfs 10:0:0)
NTFS volume version: 3.1
Cluster size       : 4096 bytes
Current volume size: 25802666496 bytes (25803 MB)
Current device size: 25802671104 bytes (25803 MB)
Scanning volume ...
100.00 percent completed
Accounting clusters ...
Space in use       : 10949 MB (42.4)
Saving NTFS to image ...
100.00 percent completed
```

If the disk is in really bad shape the following incantations may help:

```
ntfsclone --save-image --rescue --output /mnt/storage/windows.ntfsclone /dev/sda1
ntfsclone --save-image --ignore-fs-check --rescue --output /mnt/storage/windows.ntfsclone /dev/sda1
ntfsclone --save-image --force --ignore-fs-check --rescue --output \
  /mnt/storage/windows.ntfsclone /dev/sda1
```

After creating the clone, poweroff the system and replace the current HDD with the new disk.

## Restoring Windows Image

Use cfdisk to partition, use ntfsclone to restore the image, then ntfsresize to resize to larger volume.

Many tools can partition, such as `fdisk` or `cfdisk` or which ever. Using any of these tools create a partition on the new disk similar to the original disk. In this example the original disk was replaced with one twice the size.

Cfdisk was used to create a partition (/dev/sda1) that was 50GiB in size and then the type was set to 0x07 (NTFS) and flagged as bootable. Do not format the partition with a file-system, leave it empty.

```
# ntfsclone --restore-image --overwrite /dev/sda1 /mnt/storage/windows.ntfsclone
ntfsclone v2.0.0 (libntfs 10:0:0)
Ntfsclone image version: 10.0
Cluster size           : 4096 bytes
Image volume size      : 25802666496 bytes (25803 MB)
Image device size      : 25802671104 bytes (25803 MB)
Space in use           : 10949 MB (42.4%)
Offset to image data   : 56 (0x38) bytes
Restoring NTFS from image ...
100.00 percent completed
```

Now reboot the system, Windows will run a file-system check and all should be well. It may be a good idea to start in Safe Mode (press F8 during startup)

We have successfully use this process to archive an 80GiB /dev/sda2 Windows (/dev/sda1 was recovery partition from Dell) to /dev/sda1 on a new disk (120GiB).

Moving NTFS volumes around is a dangerous game, care should be taken. Ensure backups are available, cross fingers, etc.

## ntfsclone direct disk to disk [§](http://edoceo.com/exemplar/ntfsclone-transfer-windows#disk2disk)

It's also possible, and very useful, to directly clone one disk to another, i.e. replacing a failing disk. It an ideal world this new disk would be identical, to minimize the possibility of Windows having a fit. But even if not identical, we can make it happen.

### Clone Identical Disks

In this example /dev/sdb is the old disk, /dev/sda is the new one, I've booted from a CD. We create the target partition, run clone|clone

If they disk are identical then manually create a similar partition table and just use dd

```
sfdisk -d /dev/sdb | sfdisk --force /dev/sda
sfdisk --re-read /dev/sda
dd if=/dev/sdb1 of=/dev/sda1
```

### Clone to Smaller Disk

If not identical then ntfsclone comes in, this allows us to copy differently sized NTFS partitions. Here, /dev/sdb3 is the source partition (160G) from our old dual-boot disk and /dev/sda3 is the smaller sized target (128G). First, shrink the old NTFS to less than the limit, clone, then resize new NTFS to fill the partition.

```
ntfsresize --size 120G /dev/sdb3
ntfsclone \
    --force \
    --overwrite /dev/sda3 \
    /dev/sdb3
# Boot the Window Here and chkdsk
ntfsresize --size MAX /dev/sda3
```

Note that it's not wise to try to move the partitions around on Windows. That is, don't clone from /dev/sdb3 to /dev/sda2 or other such, Windows is very sensitive to those changes and will likely blue-screen on you. It's a STOP 0x0000007B, inaccessible boot device.