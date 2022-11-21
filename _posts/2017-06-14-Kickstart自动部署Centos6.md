---
layout: post
title: Kickstart自动部署Centos6过程说明
date: 2017-06-14 12:00
author: felo
tags: centos pxe
<!-- published: false -->
---


使用tcpdump抓取自动部署过程，tcpdump是一个简单的抓包工具，
抓包测试一下在部署一个操作系统中都发生了啥。
> tcpdump参考资料：
- [Linux tcpdump命令详解](http://www.cnblogs.com/ggjucheng/archive/2012/01/14/2322659.html)
- [tcpdump非常实用的抓包实例](http://blog.csdn.net/nanyun2010/article/details/23445223)
- [TCPDUMP man page](http://www.tcpdump.org/manpages/tcpdump.1.html)

测试使用自动部署过程中的dhcp和tftp服务器发生什么。。。

```bash
# 整个部署过程中67和69端口的情况：
[root@centos603 ~]# tcpdump -i eth1 port 67 or 69 -n
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on eth1, link-type EN10MB (Ethernet), capture size 65535 bytes
# 0.0.0.0 代表新服务器，广播请求IP地址
23:33:44.488227 IP 0.0.0.0.bootpc > 255.255.255.255.bootps:
                BOOTP/DHCP, Request from 00:50:56:3b:f6:2b, length 548
# dhcp响应，提供IP地址，nextserver（tftp服务器）地址，pxelinux.0文件的位置
23:33:45.000848 IP 10.10.3.167.bootps > 255.255.255.255.bootpc:
                BOOTP/DHCP, Reply, length 300
# 客户端收到后，确认信息
23:33:46.574315 IP 0.0.0.0.bootpc > 255.255.255.255.bootps:
                BOOTP/DHCP, Request from 00:50:56:3b:f6:2b, length 548
# 服务器确认，保存配置
23:33:46.575219 IP 10.10.3.167.bootps > 255.255.255.255.bootpc:
                BOOTP/DHCP, Reply, length 300
# 到tftp服务器请求pxelinux.0
23:33:46.576115 IP 10.10.3.110.ah-esp-encap > 10.10.3.167.tftp:  
                28 RRQ "/pxelinux.0" octet tsize 0
23:33:46.577817 IP 10.10.3.110.acp-port > 10.10.3.167.tftp:
                33 RRQ "/pxelinux.0" octet blksize 1456
# 请求启动配置文件，分成各种角度请求（mac，ip地址，网段），最后使用default
23:33:46.661674 IP 10.10.3.110.49152 > 10.10.3.167.tftp:
                80 RRQ "/pxelinux.cfg/564d4617-634e-2ce8-4b8c-41c6e43bb44a"
                octet tsize 0 blksize 1408
23:33:46.664079 IP 10.10.3.110.49153 > 10.10.3.167.tftp:
                64 RRQ "/pxelinux.cfg/01-00-50-56-3b-f6-2b"
                octet tsize 0 blksize 1408
23:33:46.665523 IP 10.10.3.110.49154 > 10.10.3.167.tftp:
                52 RRQ "/pxelinux.cfg/0A0A036E" octet tsize 0 blksize 1408
23:33:46.666831 IP 10.10.3.110.49155 > 10.10.3.167.tftp:
                51 RRQ "/pxelinux.cfg/0A0A036" octet tsize 0 blksize 1408
23:33:46.668137 IP 10.10.3.110.49156 > 10.10.3.167.tftp:
                50 RRQ "/pxelinux.cfg/0A0A03" octet tsize 0 blksize 1408
23:33:46.669335 IP 10.10.3.110.49157 > 10.10.3.167.tftp:
                49 RRQ "/pxelinux.cfg/0A0A0" octet tsize 0 blksize 1408
23:33:46.670963 IP 10.10.3.110.49158 > 10.10.3.167.tftp:
                48 RRQ "/pxelinux.cfg/0A0A" octet tsize 0 blksize 1408
23:33:46.672498 IP 10.10.3.110.49159 > 10.10.3.167.tftp:
                47 RRQ "/pxelinux.cfg/0A0" octet tsize 0 blksize 1408
23:33:46.673930 IP 10.10.3.110.49160 > 10.10.3.167.tftp:
                46 RRQ "/pxelinux.cfg/0A" octet tsize 0 blksize 1408
23:33:46.675185 IP 10.10.3.110.49161 > 10.10.3.167.tftp:  
                45 RRQ "/pxelinux.cfg/0" octet tsize 0 blksize 1408
23:33:46.676840 IP 10.10.3.110.49162 > 10.10.3.167.tftp:
                51 RRQ "/pxelinux.cfg/default" octet tsize 0 blksize 1408
# 这里的客户端读取default的内容，注意 vmlinuz 和initrd.img两个文件是从tftp服务器
# 上得到的，而ks文件从http（或者nfs，ftp等）服务器上获取的。
23:33:46.678128 IP 10.10.3.110.49163 > 10.10.3.167.tftp:
                38 RRQ "/vmlinuz" octet tsize 0 blksize 1408
23:33:47.169991 IP 10.10.3.110.49164 > 10.10.3.167.tftp:  
                41 RRQ "/initrd.img" octet tsize 0 blksize 1408
# 开始自启动安装了。安装介质的位置在ks文件中指定了。
```

图示如下：

![](/images/centos/pxe_process.png)

说明：

- 请求IP地址后返回的内容在dhcpd的配置文件中，租用的ip地址在dhcpd.leases文件中。
```bash
[root@centos603 ~]# cat /etc/dhcp/dhcpd.conf |grep -v "^#"
subnet 10.10.3.0 netmask 255.255.255.0 {
        range 10.10.3.100 10.10.3.200;   # 分配地址范围
        option subnet-mask 255.255.255.0;  
        default-lease-time 21600;  # 默认租用时间
        max-lease-time 43200;  # 最长租用时间
        next-server 10.10.3.167;  # tftp服务器地址
        filename "/pxelinux.0";  # pxelinux.0文件位置
      }
[root@centos603 ~]# cat /var/lib/dhcpd/dhcpd.leases
... # 其他内容未列出
lease 10.10.3.110 {
    starts 5 2017/06/16 15:33:46;
    ends 5 2017/06/16 21:33:46;
    cltt 5 2017/06/16 15:33:46;
    binding state active;
    next binding state free;
    hardware ethernet 00:50:56:3b:f6:2b;
    uid "\000VMF\027cN,\350K\214A\306\344;\264J";
```

- pxelinux.0文件:网络安装都依赖于pxelinux.0。PXELINUX is a Syslinux derivative,
for booting from a network server using a network ROM conforming to the
Intel PXE (Pre-Execution Environment) specification.
PXELINUX is not a program intended to be flashed or burned into
a PROM on the network card. For such possibility,
check out [iPXE](http://ipxe.org/)。
可以参考[这里](http://www.syslinux.org/wiki/index.php?title=PXELINUX)
```bash
# 可以通过安装syslinux来获得该文件
[root@centos603 ~]# yum install syslinux
[root@centos603 ~]# rpm -qa |grep syslinux
syslinux-4.04-3.el6.x86_64
syslinux-nonlinux-4.04-3.el6.noarch
[root@centos603 ~]# find / -name pxelinux.0
/usr/share/syslinux/pxelinux.0
```


- default文件:其中指定了vmlinuz、initrd和ks文件的位置。
该文件是一个grub配置文件，系统安装必备文件。
```bash
[root@centos603 ~]# cat /var/lib/tftpboot/pxelinux.cfg/default
default ks
prompt 0
label ks
    menu label ^Install a system
    kernel vmlinuz
    append initrd=initrd.img ks=http://10.10.3.167/ks_config/CentOS-6.9-ks.cfg ksdevice=eth0
```


- kickstart配置文件：在文件中指定了系统安装包的位置
```bash
[root@centos603 ~]# cat /var/www/html/ks_config/CentOS-6.9-ks.cfg  |grep url
url --url="http://10.10.3.167/CentOS-6.9/"
```

安装过程参考http://www.zyops.com/autoinstall-kickstart
