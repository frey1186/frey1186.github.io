---
layout: post
title: Lustre学习笔记（1）-编译Lustre
date: 2019-01-07 12:00
tags: lustre
categories: public
typora-root-url: ..
---

# 1.编译Lustre

Lustre可以有多种编译和安装的方式，其主要区别就是OSD的选择方式，一种是基于ext4变种的LDISKFS，一种是ZFS，两种方式也可以同时编译并安装到服务器上。
由于使用LDISKFS的方式需要调整内核，一般是为内核进行补丁的方式。因此，使用LDISKFS作为OSD的话，需要重新编译内核并安装。

此外，ZFS和Lustre都要作为内核模块的方式加载入内核，那么可以选择三种方式进行编译：分别是DKMS、KMOD和Kabi的KMOD。选择KMOD的方式是简单而且好用的。

根据文档[Compiling_Lustre](http://wiki.lustre.org/Compiling_Lustre)，查看Lustre的ChangeLog，发现如果使用RHEL7.6的话，可以使用3.10.0-957.el7的内核，不用额外升级内核小版本。不升级的话，对于我们编译和安装，会简单好多...

```bash
# lustre/ChangeLog
12-21-2018 Whamcloud
       * version 2.12.0
       * See https://wiki.whamcloud.com/display/PUB/Lustre+Support+Matrix
         for currently supported client and server kernel versions.
       * Server known to build on the following kernels (others may also work):
         2.6.32-696.18.7.el6 (RHEL6.9)
         3.10.0-862.14.4.el7 (RHEL7.5)
         3.10.0-957.el7 (RHEL7.6)
         4.4.120-92.70 (SLES12 SP2)
         4.4.162-94.69 (SLES12 SP3)
         4.4.0-131 (Ubuntu 16.04)
         4.15.0-32 (Ubuntu 18.04)
         vanilla linux 4.6.7 (ZFS only)
       * ldiskfs needs an ldiskfs patch series for that kernel, ZFS does not
       * Client known to build on unpatched kernels (others may also work):
         2.6.32-696.18.7.el6 (RHEL6.9)
         2.6.32-754.6.3.el6 (RHEL6.10)
         3.10.0-862.14.4.el7 (RHEL7.5)
         3.10.0-957.el7 (RHEL7.6)
         4.14.0-49.13.1.el7a (RHEL7.5)
         4.14.0-115.2.2.el7a (RHEL7.6)
         4.4.120-92.70 (SLES12 SP2)
         4.4.162-94.69 (SLES12 SP3)
         4.4.0-131 (Ubuntu 16.04)
         4.15.0-32 (Ubuntu 18.04)
         vanilla linux 4.15.0 (ZFS only)
       * Recommended e2fsprogs version: 1.44.3.wc1 or newer
       * Recommended ZFS / SPL version: 0.7.9
       * Tested with ZFS / SPL version: 0.7.9
       * NFS export disabled when stack size < 8192 (32-bit Lustre clients),
         since the NFSv4 export of Lustre filesystem with 4K stack may cause a
         stack overflow. For more information, please refer to bugzilla 17630.
       * NFSv4 reexport to 32-bit NFS client nodes requires Lustre client on
         the re-exporting nodes to be mounted with "32bitapi" mount option
       * Note for Ubuntu 14.04.5:
         The 4.4.0 series is the HWE Kernel derived from 16.04 (Xenial).
         See: https://wiki.ubuntu.com/Kernel/LTSEnablementStack
```

使用ldiskfs的话，还需要编译和安装内核补丁，编译内核补丁会花费好多时间。同时，因为测试环境不使用IB或者OPA，所以也不编译IB内核。综上所述，选型如下：
- 操作系统：3.10.0-957.el7 (RHEL7.6)
- LDISKFS：不选
- ZFS：0.7.9版本，KMOD方式（因为没事不升级内核）

# 2.操作步骤

## 2.1准备构建环境

- 操作系统：

```bash
版本：RHEL7.6
内核版本：3.10.0-957.el7
```

- 创建一个用户：build，当然用root也完全可以。

```bash
usermod -m build
passwd build
# 添加sudo权限，在/etc/sudoers中添加
build  ALL=(ALL) ALL
```

- 安装一些必备的包

```bash
yum install asciidoc audit-libs-devel automake bc binutils-devel \
bison device-mapper-devel elfutils-devel elfutils-libelf-devel expect \
flex gcc gcc-c++ git glib2 glib2-devel hmaccalc keyutils-libs-devel \
krb5-devel ksh libattr-devel libblkid-devel libselinux-devel libtool \
libuuid-devel libyaml-devel lsscsi make ncurses-devel net-snmp-devel \
net-tools newt-devel numactl-devel parted patchutils pciutils-devel \
perl-ExtUtils-Embed pesign python-devel redhat-rpm-config rpm-build \
systemd-devel tcl tcl-devel tk tk-devel wget xmlto yum-utils zlib-devel
```

- 安装kernel-devel

```bash
yum install kernel-devel
```

## 2.2编译zfs&spl

- 下载源码

```bash
cd $HOME
git clone https://github.com/zfsonlinux/spl.git
git clone https://github.com/zfsonlinux/zfs.git
```

- 切换到0.7.9版本

```bash
# spl
cd $HOME/spl
git checkout spl-0.7.9
sh autogen.sh
#zfs
cd $HOME/zfs
git checkout zfs-0.7.9
sh autogen.sh
```

- 编译spl

```bash
cd $HOME/spl
./configure --with-spec=redhat \
--with-linux=/usr/src/kernels/3.10.0-* \
&& make pkg-utils pkg-kmod
# 将生成的安装包剪切到指定目录
mkdir -p $HOME/releases/zfs-spl
mv $HOME/spl/*.rpm $HOME/releases/zfs-spl
```

- 编译zfs

```bash
# 先安装spl
yum localinstall \
$HOME/releases/zfs-spl/{spl-[0-9].*,kmod-spl-[0-9].*,kmod-spl-devel-[0-9].*}.x86_64.rpm
# 编译zfs
cd $HOME/zfs
./configure --with-spec=redhat \
--with-spl=/usr/src/spl-0.7.0 \
--with-linux=/usr/src/kernels/3.10.0-514.16.1.el7.x86_64 \
&& make pkg-utils pkg-kmod
# 将生成的安装包剪切到指定目录
mkdir -p $HOME/releases/zfs-spl
mv $HOME/spl/*.rpm $HOME/releases/zfs-spl
# 安装zfs
yum localinstall \
$HOME/releases/zfs-spl/{spl-[0-9].*,kmod-spl-[0-9].*,kmod-spl-devel-[0-9].*}.x86_64.rpm \
$HOME/releases/zfs-spl/{zfs-[0-9].*,zfs-dracut-[0-9].*,kmod-zfs-[0-9].*,kmod-zfs-devel-[0-9].*,lib*}.x86_64.rpm
```

## 2.3编译Lustre

- 下载源码

```bash
cd $HOME
git clone git://git.whamcloud.com/fs/lustre-release.git
cd lustre-release
# 切换到2.12.0
git checkout 2.12.0
sh autogen.sh 
```

- 编译Lustre-server

```bash
# 切换到repo目录
cd $HOME/lustre-release
# 清除编译配置
make distclean
# 配置luster-server
./configure --enable-server \
--disable-ldiskfs \
--with-linux=/usr/src/kernel/3.10* \
--with-zfs=/usr/src/zfs* \
--with-spl=/usr/src/spl*
# 编译lustre-server
make rpms
# 剪切Lustre-server包到发行版目录中

mkdir -p $HOME/releases/lustre-server
mv $HOME/lustre-release/*.rpm $HOME/releases/lustre-server
```

- 编译Lustre-client

```bash
# 切换到repo目录
cd $HOME/lustre-release
# 清除编译配置
make distclean
# 配置luster-client
./configure --disable-server --enable-client \
--disable-ldiskfs \
--with-linux=/usr/src/kernel/3.10* \
--with-zfs=/usr/src/zfs* \
--with-spl=/usr/src/spl*
# 编译lustre-client
make rpms
# 剪切Lustre-client包到发行版目录中
mkdir -p $HOME/releases/lustre-client
mv $HOME/lustre-release/*.rpm $HOME/releases/lustre-client
```

完成后的下载链接: https://pan.baidu.com/s/1EdOhgBtC-NLhjQ42ogvahQ 提取码: 4ujm 


# 参考

- http://wiki.lustre.org/Compiling_Lustre
