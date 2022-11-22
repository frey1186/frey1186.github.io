---
layout: post
title: GPFS安装部署测试2
date: 2017-10-07 21:00
author: felo
tags: centos gpfs
---


# 0.环境准备


## 主机

ID | hostname | IP Address    |   disk  
---|----------|---------------|---------
1  |    c01   | 192.168.56.101| sda:8GB 
2  |    c02   | 192.168.56.102| sda:8GB 
3  |    c03   | 192.168.56.103| sda:8GB 



## 内核
```bash
[root@c01 ~]# uname -r
2.6.32-431.el6.x86_64
[root@c01 ~]# cat /etc/redhat-release
CentOS release 6.5 (Final)
```


# 1.删除gpfs配置

只在其中一个节点进行操作即可，原来有一个3个节点的gpfs集群，先删除它，删除之前确保上面没有重要的数据。

```bash
# 卸载文件系统
[root@c01 ~]# mmumount /gpfs1 -a
Sat Oct  7 17:56:20 CST 2017: mmumount: Unmounting file systems ...
[root@c01 ~]# mmdel
mmdelacl        mmdelfileset    mmdelnodeclass
mmdelcallback   mmdelfs         mmdelnsd
mmdeldisk       mmdelnode       mmdelsnapshot

# 删除文件系统
[root@c01 ~]# mmdelfs gpfs1
All data on the following disks of gpfs1 will be destroyed:
    nsd01
    nsd02
    nsd03
    nsd04
Completed deletion of file system /dev/gpfs1.
mmdelfs: Propagating the cluster configuration data to all
  affected nodes.  This is an asynchronous process.

# 删除nsd
[root@c01 ~]# mmdelnsd nsd01
[root@c01 ~]# mmdelnsd nsd02
[root@c01 ~]# mmdelnsd nsd03
[root@c01 ~]# mmdelnsd nsd04

# 关闭集群
[root@c01 ~]# mmshutdown -a
Sat Oct  7 18:02:45 CST 2017: mmshutdown: Starting force unmount of GPFS file systems
Sat Oct  7 18:02:50 CST 2017: mmshutdown: Shutting down GPFS daemons
c02:  Shutting down!
c03:  Shutting down!
c01:  Shutting down!
c03:  'shutdown' command about to kill process 2729
c03:  Unloading modules from /lib/modules/2.6.32-696.10.3.el6.x86_64/extra
c02:  'shutdown' command about to kill process 3262
c02:  Unloading modules from /lib/modules/2.6.32-696.10.3.el6.x86_64/extra
c01:  'shutdown' command about to kill process 1919
c01:  Unloading modules from /lib/modules/2.6.32-696.10.3.el6.x86_64/extra
c03:  Unloading module mmfs26
c02:  Unloading module mmfs26
c01:  Unloading module mmfs26
c02:  Unloading module mmfslinux
c02:  Unloading module tracedev
c03:  Unloading module mmfslinux
c03:  Unloading module tracedev
c01:  Unloading module mmfslinux
c01:  Unloading module tracedev
Sat Oct  7 18:03:00 CST 2017: mmshutdown: Finished

# 删除所有节点
[root@c01 ~]# mmdelnode -a
Verifying GPFS is stopped on all affected nodes ...
mmdelnode: Propagating the cluster configuration data to all
  affected nodes.  This is an asynchronous process.
mmdelnode: Command successfully completed
[root@c01 ~]# mmlscluster
mmlscluster: This node does not belong to a GPFS cluster.
mmlscluster: Command failed.  Examine previous error messages to determine cause.
```

# 2.安装部署2个节点

## 2.1拓扑

![](/images/2017-10-07-gpfs-install-test2/gpfs_top.png)


其中c01，c02作为服务端，c03作为客户端。


name         |  value    
-------------|-------------------
集群名称      | 3NodeCluster
主，备节点     | c01,c02
manager      | c01
quorum       | c01,c02
shared disk  | sdb,sdc,sdd,sde

