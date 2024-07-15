---
layout: post
title: 使用QEMU运行一个最小的Linux
date: 2024-07-10 00:00
tags: linux
categories: public
---


# 一、 使用QEMU运行一个最小的Linux

使用qemu运行一个Linux，可以直接使用qemu来加载内核，可以不使用bootloader。使用-kernel选项直接加载内核的bzImage，只需要直接下载一个vmlinz即可。

```bash
(py01) [frey@workpc:~]$ qemu-system-x86_64 --help |grep '\-kernel'
-kernel bzImage use 'bzImage' as kernel image
```

有了内核之后，需要一个initrd（或者initramfs,可以查看https://developer.aliyun.com/article/243822)，内核引导时需要的一个根文件系统（rootfs)，使用cpio创建。


```bash
$ cd build/initramfs && \
    find . -print0 \
    | cpio --null -ov --format=newc \
    | gzip -9 > ../initramfs.cpio.gz
```

initramfs中需要什么？ 一个busybox（https://www.busybox.net/about.html，The Swiss Army Knife of Embedded Linux）就够了，但需要稍微调整下。

总结一下，如下步骤：

## 1. 下载工具

使用测试环境是： WSL2-Fedora-40

```bash
(py01) [frey@workpc:minlinux]$ cat /etc/redhat-release
Fedora release 40 (Forty)
(py01) [frey@workpc:minlinux]$ uname -a
Linux workpc 5.15.153.1-microsoft-standard-WSL2 #1 SMP Fri Mar 29 23:14:13 UTC 2024 x86_64 GNU/Linux
```

下载安装工具包

```bash
(py01) [frey@workpc:minlinux]$ sudo dnf install qemu-system-x86 busybox
```

创建目录

```bash
(py01) [frey@workpc:testlinux]$ mkdir -p build/initramfs
```

busybox 必须是静态链接的，否则运行时缺少依赖共享库就很麻烦。

```bash
(py01) [frey@workpc:testlinux]$ file $(which busybox) 
/usr/sbin/busybox: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), statically linked, BuildID[sha1]=01a9de12c01550ce06a53f129a8cbcde53913361, stripped
(py01) [frey@workpc:testlinux]$ mkdir -p build/initramfs/bin/
(py01) [frey@workpc:testlinux]$ cp $(which busybox) build/initramfs/bin/
```

- fedora提供的busybox正好是静态编译的，或者从官网直接下载静态编译包

准备一个内核bzImage, 正常的Linux发行版可以在/boot目录找到。

```bash
# cp /boot/vmlinux-$(uname -r)  vmlinuz
```

在WSL下使用的内核不太一样，可以单独下载rpm包解压出来，参考命令如下：

```bash
# dnf download --downloaddir /tmp kernel-core
# rpm2cpio kernel-core*.rpm | cpio -div -D /tmp
# find /tmp -name vmlinuz -exec cp {} . \;
```


## 2. 制作initramfs


内核加载initramfs到内存后，会执行一个init文件，可以通过内核引导命令append来指定，比如：

```bash
(py01) [frey@workpc:minlinux]$ qemu-system-x86_64 --help |grep '\-append'
-append cmdline use 'cmdline' as kernel command line
```

在append后添加(参考https://www.jinbuguo.com/kernel/boot_parameters.html)，rdinit=全路径,设置从initramfs中运行的第一个用户空间程序的绝对路径，默认为"/init"。

我们直接制作一个init脚本，放在initramfs的/init位置上即可。

```bash
(py01) [frey@workpc:testlinux]$ echo #!/bin/busybox sh  > build/initramfs/init
(py01) [frey@workpc:testlinux]$ echo bin/busybox sh  >> build/initramfs/init
(py01) [frey@workpc:testlinux]$ chmod +x build/initramfs/init
```

- 需要添加`#!/bin/busybox sh`，否则无法直接执行该脚本
- 需要添加执行权限，否则无法执行


制作initramfs

```bash
(py01) [frey@workpc:testlinux]$ cd build/initramfs && \
                find . -print0 \
                | cpio --null -ov --format=newc \
                | gzip -9 > ../../initramfs.cpio.gz
(py01) [frey@workpc:testlinux]$ cd ../.. ; ls
build  initramfs.cpio.gz  vmlinuz
```

## 3. 启动

使用qemu启动这个最小的Linux

```bash
sudo qemu-system-x86_64 \
                -serial mon:stdio -nographic \
                -kernel vmlinuz \
                -initrd initramfs.cpio.gz \
                -machine accel=kvm:tcg \
                -append "console=ttyS0 quiet"
...
# 进入这个最小的Linux
sh: can't access tty; job control turned off
~ # /bin/busybox ls -l
total 4
drwxr-xr-x    2 1000     1000            60 Jul 10 02:37 bin
drwxr-xr-x    2 0        0               60 Jul 10 02:37 dev
-rwxr-xr-x    1 1000     1000            34 Jul 10 02:37 init
drwx------    2 0        0               40 Jul 10 02:37 root
```

- 使用串口输出，并不显示图形界面 
- kvm加速选项，会适当提高运行速度
- 执行console为ttyS0串口， quiet减少启动过程中的输出


# 二、完善一下

## 1. init文件比较简陋

- 为busybox创建链接，方便使用

```bash
BB=/bin/busybox
for cmd in $($BB --list);do
        $BB ln -s $BB /bin/$cmd
done
```

- 创建虚拟文件系统

```bash
mkdir /tmp  && mount -t tmpfs none /tmp
mkdir /proc && mount -t proc none /proc
mkdir /sys  && mount -t sysfs none /sys
```

- dev文件

```bash
mknod /dev/tty c 4 0
mknod /dev/null c 1 3
mknod /dev/zero c 1 5
mknod /dev/random c 1 8
mknod /dev/urandom c 1 9
```

## 2. initramfs是一个内存文件系统，更改不能持久化

- 使用disk.img模拟一个硬盘

```bash
dd if=/dev/zero of=build/disk.img bs=1M count=64
mkfs.ext2 build/disk.img
```

- 完善下rinit

```bash
mknod /dev/sda b 8 0
mkdir -p /newroot
mount -t ext2 /dev/sda /newroot/
cd /newroot/
exec switch_root . /sbin/init
```

- qemu启动脚本中添加disk选项

```bash
-drive format=raw,file=build/disk.img
```

## 3. 没有网络可以使用

使用e1000网卡驱动

```bash
sudo dnf dwonload --downloaddir /tmp  kernel-modules
rpm2cpio /tmp/kernel-modules*.rpm |cpio -div -D /tmp
find /tmp -name e1000.ko.xz -exec cp {} . \;
```

修改init文件

```bash
# load the e1000 drive and set nic
insmod /modules/e1000.ko.xz
ip l set lo up
ip l set eth0 up
ip a add 10.0.0.25/24 dev eth0
```

增加qemu启动选项，并提供网络启动脚本start-net.sh

```bash
-netdev tap,id=net0,script=start-net.sh  -device e1000,netdev=net0
```


# 三、参考

- [init](/lib/staticfile/minlinux/init): 内核挂载根文件系统后运行的第一个用户空间程序,默认为"/sbin/init"；
- [rdinit](/lib/staticfile/minlinux/rdinit): 设置从initramfs中运行的第一个用户空间程序的绝对路径，默认为"/init";  
- [Makefile](/lib/staticfile/minlinux/Makefile): Makefile
- [start-net.sh](/lib/staticfile/minlinux/start-net.sh): qemu 启动网卡脚本
- 参考 https://jyywiki.cn/OS/2024/lect18.md
