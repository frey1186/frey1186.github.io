---
layout: post
title: 简单的dhcp配置记录
date: 2017-11-13 12:00
author: felo
tags: redhat dhcp
---


Dynamic Host Configuration Protocol (DHCP)：为客户端自动配置tcpip的一种网络协议。
可以为客户端配置：IP地址，网关，dns服务器等；

# 1.配置DHCPV4服务器

环境：
```bash
[root@xcatmn ~]# cat /etc/redhat-release 
Red Hat Enterprise Linux Server release 6.9 (Santiago)
[root@xcatmn ~]# uname -a
Linux xcatmn 2.6.32-696.el6.x86_64 #1 SMP Tue Feb 21 00:53:17 EST 2017 x86_64 x86_64 x86_64 GNU/Linux
```

使用root用户进行安装

```bash
[root@xcatmn ~]# yum -y install dhcp
```

安装后生成一个空文件`/etc/dhcp/dhcpd.conf`
```bash
[root@xcatmn ~]# cat /etc/dhcp/dhcpd.conf
[root@xcatmn ~]# ls -l /usr/share/doc/dhcp-4.1.1/dhcpd.conf.sample 
-rw-r--r--. 1 root root 3262 Aug 13  2002 /usr/share/doc/dhcp-4.1.1/dhcpd.conf.sample
```
这个文件的模板来自`/usr/share/doc/dhcp- <version>/dhcpd.conf.sample`。
`/var/lib/dhcpd/dhcpd.leases`保存客户端的数据库。

## 1.1 配置文件`/etc/dhcp/dhcpd.conf`

> 每次修改配置文件后，需要重启dhcp服务，当然也可以使用omshell进行在线修改。

例子1：
```bash
subnet 192.168.1.0 netmask 255.255.255.0 {
	option routers	192.168.1.254;
	option subnet-mask	255.255.255.0;
	option domain-search	"example.com";
	option domain-name-servers	192.168.1.1;
	option time-offset	-18000;
	range 192.168.1.10 192.168.1.100;
}
```

例子2：
```bash
default-lease-time 600;
max-lease-time 7200;
option subnet-mask 255.255.255.0;
option broadcast-address 192.168.1.255;
option routers 192.168.1.254;
option domain-name-servers 192.168.1.1, 192.168.1.2; 
option domain-search "example.com";
subnet 192.168.1.0 netmask 255.255.255.0 {
	range 192.168.1.10 192.168.1.100; 
}
```


例子3：使用固定IP地址
```bash
host apex {
	option host-name "apex.example.com"; 
	hardware ethernet 00:A0:78:8E:9E:AA; 
	fixed-address 192.168.1.4;
}
```



例子4：
```bash
shared-network name {
option domain-search		"test.redhat.com"; 
option domain-name-servers		ns1.redhat.com, ns2.redhat.com; 
option routers		192.168.0.254;
#more parameters for EXAMPLE shared-network 
subnet 192.168.1.0 netmask 255.255.252.0 {
	range 192.168.1.1 192.168.1.254; 
	}
subnet 192.168.2.0 netmask 255.255.252.0 { 
	#parameters for subnet
	range 192.168.2.1 192.168.2.254;
	} 
}

```


例子5：
```bash
group {
	option routers		192.168.1.254;
	option subnet-mask		255.255.255.0;
	option domain-search 		"example.com";
	option domain-name-servers 		192.168.1.1;
	option time-offset		-18000; # Eastern Standard Time
	host apex {
		option host-name "apex.example.com"; 
		hardware ethernet 00:A0:78:8E:9E:AA; 
		fixed-address 192.168.1.4;
	}
	host raleigh {
		option host-name "raleigh.example.com"; 
		hardware ethernet 00:A1:DD:74:C3:F2; 
		fixed-address 192.168.1.6;
	} 
}
```

## 1.2 租约数据库（Lease Database）

