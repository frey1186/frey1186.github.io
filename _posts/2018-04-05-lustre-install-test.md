---
layout: post
title: lustre文件系统安装测试
date: 2018-04-05 12:00
author: felo
tags: lustre
categories: public
typora-root-url: ..
---

![](/images/lustre/lustre-arch.png)

# 0.环境准备

使用`vagrant`安装和部署基本操作系统：

```bash
localhost:lustre_cluster$ vagrant status
Current machine states:

io1                       running (virtualbox)
io2                       running (virtualbox)
io3                       running (virtualbox)
io4                       running (virtualbox)
```

其中，四个节点规划如下：

```bash
192.168.56.191  io1  (mgs)
192.168.56.192  io2  (oss)
192.168.56.193  io3  (oss)
192.168.56.194  io4  (client)
```

内核版本

```bash
3.10.0-693.el7.x86_64
```

操作系统

```bash
[root@io1 modules]# cat /etc/redhat-release 
CentOS Linux release 7.4.1708 (Core) 
```

准备`base repo`，可以使用`aliyun`，下载地址

```bash
http://mirrors.aliyun.com/repo/Centos-7.repo
```

准备`lustre repo`:

- 创建一个临时`YUM repo`

```bash
cat >/tmp/lustre-repo.conf <<\__EOF
[lustre-server]
name=lustre-server
baseurl=https://downloads.hpdd.intel.com/public/lustre/latest-release/el7/server
# exclude=*debuginfo*
gpgcheck=0

[lustre-client]
name=lustre-client
baseurl=https://downloads.hpdd.intel.com/public/lustre/latest-release/el7/client
# exclude=*debuginfo*
gpgcheck=0

[e2fsprogs-wc]
name=e2fsprogs-wc
baseurl=https://downloads.hpdd.intel.com/public/e2fsprogs/latest/el7
# exclude=*debuginfo*
gpgcheck=0
__EOF
```

- 下载这些包，使用`reposync`，需要安装`yum-utils`包；下面的命令可以将这些RPM包都下载到本地：

```bash
reposync -c /tmp/lustre-repo.conf -n \
-r lustre-server \
-r lustre-client \
-r e2fsprogs-wc
```

- 创建repo，需要安装`createrepo`包；

```bash
for i in e2fsprogs-wc lustre-client lustre-server; do
(cd $i && createrepo .)
done
```

- 编写一个可用的lustre安装repo

```bash
[root@io2 ~]# cat /etc/yum.repos.d/lustre.repo 
[lustre-server]
name=lustre-server
baseurl=file:///vagrant/lustre_repo/lustre-server  
# 这里使用/vagrant共享目录，如果需要也可以使用http来安装。
# baseurl=http://ip_address/lustre_repo/lustre-server  
enabled=0
gpgcheck=0
proxy=_none_

[lustre-client]
name=lustre-client
baseurl=file:///vagrant/lustre_repo/lustre-client
enabled=0
gpgcheck=0

[e2fsprogs-wc]
name=e2fsprogs-wc
baseurl=file:///vagrant/lustre_repo/e2fsprogs-wc
enabled=0
gpgcheck=0
```

完成之后

```bash
[root@io2 ~]# cd /etc/yum.repos.d/
[root@io2 yum.repos.d]# ls
Centos-7.repo  lustre.repo
[root@io2 ~]# yum repolist all
Loaded plugins: fastestmirror
Loading mirror speeds from cached hostfile
 * base: mirrors.aliyun.com
 * extras: mirrors.aliyun.com
 * updates: mirrors.aliyun.com
repo id                                repo name                                                   status
base/7/x86_64                          CentOS-7 - Base - mirrors.aliyun.com                        enabled: 9,591
centosplus/7/x86_64                    CentOS-7 - Plus - mirrors.aliyun.com                        disabled
contrib/7/x86_64                       CentOS-7 - Contrib - mirrors.aliyun.com                     disabled
e2fsprogs-wc                           e2fsprogs-wc                                                disabled
extras/7/x86_64                        CentOS-7 - Extras - mirrors.aliyun.com                      enabled:   448
lustre-client                          lustre-client                                               disabled
lustre-server                          lustre-server                                               disabled
updates/7/x86_64                       CentOS-7 - Updates - mirrors.aliyun.com                     enabled: 2,416
repolist: 12,455
```



