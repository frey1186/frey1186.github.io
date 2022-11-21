---

layout: post
title: Lustre学习笔记（5）-操作Lustre
date: 2019-03-01 12:00
tags: lustre 
categories: public
typora-root-url: ..
---


## 1.mount by label 

lustre文件系统的fsname不能超过8个字符，挂载文件系统的时候可以使用label，这就允许管理员任意移动磁盘位置而且不用担心/dev/short_name错误。当前情况下linux的disk label最长16个字符，所以在标识文件系统存储目标的时候一般采用：**8个字符文件系统名称-7个字符存储目标名称**，如：

```bash
fsname-MDT0000
fsname-OSTa018
```

挂载方法如下：

```bash
mount -t lustre -L testfs-MDT0000 /mnt/mdt
```

注意：
- 不适用于多路径存储环境
- fsname有长度限制，但是客户端挂载点的长度无所谓。
```bash
client# mount -t lustre mds0@tcp0:/short  /dev/long_mountpoint_name
```

## 2.启动Lustre

首次启动顺序：MGT--MDT--OST--Client
以后启动顺序：MGT--OST--MDT--Client

## 3.挂载一个服务器

可以将挂载的配置编写在 /etc/fstab文件中，通过mount -t lustre命令可以查看挂载情况，
- 在HA环境中一般不建议自动挂载lustre服务器；
- 自动挂载需要确保网络服务在此之前启动，rhel环境下在fstab文件中参数要求添加：_netdev 即可；
```bash
# 如下：/etc/fstab
LABEL=testfs-OST0000 /mnt/test/ost0 lustre defaults,_netdev,noauto 0 0
```
- 不要将oss和client都部署在一台机器上，容易导致死锁；
- Mount-by-label 不适用于多路径环境；

## 4.停止文件系统

一个完整的停止过程需要停止所有的client和server。顺序为：Client--MDT&MGT--OSS
```bash
# 卸载所有lustre类型的文件系统挂载点
umount -a -t lustre
```

## 5.指定卸载一个存储目标

```bash
umount /mnt/ost0
```

- 正常方式卸载会保存客户端的连接信息，下次挂载的时候会等待客户端连接，并开始还原IO操作；
- 如果使用`-f`标签，强制停止客户端连接并`WITHOUT recovery`，启动后所有的当前连接客户端将会返回一个IO错误；

## 6.为ost指定failout/failover模式

当一个ost发生错误导致不能访问，有两种方法：
- failout模式：客户端不等待ost恢复直接在超时后返回io错误；
- failover模式：客户端等待ost恢复，系统默认使用此模式；

创建fs的时候采用：
```bash
oss# mkfs.lustre --fsname=fsname \
--mgsnode=mgs_NID \
--param=failover.mode=failout  \ # 在这里指定
--ost --index=ost_index  \
/dev/ost_block_device
```
- 也可以用tunefs.lustre修改属性，但是要在umount的情况下执行

## 7.处理降级的RAID组成的OST

如果OST由一套RAID阵列组成，但是RAID中的某个磁盘发生故障，那么不建议再想该RAID中写入新的数据，所以需要将该OST进行降级处理。原因如下：
- RAID中有磁盘损坏会导致性能降低；
- 如果更换磁盘后，需要进行数据同步；
- 如果没有更换磁盘，数据安全性降低；
针对这种情况，需要将该OST标记为降级的（degraded）：
```bash
# 设置降级参数
lctl set_param obdfilter.{OST_name}.degraded=1  # 1为降级的，0为正常状态
# 查看降级参数
lctl get_param obdfilter.*.degraded
```
- ost被重新挂载后该参数会自动被还原为0
- 强烈建议将此功能部署成为自动执行脚本，监控raid的状态来设置和还原这个参数；

## 8.运行多个lustre文件系统

lustre支持多个文件系统，通过NID:fsname来区分，在使用同一个MGS的情况下，每个文件系统必须使用不同的名称。lustre支持在同一个MGS的情况下，创建多个lustre文件系统。

- 默认在mkfs.lustre命令中，fsname默认名称为lustre
- MDT和OST名称必须与fsname相关，如：fsname-MDT0000
- **如果一个Client挂载了多个文件系统，需要在/etc/xattr.conf 文件中添加参数，避免两个文件系统之间移动文件时产生问题：**
```bash
# /etc/xattr.conf 文件中添加
lustre.* skip
```
- 两个文件系统可以使用一个MGS的NID，但是MDS和OSS必须是不同的服务器；

```bash
mgsnode# mkfs.lustre --mgs /dev/sda
mdtfoonode# mkfs.lustre --fsname=foo --mgsnode=mgsnode@tcp0 --mdt --index=0 /dev/sdb
ossfoonode# mkfs.lustre --fsname=foo --mgsnode=mgsnode@tcp0 --ost --index=0 /dev/sda
ossfoonode# mkfs.lustre --fsname=foo --mgsnode=mgsnode@tcp0 --ost --index=1 /dev/sdb
mdtbarnode# mkfs.lustre --fsname=bar --mgsnode=mgsnode@tcp0 --mdt --index=0 /dev/sda
ossbarnode# mkfs.lustre --fsname=bar --mgsnode=mgsnode@tcp0 --ost --index=0 /dev/sdc
ossbarnode# mkfs.lustre --fsname=bar --mgsnode=mgsnode@tcp0 --ost --index=1 /dev/sdd
client# mount -t lustre mgsnode@tcp0:/foo /mnt/foo
client# mount -t lustre mgsnode@tcp0:/bar /mnt/bar
```

## 9.让子目录使用特定的MDT
lustre2.4版本以后，可以为某个子目录指定一个单独的MDT，命令如下：

