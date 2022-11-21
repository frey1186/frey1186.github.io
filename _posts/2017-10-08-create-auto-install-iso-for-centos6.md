---
layout: post
title: 制作自动安装CentOS6的ISO镜像
date: 2017-10-08 12:00
author: felo
tags: centos
---


# 挂载并复制原iso

```bash
[root@c01 ~]# mount /dev/cdrom /mnt/
mount: block device /dev/sr0 is write-protected, mounting read-only
[root@c01 mnt]# mkdir /iso
[root@c01 mnt]# cd /
[root@c01 /]# cp -ar /mnt/ /iso/
```

# 修改kickstart配置文件

```bash
# 设置初始密码password:123456
[root@c01 ~]# grub-crypt
Password:
Retype password:
$6$SvoTbh/dPdmNvlh1$ijl7FTdZnAZyrBAEBdKGxR0jRidSlUAoQu6WHI1p5crn6CZKlj6EIVY8tn6dZ0xzbBJypqYnQieECM8S2mgK7/

[root@c01 mnt]# vi /iso/mnt/ks.cfg
[root@c01 mnt]# cat /iso/mnt/ks.cfg
#platform=x86, AMD64, or Intel EM64T
#version=DEVEL
# Firewall configuration
firewall --disabled
# Install OS instead of upgrade
install
# Use CDROM installation media
cdrom
# Root password 123456
rootpw --iscrypted $6$SvoTbh/dPdmNvlh1$ijl7FTdZnAZyrBAEBdKGxR0jRidSlUAoQu6WHI1p5crn6CZKlj6EIVY8tn6dZ0xzbBJypqYnQieECM8S2mgK7/
# System authorization information
auth  --useshadow  --passalgo=sha512
# Use graphical install
graphical
# System keyboard
keyboard us
# System language
lang en_US
# SELinux configuration
selinux --disabled
# Do not configure the X Window System
skipx
# Installation logging level
logging --level=info
# Reboot after installation
#reboot
# System timezone
timezone --isUtc Asia/Shanghai
# Network information
network  --bootproto=dhcp --device=eth0 --onboot=on
# System bootloader configuration
bootloader --location=mbr
# Clear the Master Boot Record
zerombr
# Partition clearing information
clearpart --all --initlabel
# Disk partitioning information
part /boot --asprimary --fstype="ext4" --ondisk=sda --size=200
part swap --asprimary --fstype="swap" --ondisk=sda --size=1024
part / --asprimary --fstype="ext4" --grow --ondisk=sda --size=1
reboot

```

# 修改isolinux.cfg

修改两个地方：
- 修改timeout 100
- 增加ks=cdrom:ks.cfg

```bash
[root@c01 mnt]# cat /iso/mnt/isolinux/isolinux.cfg
default vesamenu.c32
#prompt 1
timeout 100

...

label linux
  menu label ^Install or upgrade an existing system
  menu default
  kernel vmlinuz
  append initrd=initrd.img ks=cdrom:ks.cfg
```


# 开始创建iso
```bash
# 安装mkisofs
[root@c01 mnt]# yum -y install  mkisofs

[root@c01 mnt]# pwd
/iso/mnt
[root@c01 mnt]# mkisofs -o /root/Cent65_y.iso -V centos6 \
-b isolinux/isolinux.bin -c isolinux/boot.cat \
-no-emul-boot -boot-load-size 4 -boot-info-table -R -J -T -v .

...


[root@c01 mnt]# file /root/Cent65_y.iso
Cent65_yfl.iso: ISO 9660 CD-ROM filesystem data 'centos6' (bootable)
```

# 参考

 - [使用光盘iso实现Linux操作系统的自动安装部署](http://www.linuxidc.com/Linux/2017-02/140815.htm)
 - [KICKSTART无人值守安装](http://www.zyops.com/autoinstall-kickstart)