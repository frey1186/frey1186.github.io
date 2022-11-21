---
layout: post
title:  格式化和创建文件系统
date: 2019-08-25 12:00
tags: linux
categories: linux-basics 
typora-root-url: ..
---

上一节将磁盘分区之后，就可以创建需要的文件系统并挂载到合适的目录，然后就可以快乐地写入文件了。

# 1 `mkfs`

常见的文件系统类型有：`ext2`、`ext3`、`ext4`、`xfs`、`btrfs`、`fat`等等，一般也不会有什么特殊要求，`ext4`和`xfs`是不错的选择。

```bash
mkfs.ext4  /dev/sdb1
mkfs.xfs  /dev/sdb2
# 也可以写成，如果系统不支持xfs的话，就会报错。
mkfs -t xfs  /dev/sdb2
```

还有一些其他可能用到的选项

```bash
# 指定块大小，可以用1k,2k,4k
mkfs.ext4 -b 1k /dev/sdb1
```

# 2 `mount`

将一个文件系统挂载到指定的目录

```bash
mount /dev/sdb1 /mnt
```

可以使用-o选项指定一些特殊的参数

```bash
# 比如只读的方式挂载
mount -o ro /dev/sdb1 /mnt
# 挂载iso文件
mount -o loop,ro /iso_path.iso /mnt
```

# 3 `/etc/fstab`

需要开机自动挂载的话，需要编辑这个文件

```bash
# 最简单的方式
echo "/dev/sdb1 /mnt ext4 defaults 0 0 " >> /etc/fstab
# iso的开机自启动挂载方式
echo "/iso/path /mnt/cdrom iso9660 loop 0 0" >> /etc/fstab
# 或者echo "/iso/path /mnt/cdrom iso9660 defaults 0 0" >> /etc/fstab

# /etc/fstab
# 这个文件有六列，每列之间用空格或者tab区分
# 第一列：设备，可以用名称，UUID，或者label
# 第二列：挂载点，就是挂载的目录
# 第三列：文件系统类型，与mkfs -t的属性一致，除了swap
# 第四列：与mount -o 的选项一致
    # ro     #表示只读
    # ro，acl
    # loop
    # defaults # 默认使用这个
# 第五列：备份，0表示不备份，1表示使用工具备份
# 第六列：开机时fsck文件系统，0表示不检查，1表示第一个检查，一次类推
```

# 4 其他一些常用的命令和例子

## 4.1 其他一些命令

`lsblk`:用于列出所有可用块设备的信息，而且还能显示他们之间的依赖关系，但是它不会列出RAM盘的信息。

```bash
[root@localhost /]# lsblk -m /dev/sda
NAME             SIZE OWNER GROUP MODE
sda               20G root  disk  brw-rw----
├─sda1           200M root  disk  brw-rw----
├─sda2             1G root  disk  brw-rw----
└─sda3          18.8G root  disk  brw-rw----
  ├─centos-root 16.8G root  disk  brw-rw----
  └─centos-swap    2G root  disk  brw-rw----
```

`xfs_grow`：比如修改lv之后，需要用这个命令来扩展xfs的容量

```bash
xfs_grow /dev/mapper/vg00-lv00
```

`resize2fs`:增大或者收缩未加载的“ext2/ext3”文件系统的大小，一般用来增大

```bash
resize2fs  /dev/mapper/vg00-lv00
```

`fsck`:用于 检查与修复 Linux 档案系统，可以同时检查一个或多个 Linux 档案系统

```bash
fsck /dev/sdb1
```

## 4.2 一些例子

挂载一个光驱到指定目录

```bash
mount /dev/sr0 /mnt
```

挂载一个iso文件到指定目录

```bash
mount -o loop /iso/path.iso /mnt
```

增加系统的`swap`

```bash
mkswap /dev/sdb2
swapon /dev/sdb2
echo "/dev/sdb2 swap swap defaults 0 0">> /etc/fatab
```

迁移`/home`目录到一个文件系统

```bash
# 创建一个新的文件系统
mkfs.xfs /dev/sdb3
mount /dev/sdb3 /mnt/home
# 迁移/home文件到/mnt/home，需要确保没有人访问/home
cp -av /home/* /mnt/home/
# 修改 /etc/fstab
echo "/dev/sdb3 /home xfs defaults 0 0">> /etc/fstab
# 修改挂载点
umount /mnt/home
rm -rf /home/*
mount -a
```

# 参考

- [mount ,mkfs 工具详细说明](https://www.cnblogs.com/miaoxg/p/9312156.html)
- [Linux: 文件系统创建mkfs、挂载mount](https://blog.csdn.net/weixin_40001704/article/details/81592915)
- [man mount]()
- [man mkfs]()