# 1. 安装lustre server

`lustre2.10.3`支持两种后台文件系统`ZFS`和`ldiskfs`，这里用`ldiskfs`。

- 安装`e2fsprogs`

```bash
yum --nogpgcheck --disablerepo=* --enablerepo=e2fsprogs-wc \
install e2fsprogs
```

- 安装并升级内核

```bash
yum --nogpgcheck --disablerepo=base,extras,updates \
--enablerepo=lustre-server install \
kernel \
kernel-devel \
kernel-headers \
kernel-tools \
kernel-tools-libs \
kernel-tools-libs-devel
```

- 重启

```bash
reboot
```

- 安装ldiskfs kmod和lustre包

```bash
yum --nogpgcheck --enablerepo=lustre-server install \
kmod-lustre \
kmod-lustre-osd-ldiskfs \
lustre-osd-ldiskfs-mount \
lustre \
lustre-resource-agents
```



# 2.安装lustre client

- 升级内核

```bash
yum install \
kernel \
kernel-devel \
kernel-headers \
kernel-abi-whitelists \
kernel-tools \
kernel-tools-libs \
kernel-tools-libs-devel
```

- 重启

```bash
reboot
```

- 安装kmod包

```bash
yum --nogpgcheck --enablerepo=lustre-client install \
kmod-lustre-client \
lustre-client
```



# 3.创建lustre文件系统

## 3.1 mgs

这里使用的是`io1`:

- 修改lustre.conf

```bash
[root@io1 ~]# cat /etc/modprobe.d/lustre.conf 
options lnet networks="tcp0(enp0s8)"
```

- 加载内核

```bash
modprobe -v lustre
modprobe -v ldiskfs
```

- 格式化MDT磁盘

```bash
mkfs.lustre --fsname=lustrefs --mgs --mdt --index=0 --reformat /dev/sdb
# --fsname : 文件系统名称
# --mgs
# --mdt
# --index：指定序号，从0开始
```

- 挂载

```bash
mkdir /mnt/mdt/
mount.lustre /dev/sdb /mnt/mdt/
```

- 查看状态

```bash
lctl dl
```

## 3.2 oss

这里使用的是`io2`和`io3`：

- 修改lustre.conf

```bash
[root@io2 ~]# cat /etc/modprobe.d/lustre.conf 
options lnet networks="tcp0(enp0s8)"
```

- 加载内核

```bash
modprobe -v lustre
modprobe -v ldiskfs
```

- 格式化OST磁盘

```bash
mkfs.lustre --fsname=lustrefs --mgsnode=io1@tcp0 --ost --index=0 --reformat /dev/sdb
# --fsname : 文件系统名称
# --mgsnode：指定mgs节点
# --ost
# --index：指定序号，从0开始，这里在io2和io3分别使用0和1
```

- 挂载

```bash
# io2
mkdir /mnt/ost0
mount.lustre /dev/sdb /mnt/ost0
# io3
mkdir /mnt/ost1
mount.lustre /dev/sdb /mnt/ost1
```

- 查看状态

```bash
lctl dl
```



## 3.3 client

- 加载内核

```bash
modprobe -v lustre
```

- 挂载文件系统

```bash
mkdir /mnt/lustre/
mount.lustre 192.168.56.191@tcp:/lustrefs /mnt/lustre/
# 192.168.56.191@tcp:/lustrefs：mgs的IP地址，端口，文件系统名称
```

- 查看文件系统

```bash
[root@io4 ~]# df -h
Filesystem                    Size  Used Avail Use% Mounted on
/dev/sda3                      39G  1.6G   38G   5% /
devtmpfs                      487M     0  487M   0% /dev
tmpfs                         497M     0  497M   0% /dev/shm
tmpfs                         497M  6.6M  490M   2% /run
tmpfs                         497M     0  497M   0% /sys/fs/cgroup
/dev/sda1                     197M  123M   75M  63% /boot
192.168.56.191@tcp:/lustrefs   39G  591M   36G   2% /mnt/lustre
tmpfs                         100M     0  100M   0% /run/user/0
```



# 参考

- [Lustre Software Installation](http://wiki.lustre.org/Category:Lustre_Software_Installation)
- [Mounting a Lustre File System on Client Nodes](http://wiki.lustre.org/Mounting_a_Lustre_File_System_on_Client_Nodes)

