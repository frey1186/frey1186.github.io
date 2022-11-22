---

layout: post
title: Lustre学习笔记（4.2）-配置lustre & pacemaker
date: 2019-02-24 12:00
tags: pacemaker lustre 
categories: public
typora-root-url: ..

---



# 1. 拓扑结构


![](/images/2019-02-24-lustrenote-config-lustre-pacemaker/config-lustre-pacemaker.png)

## 1.1 iscsi 服务器

主要为io1-io4这四台服务器提供iscsi存储，其中，
- mgt和mdt为io1和io2的共享空间；
- ost0-ost3为io3和io4的共享空间；

## 1.2 io1-io4服务器

- io1和io2组成一个集群，作为MGS和MDS；
- io3和io4组成一个集群，作为OSS；

## 1.3 cn1服务器

- lustre客户端


# 2. 准备磁盘

磁盘对应关系：
- mgt，200M，对应io1和io2；
- mdt，8GB，对应io1和io2；
- ost0-ost3，8GB，对应io3和io4；


```bash
[root@xserver ~]# psh iscsi targetcli ls
iscsi: o- / ......................................................................................................................... [...]
iscsi: o- backstores .............................................................................................................. [...]
iscsi: | o- block .................................................................................................. [Storage Objects: 6]
iscsi: | | o- mdt .............................................................................. [/dev/sdc (8.0GiB) write-thru activated]
iscsi: | | | o- alua ................................................................................................... [ALUA Groups: 1]
iscsi: | | | o- default_tg_pt_gp ....................................................................... [ALUA state: Active/optimized]
iscsi: | | o- mgt ............................................................................ [/dev/sdb (200.0MiB) write-thru activated]
iscsi: | | | o- alua ................................................................................................... [ALUA Groups: 1]
iscsi: | | | o- default_tg_pt_gp ....................................................................... [ALUA state: Active/optimized]
iscsi: | | o- ost0 ............................................................................. [/dev/sdd (8.0GiB) write-thru activated]
iscsi: | | | o- alua ................................................................................................... [ALUA Groups: 1]
iscsi: | | | o- default_tg_pt_gp ....................................................................... [ALUA state: Active/optimized]
iscsi: | | o- ost1 ............................................................................. [/dev/sde (8.0GiB) write-thru activated]
iscsi: | | | o- alua ................................................................................................... [ALUA Groups: 1]
iscsi: | | | o- default_tg_pt_gp ....................................................................... [ALUA state: Active/optimized]
iscsi: | | o- ost2 ............................................................................. [/dev/sdf (8.0GiB) write-thru activated]
iscsi: | | | o- alua ................................................................................................... [ALUA Groups: 1]
iscsi: | | | o- default_tg_pt_gp ....................................................................... [ALUA state: Active/optimized]
iscsi: | | o- ost3 ............................................................................. [/dev/sdg (8.0GiB) write-thru activated]
iscsi: | | o- alua ................................................................................................... [ALUA Groups: 1]
iscsi: | | o- default_tg_pt_gp ....................................................................... [ALUA state: Active/optimized]
iscsi: | o- fileio ................................................................................................. [Storage Objects: 0]
iscsi: | o- pscsi .................................................................................................. [Storage Objects: 0]
iscsi: | o- ramdisk ................................................................................................ [Storage Objects: 0]
iscsi: o- iscsi ............................................................................................................ [Targets: 6]
iscsi: | o- iqn.2019-01.f.com:mgt ............................................................................................. [TPGs: 1]
iscsi: | | o- tpg1 ............................................................................................... [no-gen-acls, no-auth]
iscsi: | | o- acls .......................................................................................................... [ACLs: 2]
iscsi: | | | o- iqn.2019-01.f.com:io1 ................................................................................ [Mapped LUNs: 1]
iscsi: | | | | o- mapped_lun0 ................................................................................... [lun0 block/mgt (rw)]
iscsi: | | | o- iqn.2019-01.f.com:io2 ................................................................................ [Mapped LUNs: 1]
iscsi: | | | o- mapped_lun0 ................................................................................... [lun0 block/mgt (rw)]
iscsi: | | o- luns .......................................................................................................... [LUNs: 1]
iscsi: | | | o- lun0 ........................................................................ [block/mgt (/dev/sdb) (default_tg_pt_gp)]
iscsi: | | o- portals .................................................................................................... [Portals: 1]
iscsi: | | o- 192.168.56.130:3260 .............................................................................................. [OK]
iscsi: | o- iqn.2019-02.f.com:mdt ............................................................................................. [TPGs: 1]
iscsi: | | o- tpg1 ............................................................................................... [no-gen-acls, no-auth]
iscsi: | | o- acls .......................................................................................................... [ACLs: 2]
iscsi: | | | o- iqn.2019-01.f.com:io1 ................................................................................ [Mapped LUNs: 1]
iscsi: | | | | o- mapped_lun0 ................................................................................... [lun0 block/mdt (rw)]
iscsi: | | | o- iqn.2019-01.f.com:io2 ................................................................................ [Mapped LUNs: 1]
iscsi: | | | o- mapped_lun0 ................................................................................... [lun0 block/mdt (rw)]
iscsi: | | o- luns .......................................................................................................... [LUNs: 1]
iscsi: | | | o- lun0 ........................................................................ [block/mdt (/dev/sdc) (default_tg_pt_gp)]
iscsi: | | o- portals .................................................................................................... [Portals: 1]
iscsi: | | o- 192.168.56.130:3260 .............................................................................................. [OK]
iscsi: | o- iqn.2019-02.f.com:ost0 ............................................................................................ [TPGs: 1]
iscsi: | | o- tpg1 ............................................................................................... [no-gen-acls, no-auth]
iscsi: | | o- acls .......................................................................................................... [ACLs: 2]
iscsi: | | | o- iqn.2019-01.f.com:io3 ................................................................................ [Mapped LUNs: 1]
iscsi: | | | | o- mapped_lun0 .................................................................................. [lun0 block/ost0 (rw)]
iscsi: | | | o- iqn.2019-01.f.com:io4 ................................................................................ [Mapped LUNs: 1]
iscsi: | | | o- mapped_lun0 .................................................................................. [lun0 block/ost0 (rw)]
iscsi: | | o- luns .......................................................................................................... [LUNs: 1]
iscsi: | | | o- lun0 ....................................................................... [block/ost0 (/dev/sdd) (default_tg_pt_gp)]
iscsi: | | o- portals .................................................................................................... [Portals: 1]
iscsi: | | o- 192.168.56.130:3260 .............................................................................................. [OK]
iscsi: | o- iqn.2019-02.f.com:ost1 ............................................................................................ [TPGs: 1]
iscsi: | | o- tpg1 ............................................................................................... [no-gen-acls, no-auth]
iscsi: | | o- acls .......................................................................................................... [ACLs: 2]
iscsi: | | | o- iqn.2019-01.f.com:io3 ................................................................................ [Mapped LUNs: 1]
iscsi: | | | | o- mapped_lun0 .................................................................................. [lun0 block/ost1 (rw)]
iscsi: | | | o- iqn.2019-01.f.com:io4 ................................................................................ [Mapped LUNs: 1]
iscsi: | | | o- mapped_lun0 .................................................................................. [lun0 block/ost1 (rw)]
iscsi: | | o- luns .......................................................................................................... [LUNs: 1]
iscsi: | | | o- lun0 ....................................................................... [block/ost1 (/dev/sde) (default_tg_pt_gp)]
iscsi: | | o- portals .................................................................................................... [Portals: 1]
iscsi: | | o- 192.168.56.130:3260 .............................................................................................. [OK]
iscsi: | o- iqn.2019-02.f.com:ost2 ............................................................................................ [TPGs: 1]
iscsi: | | o- tpg1 ............................................................................................... [no-gen-acls, no-auth]
iscsi: | | o- acls .......................................................................................................... [ACLs: 2]
iscsi: | | | o- iqn.2019-01.f.com:io3 ................................................................................ [Mapped LUNs: 1]
iscsi: | | | | o- mapped_lun0 .................................................................................. [lun0 block/ost2 (rw)]
iscsi: | | | o- iqn.2019-01.f.com:io4 ................................................................................ [Mapped LUNs: 1]
iscsi: | | | o- mapped_lun0 .................................................................................. [lun0 block/ost2 (rw)]
iscsi: | | o- luns .......................................................................................................... [LUNs: 1]
iscsi: | | | o- lun0 ....................................................................... [block/ost2 (/dev/sdf) (default_tg_pt_gp)]
iscsi: | | o- portals .................................................................................................... [Portals: 1]
iscsi: | | o- 192.168.56.130:3260 .............................................................................................. [OK]
iscsi: | o- iqn.2019-02.f.com:ost3 ............................................................................................ [TPGs: 1]
iscsi: | o- tpg1 ............................................................................................... [no-gen-acls, no-auth]
iscsi: | o- acls .......................................................................................................... [ACLs: 2]
iscsi: | | o- iqn.2019-01.f.com:io3 ................................................................................ [Mapped LUNs: 1]
iscsi: | | | o- mapped_lun0 .................................................................................. [lun0 block/ost3 (rw)]
iscsi: | | o- iqn.2019-01.f.com:io4 ................................................................................ [Mapped LUNs: 1]
iscsi: | | o- mapped_lun0 .................................................................................. [lun0 block/ost3 (rw)]
iscsi: | o- luns .......................................................................................................... [LUNs: 1]
iscsi: | | o- lun0 ....................................................................... [block/ost3 (/dev/sdg) (default_tg_pt_gp)]
iscsi: | o- portals .................................................................................................... [Portals: 1]
iscsi: | o- 192.168.56.130:3260 .............................................................................................. [OK]
iscsi: o- loopback ......................................................................................................... [Targets: 0]
```



