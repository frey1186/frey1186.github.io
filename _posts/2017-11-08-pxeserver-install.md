---
layout: post
title: 配置一个PXE服务器（rhel6.8）
date: 2017-11-08 12:00
author: felo
tags: redhat pxe
---


# 0.环境

```bash
[root@pxeserver ~]# cat /etc/redhat-release
Red Hat Enterprise Linux Server release 6.8 (Santiago)
[root@pxeserver ~]# cat /etc/hosts
127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4
::1         localhost localhost.localdomain localhost6 localhost6.localdomain6


192.168.88.21 pxeserver
192.168.88.22 cpt01
192.168.88.23 cpt02
```
![](/images/pxeserver_install/pxeserver-install-top.png)

## 设置iptables和selinux
```bash
[root@pxeserver ~]# /etc/init.d/iptables stop
iptables: Setting chains to policy ACCEPT: filter          [  OK  ]
iptables: Flushing firewall rules:                         [  OK  ]
iptables: Unloading modules:                               [  OK  ]
[root@pxeserver ~]# chkconfig iptables off

[root@pxeserver ~]# sed -i "s#SELINUX=enforcing#SELINUX=disabled#g" /etc/selinux/config
[root@pxeserver ~]# getenforce
Enforcing
[root@pxeserver ~]# setenforce 0
[root@pxeserver ~]# getenforce
Permissive

```

# 1. 安装dhcp&tftp&httpd 

```bash
[root@pxeserver ~]# mount -t iso9660 /dev/sr0 /mnt/
mount: no medium found on /dev/sr0

[root@pxeserver ~]# cat /etc/yum.repos.d/rhel-source.repo
...
[rhel-local]
name=Red Hat Enterprise Linux $releasever Local Media
baseurl=file:///mnt
enabled=1
gpgcheck=0
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-beta,file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release

# install dhcp
[root@pxeserver yum.repos.d]# yum install dhcp -y
[root@pxeserver yum.repos.d]# rpm -ql dhcp |grep dhcpd.conf
/etc/dhcp/dhcpd.conf

# config file
[root@pxeserver yum.repos.d]# vim /etc/dhcp/dhcpd.conf
[root@pxeserver ~]# cat /etc/dhcp/dhcpd.conf
#
# DHCP Server Configuration file.
#   see /usr/share/doc/dhcp*/dhcpd.conf.sample
#   see 'man 5 dhcpd.conf'
#		
subnet 192.168.88.0 netmask 255.255.255.0 {
        range 192.168.88.100 192.168.88.200;
        option subnet-mask 255.255.255.0;
        #next-server 192.168.88.21;
        #filename "/pxelinux.0";
       }

group  {
        filename "/rhel6.8/pxelinux.0";
        next-server 192.168.88.21;

        host cpt01 { hardware ethernet 00:50:56:23:F9:14;fixed-address 192.168.88.22;}
       }

group  {
        filename "/centos7.0/pxelinux.0";
        next-server 192.168.88.21;

        host cpt02 { hardware ethernet 00:50:56:33:DC:57;fixed-address 192.168.88.23;}
       }

[root@pxeserver yum.repos.d]# /etc/init.d/dhcpd start
Starting dhcpd:                                            [  OK  ]
[root@pxeserver yum.repos.d]# netstat -nltup| grep dhcpd
udp        0      0 0.0.0.0:67                  0.0.0.0:*                               31437/dhcpd

# install tftp-server
[root@pxeserver yum.repos.d]# yum install tftp-server tftp -y
[root@pxeserver yum.repos.d]# rpm -ql tftp-server |grep tftp
/etc/xinetd.d/tftp
...
# disable tftp no
[root@pxeserver yum.repos.d]# vim /etc/xinetd.d/tftp
[root@pxeserver yum.repos.d]# cat /etc/xinetd.d/tftp |grep disable
        disable                 = no
[root@pxeserver yum.repos.d]# /etc/init.d/xinetd restart
Stopping xinetd:                                           [FAILED]
Starting xinetd:                                           [  OK  ]
[root@pxeserver yum.repos.d]# netstat -nltup |grep tftp
[root@pxeserver yum.repos.d]# netstat -nltup |grep xinetd
udp        0      0 0.0.0.0:69                  0.0.0.0:*                               31485/xinetd

# install httpd
[root@pxeserver yum.repos.d]# yum install httpd -y
Loaded plugins: product-id, search-disabled-repos, security, subscription-manager
This system is not registered to Red Hat Subscription Management. You can use subscription-manager to register.
Setting up Install Process
Package httpd-2.2.15-53.el6.x86_64 already installed and latest version
Nothing to do
[root@pxeserver yum.repos.d]# rpm -ql httpd |grep httpd.conf
/etc/httpd/conf
...
[root@pxeserver yum.repos.d]# vim /etc/httpd/conf/httpd.conf
[root@pxeserver yum.repos.d]# cat /etc/httpd/conf/httpd.conf |grep "^ServerName"
ServerName 127.0.0.1:80

[root@pxeserver yum.repos.d]# /etc/init.d/httpd restart
Stopping httpd:                                            [  OK  ]
Starting httpd:                                            [  OK  ]
[root@pxeserver ~]# chkconfig dhcpd on
[root@pxeserver ~]# chkconfig httpd on

# 把镜像挂到http上
[root@pxeserver ~]# cd var/www/html/
[root@pxeserver html]# mkdir centos7.0
[root@pxeserver html]# mount -t iso9660 /dev/sr1 centos7.0
[root@pxeserver html]# ln -s /mnt rhel6.8
```

