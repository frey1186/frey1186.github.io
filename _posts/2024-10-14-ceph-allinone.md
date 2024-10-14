---
layout: post
title: Ceph单节点部署测试
date: 2024-10-14 00:00
tags: ceph, linux
categories: public
---

# 部署环境

- OS: CentOS Linux release 7.8.2003 (AltArch)
- Ceph: 15.2.17

# 安装软件包

```bash
yum -y install ceph-mon ceph-mgr ceph-osd
```

# 配置主机名

```bash
hostnamectl set-hostname host173
echo 10.128.11.173 host173 >> /etc/hosts
```

# 配置ceph.conf

```bash
mkdir -p /etc/ceph/
echo "[global]" > /etc/ceph/ceph.conf
echo "fsid = $(uuidgen)" >> /etc/ceph/ceph.conf
echo "mon initial members = $(hostname)" >> /etc/ceph/ceph.conf
echo "mon host = 10.128.11.173" >> /etc/ceph/ceph.conf
```

完成后ceph.conf配置如下：

```bash
# cat /etc/ceph/ceph.conf
fsid = f43b8ed6-26b4-4fc2-b95e-f2d4c8381fa0
mon initial members = host173
mon host = 10.128.11.173
```

# 配置ceph-mon

```bash
# 设置密钥环，使用ceph-authtool工具，默认集群名是ceph
ceph-authtool -C /etc/ceph/ceph.mon.keyring -g -n mon. --cap mon "allow *"
ceph-authtool -C /etc/ceph/ceph.client.admin.keyring -g -n client.admin --cap mon "allow *" --cap osd "allow *"
ceph-authtool /etc/ceph/ceph.mon.keyring --import-keyring /etc/ceph/ceph.client.admin.keyring
# 创建monmap
monmaptool --create --add host173 10.128.11.173 --fsid=f43b8ed6-26b4-4fc2-b95e-f2d4c8381fa0 /etc/ceph/monmap
monmaptool --print  /etc/ceph/monmap
# 初始化mon
mkdir -p /var/lib/ceph/mon/ceph-host173
chown -R ceph:ceph /var/lib/ceph /etc/ceph/ /var/log/ceph/
sudo -u ceph ceph-mon --mkfs -i host173 --monmap /etc/ceph/monmap --keyring /etc/ceph/ceph.mon.keyring
# 使用系统默认的systemctl配置文件，启动mon服务
systemctl start ceph-mon@host173
```

# 配置ceph-osd

```bash
for i in 0 1 2;
do
ceph osd create
ceph-authtool -C /etc/ceph/ceph.osd.$i.keyring -g -n osd.$i --cap mon "allow profile osd" --cap osd "allow *"
ceph auth import -i /etc/ceph/ceph.osd.$i.keyring
mkdir -p /var/lib/ceph/osd/ceph-$i
ceph auth get-or-create osd.$i -o /var/lib/ceph/osd/ceph-$i/keyring
chown -R ceph:ceph /var/lib/ceph /etc/ceph/ /var/log/ceph/
sleep 1;sudo -u ceph ceph-osd -i $i --mkfs
ceph osd crush add osd.$i 0.1 root=default host=host173
done

systemctl start ceph-osd@0
systemctl start ceph-osd@1
systemctl start ceph-osd@2
```

检查osd启动状态，已启动并生效3个osd

```bash
[root@localhost ~]# ceph -s |grep osd
    osd: 3 osds: 3 up (since 8s), 3 in (since 8s)
```

#  配置ceph-mgr

ceph-mgr需要下面两个python库，有警告

```bash
pip3  install werkzeug pecan
```

配置ceph-mgr

```bash
mkdir -p /var/lib/ceph/mgr/ceph-host173
chown -R ceph:ceph /var/lib/ceph/mgr/
ceph-authtool -C /etc/ceph/ceph.mgr.host173.keyring -g -n mgr.host173 --cap mon "allow profile mgr" --cap osd "allow *"
ceph auth import -i /etc/ceph/ceph.mgr.host173.keyring
ceph auth get-or-create mgr.host173 -o /var/lib/ceph/mgr/ceph-host173/keyring
systemctl start ceph-mgr@host173
```

# 创建pool和rbd

```bash
ceph osd pool create rbd 128 128
ceph osd pool application enable rbd rbd
rbd create -s 10G test
```

# 本机映射rbd，创建文件系统并使用

