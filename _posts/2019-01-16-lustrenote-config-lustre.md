---
layout: post
title: Lustre学习笔记（4）-配置lustre
date: 2019-01-16 12:00
tags: lustre
categories: public
typora-root-url: ..

---


这个例子中使用3个lustre服务器节点，io1作为mgs/mds，io2和io3作为oss，cn1作为client。



![](/images/2019-01-16-lustrenote-config-lustre/config-lustre-top.png)




在此之前，需要完成：
- 在io1-io3这三个节点安装lustre-server相关的安装包；
- 在cn1节点安装lustre-client相关的安装包；
- 在4个节点上都配置好lnet（这个例子里将enp0s3配置为tcp0）；

当前四个节点的ip地址如下：

```bash
#node,ip,hostnames,otherinterfaces,comments,disable
"cn1","192.168.56.101",,,,
"io1","192.168.56.121",,,,
"io2","192.168.56.122",,,,
"io3","192.168.56.123",,,,
```

io1-io3三个节点上每个有一块20TB的磁盘/dev/sdb：

```bash
[root@xserver ~]# psh io1-io3 lsblk /dev/sdb 
io1: NAME MAJ:MIN RM SIZE RO TYPE MOUNTPOINT
io1: sdb 8:16 0 20G 0 disk 
io2: NAME MAJ:MIN RM SIZE RO TYPE MOUNTPOINT
io2: sdb 8:16 0 20G 0 disk 
io3: NAME MAJ:MIN RM SIZE RO TYPE MOUNTPOINT
io3: sdb 8:16 0 20G 0 disk 
```

### a.创建MGS/MDS：

使用mkfs.lustre直接创建格式化文件系统：

```bash
mkdir -p /lustre/mdt
mkfs.lustre --fsname=fs00 --mgs --mdt --index=0 \
--backfstype=zfs --reformat mdspool/mdt /dev/sdb 
mount.lustre mdspool/mdt /lustre/mdt/
```

也可以分成两步，先创建zpool，在进行mkfs.lustre格式化文件系统，下面的方式与上面方式等价：

```bash
mkdir -p /lustre/mdt
zpool create mdspool  /dev/sdb
mkfs.lustre --fsname=fs00 --mgs --mdt --index=0 \
--backfstype=zfs --reformat mdspool/mdt 
mount.lustre mdspool/mdt /lustre/mdt/
```

使用zpool&mkfs.lustre来创建MDS是推荐的方式，因为可以使用zpool命令来配置一些zfs的创建参数，提供更好的配置，如：

```
zpool create -O canmount=off -o multihost=on   -o cachefile=none mdspool /dev/sdb
```

### b.创建OSS

```bash
# io2
mkdir -p /lustre/ost0
mkfs.lustre --ost --reformat --fsname fs00 --index 0 \
--mgsnode 192.168.56.121@tcp0 --backfstype zfs osspool/ost0 /dev/sdb 
mount.lustre osspool/ost0 /lustre/ost0/
# io3
mkdir -p /lustre/ost1
mkfs.lustre --ost --reformat --fsname fs00 --index 1 \
--mgsnode 192.168.56.121@tcp0 --backfstype zfs osspool/ost1 /dev/sdb 
mount.lustre osspool/ost1 /lustre/ost1/
```


### c.挂载客户端

```bash
[root@cn1 ~]# mkdir -p /lustre/f00 
[root@cn1 ~]# mount.lustre 192.168.56.121@tcp0:/fs00 /lustre/f00/
[root@cn1 ~]# lctl dl
  0 UP mgc MGC192.168.56.121@tcp 2bce2de2-81ef-fdcb-be01-33f6e196b294 4
  1 UP lov fs00-clilov-ffff90523b0ed800 eefdc044-f295-1771-5ccc-b62a6ae5a6ec 3
  2 UP lmv fs00-clilmv-ffff90523b0ed800 eefdc044-f295-1771-5ccc-b62a6ae5a6ec 4
  3 UP mdc fs00-MDT0000-mdc-ffff90523b0ed800 eefdc044-f295-1771-5ccc-b62a6ae5a6ec 4
  4 UP osc fs00-OST0000-osc-ffff90523b0ed800 eefdc044-f295-1771-5ccc-b62a6ae5a6ec 4
  5 UP osc fs00-OST0001-osc-ffff90523b0ed800 eefdc044-f295-1771-5ccc-b62a6ae5a6ec 4
```