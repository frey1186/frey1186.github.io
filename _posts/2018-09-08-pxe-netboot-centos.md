---
layout: post
title: 网络启动RHEL/CENTOS的两种方法
date: 2018-09-8 12:00
author: felo
tags: centos pxe
categories: public
typora-root-url: ..
---

`Linux`可以有三种形式运行，在`硬盘`中、`网络`中或者`内存`中。`Linux`运行在硬盘中的方式是最常见的操作系统运行方式。在网络和内存中运行，都可以使用`PXE`服务器实现，下面来测试安装下这两种方式。

# 0.准备工作

先来安装一个`PXE`服务器

- 安装需要的几个包

```bash
[root@pxe ~]# yum -y install syslinux xinetd tftp-server dhcp
```

- 准备`pxelinux.0`

```bash
[root@pxe ~]# mkdir /var/lib/tftpboot/pxelinux.cfg
[root@pxe ~]# cp /usr/share/syslinux/pxelinux.0 /var/lib/tftpboot/
```

- 启动`tftp`服务

```bash
[root@pxe ~]# vi /etc/xinetd.d/tftp
# disable = no
[root@pxe ~]# systemctl start xinetd
[root@pxe ~]# systemctl enable xinetd
```

- 启动`dhcp`服务器

```bash
[root@pxe ~]# vi /etc/dhcp/dhcpd.conf
subnet 192.168.56.0 netmask 255.255.255.0 {
        range 192.168.56.100 192.168.56.200;
        option subnet-mask 255.255.255.0;
        next-server 192.168.56.171;
        filename "/pxelinux.0";
       }
[root@pxe ~]# systemctl start dhcpd
[root@pxe ~]# systemctl enable dhcpd
```



# 1. 网络启动（`pxe+nfs`）

这种方式的原理主要是通过`tftp`服务器提供的`vmlinuz`和`initrd`镜像启动后，将原来使用本地硬盘的根目录，采用`NFS`的网络方式来实现。这种方式的优势在于不需要使用本地硬盘，不过需要依赖于网络。

- 安装依赖包

```bash
yum -y install dracut-network nfs-utils
```

- 安装一个可网络运行的操作系统

```bash
[root@pxe ~]# mkdir /centos7-netboot/
[root@pxe ~]# yum groupinstall "Minimal Install" --releasever=/ --installroot=/centos7-netboot/
# 下面这两个包不确定是不是必须的
[root@pxe ~]# yum install nfs-utils dracut-network --releasever=/ --installroot=/centos7-netboot/  
```

- 修改`root`密码

```bash
[root@pxe pxelinux.cfg]# openssl passwd -1
Password: 123456
Verifying - Password: 123456
$1$iQnz.381$2Yhkd1es5R5FcIqdh4R97/
[root@pxe pxelinux.cfg]# vi /centos7-netboot/etc/shadow
```

- 修改`fstab`

```bash
[root@pxe pxelinux.cfg]# cat /centos7-netboot/etc/fstab 
none    /tmp        tmpfs   defaults   0 0
tmpfs   /dev/shm    tmpfs   defaults   0 0
sysfs   /sys        sysfs   defaults   0 0
proc    /proc       proc    defaults   0 0
```

- 下载`vmlinuz`和`initrd`

```bash
cd /var/lib/tftpboot
wget http://mirrors.163.com/centos/7/os/x86_64/images/pxeboot/vmlinuz
wget http://mirrors.163.com/centos/7/os/x86_64/images/pxeboot/initrd.img
```

- 新建default，可以使用`rw`或者`ro`

```bash
[root@pxe tftpboot]# cat pxelinux.cfg/default
default centos7

label centos7
    kernel vmlinuz
    append initrd=initrd.img root=nfs:192.168.56.171:/centos7-netboot/ rw selinux=0
```

启动一个虚拟机，测试一下

![](/images/2018-09-08-pxe-netboot-centos/diskless-netboot-01.png)

# 2.内存启动（`pxe+livecd`）

这种方式的原理是将`livecd`的内存操作系统使用`pxe`远程网络加载到目标服务器直接启动，好处是不需要占用其他服务器的存储资源，但是数据不能保留，操作系统数据都在内存中，重启后就将丢失。

- 安装一些包

```bash
[root@pxe tftpboot]# yum install livecd-tools
# livecd-iso-to-pxeboot 需要这个工具进行转换
[root@pxe tftpboot]# livecd-
livecd-creator         livecd-iso-to-disk     livecd-iso-to-pxeboot  
```

- 准备一个`livecd`，可以自己制作，也可以使用现成的
- 转换一下`livecd`，之前已准备好一个`migration-tools.iso`，制作过程略

```bash

[root@pxe ~]# livecd-iso-to-pxeboot  migration-tools.iso
# 当前目录生成tftpboot目录,将文件全部复制，注意是否覆盖部分文件
[root@pxe ~]# cp -rf tftpboot/* /var/lib/tftpboot/
[root@pxe ~]# cp migration-tools.iso /var/lib/tftpboot/
```

- 就可以直接启动一个虚拟机来测试了

![](/images/2018-09-08-pxe-netboot-centos/pxe-livecd-01.png)



# 参考

- https://github.com/livecd-tools/livecd-tools/blob/master/tools/livecd-iso-to-pxeboot.sh
- https://xcat-docs.readthedocs.io/en/2.11/advanced/hierarchy/provision/diskful_sn.html

- https://www.server-world.info/en/note?os=CentOS_7&p=pxe&f=4
- http://cobbler.github.io/manuals/2.8.0/Appendix/G_-_Booting_Live_CDs.html