# 3. 格式化磁盘

准备了四个磁盘分别作为ost0~ost3，分别对应oss服务器上的sdb，sdc，sdd，sde。（注意，有时候会不完全对应，因此使用id来格式化磁盘是最好的。）

```
[root@xserver ~]# psh io3,io4 ls -l /dev/disk/by-id/ |grep -E "sd[bcde]"|grep scsi
io3: lrwxrwxrwx 1 root root 9 Feb 14 13:39 scsi-360014054c17042b61f8421ebe54990f8 -> ../../sde
io3: lrwxrwxrwx 1 root root 9 Feb 14 13:54 scsi-3600140566c900b59aa24a0884d1b3961 -> ../../sdd
io3: lrwxrwxrwx 1 root root 9 Feb 14 13:39 scsi-360014058f850496f1d84c9996647adaa -> ../../sdc
io4: lrwxrwxrwx 1 root root 9 Feb 14 13:48 scsi-360014054c17042b61f8421ebe54990f8 -> ../../sde
io4: lrwxrwxrwx 1 root root 9 Feb 14 13:48 scsi-3600140566c900b59aa24a0884d1b3961 -> ../../sdb
io4: lrwxrwxrwx 1 root root 9 Feb 14 13:48 scsi-360014058f850496f1d84c9996647adaa -> ../../sdd
io4: lrwxrwxrwx 1 root root 9 Feb 14 13:48 scsi-36001405a90f61a116e0424081565b589 -> ../../sdc
```
zfs在多个节点上可用需要为每一个oss创建唯一的hostid，这里直接使用每个节点的主机名作为hostid：

