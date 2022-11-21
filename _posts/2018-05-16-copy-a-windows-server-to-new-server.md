---
layout: post
title: 使用ntfsclone迁移一个WindowsServer 
date: 2018-05-16 12:00
author: felo
tags: migrate
categories: public
typora-root-url: ..
---

## 1. 制作一个livecd

准备一个linux系统，如centos7

```bash
[root@localhost ~]# cat /etc/redhat-release
CentOS Linux release 7.4.1708 (Core)
[root@localhost ~]# uname -a
Linux localhost 3.10.0-693.el7.x86_64 #1 SMP Tue Aug 22 21:09:27 UTC 2017 x86_64 x86_64 x86_64 GNU/Linux
```

挂载光盘或者使用163源，安装一些包

```bash
[root@localhost ~]# yum install livecd-tools syslinux createrepo
```

准备一些ntfs工具包：`ntfsprogs`，如果是centos7需要安装下面两个包

```bash
ntfs-3g-2017.3.23-1.el7.x86_64.rpm  
ntfsprogs-2017.3.23-1.el7.x86_64.rpm
```

制作一个本地repo源

```bash
[root@localhost ~]# cd ntfstools/
[root@localhost ntfstools]# ls
ntfs-3g-2017.3.23-1.el7.x86_64.rpm  ntfsprogs-2017.3.23-1.el7.x86_64.rpm
[root@localhost ntfstools]# createrepo .
Spawning worker 0 with 2 pkgs
Workers Finished
Saving Primary metadata
Saving file lists metadata
Saving other metadata
Generating sqlite DBs
Sqlite DBs complete
```

准备一个ks配置文件

```bash
[root@localhost ~]# cat centos7-based-migration-livecd.cfg
lang en_US.UTF-8
keyboard us
timezone Asia/Shanghai
# 自定义root密码
rootpw root  
auth --useshadow --enablemd5
selinux --disabled
firewall --disabled
# 光盘 和ntfs工具的本地repo
repo --name="cdrom" --baseurl=file:///mnt  
repo --name="ntfsclone" --baseurl=file:///root/ntfstools

%packages
kernel
firewalld
bash
syslinux
passwd
perl
systemd
grub2
authconfig
coreutils
parted
ntfsprogs
openssh
openssh-clients
openssh-server
nmap-ncat
tar
e2fsprogs
xfsprogs
vim
dialog
%end
```

制作一个livecd

```bash
[root@localhost ~]# livecd-creator -c centos7-based-migration-livecd.cfg -f migration-livecd
```



## 2. 在源端服务器和目标端服务器启动这个livecd

源端操作系统，本次测试用的`2008r2`。

```bash
# 个人试过的可以成功迁移的系统有：
windows server 2008 r2
windows server 2012 r2
```

启动选择`livecd`即可

![](/images/copy-a-windows-server-to-new-server/livecd-start.PNG)

输入用户名和密码，这里是`root`/`root`

首先配置IP地址

```bash
# 为eth0配置ip
ip addr add 192.168.30.221/24 dev eth0
# 启动设备
ip link set eth0 up
```

同样的，在目标端设置IP地址为`192.168.30.222`，为了区别源端和目标端，可以配置不同的主机名

```bash
# 源端配置为WIN-SOURCE
-bash-4.2# hostname WIN-SOURCE
-bash-4.2# export PS1="\h-\w $"
WIN-SOURCE-~ $

# 目标端配置为WIN-TARGET
-bash-4.2# hostname WIN-TARGET
-bash-4.2# export PS1="\h-\w $"
WIN-TARGET-~ $
```



## 3. 在目标端分区

查看源端分区情况

```bash
WIN-SOURCE-~ $ fdisk -l /dev/vda
# 30G 的大小
# 两个分区，一个boot，一个c盘
Disk /dev/vda: 32.2 GB, 32212254720 bytes, 62914560 sectors
Units = sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disk label type: dos
Disk identifier: 0xda18373e

   Device Boot      Start         End      Blocks   Id  System
/dev/vda1   *        2048      206847      102400    7  HPFS/NTFS/exFAT
/dev/vda2          206848    62912511    31352832    7  HPFS/NTFS/exFAT

```

在目标端划分相同的分区

```bash
# 先查看一下
WIN-TARGET-~ $ fdisk -l /dev/vda

Disk /dev/vda: 107.4 GB, 107374182400 bytes, 209715200 sectors
Units = sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disk label type: dos
Disk identifier: 0x7723064b

# 100个G，分vda1一样分，其他的分成c盘，或者c盘分小一点，再加一个d盘
# 这里测试，就全部c盘啦
# fdisk 使用方法参见其他地方
# 注意 1.要将vda1设置为boot分区，fdisk的a选项
#     2. 要将两个分区的id都改为7，NTFS的格式，fdisk的t选项
# 就是要与源端分区一致
   Device Boot      Start         End      Blocks   Id  System
/dev/vda1   *        2048      206847      102400    7  HPFS/NTFS/exFAT
/dev/vda2          206848   209715199   104754176    7  HPFS/NTFS/exFAT
```



