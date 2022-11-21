---
layout: post
title:  包管理工具 - YUM & RPM
date: 2019-09-03 12:00
tags: linux
categories: linux-basics 
---


Linux的软件包需要管理，否则只能通过源码编译后安装，编译和安装过程都很慢也很麻烦，我们只在有特殊需要的时候才用源码编译。

根据Linux的派系，可以分成下面几个类别的：

- CentOS/RHEL/Fedora: YUM(DNF) & RPM
- OpenSuse/SUSE : Yast & RPM
- Ubuntu/Debian: APT & DEB

此外，还有一些其他的包管理工具，这里就说RPM和YUM。

# 1. RPM

RPM是CentOS的低级包管理工具。

一些常见的使用例子：

```bash
# 安装一个rpm包
rpm -ivh pidgin-2.7.9-5.el6.2.i686.rpm

# 查看一个包需要的依赖包
rpm -qpR BitTorrent-5.2.2-1-Python2.4.noarch.rpm

# 确认一个包是否安装
rpm -q BitTorrent

# 查看安装的所有包
rpm -qa 

# 查看包安装了哪些文件
rpm -ql BitTorrent

# 卸载一个包，包含他的依赖
rpm -evv nx

# 卸载一个包，不包含依赖包
rpm -ev --nodeps vsftpd

# 查看一个文件属于哪个包
rpm -qf /usr/bin/htpasswd

# 查看安装信息
rpm -qi vsftpd

# 安装之前获取包的详细信息
rpm -qip sqlbuddy-1.3.3-1.noarch.rpm
```

# 2. YUM

DNF曾经是YUM的一个分支，但是因为DNF对于python2和python3的支持，DNF将要逐渐取代YUM。

YUM是CentOS的高级包管理工具。

一些常见的使用例子：

```bash
# 安装一个包
yum install firefox
yum -y install firefox

# 删除一个包，包括依赖
yum remove firefox

# 升级一个包
yum update mysql

# 列举一个包
yum list openssh

# 查询
yum search vsftpd

# 详细信息
yum info firefox

# 显示软件包的依赖关系
yum deplist firefox

# 列举已经安装了哪些包
yum list installed | less

# 查看文件属于哪个软件包
yum provides /etc/httpd/conf/httpd.conf

# 升级
yum update

# 重建cache
yum clean all && yum makecache

# 列举所有组包
yum grouplist

# 安装组包
yum groupinstall 'MySQL Database'

# 列举repo
yum repolist
yum repolist all

# 使用指定的repo安装包
yum --enablerepo=epel install phpmyadmin
yum --disablerepo=* --enablerepo=base install vim

# 安装yum-utils后，可以使用yum-config-manager命令维护repo
yum-config-manager --disable epel --enable extra

# yum历史
yum history
```

## 2.1 repo 管理


将iso文件作为本地base repo使用

```bash
# 挂载光驱
mount /dev/sr0 /mnt
##  mount -o loop /path/of/iso/centos7.iso /mnt

# 禁用其他repo
rm -f /etc/yum.repos.d/*

# 编写新的repo
cat > /etc/yum.repos.d/cdrom.repo <<EOF
[cdrom]
name=BASE
baseurl=file:///mnt
enabled=1
gpgcheck=0
EOF

# 启用repo
yum clean all && yum makecache
```

使用网络repo的时候就将baseurl修改成为http地址即可。

另外，使用yum-config-manager会更加简单明了

```bash
[root@vm-centos7 ~]# yum repolist all |grep enabled
!base/7/x86_64                            CentOS-7 - Base - mirrors.aliyun.com                                         enabled: 10,019
!epel/x86_64                              Extra Packages for Enterprise Linux 7 - x86_64                               enabled: 13,382
[root@vm-centos7 ~]# yum-config-manager --disable base --disable epel
[root@vm-centos7 ~]# mount /dev/sr0 /mnt/
# 命令增加一个repo
[root@vm-centos7 ~]# yum-config-manager --add-repo file:///mnt
Loaded plugins: fastestmirror
adding repo from: file:///mnt

[mnt]
name=added from: file:///mnt
baseurl=file:///mnt
enabled=1

[root@vm-centos7 ~]# yum clean all && yum makecache
[root@vm-centos7 ~]# yum repolist
Loaded plugins: fastestmirror
Loading mirror speeds from cached hostfile
repo id                                                 repo name                                                               status
mnt                                                     added from: file:///mnt                                                 4,021
repolist: 4,021


```




# x. reference

- [1][20 rpm Command Examples](https://www.tecmint.com/20-practical-examples-of-rpm-commands-in-linux/)
- [2][20 yum Command Examples](https://www.tecmint.com/20-linux-yum-yellowdog-updater-modified-commands-for-package-mangement/)
- [3][Linux Package Management with Yum, RPM, Apt, Dpkg, Aptitude and Zypper – Part 9](https://www.tecmint.com/linux-package-management/)