```bash
[root@xserver ~]# psh io3,io4 " hostname > /etc/hostid "
```

设计一个磁盘和ost的对应关系，两个oss节点io3和io4都遵循这个关系来创建

```
scsi-360014054c17042b61f8421ebe54990f8 -> ost0
scsi-3600140566c900b59aa24a0884d1b3961 -> ost1
scsi-360014058f850496f1d84c9996647adaa -> ost2
scsi-36001405a90f61a116e0424081565b589 -> ost3
```

创建zpool

```bash
# 在io3上创建zpool，其中“-o cachefile=none -o multihost=on”这两个参数是必须的。
[root@xserver ~]# psh io3 zpool create -O canmount=off -o cachefile=none -o multihost=on ost0pool /dev/disk/by-id/scsi-360014054c17042b61f8421ebe54990f8
[root@xserver ~]# psh io3 zpool create -O canmount=off -o cachefile=none -o multihost=on ost1pool /dev/disk/by-id/scsi-3600140566c900b59aa24a0884d1b3961
[root@xserver ~]# psh io3 zpool create -O canmount=off -o cachefile=none -o multihost=on ost2pool /dev/disk/by-id/scsi-360014058f850496f1d84c9996647adaa
[root@xserver ~]# psh io3 zpool create -O canmount=off -o cachefile=none -o multihost=on ost3pool /dev/disk/by-id/scsi-36001405a90f61a116e0424081565b589
[root@xserver ~]# psh io3 zpool export ost0pool
[root@xserver ~]# psh io3 zpool export ost1pool
[root@xserver ~]# psh io3 zpool export ost2pool
[root@xserver ~]# psh io3 zpool export ost3pool
# 在io4上创建zpool
[root@xserver ~]# psh io4 zpool create -O canmount=off -o cachefile=none -o multihost=on ost0pool /dev/disk/by-id/scsi-360014054c17042b61f8421ebe54990f8
[root@xserver ~]# psh io4 zpool create -O canmount=off -o cachefile=none -o multihost=on ost1pool /dev/disk/by-id/scsi-3600140566c900b59aa24a0884d1b3961
[root@xserver ~]# psh io4 zpool create -O canmount=off -o cachefile=none -o multihost=on ost2pool /dev/disk/by-id/scsi-360014058f850496f1d84c9996647adaa
[root@xserver ~]# psh io4 zpool create -O canmount=off -o cachefile=none -o multihost=on ost3pool /dev/disk/by-id/scsi-36001405a90f61a116e0424081565b589
# 查看两个oss节点上zpool情况：
[root@xserver ~]# psh io3,io4 zpool list
io3: no pools available
io4: NAME SIZE ALLOC FREE EXPANDSZ FRAG CAP DEDUP HEALTH ALTROOT
io4: ost0pool 7.94G 318K 7.94G - 0% 0% 1.00x ONLINE -
io4: ost1pool 7.94G 285K 7.94G - 0% 0% 1.00x ONLINE -
io4: ost2pool 7.94G 285K 7.94G - 0% 0% 1.00x ONLINE -
io4: ost3pool 7.94G 273K 7.94G - 0% 0% 1.00x ONLINE -
```

测试一下，是否能够正确的在两个oss上进行导入和导出zpool：

```bash
# 在io4上导出
[root@xserver ~]# psh io4 zpool export ost0pool
[root@xserver ~]# psh io4 zpool export ost1pool
[root@xserver ~]# psh io4 zpool export ost2pool
[root@xserver ~]# psh io4 zpool export ost3pool
# 在io3中导入，注意一定需要加上”-o cachefile=none“参数，无输出说明导入正确
[root@xserver ~]# psh io3 zpool import -o cachefile=none ost0pool
[root@xserver ~]# psh io3 zpool import -o cachefile=none ost1pool
[root@xserver ~]# psh io3 zpool import -o cachefile=none ost2pool
[root@xserver ~]# psh io3 zpool import -o cachefile=none ost3pool
# 可见所有的ost pool 都可以正确的切换到io3上
[root@xserver ~]# psh io3,io4 zpool list
io3: NAME SIZE ALLOC FREE EXPANDSZ FRAG CAP DEDUP HEALTH ALTROOT
io3: ost0pool 7.94G 100K 7.94G - 0% 0% 1.00x ONLINE -
io3: ost1pool 7.94G 105K 7.94G - 0% 0% 1.00x ONLINE -
io3: ost2pool 7.94G 100K 7.94G - 0% 0% 1.00x ONLINE -
io3: ost3pool 7.94G 105K 7.94G - 0% 0% 1.00x ONLINE -
io4: no pools available
```

使用相同的方法在io1和io2上创建mgtpool和mdtpool两个zpool，创建方法与oss池基本一致。

```bash
[root@xserver ~]# psh io1,io2 zpool list
# io1 上无zpool
io1: no pools available
# io2 上有两个zpool
io2: NAME SIZE ALLOC FREE EXPANDSZ FRAG CAP DEDUP HEALTH ALTROOT
io2: mdtpool 7.94G 110K 7.94G - 0% 0% 1.00x ONLINE -
io2: mgtpool 176M 105K 176M - 4% 0% 1.00x ONLINE -
```


## 3.1 配置和创建mgt