## 4. 将源端分区拷贝到目标端

拷贝方案，使用`ntfsclone`拷贝，使用`nc`工具传输，直接看命令。

先在目标端执行：

```bash
WIN-TARGET-~ $ nc -l 9999 | gunzip -c |ntfsclone --restore-image --overwrite /dev/vda1 -
ntfsclone v2017.3.23 (libntfs-3g)
# 这里会等待源端命令执行后才会开始
# 
Ntfsclone image version: 10.1
Cluster size           : 4096 bytes
Image volume size      : 104853504 bytes (105 MB)
Image device size      : 104857600 bytes
Space in use           : 26 MB (24.1%)
Offset to image data   : 56 (0x38) bytes
Restoring NTFS from image ...
100.00 percent completed
Syncing ...
WIN-TARGET-~ $ 
```

然后在源端执行：

```bash
WIN-SOURCE-~ $ ntfsclone --save-image --output - /dev/vda1 |gzip -c |nc 192.168.30.222 9999
ntfsclone v2017.3.23 (libntfs-3g)
NTFS volume version: 3.1
Cluster size       : 4096 bytes
Current volume size: 104853504 bytes (105 MB)
Current device size: 104853504 bytes (105 MB)
Scanning volume ...
100.00 percent completed
Accounting clusters ...
Space in use       : 26 MB (24.1%)
Saving NTFS to image ...
100.00 percent completed
Syncing ...
WIN-SOURCE-~ $ 
```

同样的，vda2使用相同的方法进行拷贝，注意先在目标端执行，再源端执行。

- `ntfsclone --save-image` 将ntfs文件系统保存为镜像文件，ntfsclone按照扇区的方式继续复制，只会复制使用到的空间；
- `ntfsclone --restore-image` 将ntfs文件系统从镜像文件恢复到一个新的ntfs文件系统中；
- `gunzip -c`和`gzip -c` 表示压缩和解压缩；
- `nc -l 9999`  在9999号端口监听；
- `nc 192.168.30.222 9999` 将数据发送给到这个主机的9999端口。



## 5. 为目标端增加MBR引导代码

迁移完成ntfs文件系统后，其实目标端的硬盘中虽然有源端系统所有数据，但是并不能直接启动，会卡在“Booting from Hard disk...”，需要为目标端硬盘增加引导程序。

查看目标端mbr

```bash
# 将mbr导出
WIN-TARGET-~ $ dd if=/dev/vda of=mbr.hex bs=512 count=1
# 使用hexdump查看
WIN-TARGET-~ $ hexdump mbr.hex
0000000 0000 0000 0000 0000 0000 0000 0000 0000
*
00001b0 0000 0000 0000 0000 064b 7723 0000 0080
00001c0 0221 0307 cd13 0800 0000 2000 0003 0300
00001d0 cd14 0c07 b22c 2800 0003 d800 0c7c 0000
00001e0 0000 0000 0000 0000 0000 0000 0000 0000
00001f0 0000 0000 0000 0000 0000 0000 0000 aa55
0000200
# 前面有一段都是0，分区表和结束符都在，没有引导程序
```

查看源端mbr