## 2.2 安装和部署过程

```bash
# 已经安装好软件并做好ssh互信
[root@c01 ~]# rpm -qa |grep gpfs
gpfs.gpl-3.5.0-34.noarch
gpfs.docs-3.5.0-34.noarch
gpfs.base-3.5.0-34.x86_64
gpfs.msg.en_US-3.5.0-34.noarch
[root@c01 ~]# for i in c01 c02 c03;do ssh $i date;done
Sat Oct  7 18:12:28 CST 2017
Sat Oct  7 18:12:28 CST 2017
Sat Oct  7 18:12:28 CST 2017
[root@c01 ~]# ls -l /lib/modules/2.6.32-696.10.3.el6.x86_64/extra/
total 6332
-rw-r--r-- 1 root root 2760629 Oct  5 23:00 mmfs26.ko
-rw-r--r-- 1 root root 2798374 Oct  5 23:00 mmfslinux.ko
-rw-r--r-- 1 root root  918694 Oct  5 23:00 tracedev.ko

# 准备4个磁盘，两个节点均能够识别到
[root@c01 ~]# fdisk -l |grep /dev/
Disk /dev/sdb: 1073 MB, 1073741824 bytes
Disk /dev/sdc: 1073 MB, 1073741824 bytes
Disk /dev/sdd: 1073 MB, 1073741824 bytes
Disk /dev/sde: 1073 MB, 1073741824 bytes

# 创建集群，接受许可
[root@c01 ~]# mmcrcluster -N "c01:manager-quorum,c02:quorum" -p c01 -s c02 \
-r /usr/bin/ssh -R /usr/bin/scp -C 3NodeCluster
Sat Oct  7 19:00:31 CST 2017: mmcrcluster: Processing node c01
Sat Oct  7 19:00:31 CST 2017: mmcrcluster: Processing node c02
mmcrcluster: Command successfully completed
mmcrcluster: Warning: Not all nodes have proper GPFS license designations.
    Use the mmchlicense command to designate licenses as needed.
mmcrcluster: Propagating the cluster configuration data to all
  affected nodes.  This is an asynchronous process.
[root@c01 ~]# mmchlicense server --accept -N c01,c02

The following nodes will be designated as possessing GPFS server licenses:
        c01
        c02
mmchlicense: Command successfully completed
mmchlicense: Propagating the cluster configuration data to all
  affected nodes.  This is an asynchronous process.

# 创建nsd
[root@c01 ~]# vi /tmp/2nodecluster.nsd
[root@c01 ~]# cat /tmp/2nodecluster.nsd
/dev/sdb:c01,c02::dataAndMetadata:40:nsd01
/dev/sdc:c01,c02::dataAndMetadata:40:nsd02

[root@c01 ~]# mmcrnsd -F /tmp/2nodecluster.nsd -v yes
mmcrnsd: Processing disk sdb
mmcrnsd: Processing disk sdc
mmcrnsd: Propagating the cluster configuration data to all
  affected nodes.  This is an asynchronous process.
[root@c01 ~]# mmlsnsd

 File system   Disk name    NSD servers
---------------------------------------------------------------------------
 (free disk)   nsd01        c01,c02
 (free disk)   nsd02        c01,c02

# 创建文件系统
[root@c01 ~]# mmstartup -a
Sat Oct  7 19:14:39 CST 2017: mmstartup: Starting GPFS ...
[root@c01 ~]# mmgetstate -aL

 Node number  Node name       Quorum  Nodes up  Total nodes  GPFS state  Remarks
------------------------------------------------------------------------------------
       1      c01                2        2          2       active      quorum node
       2      c02                2        2          2       active      quorum node
[root@c01 ~]# mmcrfs /dev/gpfs2 -F /tmp/2nodecluster.nsd -T /gpfs2 -Q yes -A yes

The following disks of gpfs2 will be formatted on node c01:
    nsd01: size 1048576 KB
    nsd02: size 1048576 KB
Formatting file system ...
Disks up to size 24 GB can be added to storage pool system.
Creating Inode File
Creating Allocation Maps
Creating Log Files
Clearing Inode Allocation Map
Clearing Block Allocation Map
Formatting Allocation Map for storage pool system
Completed creation of file system /dev/gpfs2.
mmcrfs: Propagating the cluster configuration data to all
  affected nodes.  This is an asynchronous process.
[root@c01 ~]# mmmount gpfs2 -a
Sat Oct  7 19:15:20 CST 2017: mmmount: Mounting file systems ...
[root@c01 ~]# df
Filesystem                 1K-blocks    Used Available Use% Mounted on
/dev/mapper/vg_c01-lv_root   6795192 1171104   5272244  19% /
tmpfs                         510024       0    510024   0% /dev/shm
/dev/sda1                     487652   51796    410256  12% /boot
/dev/gpfs2                   2097152  174080   1923072   9% /gpfs2

[root@c01 ~]# mmdf gpfs2
disk                disk size  failure holds    holds              free KB             free KB
name                    in KB    group metadata data        in full blocks        in fragments
--------------- ------------- -------- -------- ----- -------------------- -------------------
Disks in storage pool: system (Maximum disk size allowed is 22 GB)
nsd01                 1048576       40 Yes      Yes          961024 ( 92%)           472 ( 0%)
nsd02                 1048576       40 Yes      Yes          962048 ( 92%)           488 ( 0%)
                -------------                         -------------------- -------------------
(pool total)          2097152                               1923072 ( 92%)           960 ( 0%)

                =============                         ==================== ===================
(total)               2097152                               1923072 ( 92%)           960 ( 0%)

Inode Information
-----------------
Number of used inodes:            4041
Number of free inodes:           62519
Number of allocated inodes:      66560
Maximum number of inodes:        66560

# 增加c03客户端
[root@c01 ~]# mmaddnode c03
Sat Oct  7 19:17:28 CST 2017: mmaddnode: Processing node c03
mmaddnode: Command successfully completed
mmaddnode: Warning: Not all nodes have proper GPFS license designations.
    Use the mmchlicense command to designate licenses as needed.
mmaddnode: Propagating the cluster configuration data to all
  affected nodes.  This is an asynchronous process.
[root@c01 ~]# mmchlicense client --accept -N c03

The following nodes will be designated as possessing GPFS client licenses:
        c03
mmchlicense: Command successfully completed
mmchlicense: Propagating the cluster configuration data to all
  affected nodes.  This is an asynchronous process.
  
[root@c01 ~]# mmstartup -N c03
Sat Oct  7 19:19:32 CST 2017: mmstartup: Starting GPFS ...
[root@c01 ~]# mmgetstate -a

 Node number  Node name        GPFS state
------------------------------------------
       1      c01              active
       2      c02              active
       3      c03              active
[root@c01 ~]# mmlslicense -L
 Node name                      Required license   Designated license
---------------------------------------------------------------------
c01                                server              server
c02                                server              server
c03                                client              client

 Summary information
---------------------
Number of nodes defined in the cluster:                          3
Number of nodes with server license designation:                 2
Number of nodes with client license designation:                 1
Number of nodes still requiring server license designation:      0
Number of nodes still requiring client license designation:      0

# 在c03上查看gpfs2文件系统
[root@c03 ~]# df
Filesystem                 1K-blocks    Used Available Use% Mounted on
/dev/mapper/vg_c01-lv_root   6795192 1157952   5285396  18% /
tmpfs                         510024       0    510024   0% /dev/shm
/dev/sda1                     487652   51797    410255  12% /boot
/dev/gpfs2                   2097152  174336   1922816   9% /gpfs2
[root@c03 ~]# mmgetstate -aL

 Node number  Node name       Quorum  Nodes up  Total nodes  GPFS state  Remarks
------------------------------------------------------------------------------------
       1      c01                2        2          3       active      quorum node
       2      c02                2        2          3       active      quorum node
       3      c03                2        2          3       active
```