```bash
[root@xserver ~]# psh io2 zpool export mgtpool
[root@xserver ~]# psh io1 zpool import -o cachefile=none mgtpool
[root@xserver ~]# psh io1,io2 zpool list
io1: NAME SIZE ALLOC FREE EXPANDSZ FRAG CAP DEDUP HEALTH ALTROOT
io1: mgtpool 176M 118K 176M - 4% 0% 1.00x ONLINE -
io2: NAME SIZE ALLOC FREE EXPANDSZ FRAG CAP DEDUP HEALTH ALTROOT
io2: mdtpool 7.94G 110K 7.94G - 0% 0% 1.00x ONLINE -
[root@xserver ~]# psh io1 mkdir -p /fs00/mgt
[root@xserver ~]# psh io1 mkfs.lustre --fsname=fs00 --mgs --backfstype=zfs --reformat mgtpool/mgt
[root@xserver ~]# psh io1 mount.lustre mgtpool/mgt /fs00/mgt
```

## 3.2 配置mdt

```bash
[root@xserver ~]# psh io2 mkdir -p /fs00/mdt000
[root@xserver ~]# psh io2 mkfs.lustre --fsname=fs00 --mgsnode=192.168.56.121@tcp0 --mdt --index=0 --backfstype=zfs --reformat mdtpool/mdt000
[root@xserver ~]# psh io2 mount.lustre mdtpool/mdt000 /fs00/mdt000
```

```bash
[root@xserver ~]# psh io3,io4 modprobe lnet
[root@xserver ~]# psh io3,io4 lnetctl lnet configure
[root@xserver ~]# psh io3,io4 lnetctl net add --net tcp0 --if enp0s3
[root@xserver ~]# psh io3,io4 "lnetctl net show --net tcp0 > /etc/lnet.conf "
[root@xserver ~]# psh io3,io4 lnetctl net del --net tcp0
[root@xserver ~]# psh io3,io4 systemctl enable lnet
io3: Created symlink from /etc/systemd/system/multi-user.target.wants/lnet.service to /usr/lib/systemd/system/lnet.service.
io4: Created symlink from /etc/systemd/system/multi-user.target.wants/lnet.service to /usr/lib/systemd/system/lnet.service.
[root@xserver ~]# psh io3,io4 systemctl start lnet
[root@xserver ~]# psh io3,io4 lnetctl net show --net tcp0
io3: net:
io3: - net type: tcp
io3: local NI(s):
io3: - nid: 192.168.56.123@tcp
io3: status: up
io3: interfaces:
io3: 0: enp0s3
io4: net:
io4: - net type: tcp
io4: local NI(s):
io4: - nid: 192.168.56.124@tcp
io4: status: up
io4: interfaces:
io4: 0: enp0s3
```

## 3.3 配置ost

```bash
# 修改一下zpool的分布
[root@xserver ~]# psh io3 zpool export ost2pool 
[root@xserver ~]# psh io3 zpool export ost3pool 
[root@xserver ~]# psh io4 zpool import -o cachefile=none ost2pool
[root@xserver ~]# psh io4 zpool import -o cachefile=none ost3pool
[root@xserver ~]# psh io3,io4 zpool list
io3: NAME SIZE ALLOC FREE EXPANDSZ FRAG CAP DEDUP HEALTH ALTROOT
io3: ost0pool 7.94G 100K 7.94G - 0% 0% 1.00x ONLINE -
io3: ost1pool 7.94G 105K 7.94G - 0% 0% 1.00x ONLINE -
io4: NAME SIZE ALLOC FREE EXPANDSZ FRAG CAP DEDUP HEALTH ALTROOT
io4: ost2pool 7.94G 105K 7.94G - 0% 0% 1.00x ONLINE -
io4: ost3pool 7.94G 135K 7.94G - 0% 0% 1.00x ONLINE -
```

io3上配置ost0和ost1，io4上配置ost2和ost3

```bash
[root@xserver ~]# psh io3,io4 mkdir -p /fs00/ost000
[root@xserver ~]# psh io3,io4 mkdir -p /fs00/ost001
[root@xserver ~]# psh io3,io4 mkdir -p /fs00/ost002
[root@xserver ~]# psh io3,io4 mkdir -p /fs00/ost003
[root@xserver ~]# psh io3 mkfs.lustre --fsname=fs00 --mgsnode=192.168.56.121@tcp0 --ost --index=0 --reformat ost0pool/ost000 
[root@xserver ~]# psh io3 mkfs.lustre --fsname=fs00 --mgsnode=192.168.56.121@tcp0 --ost --index=1 --reformat ost1pool/ost001 
[root@xserver ~]# psh io4 mkfs.lustre --fsname=fs00 --mgsnode=192.168.56.121@tcp0 --ost --index=2 --reformat ost2pool/ost002 
[root@xserver ~]# psh io4 mkfs.lustre --fsname=fs00 --mgsnode=192.168.56.121@tcp0 --ost --index=3 --reformat ost3pool/ost003 
[root@xserver ~]# psh io3 mount.lustre ost0pool/ost000 /fs00/ost000
[root@xserver ~]# psh io3 mount.lustre ost1pool/ost001 /fs00/ost001
[root@xserver ~]# psh io4 mount.lustre ost2pool/ost002 /fs00/ost002
[root@xserver ~]# psh io4 mount.lustre ost3pool/ost003 /fs00/ost003
```

因为没有在mkfs指定--servicenode节点，需要进行修改，修改--servicenode指向如下：

