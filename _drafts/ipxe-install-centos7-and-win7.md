---
layout: post
title: Install Centos7 and Win7 with iPXE
date: 2018-09-10 12:00
author: felo
tags: pxe
typora-root-url: ../../yangfeiffei.github.io
---

iPXE是一个开源的网络启动固件，它提供完整的PXE功能同时，还有更高级的特性：

- 启动自http服务器
- 启动自iSCSI或者SAN
- 启动自FCOE SAN
- 启动自Infiniband
- 通过脚本控制启动进程

可以通过iPXE去代替现有网卡中的PXE ROM，iPXE是免费的开源软件，可以根据自己的需求修改编译它。

# 0.准备一个iPXE环境

## 0.1 基本原理

`PXE`(`preboot execute environment`，预启动执行环境)，是实现网络安装Linux或者UNIX操作系统的常用方式，其工作方式简单来说如下所示：

- 客户机开机后，选择网卡启动
- 网卡启动过程中，从DHCP服务器中获取一个IP地址，同时从DHCP服务器获得一个next-server的位置，在这个服务器上获得开机启动文件，这个文件可以有两种方式获得
  - `syslinux`：这是一个常用的软件包，里面有开机相关的基本配置，只需要简单修改就可以实现安装操作系统或者网络启动，其中pxelinux.0，就是这个开机启动文件；
  - `ipxe`：这是另一个常用的方式，功能更强大，更灵活。
- 获取Linux内核和initrd镜像文件，启动操作系统或或者安装程序。

## 0.2 操作步骤

按照syslinux部署pxe的方式进行安装，这里不赘述。使用ipxe需要安装httpd服务，必要的时候进行安装。

```bash
yum install httpd  -y
```

为了运行ipxe，需要修改dhcpd.conf，符合ipxe的运行

- 增加一些ipxe的专用参数，
```bash
  option space ipxe;
  option ipxe-encap-opts code 175 = encapsulate ipxe;
  option ipxe.priority code 1 = signed integer 8;
  option ipxe.keep-san code 8 = unsigned integer 8;
  option ipxe.skip-san-boot code 9 = unsigned integer 8;
  option ipxe.syslogs code 85 = string;
  option ipxe.cert code 91 = string;
  option ipxe.privkey code 92 = string;
  option ipxe.crosscert code 93 = string;
  option ipxe.no-pxedhcp code 176 = unsigned integer 8;
  option ipxe.bus-id code 177 = string;
  option ipxe.san-filename code 188 = string;
  option ipxe.bios-drive code 189 = unsigned integer 8;
  option ipxe.username code 190 = string;
  option ipxe.password code 191 = string;
  option ipxe.reverse-username code 192 = string;
  option ipxe.reverse-password code 193 = string;
  option ipxe.version code 235 = string;
  option iscsi-initiator-iqn code 203 = string;
  # Feature indicators
  option ipxe.pxeext code 16 = unsigned integer 8;
  option ipxe.iscsi code 17 = unsigned integer 8;
  option ipxe.aoe code 18 = unsigned integer 8;
  option ipxe.http code 19 = unsigned integer 8;
  option ipxe.https code 20 = unsigned integer 8;
  option ipxe.tftp code 21 = unsigned integer 8;
  option ipxe.ftp code 22 = unsigned integer 8;
  option ipxe.dns code 23 = unsigned integer 8;
  option ipxe.bzimage code 24 = unsigned integer 8;
  option ipxe.multiboot code 25 = unsigned integer 8;
  option ipxe.slam code 26 = unsigned integer 8;
  option ipxe.srp code 27 = unsigned integer 8;
  option ipxe.nbi code 32 = unsigned integer 8;
  option ipxe.pxe code 33 = unsigned integer 8;
  option ipxe.elf code 34 = unsigned integer 8;
  option ipxe.comboot code 35 = unsigned integer 8;
  option ipxe.efi code 36 = unsigned integer 8;
  option ipxe.fcoe code 37 = unsigned integer 8;
  option ipxe.vlan code 38 = unsigned integer 8;
  option ipxe.menu code 39 = unsigned integer 8;
  option ipxe.sdi code 40 = unsigned integer 8;
  option ipxe.nfs code 41 = unsigned integer 8;
```

修改在filename,

```bash
if exists user-class and option user-class = "iPXE" { 
      filename "http://192.168.56.171/c7.cfg";
  } 
  else if option client-arch != 00:00 { 
     filename "ipxe.efi";
  }
  else { 
      filename "undionly.kpxe";
  }

```
其中，c7.cfg是ipxe的主要配置文件，类似于syslinux中的pxelinux.cfg/default配置文件；ipxe.efi支持UEFI

完成后的dhcpd.conf如下所示：

```bash
subnet 192.168.56.0 netmask 255.255.255.0 { 
        range 192.168.56.100 192.168.56.200;
        option subnet-mask 255.255.255.0;
        next-server 192.168.56.171;
        #filename "/pxelinux.0";
        if exists user-class and option user-class = "iPXE" { 
            filename "http://192.168.56.171/c7.cfg";
            } 
        else if option client-arch != 00:00 { 
            filename "ipxe.efi";
            }
        else { 
            filename "undionly.kpxe";
            }
        } 
}
```
下载需要的几个文件
```bash

```




# net install a centos 7 






# net install a win 7

## make a winpe for win7

## install a win7