# 2.配置pxe


```bash
# 文件复制：需要将syslinux中的几个文件`pxelinux.0`,`vmlinuz`,`initrd.img`复制到tftp路径上，其他文件都可不用。
[root@pxeserver html]# yum -y install syslinux
[root@pxeserver html]# mkdir /var/lib/tftpboot/rhel6.8
[root@pxeserver html]# cp /usr/share/syslinux/pxelinux.0 /var/lib/tftpboot/rhel6.8
[root@pxeserver html]# cp /var/www/html/rhel6.8/isolinux/* /var/lib/tftpboot/rhel6.8

[root@pxeserver html]# mkdir -p /var/lib/tftpboot/rhel6.8/pxelinux.cfg
[root@pxeserver html]# cp /var/www/html/rhel6.8/isolinux/isolinux.cfg /var/lib/tftpboot/rhel6.8/pxelinux.cfg/default
...省略创建和复制centos7.0的pxe配置文件步骤
[root@pxeserver ~]# cd /var/lib/tftpboot/
[root@pxeserver tftpboot]# tree
.
├── centos7.0
│   ├── boot.msg
│   ├── initrd.img
│   ├── pxelinux.0
│   ├── pxelinux.cfg
│   │   ├── default
│   │   └── default.bak
│   ├── vesamenu.c32
│   └── vmlinuz
└── rhel6.8
    ├── initrd.img
    ├── pxelinux.0
    ├── pxelinux.cfg
    │   ├── 01-00-50-56-23-f9-14
    │   └── default.bak
    └── vmlinuz
    
# 修改启动菜单，默认加载菜单的顺序按照文件名称：
# 	1.01-mac地址；
# 	2.IP地址，转换为16进制
# 	3.default

# 这里用了一个mac地址的配置文件
[root@pxeserver tftpboot]# cat rhel6.8/pxelinux.cfg/01-00-50-56-23-f9-14
default kslinux
prompt 0

label kslinux
  menu label ^Install system with kickstart
  kernel vmlinuz
  append initrd=initrd.img ks=http://192.168.88.21/ksconfig/rhel6.8-ks.cfg ksdevice=eth0

# 编写ks配置文件，配置文件的写法略
[root@pxeserver html]# cd /var/www/html
[root@pxeserver html]# tree
.
├── centos7.0
	...
├── ksconfig
│   ├── anaconda-ks.cfg
│   ├── centos7.0-ks.cfg
│   └── rhel6.8-ks.cfg
└── rhel6.8
	...
```

# 说明

## 说明1：dhcpd.conf
`dhcpd.conf`配置文件是最重要的一个配置，如果只有一个类型的操作系统需要安装，可以：
```bash
subnet 192.168.88.0 netmask 255.255.255.0 {
        range 192.168.88.100 192.168.88.200;
        option subnet-mask 255.255.255.0;
        next-server 192.168.88.21;
        filename "/pxelinux.0";
       }
```
如果有几个类型，可以使用group，最好固定IP地址，这样可以保证在可控的范围内安装操作系统。
```bash
subnet 192.168.88.0 netmask 255.255.255.0 {
        range 192.168.88.100 192.168.88.200;
        option subnet-mask 255.255.255.0;
        #next-server 192.168.88.21;
        #filename "/pxelinux.0";
       }

group  {
        filename "/rhel6.8/pxelinux.0";
        next-server 192.168.88.21;

        host cpt01 { hardware ethernet 00:50:56:23:F9:14;fixed-address 192.168.88.22;}
       }

group  {
        filename "/centos7.0/pxelinux.0";
        next-server 192.168.88.21;

        host cpt02 { hardware ethernet 00:50:56:33:DC:57;fixed-address 192.168.88.23;}
       }
```

> 注意不要出现重启，无意中重装系统的窘境。

## 说明2：pxelinux.cfg配置文件

同样的，`pxelinux.cfg`中的启动菜单最好也按照mac地址进行命名。

```bash
[root@pxeserver tftpboot]# cat rhel6.8/pxelinux.cfg/01-00-50-56-23-f9-14
default kslinux
prompt 0

label kslinux
  menu label ^Install system with kickstart
  kernel vmlinuz
  append initrd=initrd.img ks=http://192.168.88.21/ksconfig/rhel6.8-ks.cfg ksdevice=eth0
```
> 可以使用`ksdevice`来指定网卡，但是需要注意的是centos7和6中的网卡名称的改变问题。

# 参考文件 

- [这里提到用grub4dos的pxe引导代码替换pexlinux.0那个文件,引导封装好的Pe的img](http://www.boobooke.com/m/dl.php?vid=5358)
- [KICKSTART无人值守安装](http://www.zyops.com/autoinstall-kickstart)
- [The Syslinux Project](http://www.syslinux.org/wiki/index.php?title=The_Syslinux_Project)