```bash
[root@xserver ~]# psh io2 umount /fs00/mdt000
[root@xserver ~]# psh io3 umount /fs00/ost000 
[root@xserver ~]# psh io3 umount /fs00/ost001
[root@xserver ~]# psh io4 umount /fs00/ost002
[root@xserver ~]# psh io4 umount /fs00/ost003
[root@xserver ~]# psh io1 umount /fs00/mgt

[root@xserver ~]# psh io1 tunefs.lustre --servicenode=192.168.56.121@tcp0 --servicenode=192.168.56.122@tcp0 mgtpool/mgt
[root@xserver ~]# psh io2 tunefs.lustre --servicenode=192.168.56.121@tcp0 --servicenode=192.168.56.122@tcp0 mdtpool/mdt000
[root@xserver ~]# psh io3 tunefs.lustre --servicenode=192.168.56.123@tcp0 --servicenode=192.168.56.124@tcp0 ost0pool/ost000
[root@xserver ~]# psh io3 tunefs.lustre --servicenode=192.168.56.123@tcp0 --servicenode=192.168.56.124@tcp0 ost1pool/ost001
[root@xserver ~]# psh io4 tunefs.lustre --servicenode=192.168.56.123@tcp0 --servicenode=192.168.56.124@tcp0 ost2pool/ost002
[root@xserver ~]# psh io4 tunefs.lustre --servicenode=192.168.56.123@tcp0 --servicenode=192.168.56.124@tcp0 ost3pool/ost003

[root@xserver ~]# psh io1 mount.lustre mgtpool/mgt /fs00/mgt
[root@xserver ~]# psh io2 mount.lustre mdtpool/mdt000 /fs00/mdt000
[root@xserver ~]# psh io3 mount.lustre ost0pool/ost000 /fs00/ost000
[root@xserver ~]# psh io3 mount.lustre ost1pool/ost001 /fs00/ost001
[root@xserver ~]# psh io4 mount.lustre ost2pool/ost002 /fs00/ost002
[root@xserver ~]# psh io4 mount.lustre ost3pool/ost003 /fs00/ost003
```

测试一下能否手动进行切换，如切换ost2

```bash
# 从io4上umount，导出
[root@xserver ~]# psh io4 umount /fs00/ost002
[root@xserver ~]# psh io4 zpool export ost2pool
# 导入io3中，并mount
[root@xserver ~]# psh io3 zpool import -o cachefile=none ost2pool
[root@xserver ~]# psh io3 mount.lustre ost2pool/ost002 /fs00/ost002
# 可以看到ost0，ost1，ost2都运行在io3上
[root@xserver ~]# psh io3 lctl dl
io3: 0 UP osd-zfs fs00-OST0000-osd fs00-OST0000-osd_UUID 4
io3: 1 UP mgc MGC192.168.56.121@tcp 14a8bf49-1862-15cf-63bd-0eec1362caa3 4
io3: 2 UP ost OSS OSS_uuid 2
io3: 3 UP obdfilter fs00-OST0000 fs00-OST0000_UUID 4
io3: 4 UP lwp fs00-MDT0000-lwp-OST0000 fs00-MDT0000-lwp-OST0000_UUID 4
io3: 5 UP osd-zfs fs00-OST0001-osd fs00-OST0001-osd_UUID 4
io3: 6 UP obdfilter fs00-OST0001 fs00-OST0001_UUID 4
io3: 7 UP lwp fs00-MDT0000-lwp-OST0001 fs00-MDT0000-lwp-OST0001_UUID 4
io3: 8 UP osd-zfs fs00-OST0002-osd fs00-OST0002-osd_UUID 4
io3: 9 UP obdfilter fs00-OST0002 fs00-OST0002_UUID 6
io3: 10 UP lwp fs00-MDT0000-lwp-OST0002 fs00-MDT0000-lwp-OST0002_UUID 4
# io4上只运行了 ost3
[root@xserver ~]# psh io4 lctl dl 
io4: 1 UP mgc MGC192.168.56.121@tcp 103e5d0b-2322-ed31-7a4f-9751c8fd8e46 4
io4: 2 UP ost OSS OSS_uuid 2
io4: 5 UP osd-zfs fs00-OST0003-osd fs00-OST0003-osd_UUID 4
io4: 6 UP obdfilter fs00-OST0003 fs00-OST0003_UUID 4
io4: 7 UP lwp fs00-MDT0000-lwp-OST0003 fs00-MDT0000-lwp-OST0003_UUID 4

# 将ost2再次切换会io4
[root@xserver ~]# psh io3 umount /fs00/ost002
[root@xserver ~]# psh io3 zpool export ost2pool
[root@xserver ~]# psh io4 zpool import -o cachefile=none ost2pool
[root@xserver ~]# psh io4 mount.lustre ost2pool/ost002 /fs00/ost002
```

完成后最终分布如下：