```bash
WIN-SOURCE-~ $ dd if=/dev/vda of=mbr.hex bs=512 count=1
1+0 records in
1+0 records out
512 bytes (512 B) copied, 0.00245738 s, 208 kB/s
WIN-SOURCE-~ $ hexdump -C mbr.hex
00000000  33 c0 8e d0 bc 00 7c 8e  c0 8e d8 be 00 7c bf 00  |3.....|......|..|
00000010  06 b9 00 02 fc f3 a4 50  68 1c 06 cb fb b9 04 00  |.......Ph.......|
00000020  bd be 07 80 7e 00 00 7c  0b 0f 85 0e 01 83 c5 10  |....~..|........|
00000030  e2 f1 cd 18 88 56 00 55  c6 46 11 05 c6 46 10 00  |.....V.U.F...F..|
00000040  b4 41 bb aa 55 cd 13 5d  72 0f 81 fb 55 aa 75 09  |.A..U..]r...U.u.|
00000050  f7 c1 01 00 74 03 fe 46  10 66 60 80 7e 10 00 74  |....t..F.f`.~..t|
00000060  26 66 68 00 00 00 00 66  ff 76 08 68 00 00 68 00  |&fh....f.v.h..h.|
00000070  7c 68 01 00 68 10 00 b4  42 8a 56 00 8b f4 cd 13  ||h..h...B.V.....|
00000080  9f 83 c4 10 9e eb 14 b8  01 02 bb 00 7c 8a 56 00  |............|.V.|
00000090  8a 76 01 8a 4e 02 8a 6e  03 cd 13 66 61 73 1c fe  |.v..N..n...fas..|
000000a0  4e 11 75 0c 80 7e 00 80  0f 84 8a 00 b2 80 eb 84  |N.u..~..........|
000000b0  55 32 e4 8a 56 00 cd 13  5d eb 9e 81 3e fe 7d 55  |U2..V...]...>.}U|
000000c0  aa 75 6e ff 76 00 e8 8d  00 75 17 fa b0 d1 e6 64  |.un.v....u.....d|
000000d0  e8 83 00 b0 df e6 60 e8  7c 00 b0 ff e6 64 e8 75  |......`.|....d.u|
000000e0  00 fb b8 00 bb cd 1a 66  23 c0 75 3b 66 81 fb 54  |.......f#.u;f..T|
000000f0  43 50 41 75 32 81 f9 02  01 72 2c 66 68 07 bb 00  |CPAu2....r,fh...|
00000100  00 66 68 00 02 00 00 66  68 08 00 00 00 66 53 66  |.fh....fh....fSf|
00000110  53 66 55 66 68 00 00 00  00 66 68 00 7c 00 00 66  |SfUfh....fh.|..f|
00000120  61 68 00 00 07 cd 1a 5a  32 f6 ea 00 7c 00 00 cd  |ah.....Z2...|...|
00000130  18 a0 b7 07 eb 08 a0 b6  07 eb 03 a0 b5 07 32 e4  |..............2.|
00000140  05 00 07 8b f0 ac 3c 00  74 09 bb 07 00 b4 0e cd  |......<.t.......|
00000150  10 eb f2 f4 eb fd 2b c9  e4 64 eb 00 24 02 e0 f8  |......+..d..$...|
00000160  24 02 c3 49 6e 76 61 6c  69 64 20 70 61 72 74 69  |$..Invalid parti|
00000170  74 69 6f 6e 20 74 61 62  6c 65 00 45 72 72 6f 72  |tion table.Error|
00000180  20 6c 6f 61 64 69 6e 67  20 6f 70 65 72 61 74 69  | loading operati|
00000190  6e 67 20 73 79 73 74 65  6d 00 4d 69 73 73 69 6e  |ng system.Missin|
000001a0  67 20 6f 70 65 72 61 74  69 6e 67 20 73 79 73 74  |g operating syst|
000001b0  65 6d 00 00 00 63 7b 9a  3e 37 18 da 00 00 80 20  |em...c{.>7..... |
000001c0  21 00 07 df 13 0c 00 08  00 00 00 20 03 00 00 df  |!.......... ....|
000001d0  14 0c 07 fe ff ff 00 28  03 00 00 d0 bc 03 00 00  |.......(........|
000001e0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
000001f0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 55 aa  |..............U.|
00000200
```

将源端的引导程序拷贝到目标端即可，引导代码长度为440字节，加上磁盘签名4个字节。

> MBR扇区由以下四部分组成：
>
> - 引导代码：引导代码占MBR分区的前440字节，负责整个系统启动。如果引导代码被破坏，系统将无法启动。
> - Windows磁盘签名：占引导代码后面的4字节，是Windows初始化磁盘写入的磁盘标签，如果此标签被破坏，则系统会提示“初始化磁盘”。
> - MBR分区表：占Windows磁盘标签后面的64个字节，是整个硬盘的分区表。
> - MBR结束标志：占MBR扇区最后2个字节，一直为“55 AA”。

在源端执行：

```bash
WIN-SOURCE-~ $ dd if=/dev/vda of=boot.hex bs=444 count=1
1+0 records in
1+0 records out
440 bytes (440 B) copied, 0.00369655 s, 119 kB/s
WIN-SOURCE-~ $ scp boot.hex root@192.168.30.222:/root/
root@192.168.30.222's password:
boot.hex                                                                                                                                    100%  440   843.3KB/s   00:00
```

目标端覆盖到vda中：

```bash
WIN-TARGET-~ $ ls
boot.hex  mbr.hex
WIN-TARGET-~ $ dd if=boot.hex of=/dev/vda
0+1 records in
0+1 records out
440 bytes (440 B) copied, 0.054984 s, 8.0 kB/s
```

重启目标端服务器，首次启动会比较慢。

其实在整个迁移中最关键的驱动问题，如果迁移的操作系统中没有目标服务器的硬盘驱动的话，就会不能启动。
- 如果目标系统与源系统硬件环境一致就不存在问题；
- 目标是虚拟机，可以修改为IDE模式；


## 参考

- [Transfer Windows to New Hard Disk using ntfsclone](http://edoceo.com/exemplar/ntfsclone-transfer-windows)
- [ntfsclone man page](https://linux.die.net/man/8/ntfsclone)
- [netcat](http://man.linuxde.net/nc_netcat)
- [nc man page](https://linux.die.net/man/1/nc)
