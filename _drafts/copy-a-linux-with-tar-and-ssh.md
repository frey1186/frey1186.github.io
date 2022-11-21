使用 tar & ssh 迁移一个LinuxServer



# 0. 源端配置









# 1.配置目标端

为目标端LiveCD配置IP地址，确保能够使用ssh联通源端，这里源端IP是192.168.56.172，配置目标端IP为192.168.56.173。

```bash
-bash-4.2# ip a add 192.168.56.173/24 dev enp0s3
-bash-4.2# ip l set enp0s3 up
```

为目标端硬盘进行分区，与源端一致或者不一致，但要确保足够空间存放文件

```bash
# 源端分区
#[root@rh01 ~]# fdisk -l /dev/sda
#
#Disk /dev/sda: 8589 MB, 8589934592 bytes
#255 heads, 63 sectors/track, 1044 cylinders
#Units = cylinders of 16065 * 512 = 8225280 bytes
#Sector size (logical/physical): 512 bytes / 512 bytes
#I/O size (minimum/optimal): 512 bytes / 512 bytes
#Disk identifier: 0x00055866
#
#   Device Boot      Start         End      Blocks   Id  System
#/dev/sda1   *           1          26      204800   83  Linux
#/dev/sda2              26         157     1048576   82  Linux swap / Solaris
#/dev/sda3             157        1045     7134208   83  Linux

# 这里就直接分两个分区，一个swap，一个/
-bash-4.2# parted -s /dev/sda -- \
> mklabel msdos \
> mkpart primary 2048s 512M \
> mkpart primary 512M -1s

# 查看分区情况
-bash-4.2# parted -s /dev/sda print
Model: ATA VBOX HARDDISK (scsi)
Disk /dev/sda: 8590MB
Sector size (logical/physical): 512B/512B
Partition Table: msdos
Disk Flags: 

Number  Start   End     Size    Type     File system  标志
 1      1049kB  512MB   511MB   primary
 2      512MB   8590MB  8078MB  primary
```

创建目标端迁移的根文件系统/sysroot用于保存复制过来的文件，文件系统建议与源端系统保持一致，这样不需要对目标端进行过多的调整。

```bash
-bash-4.2# mkdir /sysroot
-bash-4.2# mkfs.ext4 /dev/sda2
-bash-4.2# mount /dev/sda2 /sysroot/
```

# 2. 开始复制

在目标端执行，根据提示输入密码，等待完成即可。

```bash
-bash-4.2# ssh 192.168.56.172 " \
> cd /;
> tar --exclude=/dev \
> --exclude=/lost+found \
> --exclude=/media \
> --exclude=/proc \
> --exclude=/srv \
> --exclude=/sys \
> -zcpf - / \
> " |tar -zxvpf - -C /sysroot
```



# 3. 调整一下

创建之前排除掉的几个目录

```bash
-bash-4.2# mkdir -p /sysroot/{dev,media,proc,srv,sys}
```

创建一些必要的设备

```bash
-bash-4.2# mknod -m 600 /sysroot/dev/console c 5 1
-bash-4.2# mknod -m 666 /sysroot/dev/null c 1 3
```

挂载一些虚拟文件系统

```bash
-bash-4.2# mount --bind /dev /sysroot/dev/
```

使用chroot切换到新系统

```bash
-bash-4.2# chroot /sysroot /bin/env -i HOME=/root/ PATH=/bin:/usr/bin:/sbin:/usr/sbin:/usr/local/bin /bin/bash --login +h
```

修改网卡配置，删除mac地址，或者根据实际MAC地址进行修改

```bash
vi /etc/sysconfig/network-scripts/ifcfg-eth0
```

重做`initrd.img`文件

```bash
mkinitrd /boot/intrd.img 2.6.18-308.el5
```

重建引导分区

```bash
grub-install /dev/sda
```





# 4.参考

- [Linux From Scratch](http://www.linuxfromscratch.org/lfs/downloads/stable/LFS-BOOK-8.2-NOCHUNKS.html)