```bash
[root@xserver ~]# psh io1-io4 zpool list
io3: NAME SIZE ALLOC FREE EXPANDSZ FRAG CAP DEDUP HEALTH ALTROOT
io3: ost0pool 7.94G 3.31M 7.93G - 0% 0% 1.00x ONLINE -
io3: ost1pool 7.94G 3.26M 7.93G - 0% 0% 1.00x ONLINE -
io1: NAME SIZE ALLOC FREE EXPANDSZ FRAG CAP DEDUP HEALTH ALTROOT
io1: mgtpool 176M 2.94M 173M - 6% 1% 1.00x ONLINE -
io2: NAME SIZE ALLOC FREE EXPANDSZ FRAG CAP DEDUP HEALTH ALTROOT
io2: mdtpool 7.94G 3.42M 7.93G - 0% 0% 1.00x ONLINE -
io4: NAME SIZE ALLOC FREE EXPANDSZ FRAG CAP DEDUP HEALTH ALTROOT
io4: ost2pool 7.94G 3.42M 7.93G - 0% 0% 1.00x ONLINE -
io4: ost3pool 7.94G 3.26M 7.93G - 0% 0% 1.00x ONLINE -
[root@xserver ~]# 
[root@xserver ~]# 
[root@xserver ~]# psh io1-io4 lctl dl
io1: 0 UP osd-zfs MGS-osd MGS-osd_UUID 4
io1: 1 UP mgs MGS MGS 12
io1: 2 UP mgc MGC192.168.56.121@tcp 431a178a-1beb-fd0a-2a57-7ced7789e015 4
io2: 0 UP osd-zfs fs00-MDT0000-osd fs00-MDT0000-osd_UUID 10
io2: 1 UP mgc MGC192.168.56.121@tcp 659b52cf-1971-5b06-2695-79e4155bfab2 4
io2: 2 UP mds MDS MDS_uuid 2
io2: 3 UP lod fs00-MDT0000-mdtlov fs00-MDT0000-mdtlov_UUID 3
io2: 4 UP mdt fs00-MDT0000 fs00-MDT0000_UUID 14
io2: 5 UP mdd fs00-MDD0000 fs00-MDD0000_UUID 3
io2: 6 UP qmt fs00-QMT0000 fs00-QMT0000_UUID 3
io2: 7 UP osp fs00-OST0000-osc-MDT0000 fs00-MDT0000-mdtlov_UUID 4
io2: 8 UP osp fs00-OST0001-osc-MDT0000 fs00-MDT0000-mdtlov_UUID 4
io2: 9 UP osp fs00-OST0002-osc-MDT0000 fs00-MDT0000-mdtlov_UUID 4
io2: 10 UP osp fs00-OST0003-osc-MDT0000 fs00-MDT0000-mdtlov_UUID 4
io2: 11 UP lwp fs00-MDT0000-lwp-MDT0000 fs00-MDT0000-lwp-MDT0000_UUID 4
io3: 0 UP osd-zfs fs00-OST0000-osd fs00-OST0000-osd_UUID 4
io3: 1 UP mgc MGC192.168.56.121@tcp 14a8bf49-1862-15cf-63bd-0eec1362caa3 4
io3: 2 UP ost OSS OSS_uuid 2
io3: 3 UP obdfilter fs00-OST0000 fs00-OST0000_UUID 4
io3: 4 UP lwp fs00-MDT0000-lwp-OST0000 fs00-MDT0000-lwp-OST0000_UUID 4
io3: 5 UP osd-zfs fs00-OST0001-osd fs00-OST0001-osd_UUID 4
io3: 6 UP obdfilter fs00-OST0001 fs00-OST0001_UUID 4
io3: 7 UP lwp fs00-MDT0000-lwp-OST0001 fs00-MDT0000-lwp-OST0001_UUID 4
io4: 0 UP osd-zfs fs00-OST0002-osd fs00-OST0002-osd_UUID 4
io4: 1 UP mgc MGC192.168.56.121@tcp 103e5d0b-2322-ed31-7a4f-9751c8fd8e46 4
io4: 2 UP ost OSS OSS_uuid 2
io4: 3 UP obdfilter fs00-OST0002 fs00-OST0002_UUID 6
io4: 4 UP lwp fs00-MDT0000-lwp-OST0002 fs00-MDT0000-lwp-OST0002_UUID 4
io4: 5 UP osd-zfs fs00-OST0003-osd fs00-OST0003-osd_UUID 4
io4: 6 UP obdfilter fs00-OST0003 fs00-OST0003_UUID 4
io4: 7 UP lwp fs00-MDT0000-lwp-OST0003 fs00-MDT0000-lwp-OST0003_UUID 4
```







# 4. 配置集群

## 4.1 安装和配置软件包

安装软件包，需要在每个节点上都进行安装

```bash
psh io1-io4 yum -y install pcs pacemaker corosync fence-agents
```

 安装过程会自动创建hacluster用户，修改hacluster用户密码（所有节点一致）。

```bash
passwd hacluster
# 批量修改密码
psh io1-io4 ' echo "hacluster:hacluster" | chpasswd '
```

停用或配置防火墙，默认情况下已经关闭防火墙

```bash
# 如果需要关闭使用：
systemctl stop firewalld; systemctl disable firewalld
# 或者开放端口
```

## 4.2 创建和配置集群

打开pcsd后台进程

```bash
systemctl start pcsd.service
systemctl enable pcsd.service
```

pcs认证

```bash
# 在一个节点上运行即可。两个集群，分别在io1和io3上执行
[root@io1 ~]# pcs cluster auth io1 io2 -u hacluster -p hacluster
[root@io3 ~]# pcs cluster auth io3 io4 -u hacluster -p hacluster
```

创建集群，命令格式如下：
```bash
pcs cluster setup [ --start ] --name <cluster name> \
  <node 1 specification> [ <node 2 specification> ] \
  [ --transport {udpu|udp} ] \
  [ --rrpmode {active|passive} ] \
  [ --addr0 <address> ] \
  [ --addr1 <address> ] \
  [ --mcast0 <address> ] [ --mcastport0 <port> ] \
  [ --mcast1 <address> ] [ --mcastport1 <port> ] \
  [ --token <timeout> ] [ --join <timeout> ] \
  [ ... ]
```

在这里使用命令：

```bash
[root@io1 ~]# pcs cluster setup --start --name cluster_io1_2 io1 io2
[root@io3 ~]# pcs cluster setup --start --name cluster_io3_4 io3 io4
```

创建资源