```bash
[root@host173 ceph]# rbd map test
/dev/rbd0
[root@host173 ceph]# ceph -s
  cluster:
    id:     f43b8ed6-26b4-4fc2-b95e-f2d4c8381fa0
    health: HEALTH_OK

  services:
    mon: 1 daemons, quorum host173 (age 13m)
    mgr: host173(active, since 12m)
    osd: 3 osds: 3 up (since 21m), 3 in (since 78m)

  data:
    pools:   2 pools, 89 pgs
    objects: 4 objects, 36 B
    usage:   3.1 GiB used, 297 GiB / 300 GiB avail
    pgs:     1.124% pgs not active
             88 active+clean
             1  peering

  progress:
    PG autoscaler decreasing pool 5 PGs from 128 to 32 (3m)
      [=========...................] (remaining: 5m)

[root@host173 ceph]# ls /dev/rbd0
/dev/rbd0
[root@host173 ceph]# mkfs.xfs /dev/rbd0
[root@host173 ceph]# mount /dev/rbd0 /mnt/
[root@host173 ceph]# ls /mnt/
[root@host173 ceph]# echo aaaa > /mnt/1.txt
[root@host173 ceph]# cat /mnt/1.txt
aaaa
[root@host173 ceph]# umount /mnt
```

# 错误处理
## 1. error reading config file

```bash
# 现象：
[root@localhost ~]# sudo -u ceph ceph-mon --mkfs -i host173 --monmap /etc/ceph/monmap --keyring /etc/ceph/ceph.mon.keyring
global_init: error reading config file.
# 处理方法：
I think it is trying to say that it can't find the [global] section in /etc/ceph/ceph.conf
```

## 2. 1 monitors have not enabled msgr2

```bash
现象：
[root@localhost ~]# ceph health
HEALTH_WARN mon is allowing insecure global_id reclaim; 1 monitors have not enabled msgr2
处理方法：
[root@localhost ~]# ceph mon enable-msgr2
[root@localhost ~]# ceph config set mon auth_allow_insecure_global_id_reclaim false
[root@localhost ~]# systemctl restart ceph-mon.target
[root@localhost ~]# ceph health
HEALTH_OK
```

## 3. failed to open block

```bash
现象：
2024-10-11T09:46:34.236+0800 7fff811a0000 -1 bluestore(/var/lib/ceph/osd/ceph-2/block) _read_bdev_label failed to open /var/lib/ceph/osd/ceph-2/block: (2) No such file or directory
2024-10-11T09:46:34.236+0800 7fff811a0000 -1 bluestore(/var/lib/ceph/osd/ceph-2/block) _read_bdev_label failed to open /var/lib/ceph/osd/ceph-2/block: (2) No such file or directory
2024-10-11T09:46:34.236+0800 7fff811a0000 -1 bluestore(/var/lib/ceph/osd/ceph-2/block) _read_bdev_label failed to open /var/lib/ceph/osd/ceph-2/block: (2) No such file or directory
2024-10-11T09:46:34.236+0800 7fff811a0000 -1 bluestore(/var/lib/ceph/osd/ceph-2) _read_fsid unparsable uuid
2024-10-11T09:46:34.246+0800 7fff811a0000 -1 freelist read_size_meta_from_db missing size meta in DB
方法：
重新执行 sudo -u ceph ceph-osd -i 2 --mkfs
```

## 4. 100.000% pgs not active

```bash
现象： 创建完成osd和mgr后，pgs未active
[root@localhost ~]# ceph -s

  cluster:
    id:     f43b8ed6-26b4-4fc2-b95e-f2d4c8381fa0
    health: HEALTH_WARN
            Module 'restful' has failed dependency: No module named 'pecan'

  services:
    mon: 1 daemons, quorum host173 (age 4m)
    mgr: host173(active, since 11s)
    osd: 3 osds: 3 up (since 7m), 3 in (since 14m)

  data:
    pools:   1 pools, 1 pgs
    objects: 0 objects, 0 B
    usage:   3.0 GiB used, 297 GiB / 300 GiB avail
    pgs:     100.000% pgs not active
             1 undersized+peered
处理方法：
[root@host173 ~]# ceph osd  getcrushmap -o /etc/ceph/crushmap
12
[root@host173 ~]# crushtool -d /etc/ceph/crushmap -o /etc/ceph/crushmap.txt
[root@host173 ~]# vim /etc/ceph/crushmap.txt
[root@host173 ~]# grep "step choose" /etc/ceph/crushmap.txt
        step chooseleaf firstn 0 type osd   
#由于ceph默认crushmap策略是基于host的故障域，在三副本的情况下，由于只有一个host，这时创建存储池后，ceph状态会变为HEALTH_WARN，而且一直无法重平衡PG
[root@host173 ~]# crushtool -c /etc/ceph/crushmap.txt -o /etc/ceph/crushmap.new
[root@host173 ~]# ceph osd setcrushmap -i /etc/ceph/crushmap.new
13
```

## 5. rbd: sysfs write failed

```bash
现象：
[root@host173 ceph]# rbd map test
rbd: sysfs write failed
RBD image feature set mismatch. You can disable features unsupported by the kernel with "rbd feature disable test object-map fast-diff deep-flatten".
In some cases useful info is found in syslog - try "dmesg | tail".
rbd: map failed: (6) No such device or address
处理方法：
[root@host173 ceph]# rbd feature disable test object-map fast-diff deep-flatten
```