```bash
client# lfs mkdir –i mdt_index /mount_point/remote_dir
```

- -i后面跟mdt的index标签；
- 这个子目录的父目录需要使用MDT0作为元数据存储目标，因为父目录所在MDT失败后会导致子目录的命名空间都出现问题，因此使用都使用MDT0；
- 为了打破这个限制，让所有MDT都可以在创建这种远程子目录，需要调整参数：

```bash
# 在mgs上调整：
mgs# lctl conf_param fsname.mdt.enable_remote_dir=1

# 在mds上查看
mds# lctl get_param mdt.*.enable_remote_dir
```

- 到2.8版本以后，可以指定特殊的组来创建、删除远程子目录，参数为：enable_remote_dir_gid

```
# mgs上设置，设置为-1表示所有非root组都可以
mgs# lctl conf_param fsname.mdt.enable_remote_dir_gid=-1
# mds上查看
mds# lctl get_param mdt.*.enable_remote_dir_gid
```

## 10. 创建一个分布在多个mdt上的目录

单个目录设置元数据分布在多个MDT上，可以提高性能，特别是针对5万个条目以上的目录。命令如下：

```bash
client# lfs mkdir -c mdt_count /mount_point/new_directory
```

## 11. 设置和查看lustre参数

- 使用mkfs.lustre设置

```bash
# 设置超时时间为50
mds# mkfs.lustre --mdt --param="sys.timeout=50" /dev/sda
```

- 使用tunefs.lustre设置

```bash
# 在服务停止的情况下，可以使用tunefs.lustre来调整参数
oss# tunefs.lustre --param=failover.node=192.168.0.13@tcp0 /dev/sda
# 添加 --erase-params 指的是擦除所有参数重新指定
# tunefs.lustre可以配置lctl conf_param 配置的所有参数；
```

- 使用lctl配置

```bash
# 使用 lctl set_param 设置临时参数
# 使用  lctl set_param -P or lctl conf_param 设置永久参数，注意lctl conf_param命令需要在mgs上设置
mgs# lctl conf_param testfs-MDT0000.sys.timeout=40
```

- 使用 lctl list_param 查看参数

```bash
oss# lctl list_param obdfilter.lustre-OST0000 
```

- 使用lctl get_param 报告参数当前值

```bash
oss# lctl get_param -n ost.*.ost_io.timeouts
```

## 12. 指定NID和故障转移

有两中类型：
- 一个节点有多个网卡，那么就有多个nid，指定的时候都写在里面，然后用逗号分割；
- 一对HA集群内的节点，两个nid之间用冒号分割，或者使用--mgsnode=/--servicenode=来指定；

列举一个主机上的所有nid

```bash
lctl list_nids
```

下面一个简单的例子，mds0和mds1一对，oss0和oss1一对：

```bash
mds0# mkfs.lustre --fsname=testfs --mdt --mgs \
        --servicenode=192.168.10.2@tcp0 \
        --servicenode=192.168.10.1@tcp0 \ 
    /dev/sda1
mds0# mount -t lustre /dev/sda1 /mnt/test/mdt
oss0# mkfs.lustre --fsname=testfs --servicenode=192.168.10.20@tcp0 \
        --servicenode=192.168.10.21 --ost --index=0 \
        --mgsnode=192.168.10.1@tcp0 --mgsnode=192.168.10.2@tcp0 \  # 配置两个mgsnode
        /dev/sdb
oss0# mount -t lustre /dev/sdb /mnt/test/ost0
client# mount -t lustre 192.168.10.1@tcp0:192.168.10.2@tcp0:/testfs \  # 将两个mgsnode都配置，中间用冒号分割
        /mnt/testfs
mds0# umount /mnt/mdt
mds1# mount -t lustre /dev/sda1 /mnt/test/mdt
mds1# lctl get_param mdt.testfs-MDT0000.recovery_status
```

- 使用逗号分割，lustre会选择这个节点中的最优nid进行连接；
- 使用冒号分割，lustre会按顺序尝试连接，直到连接成功为止；

## 13.擦除一个文件系统

一般情况下使用 `--reformat`即可。

```bash
$ "mkfs.lustre --reformat"
# 如果mgs没有重新格式化，只对mdt进行格式化的话，需要使用--writeconf将配置更新到mgs上
$ mkfs.lustre --reformat --writeconf --fsname spfs --mgsnode=mgs_nid --mdt --index=0  /dev/mds_device
```

## 14. 回收保留空间

使用ldiskfs格式化存储目标的时候，会默认保留5%的空间，要想利用这些空间的话：

```bash
# 执行期间不需要重启文件系统
tune2fs [-m reserved_blocks_percent] /dev/{ostdev}
```

- 降低保留空间百分比，当空间使用超过95%时可能导致性能降低，即使再次降到低于95%性能也不会再次提升。因此，强烈不建议保留空间降低到5%以下。

## 15. 替换现有的ost和mdt

参看备份和恢复部分。

## 16. 如何识别某个文件存放的OST位置

```bash
[root@cn1 fs00]# lfs getstripe t6.txt 
t6.txt
lmm_stripe_count: 2
lmm_stripe_size: 1048576
lmm_pattern: raid0
lmm_layout_gen: 0
lmm_stripe_offset: 1
        obdidx objid objid group  # obdidx 标识ost目标编号，说明这个文件分布在1和3两个ost上。
             1 354 0x162 0
             3 324 0x144 0

[root@cn1 fs00]# lfs osts
OBDS:
0: fs00-OST0000_UUID ACTIVE
1: fs00-OST0001_UUID ACTIVE
2: fs00-OST0002_UUID ACTIVE
3: fs00-OST0003_UUID ACTIVE
```