```bash
# 下载心跳的资源 https://raw.githubusercontent.com/ClusterLabs/resource-agents/master/heartbeat/ZFS
[root@xserver ~]# pscp ZFS io1-io4:/usr/lib/ocf/resource.d/heartbeat/ZFS
[root@xserver ~]# psh io1-io4 chmod 755 /usr/lib/ocf/resource.d/heartbeat/ZFS
[root@xserver ~]# psh io1-io4 pcs resource list ocf:heartbeat:ZFS
io1: ocf:heartbeat:ZFS - Manages ZFS pools
io2: ocf:heartbeat:ZFS - Manages ZFS pools
io4: ocf:heartbeat:ZFS - Manages ZFS pools
io3: ocf:heartbeat:ZFS - Manages ZFS pools
# 创建ost0资源，其他ost1-3都是类似的方法
[root@io3 ~]# pcs resource create zfs-ost0pool ocf:heartbeat:ZFS pool=ost0pool
[root@io3 ~]# pcs resource create fs00-ost0000 ocf:lustre:Lustre target=ost0pool/ost000 mountpoint=/fs00/ost000 
## 创建位置限制
[root@io3 ~]# pcs constraint location zfs-ost0pool prefers io3=100
[root@io3 ~]# pcs constraint location fs00-ost0000 prefers io3=100
[root@io3 ~]# pcs constraint location zfs-ost0pool prefers io4=50
[root@io3 ~]# pcs constraint location fs00-ost0000 prefers io4=50
## 将这两个资源添加到一个组中
[root@io3 ~]# pcs resource group add group-fs00-ost0000 zfs-ost0pool fs00-ost0000
## 将这两个资源捆绑在一个节点上
[root@io3 ~]# pcs constraint colocation add fs00-ost0000 with zfs-ost0pool 
## 定义这两个资源的运行顺序
[root@io3 ~]# pcs constraint order start zfs-ost0pool then start fs00-ost0000 
## 查看一下：
[root@io3 ~]# pcs constraint show
Location Constraints:
  Resource: fs00-ost0000
    Enabled on: io3 (score:100)
    Enabled on: io4 (score:50)
  Resource: zfs-ost0pool
    Enabled on: io3 (score:100)
    Enabled on: io4 (score:50)
Ordering Constraints:
  start zfs-ost0pool then start fs00-ost0000 (kind:Mandatory)
```

相同的方法创建ost1，ost2和ost3资源：

```bash
# ost1 资源创建
[root@io3 ~]# pcs resource create zfs-ost1pool ocf:heartbeat:ZFS pool=ost1pool
[root@io3 ~]# pcs constraint location zfs-ost1pool prefers io3=100
[root@io3 ~]# pcs resource create fs00-ost0001 ocf:lustre:Lustre target=ost1pool/ost001 mountpoint=/fs00/ost001
[root@io3 ~]# pcs constraint location fs00-ost0001 prefers io3=100
[root@io3 ~]# pcs constraint location zfs-ost1pool prefers io4=50
[root@io3 ~]# pcs constraint location fs00-ost0001 prefers io4=50
[root@io3 ~]# pcs resource group add group-fs00-ost0001 zfs-ost1pool fs00-ost0001
[root@io3 ~]# pcs constraint colocation add fs00-ost0001 with zfs-ost1pool
[root@io3 ~]# pcs constraint order start zfs-ost1pool then start fs00-ost0001
# ost2，ost3 使用相同的方法创建完成后：
[root@io3 ~]# pcs constraint show
Location Constraints:
  Resource: fs00-ost0000
    Enabled on: io3 (score:100)
    Enabled on: io4 (score:50)
  Resource: fs00-ost0001
    Enabled on: io3 (score:100)
    Enabled on: io4 (score:50)
  Resource: fs00-ost0002
    Enabled on: io4 (score:100)
    Enabled on: io3 (score:50)
  Resource: fs00-ost0003
    Enabled on: io4 (score:100)
    Enabled on: io3 (score:50)
  Resource: zfs-ost0pool
    Enabled on: io3 (score:100)
    Enabled on: io4 (score:50)
  Resource: zfs-ost1pool
    Enabled on: io3 (score:100)
    Enabled on: io4 (score:50)
  Resource: zfs-ost2pool
    Enabled on: io4 (score:100)
    Enabled on: io3 (score:50)
  Resource: zfs-ost3pool
    Enabled on: io4 (score:100)
    Enabled on: io3 (score:50)
Ordering Constraints:
  start zfs-ost0pool then start fs00-ost0000 (kind:Mandatory)
  start zfs-ost1pool then start fs00-ost0001 (kind:Mandatory)
  start zfs-ost2pool then start fs00-ost0002 (kind:Mandatory)
  start zfs-ost3pool then start fs00-ost0003 (kind:Mandatory)
Colocation Constraints:
  fs00-ost0000 with zfs-ost0pool (score:INFINITY)
  fs00-ost0001 with zfs-ost1pool (score:INFINITY)
  fs00-ost0002 with zfs-ost2pool (score:INFINITY)
  fs00-ost0003 with zfs-ost3pool (score:INFINITY)
Ticket Constraints:
```

io1和io2集群的资源配置如下，配置方法与上面的方式相同：
```bash
[root@io1 ~]# pcs constraint show
Location Constraints:
  Resource: fs00-mdt0000
    Enabled on: io2 (score:100)
    Enabled on: io1 (score:50)
  Resource: fs00-mgt
    Enabled on: io1 (score:100)
    Enabled on: io2 (score:50)
  Resource: zfs-mdtpool
    Enabled on: io2 (score:100)
    Enabled on: io1 (score:50)
  Resource: zfs-mgtpool
    Enabled on: io1 (score:100)
    Enabled on: io2 (score:50)
Ordering Constraints:
  start zfs-mgtpool then start fs00-mgt (kind:Mandatory)
  start zfs-mdtpool then start fs00-mdt0000 (kind:Mandatory)
Colocation Constraints:
  fs00-mgt with zfs-mgtpool (score:INFINITY)
  fs00-mdt0000 with zfs-mdtpool (score:INFINITY)
Ticket Constraints:
[root@io1 ~]# pcs resource show
 Resource Group: group-fs00-mgt
     zfs-mgtpool (ocf::heartbeat:ZFS): Started io1
     fs00-mgt (ocf::lustre:Lustre): Stopped
 Resource Group: group-fs00-mdt0000
     zfs-mdtpool (ocf::heartbeat:ZFS): Started io2
     fs00-mdt0000 (ocf::lustre:Lustre): Stopped
```


