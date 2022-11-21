---
layout: post
title: RHEL Disk Quota
date: 2019-11-23 12:00
tags: linux 
categories: linux-basics
typora-root-url: ..
---


# 1. about disk quota

在参考资料的17章讲述了`DISK QUOTA`的相关内容。

- 可以为单个用户或者用户组限制使用空间的额度；
- 当超过或者达到一定使用额度后，通知管理员或者直接停止用户继续写入数据；
- 可以限制`磁盘容量`或者`文件数量`；
- 需要安装`quota` rpm包；


启用quota功能需要在mount的时候添加额外的参数，如果需要永久有效，则修改/etc/fstab文件的第四列为`defaults,usrquota,grpquota`后，重新mount即可；

常见命令：

```bash
quotacheck: 确认quota规则
edquota: 编辑quota规则
repquota:
quota:
quotaon:
quotaoff:
```


# 2. xfs quota

- XFS配额子系统管理对磁盘空间（块）和文件（inode）使用的限制。
- XFS配额在用户、组、目录或项目级别控制或报告这些项的使用情况。
- 另外，请注意，虽然用户、组和目录或项目配额是独立启用的，但`组`和`项目`配额是互斥的。

有以下几种mount选项：

- uquota/uqnoenforce: User quotas
- gquota/gqnoenforce: Group quotas
- pquota/pqnoenforce: Project quota

常规命令可以是`df`或者`quota username/UserID`.

高级命令`xfs_quota`

```bash
# 显示报告
xfs_quota -x -c 'report -h' /home
# 设置limit
xfs_quota -x -c 'limit isoft=500 ihard=700 john' /home/
xfs_quota -x -c 'limit -g bsoft=1000m bhard=1200m accounting' /target/path
# 在为项目控制的目录配置限制之前，请先将它们添加到/etc/projects。项目
# 名称可以添加到/etc/projectd中，以将项目id映射到项目名称
xfs_quota -x -c 'project -s projectname' project_path
xfs_quota -x -c 'limit -p bsoft=1000m bhard=1200m projectname'
```


# 3. xfs quota example

```bash
# 写一个文件来做文件系统，200M
[root@vm-centos7 ~]# dd if=/dev/zero of=test.xfs bs=1M count=200
200+0 records in
200+0 records out
209715200 bytes (210 MB) copied, 6.87531 s, 30.5 MB/s
[root@vm-centos7 ~]# mkfs.xfs test.xfs
meta-data=test.xfs               isize=512    agcount=4, agsize=12800                                                                                blks
         =                       sectsz=512   attr=2, projid32bit=1
         =                       crc=1        finobt=0, sparse=0
data     =                       bsize=4096   blocks=51200, imaxpct=25
         =                       sunit=0      swidth=0 blks
naming   =version 2              bsize=4096   ascii-ci=0 ftype=1
log      =internal log           bsize=4096   blocks=855, version=2
         =                       sectsz=512   sunit=0 blks, lazy-count                                                                               =1
realtime =none                   extsz=4096   blocks=0, rtextents=0
[root@vm-centos7 ~]#
# 挂载到/mnt
[root@vm-centos7 ~]# mount -o uquota,gquota test.xfs /mnt/
[root@vm-centos7 ~]# df -h
Filesystem               Size  Used Avail Use% Mounted on
/dev/mapper/centos-root   17G  8.2G  8.9G  48% /
devtmpfs                 901M     0  901M   0% /dev
tmpfs                    910M     0  910M   0% /dev/shm
tmpfs                    910M  9.6M  901M   2% /run
tmpfs                    910M     0  910M   0% /sys/fs/cgroup
/dev/sda1               1014M  141M  874M  14% /boot
tmpfs                    182M     0  182M   0% /run/user/0
/dev/loop0               197M   11M  187M   6% /mnt
[root@vm-centos7 ~]# mount |grep mnt
/root/test.xfs on /mnt type xfs (rw,relatime,attr2,inode64,usrquota,grpquota)
# 有一个tom的普通用户
[root@vm-centos7 ~]# cat /etc/passwd |grep tom
tom:x:1104:1106::/home/tom:/bin/bash
# 设置配额限制
[root@vm-centos7 ~]# xfs_quota -x -c "limit -u bsoft=10M bhard=20M isoft=4 ihard=8 tom" /mnt
# 写文件测试
[root@vm-centos7 ~]# chmod 777 -R /mnt/
[root@vm-centos7 ~]# su - tom
Last login: Fri Nov 15 11:46:42 CST 2019 from 192.168.72.1 on pts/1
[tom@vm-centos7 ~]$ cd /mnt/
[tom@vm-centos7 mnt]$ cd tom/
[tom@vm-centos7 tom]$ ls -l
total 0
# 写9个文件，实际完成7个
[tom@vm-centos7 tom]$ touch tom{1..9}.txt
touch: cannot touch ‘tom8.txt’: Disk quota exceeded
touch: cannot touch ‘tom9.txt’: Disk quota exceeded
[tom@vm-centos7 tom]$ ls
tom1.txt  tom2.txt  tom3.txt  tom4.txt  tom5.txt  tom6.txt  tom7.txt
# 文件大小测试，15M可以写入
[tom@vm-centos7 tom]$ dd if=/dev/zero of=tom1.txt bs=1M count=15
15+0 records in
15+0 records out
15728640 bytes (16 MB) copied, 0.283153 s, 55.5 MB/s
# 25M 写入失败，只有20M成功写入
[tom@vm-centos7 tom]$ dd if=/dev/zero of=tom1.txt bs=1M count=25
dd: error writing ‘tom1.txt’: Disk quota exceeded
21+0 records in
20+0 records out
20971520 bytes (21 MB) copied, 0.238518 s, 87.9 MB/s
[tom@vm-centos7 tom]$ du -sh tom1.txt
20M     tom1.txt
[tom@vm-centos7 tom]$ exit
logout

# 显示quota的报告
[root@vm-centos7 ~]# xfs_quota -x -c 'report -h ' /mnt/
User quota on /mnt (/dev/loop0)
                        Blocks
User ID      Used   Soft   Hard Warn/Grace
---------- ---------------------------------
root            0      0      0  00 [------]
tom           20M    10M    20M  00 [6 days]

Group quota on /mnt (/dev/loop0)
                        Blocks
Group ID     Used   Soft   Hard Warn/Grace
---------- ---------------------------------
root            0      0      0  00 [------]
tom           20M      0      0  00 [------]

# 显示tom用户的quota设置
[root@vm-centos7 ~]# quota  tom
Disk quotas for user tom (uid 1104):
     Filesystem  blocks   quota   limit   grace   files   quota   limit   grace
     /dev/loop0   20480*  10240   20480   6days       8*      4       8   6days

```


# X. 参考资料

- [1] Red_Hat_Enterprise_Linux-7-Storage_Administration_Guide-en-US.pdf
- [2] https://www.cnblogs.com/llife/p/11406819.html