- 实际上都保存在这里：`/var/lib/dhcpd/dhcpd.leases `；
- 不要修改这个文件，这是一个自动保存的文件；
- 里面所有的时间都是UTC时间，不是本地时间；
- 老的文件会被保存为`dhcpd.leases~`；
- 如果在文件被重命名后，系统崩溃或者dhcp被kill的情况，可以将`dhcpd.leases~`复制回`dhcpd.leases`;


## 1.3 开启或关闭dhcp服务

使用`/sbin/service dhcpd start`启动，使用`/sbin/service dhcpd stop`停止服务。
还有几个注意的地方：

- 第一次启动没有`dhcpd.leases`会失败，可以手动创建`touch /var/lib/dhcpd/dhcpd.leases`；
- 如果这个服务器还运行了bind，那么会自动创建`dhcpd.leases`文件；
- 如果服务器有多个网卡，需要在`/etc/sysconfig/dhcpd`文件中写入DHCPDARGS
```bash
DHCPDARGS=eth0
```
- 在`/etc/sysconfig/dhcpd`里还有其他选项
	- -p：指定端口，默认端口67；
	- -f：让进程前台运行，用于debug
	- -d：写日志到message
	- -cf filename：指定配置文件，默认/etc/dhcp/dhcpd.conf
	- -lf filename：指定数据库文件，默认/var/lib/dhcpd/dhcpd.leases
	- -q：启动是不显示多余信息


## 1.4 DHCP轮换客户端

DHCP Relay Agent (dhcrelay)允许将dhcp或bootp请求从一个没有dhcp的子网轮换到一个或多个有dhcp的子网中。
在`/etc/sysconfig/dhcrelay`中写入INTERFACES参数作为监听接口，想要启动DHCP Relay Agent，使用`service dhcrelay start`。


# 2.配置DHCPV4客户端

在`/etc/sysconfig/network-scripts/ifcfg-eth0 `写入：
```bash
DEVICE=eth0
BOOTPROTO=dhcp
ONBOOT=yes
```
还有两个参数：
- DHCP_HOSTNAME：如果dhcp服务器要求客户端在给ip之前指定一个主机名
- PEERDNS：
	- yes：通过服务器修改/etc/resolv.conf，默认情况
	- no：不修改/etc/resolv.conf

# 3. 配置多子网dhcp服务器
首先在` /etc/sysconfig/dhcpd`指定使用哪个网卡来监听客户端的dhcp请求。

```bash
DHCPDARGS="eth0 eth1";  #希望两个网卡都在监听
DHCPDARGS="eth0";			  #只希望一个网卡监听
```

例子：
```bash
default-lease-time 600;
max-lease-time 7200;
subnet 10.0.0.0 netmask 255.255.255.0 {
	option subnet-mask 255.255.255.0; 
	option routers 10.0.0.1;
	range 10.0.0.5 10.0.0.15;
}
subnet 172.16.0.0 netmask 255.255.255.0 {
	option subnet-mask 255.255.255.0; 
	option routers 172.16.0.1;
	range 172.16.0.5 172.16.0.15;
}
host example0 {
	hardware ethernet 00:1A:6B:6A:2E:0B;
	fixed-address 10.0.0.20; 
}
host example1 {
	hardware ethernet 00:1A:6B:6A:2E:0B; 
	fixed-address 172.16.0.20;
}
```
> 需要注意的是：
- host后面的主机名需要唯一，不然`/var/log/messages`中会报错；
- 两个主机也不能使用相同的ip地址；

# 4. 其他

- dhcpd man page — Describes how the DHCP daemon works.
- dhcpd.conf man page — Explains how to configure the DHCP configuration file; includes some examples.
- dhcpd.leases man page — Describes a persistent database of leases.
- dhcp-options man page — Explains the syntax for declaring DHCP options in dhcpd.conf; includes some examples.
- dhcrelay man page — Explains the DHCP Relay Agent and its configuration options.
- /usr/share/doc/dhcp-<version>/ — Contains sample files, README files, and release notes for current versions of the DHCP service.
