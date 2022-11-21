---
layout: post
title: GRUB管理
date: 2019-09-11 12:00
tags: linux
categories: linux-basics 
---



GNU GRUB（GRand Unified Bootloader简称“GRUB”）是一个来自GNU项目的多操作系统启动程序。GRUB是多启动规范的实现，它允许用户可以在计算机内同时拥有多个操作系统，并在计算机启动时选择希望运行的操作系统。GRUB可用于选择操作系统分区上的不同内核，也可用于向这些内核传递启动参数。

在Centos7或者RHEL7中使用的是GRUB 2.02 版本（通常说GRUB2）。

# 1. GRUB2的基本原理

安装grub的时候基本原理就是将2个img文件放到指定的位置上。

- boot.img  放在MBR位置
- core.img  用于启动基础grub，并指向/boot和grub.cfg配置文件，放在MBR和第一个分区的夹缝中

当然，EFI的方式有所不同。



# 2. GRUB2常见管理

## 2.1 在cfg中增加一个条目

```bash
# 比如添加win7引导选项
menuentry 'Windows 7 (loader) (on /dev/sda1)' { 
insmod ntfs
set root=(hd0,1)
chainloader +1
}

# 添加一个winpe的选项
menuentry 'win7 pe' { 
kernel memdisk
initrd win7pe.iso  raw iso
}

```


## 2.2 重建grub2.cfg

grub2.cfg的位置可能两个：

```bash
# 有两个软连接分别对应他们
[root@bogon ~]# ls -l /etc/grub*
lrwxrwxrwx. 1 root root  22 Jul 28 11:58 /etc/grub2.cfg -> ../boot/grub2/grub.cfg
lrwxrwxrwx. 1 root root  31 Jul 28 11:59 /etc/grub2-efi.cfg -> ../boot/efi/EFI/centos/grub.cfg
```

因此，创建的时候可以按照下面的命令。创建过程中会重建cfg也会重建img文件。

```bash
grub2-mkconfig -o /etc/grub2.cfg
或者
grub2-mkconfg -o /boot/grub2/grub.cfg
```

## 2.3 重新安装grub

如果迁移了一个Linux到其他的服务器，因为sda的硬件信息发生变化，需要重新安装grub

```bash
# 重装grub
grub2-install /dev/sda
# 重新创建initramfs
dracut
dracut --force
```

# 3. reference

- [1] [GNU GRUB](https://www.gnu.org/software/grub/)
- [2] [LFS BOOK 8.4 systemd #6.60 GRUB-2.02]
- [3] [GNU GRUB Manual](https://www.gnu.org/software/grub/manual/grub/)
- [4] [grub2配置关键（三个核心变量prefix、root、cmdpath）和几点疑问](https://www.cnblogs.com/JMLiu/p/10318379.html)