配置 LNET Health 监控资源

```bash
# io1和io2组成的集群：
[root@io1 ~]# pcs resource create healthLNET ocf:lustre:healthLNET lctl=true multiplier=1001 device=enp0s3 host_list="192.168.56.123@tcp 192.168.56.124@tcp" --clone
[root@io1 ~]# pcs resource show
 Resource Group: group-fs00-mgt
     zfs-mgtpool (ocf::heartbeat:ZFS): Started io1
     fs00-mgt (ocf::lustre:Lustre): Stopped
 Resource Group: group-fs00-mdt0000
     zfs-mdtpool (ocf::heartbeat:ZFS): Started io2
     fs00-mdt0000 (ocf::lustre:Lustre): Stopped
 Clone Set: healthLNET-clone [healthLNET]
     Started: [ io1 io2 ]
[root@io1 ~]# pcs constraint location zfs-mgtpool rule score=-INFINITY pingd lte 0 or not_defined pingd
[root@io1 ~]# pcs constraint location zfs-mdtpool rule score=-INFINITY pingd lte 0 or not_defined pingd
[root@io1 ~]# pcs constraint location fs00-mgt rule score=-INFINITY pingd lte 0 or not_defined pingd
[root@io1 ~]# pcs constraint location fs00-mdt0000 rule score=-INFINITY pingd lte 0 or not_defined pingd

## io3 和io4组成的集群
[root@io3 ~]# pcs resource create healthLNET ocf:lustre:healthLNET lctl=true multiplier=1001 device=enp0s3 host_list="192.168.56.121@tcp 192.168.56.122@tcp" --clone
[root@io3 ~]# pcs constraint location zfs-ost0pool rule score=-INFINITY pingd lte 0 or not_defined pingd
[root@io3 ~]# pcs constraint location zfs-ost1pool rule score=-INFINITY pingd lte 0 or not_defined pingd
[root@io3 ~]# pcs constraint location zfs-ost2pool rule score=-INFINITY pingd lte 0 or not_defined pingd
[root@io3 ~]# pcs constraint location zfs-ost3pool rule score=-INFINITY pingd lte 0 or not_defined pingd
[root@io3 ~]# pcs constraint location fs00-ost0000 rule score=-INFINITY pingd lte 0 or not_defined pingd
[root@io3 ~]# pcs constraint location fs00-ost0001 rule score=-INFINITY pingd lte 0 or not_defined pingd
[root@io3 ~]# pcs constraint location fs00-ost0002 rule score=-INFINITY pingd lte 0 or not_defined pingd
[root@io3 ~]# pcs constraint location fs00-ost0003 rule score=-INFINITY pingd lte 0 or not_defined pingd
```

创建 Lustre Health 监控资源

```bash
# io1 和 io2 集群
[root@io1 ~]# pcs resource create healthLUSTRE ocf:lustre:healthLUSTRE --clone
[root@io1 ~]# pcs constraint location zfs-mgtpool rule score=-INFINITY lustred lte 0 or not_defined lustred
[root@io1 ~]# pcs constraint location fs00-mgt rule score=-INFINITY lustred lte 0 or not_defined lustred
[root@io1 ~]# pcs constraint location fs00-mdt0000 rule score=-INFINITY lustred lte 0 or not_defined lustred
[root@io1 ~]# pcs constraint location zfs-mdtpool rule score=-INFINITY lustred lte 0 or not_defined lustred
## io3 和io4 集群
[root@io3 ~]# pcs resource create healthLUSTRE ocf:lustre:healthLUSTRE --clone
[root@io3 ~]# pcs constraint location zfs-ost0pool rule score=-INFINITY lustred lte 0 or not_defined lustred
[root@io3 ~]# pcs constraint location zfs-ost1pool rule score=-INFINITY lustred lte 0 or not_defined lustred
[root@io3 ~]# pcs constraint location zfs-ost2pool rule score=-INFINITY lustred lte 0 or not_defined lustred
[root@io3 ~]# pcs constraint location zfs-ost3pool rule score=-INFINITY lustred lte 0 or not_defined lustred
[root@io3 ~]# pcs constraint location fs00-ost0000 rule score=-INFINITY lustred lte 0 or not_defined lustred
[root@io3 ~]# pcs constraint location fs00-ost0001 rule score=-INFINITY lustred lte 0 or not_defined lustred
[root@io3 ~]# pcs constraint location fs00-ost0002 rule score=-INFINITY lustred lte 0 or not_defined lustred
[root@io3 ~]# pcs constraint location fs00-ost0003 rule score=-INFINITY lustred lte 0 or not_defined lustred
```

# 5. 测试

## 5.1 断开io3的enp0s3网卡，资源自动切换到io4

```bash
# io3 操作
ip  l set enp0s3 down
# io4 查看集群状态，可以发现资源已经都切换到了io3上
pcs status
pcs resource show
```

## 5.2 关闭io4服务器
揍是不能自动切换，唉...下回再试试



# 参考
- http://wiki.lustre.org/Category:Lustre_High_Availability


