---
layout: post
title: Lustre学习笔记（6.1）- 维护Lustre
date: 2019-03-07 12:00
tags: lustre 
categories: public
typora-root-url: ..
---

## 1. 处理不活动的OSTs

挂载时排除不活动的OSTs：

```bash
# 在客户端挂载 或者挂载MDT的时候执行，多个OST的时候使用冒号分割
client# mount -o exclude=testfs-OST0000 -t lustre uml1:/testfs /mnt/testfs
# 激活不活动的OST，在client上执行
lctl --device 7 activate  # 貌似不行，不确定
```

## 2. 找到lustre文件系统中的节点

有时候需要找到系统中所有OST的名字：

```bash
# 方法1，在mgs上执行：
MGS# lctl get_param mgs.MGS.live.*  # 该命令会显示所有的mdt和ost，不激活的也会显示
# 方法2，在client上运行：
client# lfs osts   # 列举所有osts
client# lfs mdts   # 列举所有mdts
# 方法3，在mds上执行
mds:/root# lctl get_param lov.*-mdtlov.target_obd # 显示所有在线osts
```


## 3. 不以lustre服务的方式挂载服务器

如果使用MGT/MDT混合使用的情况下，当只需要挂载MGS而不挂载MDS时候：

```bash
mount -t lustre /dev/mdt_partition -o nosvc /mount_point
# 举个例子，testfs-MDT0000同时包含了mgt和mdt
$ mount -t lustre -L testfs-MDT0000 -o nosvc /mnt/test/mdt
```


## 4. 重建lustre配置日志

如果lustre系统配置日志处在文件系统不能挂载的状态，需要使用tunefs.lustre --writeconf来重建他们。执行了writeconf之后配置日志会被重建（文件系统相当于一个全新的文件系统），并保存在MGS上。
只能在下面两种情况下执行writeconf：
- The configuration logs are in a state where the file system cannot start
- A server NID is being changed

**writeconf配置会破坏部分配置，如ost 池信息和conf_param的调优配置，所以writeconf要谨慎使用。建议将ost池配置和conf_param做成执行脚本，在每次writeconf配置后执行配置脚本即可。另外，使用set_param -P执行的配置会被保留。**

配置日志可以使用命令导出：

```bash
mgs# lctl --device MGS llog_print fsname-client
mgs# lctl --device MGS llog_print fsname-MDT0000
mgs# lctl --device MGS llog_print fsname-OST0000
```

重建lustre文件系统配置日志步骤如下：
- 停止所有文件系统服务，umount client--mdt--ost，注意保留mgs启动状态；
- 保证所有的mdt和ost可连接，但是不挂载；
-  tunefs.lustre --writeconf 执行所有节点；
- 重新mount所有节点；

```bash
psh cn1 umount /fs00
psh io2 umount /fs00/mdt000
psh io3 umount /fs00/*
psh io4 umount /fs00/*
psh cn1,io1-io4 df -ht lustre 
psh io2 tunefs.lustre --writeconf mdtpool/mdt000
psh io3 tunefs.lustre --writeconf ost0pool/ost000
psh io3 tunefs.lustre --writeconf ost1pool/ost001
psh io4 tunefs.lustre --writeconf ost2pool/ost002
psh io3 tunefs.lustre --writeconf ost3pool/ost003
psh io4 tunefs.lustre --writeconf ost3pool/ost003
psh io2 mount.lustre mdtpool/mdt000 /fs00/mdt000
psh io3 mount.lustre ost0pool/ost000 /fs00/ost000
psh io3 mount.lustre ost1pool/ost001 /fs00/ost001
psh io4 mount.lustre ost2pool/ost002 /fs00/ost002
psh io4 mount.lustre ost3pool/ost003 /fs00/ost003
psh cn1 mount.lustre io1@tcp:/fs00 /fs00
```


## 5. 修改服务器的nid

在2.4版本之前，只能使用writeconf的方式来更改，但是2.4版本之后，新增了一个replace_nids 的命令帮助快速的修改服务器的nid。writeconf的方式仍然可用。


步骤如下：

- 按顺序umout所有服务

- 修改/etc/modprobe.d/lustre.conf或者使用lnetctl命令来修改nid；可以使用lctl list_nids来查看nid；

- 保证mgs服务启动状态；

- 使用下面的命令修改；



```bash

lctl replace_nids devicename nid1[,nid2,nid3 ...]
```



- 如果mgt和mdt是同一块盘的话，需要重新卸载mgt后重新挂载；



## 7. 新增一个mdt

额外的mdt可以增加到文件系统中：
- 增加文件系统中可以创建文件的数量；
- 增加元数据聚合性能；
- 隔离某些应用的元数据信息；

增加mdt的方法如下：
- 找到最大的mdt index

```bash
client$ lctl dl | grep mdc 
```

- 增加一个mdt

```bash
mds# mkfs.lustre --reformat --fsname=testfs --mdt --mgsnode=mgsnode --index 4 /dev/sdd
```

- 挂载mdt

```bash
mds# mount.lustre /dev/sdd /mnt/mdt4
```

- 根据需要创建子目录

```bash
client# lfs mkdir -i 3 /mnt/testfs/new_dir_on_mdt3  # 使用index=3的mdt
client# lfs mkdir -i 4 /mnt/testfs/new_dir_on_mdt4  # 使用mdt4
client# lfs mkdir -c 4 /mnt/testfs/new_directory_striped_across_4_mdts  # 创建一个4 mdt的条带化文件
```

## 8. 新增ost

为了保证性能的平衡，不建议在不同的OSS上设置不同的OST数量。

步骤：
- 创建ost并挂载

```bash
oss# mkfs.lustre --fsname=testfs --mgsnode=mds16@tcp0 --ost --index=12 /dev/sda
oss# mkdir -p /mnt/testfs/ost12
oss# mount -t lustre /dev/sda /mnt/testfs/ost12 
```

- 平衡ost的空闲空间

```bash
# 文件系统中新增ost后，新建的文件会自动写到新的ost上，
# 如果需要手动移动这些文件到指定的ost上可以使用lfs_migrate命令
client# lfs_migrate /mnt/lustre/dir # 移动/mnt/lustre/dir 这个目录的文件
# 找到/test目录下且test-OST0004上，并且大于4G的文件，移动到别的ost上
client# lfs find /test --ost test-OST0004 -size +4G | lfs_migrate -y 
```
