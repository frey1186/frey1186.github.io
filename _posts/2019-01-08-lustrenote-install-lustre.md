---
layout: post
title: Lustre学习笔记（2）-安装Lustre
date: 2019-01-08 12:00
tags: lustre
categories: public
typora-root-url: ..

---


准备四个节点，来自virtualbox的虚拟机

```bash
192.168.56.11 io1
192.168.56.12 io2
192.168.56.13 io3
192.168.56.14 io4
```

每个节点如下：

```bash
# 内核是7.6基础版本，不升级，参看lustre ChangeLog
[root@localhost ~]# uname -a
Linux io1 3.10.0-957.el7.x86_64 #1 SMP Thu Nov 8 23:39:32 UTC 2018 x86_64 x86_64 x86_64 GNU/Linux
[root@localhost ~]# cat /etc/redhat-release 
CentOS Linux release 7.6.1810 (Core) 
# CPU数量1核心，内存2G，操作系统外硬盘20G
[root@io1 ~]# cat /proc/cpuinfo |grep processor |wc -l
1
[root@io1 ~]# cat /proc/meminfo |grep -i memtotal
MemTotal: 2047164 kB
[root@io1 ~]# lsblk /dev/sdb 
NAME MAJ:MIN RM SIZE RO TYPE MOUNTPOINT
sdb 8:16 0 20G 0 disk 
# 网卡两个，enp0s3连接互联网，enp0s8内网
```


临时增加一个IP地址，按照节点的规划IP配置，以便使用ssh工具连接

```bash
ip l set enp0s8 up
ip a a 192.168.56.11/24 dev enp0s8
```

使用ssh工具连接后，配置基本信息

```bash
# 按照IP地址规划进行修改主机名和enp0s8的IP地址
hostnamectl set-hostname io1
echo "IPADDR=192.168.56.11" >> /etc/sysconfig/network-scripts/ifcfg-enp0s8
# 以下为所有节点都执行
echo "NETMASK=255.255.255.0" >> /etc/sysconfig/network-scripts/ifcfg-enp0s8
sed -i 's/ONBOOT=no/ONBOOT=yes/g' /etc/sysconfig/network-scripts/ifcfg-enp0s8
sed -i 's/BOOTPROTO=dhcp/BOOTPROTO=none/g' /etc/sysconfig/network-scripts/ifcfg-enp0s8
## enp0s3 在测试环境中为NAT，默认的dhcp就满足要求
sed -i 's/ONBOOT=no/ONBOOT=yes/g' /etc/sysconfig/network-scripts/ifcfg-enp0s3 
## 关闭selinux 和防火墙
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config 
systemctl disable firewalld
## 修改host表
for i in 1 2 3 4;do echo "192.168.56.1$i io$i">> /etc/hosts ;done
systemctl restart network
## 停止updates extras这两个repo，防止内核版本升级，只需要base一个repo即可
yum install yum-utils -y
yum-config-manager --disable updates extras
## 重启服务器
reboot
```

使用上篇（Lustre学习笔记（1）-编译Lustre）中编译完成的lustre-rpms安装包，在io1配置repo，使其他节点能够直接安装lustre软件包

```bash
# 解压包，解压后有lustre-server，lustre-client以及zfs-spl几个文件夹
tar -zxf lustre-rpms-2.12.0.tar.gz
yum install createrepo httpd -y 
for i in `ls`;do cd /root/releases/$i; createrepo .;done
mv /releases /var/www/html/
systemctl start httpd
systenctl enable httpd
# 创建一个新lustre.repo
> /etc/yum.repos.d/lustre.repo 
# 配置lustre.repo
cd /var/www/html/releases
for i in `ls`;do echo -e "[$i] \nname=$i \nbaseurl=http://io1/releases/$i \ngpgcheck=0 \n" >>/etc/yum.repos.d/lustre.repo ; done
```

lustre.repo完成大概如下所示：

```bash
[root@io2 ~]# cat /etc/yum.repos.d/lustre.repo 
[lustre-client] 
name=lustre-client 
baseurl=http://io1/releases/lustre-client 
gpgcheck=0 

[lustre-server] 
name=lustre-server 
baseurl=http://io1/releases/lustre-server 
gpgcheck=0 

[ofed] 
name=ofed 
baseurl=http://io1/releases/ofed 
gpgcheck=0 

[zfs-spl] 
name=zfs-spl 
baseurl=http://io1/releases/zfs-spl 
gpgcheck=0 
```

将lustre.repo复制到其他几个节点

```bash
for i in 2 3 4;do scp /etc/yum.repos.d/lustre.repo root@io$i:/etc/yum.repos.d/lustre.repo ;done
```

安装lustre-server，涉及的依赖包均来自base-repo，安装包的选择可以参看http://wiki.lustre.org/Installing_the_Lustre_Software#Lustre_Servers_with_ZFS_OSD_Support

```bash
for i in 1 2 3 4;do ssh io$i yum -y --enablerepo lustre-server --disablerepo=lustre-client install lustre-osd-zfs-mount lustre lustre-resource-agents zfs;done
```

如果要安装lustre-client，如下：

```bash
yum -y --enablerepo lustre-client--disablerepo=lustre-server install lustre-client
```

### 参考
- http://wiki.lustre.org/Installing_the_Lustre_Software
