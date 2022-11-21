---
layout: post
title: Lustre学习笔记（6.2）- 维护Lustre
date: 2019-03-10 12:00
tags: lustre 
categories: public
typora-root-url: ..

---


## 1. 删除MDT或者OST

一个OST失效后，MDS将不会分发新的文件到该OST上，client往这个OST上写文件的时候也会返回IO错误。一个OST是否永久失效，取决于场景和使用的命令。**注意：一个失效的OST/MDT依然会在文件系统中显示，除非使用writeconf重新配置或者使用的index被替代使用。**

临时失效OST或者MDT的场景有：
- 硬盘失败或者RAID正在平衡数据，OST被标记为降级的（degraded）；
- OST磁盘快满了，MDS已经不往该OST上写数据了；
- OST/MDT或者MDS/OSS失败了，短时间内无法恢复，但是希望继续使用文件系统；

### 1.1 （2.4以后）删除一个MDT

如果一个MDT失效了，使用lfs rm_entry directory_path强行删除该MDT管理的目录，使用rmdir会报io错误。
如果MDT未失效，使用rm -r 删除该目录后，还需要通过管理员将该MDT设置为不活动的。

```bash
# 将mdt设置为不活动的
lctl conf_param {MDT name}.mdc.active=0
# 查看目录使用MDT index
client$ lfs getstripe --mdt-index /mnt/lustre/remote_dir1
```

### 1.2 （2.4以后）处理不活动的MDT

在不活动的MDT管理下的文件不能够被访问，客户端访问不活动的MDT会返回io错误。

### 1.3 删除一个OST

每个OST在客户端和MDS上都有一个OSC的设备，负责该OST与client以及MDS的通讯。删除一个OST的步骤如下：

- 步骤1：如果该OST在用，需要将该OST上的文件迁移到别的OST上。同时不能让文件系统在该OST上创建新的文件。

```bash
# 2.9以后，设置max_create_count参数为0
mds# lctl set_param osp.osc_name.max_create_count=0
mds# lctl set_param osp.testfs-OST0000-osc-MDT*.max_create_count=0
```

如果是2.9之前的版本：

```
# 以前的版本，这个操作会阻止MDS与OST的通信，适用于OST要永久删除的情况。在文件系统中删除文件时，保存在OST上的对象将不会被删除，除非再次连接到了MDS上。该操作不会影响客户端正在读写的文件对象。
mds# lctl set_param osp.osc_name.active=0

```

**注意：如果要迁移数据，不要在客户端上使OST失效，这会导致IO错误和迁移失败。不要使用lctl conf_param来失效OST，该命令会在MDS或所有client上，立即和永久的失效OST。**

- 步骤2：发现该OST上的所有文件，并将上面的所有文件都迁移到其他OST上面，或者从备份中恢复。

```bash
# 如果该ost仍然在线，使用下面的命令：
client# lfs find --ost ost_name /mount/point | lfs_migrate -y
# 如果该ost已经不可用，删除该ost上保存的文件，并从备份中恢复
client# lfs find --ost ost_uuid -print0 /mount/point |
        tee /tmp/files_to_restore | xargs -0 -n 1 unlink
# 然后从/tmp/files_to_restore中找到需要恢复的文件清单，从备份中恢复这些文件
```

- 步骤3：失效OST

```bash
# 如果只是短暂的失效该OST，几天就能恢复，可在所有的client下执行下面的命令，这个命令是一个临时命令，重mount或者reboot就会重置：
client# lctl set_param osc.fsname-OSTnumber-*.active=0

# 如果要永久的失效OST，需要在MGS上执行命令，使所有的MDS和Client上的该OST都失效：
mgs# lctl conf_param ost_name.osc.active=0
```

**注意：失效后的OST依然保存在文件系统配置中，如果需要再次加入到文件系统中，需要使用mkfs.lustre --replace选项。**



## 2. 测试删除一个OST

### 2.1 当前环境

```bash
[root@xserver ~]# psh io1-io4 df -ht lustre
io1: Filesystem Size Used Avail Use% Mounted on
io1: mgtpool/mgt 72M 2.8M 67M 4% /fs00/mgt
io2: Filesystem Size Used Avail Use% Mounted on
io2: mdtpool/mdt000 7.7G 3.2M 7.7G 1% /fs00/mdt000
io3: Filesystem Size Used Avail Use% Mounted on
io3: ost0pool/ost000 7.7G 3.0M 7.7G 1% /fs00/ost000
io3: ost1pool/ost001 7.7G 53M 7.6G 1% /fs00/ost001
io4: Filesystem Size Used Avail Use% Mounted on
io4: ost2pool/ost002 7.7G 54M 7.6G 1% /fs00/ost002
io4: ost3pool/ost003 7.7G 203M 7.5G 3% /fs00/ost003
```

### 2.2 删除ost000

```bash
# 停止向ost0000上新建文件，要在mds上执行
[root@xserver ~]# psh io2 lctl set_param osp.fs00-OST0000-osc-MDT0000.max_create_count=0
io2: osp.fs00-OST0000-osc-MDT0000.max_create_count=0

# 迁移ost0000上的数据到其他ost，确保ost0上的文件在迁移中不能被修改，并且迁移过程中不能使用ctl-c终止。
[root@cn1 fs00]# lfs find ./ --ost fs00-OST0000 |lfs_migrate -y 
.//testdir/8.dd: done migrate
.//testdir/7.dd: done migrate
.//testdir/9.t: done migrate
[root@cn1 fs00]# lfs find ./ --ost fs00-OST0000 
# 暂时停用该ost
[root@cn1 fs00]# lctl set_param osc.fs00-OST0000-*.active=0
osc.fs00-OST0000-osc-ffff91947ba75000.active=0
[root@cn1 fs00]# lfs osts
OBDS:
0: fs00-OST0000_UUID INACTIVE  # ost0000 处于incative状态
1: fs00-OST0001_UUID ACTIVE
2: fs00-OST0002_UUID ACTIVE
3: fs00-OST0003_UUID ACTIVE
```