---
layout: post
title: Oracle RAC 11gR2 & OEL r6u4 install test
date: 2018-01-09 12:00
author: felo
tags: oracle rac
categories: public
typora-root-url: ..
---


# 0.准备工作
## 0.1 安装操作系统
node01节点

```bash
[root@node01 ~]# df -h
Filesystem            Size  Used Avail Use% Mounted on
/dev/sda3              91G  2.8G   84G   4% /
tmpfs                 2.0G  100K  2.0G   1% /dev/shm
/dev/sda1             194M   51M  134M  28% /boot
/dev/sdb1              99G  188M   94G   1% /data
/dev/sr0              3.5G  3.5G     0 100% /mnt
[root@node01 ~]#
[root@node01 ~]# uname -a
Linux node01 2.6.39-400.17.1.el6uek.x86_64 #1 SMP Fri Feb 22 18:16:18 PST 2013 x86_64 x86_64 x86_64 GNU/Linux
[root@node01 ~]# cat /etc/redhat-release
Red Hat Enterprise Linux Server release 6.4 (Santiago)
[root@node01 ~]# ip a
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 16436 qdisc noqueue state UNKNOWN
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
    inet6 ::1/128 scope host
       valid_lft forever preferred_lft forever
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP qlen 1000
    link/ether 08:00:27:25:5e:dc brd ff:ff:ff:ff:ff:ff
    inet 192.168.56.181/24 brd 192.168.56.255 scope global eth0
    inet6 fe80::a00:27ff:fe25:5edc/64 scope link
       valid_lft forever preferred_lft forever
3: eth1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP qlen 1000
    link/ether 08:00:27:d0:e4:f0 brd ff:ff:ff:ff:ff:ff
    inet 192.168.57.181/24 brd 192.168.56.255 scope global eth1
    inet6 fe80::a00:27ff:fed0:e4f0/64 scope link
       valid_lft forever preferred_lft forever
[root@node02 ~]# lsblk
NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
sda      8:0    0  100G  0 disk
├─sda1   8:1    0  200M  0 part /boot
├─sda2   8:2    0    8G  0 part [SWAP]
└─sda3   8:3    0 91.8G  0 part /
sdb      8:16   0  100G  0 disk
└─sdb1   8:17   0  100G  0 part /data
sdc      8:32   0    5G  0 disk
sr0     11:0    1  3.5G  0 rom  /mnt
```

node02节点：

```bash
[root@node02 ~]# uname -a
Linux node02 2.6.39-400.17.1.el6uek.x86_64 #1 SMP Fri Feb 22 18:16:18 PST 2013 x86_64 x86_64 x86_64 GNU/Linux
[root@node02 ~]# cat /etc/redhat-release
Red Hat Enterprise Linux Server release 6.4 (Santiago)
[root@node02 ~]# df -h
Filesystem            Size  Used Avail Use% Mounted on
/dev/sda3              91G  2.8G   84G   4% /
tmpfs                 2.0G   88K  2.0G   1% /dev/shm
/dev/sda1             194M   51M  134M  28% /boot
/dev/sdb1              99G  188M   94G   1% /data
/dev/sr0              3.5G  3.5G     0 100% /mnt
[root@node02 ~]# ip a
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 16436 qdisc noqueue state UNKNOWN
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
    inet6 ::1/128 scope host
       valid_lft forever preferred_lft forever
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP qlen 1000
    link/ether 08:00:27:b2:51:e9 brd ff:ff:ff:ff:ff:ff
    inet 192.168.56.182/24 brd 192.168.56.255 scope global eth0
    inet6 fe80::a00:27ff:feb2:51e9/64 scope link
       valid_lft forever preferred_lft forever
3: eth1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP qlen 1000
    link/ether 08:00:27:e7:3b:6f brd ff:ff:ff:ff:ff:ff
    inet 192.168.57.182/24 brd 192.168.57.255 scope global eth1
    inet6 fe80::a00:27ff:fee7:3b6f/64 scope link
       valid_lft forever preferred_lft forever
[root@node02 ~]# lsblk
NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
sda      8:0    0  100G  0 disk
├─sda1   8:1    0  200M  0 part /boot
├─sda2   8:2    0    8G  0 part [SWAP]
└─sda3   8:3    0 91.8G  0 part /
sdb      8:16   0  100G  0 disk
└─sdb1   8:17   0  100G  0 part /data
sdc      8:32   0    5G  0 disk
sr0     11:0    1  3.5G  0 rom  /mnt
```
## 0.2 配置准备

### 0.2.0 修改hosts文件

```bash
[root@node01 ~]# vim /etc/hosts
[root@node01 ~]# cat /etc/hosts
127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4
::1         localhost localhost.localdomain localhost6 localhost6.localdomain6

192.168.56.181  node01
192.168.56.182  node02


192.168.57.181  node01-priv
192.168.57.182  node02-priv


192.168.56.183  node01-vip
192.168.56.184  node02-vip

192.168.56.185  cluster02
192.168.56.186  cluster02
192.168.56.187  cluster02

[root@node01 ~]# scp /etc/hosts 192.168.56.182:/etc/hosts
root@192.168.56.182's password:
hosts                                  100%  399     0.4KB/s   00:00
```

### 0.2.1 配置本地yum源和安装preinstall

```bash
[root@node01 ~]# cd /etc/yum.repos.d/
[root@node01 yum.repos.d]# ls
public-yum-ol6.repo
[root@node01 yum.repos.d]# vim public-yum-ol6.repo
[root@node01 yum.repos.d]# cat public-yum-ol6.repo
[cdrom]
name=Oracle Linux cdrom
baseurl=file:///mnt
gpgcheck=0
enabled=1
[root@node01 yum.repos.d]# scp public-yum-ol6.repo  192.168.56.182:/etc/yum.repos.d/public-yum-ol6.repo
The authenticity of host '192.168.56.182 (192.168.56.182)' can't be established.
RSA key fingerprint is e3:41:74:6f:6a:c8:70:5a:40:d3:35:7f:72:bc:9d:e9.
Are you sure you want to continue connecting (yes/no)? yes
Warning: Permanently added '192.168.56.182' (RSA) to the list of known hosts.
root@192.168.56.182's password:
public-yum-ol6.repo                                                                                100%   73     0.1KB/s   00:00
[root@node01 yum.repos.d]#
[root@node01 yum.repos.d]# yum clean all
yLoaded plugins: refresh-packagekit, security
Cleaning repos: cdrom
Cleaning up Everything                                                                      [root@node01 yum.repos.d]# yum makecache
Loaded plugins: refresh-packagekit, security
cdrom                                                                                                         | 3.7 kB     00:00 ...
cdrom/filelists_db                                                                                            | 3.2 MB     00:00 ...
cdrom/primary_db                                                                                              | 2.9 MB     00:00 ...
cdrom/other_db                                                                                                | 1.2 MB     00:00 ...
cdrom/group_gz                                                                                                | 203 kB     00:00 ...
Metadata Cache Created
```
```bash
[root@node01 ~]# yum list |grep preinstall
oracle-rdbms-server-11gR2-preinstall.x86_64
[root@node01 ~]# yum install oracle-rdbms-server-11gR2-preinstall.x86_64 -y
...
[root@node01 ~]# ssh node02
The authenticity of host 'node02 (192.168.56.182)' can't be established.
RSA key fingerprint is e3:41:74:6f:6a:c8:70:5a:40:d3:35:7f:72:bc:9d:e9.
Are you sure you want to continue connecting (yes/no)? yes
Warning: Permanently added 'node02' (RSA) to the list of known hosts.
root@node02's password:
Last login: Sun Jan  7 20:33:23 2018 from 192.168.56.1
[root@node02 ~]# yum install oracle-rdbms-server-11gR2-preinstall -y
...
```

### 0.2.2 创建其他用户和用户组
oracle用户、oinstall组和dba组已经自动安装完成了，不用再次创建。

```bash
[root@node01 ~]# groupadd -g 54323 asmadmin
[root@node01 ~]# groupadd -g 54324 asmoper
[root@node01 ~]# groupadd -g 54325 asmdba
[root@node01 ~]# groupadd -g 54326 oper
[root@node01 ~]# useradd -g oinstall -G asmadmin,asmoper,asmdba,dba grid
[root@node01 ~]# ssh node02
root@node02's password:
Last login: Sun Jan  7 20:50:18 2018 from node01
[root@node02 ~]# groupadd -g 54323 asmadmin
[root@node02 ~]# groupadd -g 54324 asmoper
[root@node02 ~]# groupadd -g 54325 asmdba
[root@node02 ~]# groupadd -g 54326 oper
[root@node02 ~]# useradd -g oinstall -G asmadmin,asmoper,asmdba,dba grid
[root@node02 ~]# exit
logout
Connection to node02 closed.
```

修改用户密码

```bash
[root@node01 ~]# passwd oracle
Changing password for user oracle.
New password:
BAD PASSWORD: it is based on a dictionary word
BAD PASSWORD: is too simple
Retype new password:
passwd: all authentication tokens updated successfully.
[root@node01 ~]# passwd grid
Changing password for user grid.
New password:
BAD PASSWORD: it is too short
BAD PASSWORD: is too simple
Retype new password:
passwd: all authentication tokens updated successfully.
[root@node01 ~]# ssh node02
root@node02's password:
Permission denied, please try again.
root@node02's password:
Last login: Sun Jan  7 20:59:07 2018 from node01
[root@node02 ~]#
[root@node02 ~]# passwd oracle
Changing password for user oracle.
New password:
BAD PASSWORD: it is based on a dictionary word
BAD PASSWORD: is too simple
Retype new password:
passwd: all authentication tokens updated successfully.
[root@node02 ~]# passwd grid
Changing password for user grid.
New password:
BAD PASSWORD: it is too short
BAD PASSWORD: is too simple
Retype new password:
passwd: all authentication tokens updated successfully.
[root@node02 ~]#
[root@node02 ~]# exit
logout
Connection to node02 closed.
[root@node01 ~]#
```

### 0.2.3 配置ssh免密码

```bash
[root@node01 ~]# su - oracle
[oracle@node01 ~]$ ssh-keygen
Generating public/private rsa key pair.

Enter file in which to save the key (/home/oracle/.ssh/id_rsa): Created directory '/home/oracle/.ssh'.
Enter passphrase (empty for no passphrase):
Enter same passphrase again:
Your identification has been saved in /home/oracle/.ssh/id_rsa.
Your public key has been saved in /home/oracle/.ssh/id_rsa.pub.
The key fingerprint is:
f1:3e:a4:d8:bf:6e:05:bf:e8:74:c4:8d:b3:41:d2:91 oracle@node01
The key's randomart image is:
+--[ RSA 2048]----+
|            ..   |
|           .E.   |
|        . . o    |
|         o.+ o   |
|        S oo* .  |
|       o + .o+   |
|      . o +oo.   |
|         ooo.    |
|         +=.     |
+-----------------+
[oracle@node01 ~]$ ssh-copy-id node02
The authenticity of host 'node02 (192.168.56.182)' can't be established.
RSA key fingerprint is e3:41:74:6f:6a:c8:70:5a:40:d3:35:7f:72:bc:9d:e9.
Are you sure you want to continue connecting (yes/no)? yes
Warning: Permanently added 'node02,192.168.56.182' (RSA) to the list of known hosts.
oracle@node02's password:
Now try logging into the machine, with "ssh 'node02'", and check in:

  .ssh/authorized_keys

to make sure we haven't added extra keys that you weren't expecting.

[oracle@node01 ~]$ ssh-copy-id node01
The authenticity of host 'node01 (192.168.56.181)' can't be established.
RSA key fingerprint is e3:41:74:6f:6a:c8:70:5a:40:d3:35:7f:72:bc:9d:e9.
Are you sure you want to continue connecting (yes/no)? yes
Warning: Permanently added 'node01,192.168.56.181' (RSA) to the list of known hosts.
oracle@node01's password:
Now try logging into the machine, with "ssh 'node01'", and check in:

  .ssh/authorized_keys

to make sure we haven't added extra keys that you weren't expecting.

[oracle@node01 ~]$ exit
logout
[root@node01 ~]# su - grid
[grid@node01 ~]$ ssh-keygen -q -t rsa -N "" -f ~/.ssh/id_rsa
[grid@node01 ~]$ ssh-copy-id node02
The authenticity of host 'node02 (192.168.56.182)' can't be established.
RSA key fingerprint is e3:41:74:6f:6a:c8:70:5a:40:d3:35:7f:72:bc:9d:e9.
Are you sure you want to continue connecting (yes/no)? yes
Warning: Permanently added 'node02,192.168.56.182' (RSA) to the list of known hosts.
grid@node02's password:
Now try logging into the machine, with "ssh 'node02'", and check in:

  .ssh/authorized_keys

to make sure we haven't added extra keys that you weren't expecting.

[grid@node01 ~]$ ssh-copy-id node01
The authenticity of host 'node01 (192.168.56.181)' can't be established.
RSA key fingerprint is e3:41:74:6f:6a:c8:70:5a:40:d3:35:7f:72:bc:9d:e9.
Are you sure you want to continue connecting (yes/no)? yes
Warning: Permanently added 'node01,192.168.56.181' (RSA) to the list of known hosts.
grid@node01's password:
Now try logging into the machine, with "ssh 'node01'", and check in:

  .ssh/authorized_keys

to make sure we haven't added extra keys that you weren't expecting.

[grid@node01 ~]$
[grid@node01 ~]$ exit
logout
[root@node01 ~]# sed -i "s/.*StrictHostKeyChecking.*/StrictHostKeyChecking no/" /etc/ssh/ssh_config
[root@node01 ~]# service sshd restart
Stopping sshd:                                             [  OK  ]
Starting sshd:                                             [  OK  ]
[root@node01 ~]#
[root@node01 ~]# ssh node02
root@node02's password:
Permission denied, please try again.
root@node02's password:
Last login: Sun Jan  7 21:00:29 2018 from node01
[root@node02 ~]#
[root@node02 ~]# sed -i "s/.*StrictHostKeyChecking.*/StrictHostKeyChecking no/" /etc/ssh/ssh_config
[root@node02 ~]# service sshd restart
Stopping sshd:                                             [  OK  ]
Starting sshd:                                             [  OK  ]
[root@node02 ~]#
[root@node02 ~]# su - oracle
[oracle@node02 ~]$ ssh-keygen -q -t rsa -N "" -f ~/.ssh/id_rsa
[oracle@node02 ~]$ ssh-copy-id node01
Warning: Permanently added 'node01,192.168.56.181' (RSA) to the list of known hosts.
oracle@node01's password:
Now try logging into the machine, with "ssh 'node01'", and check in:

  .ssh/authorized_keys

to make sure we haven't added extra keys that you weren't expecting.

[oracle@node02 ~]$ ssh-copy-id node02
Warning: Permanently added 'node02,192.168.56.182' (RSA) to the list of known hosts.
oracle@node02's password:
Now try logging into the machine, with "ssh 'node02'", and check in:

  .ssh/authorized_keys

to make sure we haven't added extra keys that you weren't expecting.

[oracle@node02 ~]$ exit
logout
[root@node02 ~]# su - grid
[grid@node02 ~]$ ssh-keygen -q -t rsa -N "" -f ~/.ssh/id_rsa
[grid@node02 ~]$ ssh-copy-id node01
Warning: Permanently added 'node01,192.168.56.181' (RSA) to the list of known hosts.
grid@node01's password:
Now try logging into the machine, with "ssh 'node01'", and check in:

  .ssh/authorized_keys

to make sure we haven't added extra keys that you weren't expecting.

[grid@node02 ~]$ ssh-copy-id node02
Warning: Permanently added 'node02,192.168.56.182' (RSA) to the list of known hosts.
grid@node02's password:
Now try logging into the machine, with "ssh 'node02'", and check in:

  .ssh/authorized_keys

to make sure we haven't added extra keys that you weren't expecting.

[grid@node02 ~]$
[grid@node02 ~]$ exit
logout
[root@node02 ~]# exit
logout
Connection to node02 closed.
```

### 0.2.4 创建目录并修改权限

```bash
[root@node01 ~]# mkdir -p /u01/app/grid
[root@node01 ~]# ssh node02 mkdir -p /u01/app/grid
root@node02's password:
[root@node01 ~]# mkdir -p  /u01/app/11.2.0/grid
[root@node01 ~]# ssh node02 mkdir -p  /u01/app/11.2.0/grid
root@node02's password:
[root@node01 ~]# chown -R grid:oinstall /u01
[root@node01 ~]# mkdir /u01/app/oracle
[root@node01 ~]# chown -R oracle:oinstall /u01/app/oracle/
[root@node01 ~]# chmod -R 775 /u01
[root@node01 ~]# ssh node02
root@node02's password:
Last login: Sun Jan  7 21:04:52 2018 from node01
[root@node02 ~]# chown -R grid:oinstall /u01
[root@node02 ~]# mkdir /u01/app/oracle
[root@node02 ~]# chown -R oracle:oinstall /u01/app/oracle/
[root@node02 ~]# chmod -R 775 /u01
[root@node02 ~]# exit
logout
Connection to node02 closed.
```

### 0.2.5 上传介质

```bash
localhost:linux$ scp p13390677_112040_Linux-x86-64_1of7.zip root@192.168.56.181:/data/
The authenticity of host '192.168.56.181 (192.168.56.181)' can't be established.
RSA key fingerprint is SHA256:LvCtPnnZkqu9KXfXR/uWJk1nR3Rvb3mYQWz1uLKhd5Q.
Are you sure you want to continue connecting (yes/no)? yes
Warning: Permanently added '192.168.56.181' (RSA) to the list of known hosts.
root@192.168.56.181's password: 
p13390677_112040_Linux-x86-64_1of7.zip        100% 1331MB  36.9MB/s   00:36    
localhost:linux$ scp p13390677_112040_Linux-x86-64_2of7.zip root@192.168.56.181:/data/
root@192.168.56.181's password: 
p13390677_112040_Linux-x86-64_2of7.zip        100% 1098MB  43.1MB/s   00:25    
localhost:linux$ scp p13390677_112040_Linux-x86-64_3of7.zip root@192.168.56.181:/data/
root@192.168.56.181's password: 
p13390677_112040_Linux-x86-64_3of7.zip        100% 1149MB  37.2MB/s   00:30    
localhost:linux$ 
```

解压3_of_7.zip

```bash
修改权限
[root@node01 data]# chown -R grid:oinstall /data
[root@node01 data]# su - grid
[grid@node01 ~]$ cd /data/
[grid@node01 data]$ unzip p13390677_112040_Linux-x86-64_3of7.zip
...
```

### 0.2.6 停止ntp服务并配置dns服务

本部分可以在`runcluvfy.sh`之后再进行调整

停止ntp

```bash
[root@node01 ~]# mv /etc/ntp.conf /etc/ntp.conf.old
[root@node01 ~]# ssh node02 mv /etc/ntp.conf /etc/ntp.conf.old
root@node02's password:
```

配置dns,这里使用db-server（192.168.56.176）来配置

```bash
[root@db-server ~]# cat /etc/resolv.conf
# Generated by NetworkManager


# No nameservers found; try putting DNS servers into your
# ifcfg files in /etc/sysconfig/network-scripts like so:
#
# DNS1=xxx.xxx.xxx.xxx
# DNS2=xxx.xxx.xxx.xxx
# DOMAIN=lab.foo.com bar.foo.com
[root@db-server ~]# vim /etc/resolv.conf
[root@db-server ~]# cat /etc/resolv.conf
# Generated by NetworkManager


# No nameservers found; try putting DNS servers into your
# ifcfg files in /etc/sysconfig/network-scripts like so:
#
# DNS1=xxx.xxx.xxx.xxx
# DNS2=xxx.xxx.xxx.xxx
# DOMAIN=lab.foo.com bar.foo.com

search localdomain
nameserver 192.168.56.176
[root@db-server ~]# chattr +i /etc/resolv.conf
[root@db-server ~]# vim /etc/named.conf
[root@db-server ~]# cat /etc/named.conf
//
// named.conf
//
// Provided by Red Hat bind package to configure the ISC BIND named(8) DNS
// server as a caching only nameserver (as a localhost DNS resolver only).
//
// See /usr/share/doc/bind*/sample/ for example named configuration files.
//

options {
        listen-on port 53 { any; };
        listen-on-v6 port 53 { ::1; };
        directory       "/var/named";
        dump-file       "/var/named/data/cache_dump.db";
        statistics-file "/var/named/data/named_stats.txt";
        memstatistics-file "/var/named/data/named_mem_stats.txt";
        allow-query     { any; };
        recursion yes;

//      dnssec-enable yes;
//      dnssec-validation yes;
//      dnssec-lookaside auto;

        /* Path to ISC DLV key */
//      bindkeys-file "/etc/named.iscdlv.key";

//      managed-keys-directory "/var/named/dynamic";
};

logging {
        channel default_debug {
                file "data/named.run";
                severity dynamic;
        };
};

zone "." IN {
        type hint;
        file "named.ca";
};

include "/etc/named.rfc1912.zones";
//include "/etc/named.root.key";

[root@db-server ~]#
[root@db-server ~]# vim /etc/named.rfc1912.zones
[root@db-server ~]# tail -n 10 /etc/named.rfc1912.zones
zone "f.com" IN {
        type master;
        file "f.com.zone";
        allow-update { none; };
};
zone "56.168.192.in-addr.arpa" IN {
        type master;
        file "192.168.56.arpa";
        allow-update { none; };
};
[root@db-server ~]# cd /var/named/
[root@db-server named]# cp -p named.localhost f.com.zone
[root@db-server named]# cp -p named.localhost 192.168.56.arpa
[root@db-server named]# vim f.com.zone
[root@db-server named]# cat f.com.zone
$TTL 1D
@       IN SOA  @ rname.invalid. (
                                        0       ; serial
                                        1D      ; refresh
                                        1H      ; retry
                                        1W      ; expire
                                        3H )    ; minimum
        NS      @
        A       192.168.56.176
        AAAA    ::1

dns     A       192.168.56.176
DNS1    CNAME   dns
ftp     A       192.168.56.176
mail    A       192.168.56.176

cluster02       A       192.168.56.185
cluster02       A       192.168.56.186
cluster02       A       192.168.56.187

@ MX   5       mail.localdomain

$GENERATE 10-250        stu$ A 192.168.56.$
[root@db-server named]# vim 192.168.56.arpa
[root@db-server named]#
[root@db-server named]#
[root@db-server named]# cat 192.168.56.arpa
$TTL 1D
@       IN SOA  @ rname.invalid. (
                                        0       ; serial
                                        1D      ; refresh
                                        1H      ; retry
                                        1W      ; expire
                                        3H )    ; minimum
        NS      @
        A       127.0.0.1
        AAAA    ::1


176     PTR     dns

185     PTR     cluster02.f.com
186     PTR     cluster02.f.com
187     PTR     cluster02.f.com
[root@db-server named]# /etc/rc.d/init.d/named restart
Stopping named:                                            [  OK  ]
Generating /etc/rndc.key:                                  [  OK  ]
Starting named:                                            [  OK  ]
[root@db-server named]#
[root@db-server named]# netstat -anp |grep :53
tcp        0      0 192.168.56.176:53           0.0.0.0:*                   LISTEN      1977/named
tcp        0      0 127.0.0.1:53                0.0.0.0:*                   LISTEN      1977/named
tcp        0      0 ::1:53                      :::*                        LISTEN      1977/named
udp        0      0 192.168.56.176:53           0.0.0.0:*                               1977/named
udp        0      0 127.0.0.1:53                0.0.0.0:*                               1977/named
udp        0      0 ::1:53                      :::*                                    1977/named
[root@db-server named]# nslookup
> 192.168.56.176
Server:         192.168.56.176
Address:        192.168.56.176#53

176.56.168.192.in-addr.arpa     name = dns.56.168.192.in-addr.arpa.
> cluster02
Server:         192.168.56.176
Address:        192.168.56.176#53

** server can't find cluster02: SERVFAIL
>
> cluster02
Server:         192.168.56.176
Address:        192.168.56.176#53

** server can't find cluster02: SERVFAIL
> cluster02.f.com
Server:         192.168.56.176
Address:        192.168.56.176#53

Name:   cluster02.f.com
Address: 192.168.56.186
Name:   cluster02.f.com
Address: 192.168.56.187
Name:   cluster02.f.com
Address: 192.168.56.185
> 192.168.56.187
Server:         192.168.56.176
Address:        192.168.56.176#53

187.56.168.192.in-addr.arpa     name = cluster02.f.com.56.168.192.in-addr.arpa.
>
> exit
```

修改两个节点node01和node02的dns服务

```bash
[root@node01 ~]# vim /etc/resolv.conf
[root@node01 ~]# cat /etc/resolv.conf |grep -vE "^$|^#"
search localdomain
nameserver 192.168.56.176
[root@node01 ~]# scp /etc/resolv.conf node02:/etc/resolv.conf
root@node02's password:
resolv.conf                            100%  274     0.3KB/s   00:00
[root@node01 ~]# vim /etc/hosts
[root@node01 ~]# cat /etc/hosts
127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4
::1         localhost localhost.localdomain localhost6 localhost6.localdomain6

192.168.56.181  node01
192.168.56.182  node02


192.168.57.181  node01-priv
192.168.57.182  node02-priv


192.168.56.183  node01-vip
192.168.56.184  node02-vip

192.168.56.185  cluster02.f.com cluster02
192.168.56.186  cluster02.f.com cluster02
192.168.56.187  cluster02.f.com cluster02

[root@node01 ~]# scp /etc/hosts node02:/etc/hosts
root@node02's password:
hosts                                  100%  447     0.4KB/s   00:00

[root@node01 ~]# chattr +i /etc/resolv.conf
[root@node01 ~]# ssh node02 chattr +i /etc/resolv.conf
root@node02's password:
```

### 0.2.7 准备asm磁盘

这里只准备了一个磁盘，5GB，共享给两个节点。

```bash
[root@node01 ~]# vim /etc/udev/rules.d/60-raw.rules
[root@node01 ~]# cat /etc/udev/rules.d/60-raw.rules |grep -vE "^$|^#"
ACTION=="add", KERNEL=="sdc", RUN+="/bin/raw /dev/raw/raw1 %N"
KERNEL=="raw[1-9]*", OWNER="grid", GROUP="asmadmin", MODE="660"
[root@node01 ~]# /sbin/start_udev
Starting udev:                                             [  OK  ]
[root@node01 ~]# ls /dev/raw/
raw1  rawctl
[root@node01 ~]# echo "/sbin/start_udev" >>/etc/rc.local
# scp to node02
[root@node01 ~]# scp /etc/udev/rules.d/60-raw.rules node02:/etc/udev/rules.d/60-raw.rules
root@node02's password:
60-raw.rules                           100%  444     0.4KB/s   00:00
[root@node01 ~]# scp /etc/rc.local node02:/etc/rc.local
root@node02's password:
rc.local                               100%  237     0.2KB/s   00:00
[root@node01 ~]# ssh node02 /sbin/start_udev
root@node02's password:
Permission denied, please try again.
root@node02's password:
Starting udev: [  OK  ]

```


# 1.安装过程

## 1.1 安装前测试

检查准备情况，建议所有的选项都pass。

```bash
[grid@node01 grid]$ ./runcluvfy.sh stage -pre crsinst -n node01,node02 -fixup -verbose >/tmp/runcluvfy.log
```

修改一下`/etc/security/limits.conf`,补充一下，preinstall只能修改oracle用户的限制。

```bash
[root@node01 ~]# vim /etc/security/limits.conf
[root@node01 ~]# cat /etc/security/limits.conf|grep -vE "^$|^#"
oracle   soft   nofile    1024
grid   soft   nofile    1024
oracle   hard   nofile    65536
grid   hard   nofile    65536
oracle   soft   nproc    2047
grid   soft   nproc    2047
oracle   hard   nproc    16384
grid   hard   nproc    16384
oracle   soft   stack    10240
grid  soft   stack    10240
oracle   hard   stack    32768
[root@node01 ~]# scp /etc/security/limits.conf node02:/etc/security/limits.conf
root@node02's password:
limits.conf                            100% 2614     2.6KB/s   00:00
```

关闭selinux

```bash
[root@node01 ~]# vim /etc/selinux/config
[root@node01 ~]# cat /etc/selinux/config |grep -vE "^#|^$"
SELINUX=disabled
SELINUXTYPE=targeted
[root@node01 ~]# scp /etc/selinux/config node02:/etc/selinux/config
root@node02's password:
config                                 100%  457     0.5KB/s   00:00
[root@node01 ~]# setenforce 0
[root@node01 ~]# ssh node02 setenforce 0
root@node02's password:
```

关闭iptables，解决节点之间通信失败

```bash
[root@node01 ~]# service iptables stop
iptables: Flushing firewall rules:                         [  OK  ]
iptables: Setting chains to policy ACCEPT: filter          [  OK  ]
iptables: Unloading modules:                               [  OK  ]
[root@node01 ~]# chkconfig iptables off
[root@node01 ~]# ssh node02 service iptables stop
root@node02's password:
iptables: Flushing firewall rules: [  OK  ]
iptables: Setting chains to policy ACCEPT: filter [  OK  ]
iptables: Unloading modules: [  OK  ]
[root@node01 ~]# ssh node02 chkconfig iptables off
root@node02's password:
```

## 1.2 安装GI

```bash
[root@node01 ~]# su - grid
[grid@node01 ~]$ cd /data/grid/
[grid@node01 grid]$ ./runInstaller
```

启动后注意几个方面：

![](/images/rac-oel-install/005.png)

![](/images/rac-oel-install/00b.png)

![](/images/rac-oel-install/007.png)

![](/images/rac-oel-install/00a.png)

![](/images/rac-oel-install/00b.png)

检查安装要求，这两个都可以忽略，我们已经使用了udev的方式来代替asm驱动

![](/images/rac-oel-install/00c.png)

开始安装

![](/images/rac-oel-install/00d.png)

执行这两个脚本，root用户，在两个节点上执行

![](/images/rac-oel-install/010.png)

```bash
[root@node01 u01]# /u01/app/oraInventory/orainstRoot.sh
Changing permissions of /u01/app/oraInventory.
Adding read,write permissions for group.
Removing read,write,execute permissions for world.

Changing groupname of /u01/app/oraInventory to oinstall.
The execution of the script is complete.
[root@node01 u01]# /u01/app/11.2.0/grid/root.sh
Performing root user operation for Oracle 11g

The following environment variables are set as:
    ORACLE_OWNER= grid
    ORACLE_HOME=  /u01/app/11.2.0/grid
    ...
```

修改grid的环境变量

```
[grid@node01 ~]$ cat .bashrc
# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
        . /etc/bashrc
fi

# User specific aliases and functions


export ORACLE_BASE=/u01/app/grid
export ORACLE_HOME=/u01/app/11.2.0/grid
export PATH=$PATH:$ORACLE_HOME/bin:/usr/local/bin:.
[grid@node01 ~]$ scp .bashrc node02:/home/grid/.bashrc
.bashrc                                                100%  251     0.3KB/s   00:00
[grid@node01 ~]$ crsctl check crs
CRS-4638: Oracle High Availability Services is online
CRS-4537: Cluster Ready Services is online
CRS-4529: Cluster Synchronization Services is online
CRS-4533: Event Manager is online
```

## 1.3 安装DB

解压安装包

```bash
[root@node01 data]# su - oracle
[oracle@node01 ~]$ cd /data/
[oracle@node01 data]$ unzip p13390677_112040_Linux-x86-64_1of7.zip
[oracle@node01 data]$ unzip p13390677_112040_Linux-x86-64_2of7.zip
[oracle@node01 data]$ cd database/
[oracle@node01 database]$ ./runInstaller 
```

注意安装位置

![](/images/rac-oel-install/011.png)

![](/images/rac-oel-install/012.png)

执行脚本，两个节点，使用`root`

![](/images/rac-oel-install/013.png)

```bash
[root@node01 data]# /u01/app/oracle/product/11.2.0/dbhome_1/root.sh
Performing root user operation for Oracle 11g

The following environment variables are set as:
    ORACLE_OWNER= oracle
    ORACLE_HOME=  /u01/app/oracle/product/11.2.0/dbhome_1

Enter the full pathname of the local bin directory: [/usr/local/bin]:
The contents of "dbhome" have not changed. No need to overwrite.
The contents of "oraenv" have not changed. No need to overwrite.
The contents of "coraenv" have not changed. No need to overwrite.

Entries will be added to the /etc/oratab file as needed by
Database Configuration Assistant when a database is created
Finished running generic part of root script.
Now product-specific root actions will be performed.
Finished product-specific root actions.
```

## 1.4 创建DB

修改oracle用户的环境变量，注意sid的不同

```bash
[oracle@node01 ~]$ vim .bashrc
[oracle@node01 ~]$ cat .bashrc
export ORACLE_BASE=/u01/app/oracle
export ORACLE_HOME=$ORACLE_BASE/product/11.2.0/dbhome_1
export PATH=$PATH:$ORACLE_HOME/bin:/usr/local/bin:.
export ORACLE_SID=testdb1
[oracle@node01 ~]$ scp .bashrc node02:/home/oracle/.bashrc
.bashrc                                                100%  296     0.3KB/s   00:00
[oracle@node01 ~]$ ssh node02
[oracle@node02 ~]$ vim .bashrc
[oracle@node02 ~]$ cat .bashrc
export ORACLE_BASE=/u01/app/oracle
export ORACLE_HOME=$ORACLE_BASE/product/11.2.0/dbhome_1
export PATH=$PATH:$ORACLE_HOME/bin:/usr/local/bin:.
export ORACLE_SID=testdb2
[oracle@node02 ~]$
```

在`node01`中执行`dbca`创建数据库，数据库名称为`testdb`

![](/images/rac-oel-install/081.png)

![](/images/rac-oel-install/082.png)

![](/images/rac-oel-install/083.png)

![](/images/rac-oel-install/084.png)

![](/images/rac-oel-install/085.png)

![](/images/rac-oel-install/086.png)

完成后可以登录em查看到数据库的情况，可以使用scan-ip来登录：

![](/images/rac-oel-install/087.png)

# 2.测试

## 2.1 fail over测试

使用其他客户端连接数据库，可见目前连接的实例在`node01`中。
```bash
[oracle@db-server ~]$ sqlplus system/oracle@cluster02.f.com/testdb
SQL> select host_name from v$instance;

HOST_NAME
----------------------------------------------------------------
node01

SQL> exit
```

关闭`node01`后，所有服务都切换到了`node02`上。

```bash
[grid@node02 ~]$ crs_stat -t -v
Name           Type           R/RA   F/FT   Target    State     Host
----------------------------------------------------------------------
ora.DATA.dg    ora....up.type 0/5    0/     ONLINE    ONLINE    node02
ora....ER.lsnr ora....er.type 0/5    0/     ONLINE    ONLINE    node02
ora....N1.lsnr ora....er.type 0/5    0/0    ONLINE    ONLINE    node02
ora....N2.lsnr ora....er.type 0/5    0/0    ONLINE    ONLINE    node02
ora....N3.lsnr ora....er.type 0/5    0/0    ONLINE    ONLINE    node02
ora.asm        ora.asm.type   0/5    0/     ONLINE    ONLINE    node02
ora.cvu        ora.cvu.type   0/5    0/0    ONLINE    ONLINE    node02
ora.gsd        ora.gsd.type   0/5    0/     OFFLINE   OFFLINE
ora....network ora....rk.type 0/5    0/     ONLINE    ONLINE    node02
ora.node01.vip ora....t1.type 0/0    0/0    ONLINE    ONLINE    node02
ora....SM2.asm application    0/5    0/0    ONLINE    ONLINE    node02
ora....02.lsnr application    0/5    0/0    ONLINE    ONLINE    node02
ora.node02.gsd application    0/5    0/0    OFFLINE   OFFLINE
ora.node02.ons application    0/3    0/0    ONLINE    ONLINE    node02
ora.node02.vip ora....t1.type 0/0    0/0    ONLINE    ONLINE    node02
ora.oc4j       ora.oc4j.type  0/1    0/2    ONLINE    ONLINE    node02
ora.ons        ora.ons.type   0/3    0/     ONLINE    ONLINE    node02
ora....ry.acfs ora....fs.type 0/5    0/     ONLINE    ONLINE    node02
ora.scan1.vip  ora....ip.type 0/0    0/0    ONLINE    ONLINE    node02
ora.scan2.vip  ora....ip.type 0/0    0/0    ONLINE    ONLINE    node02
ora.scan3.vip  ora....ip.type 0/0    0/0    ONLINE    ONLINE    node02
ora.testdb.db  ora....se.type 0/2    0/1    ONLINE    ONLINE    node02
```

使用其他客户端连接测试,实例已经切换到了node02上。

```bash
[oracle@db-server ~]$ sqlplus system/oracle@cluster02.f.com/testdb

SQL*Plus: Release 11.2.0.4.0 Production on Mon Jan 8 21:39:31 2018

Copyright (c) 1982, 2013, Oracle.  All rights reserved.


Connected to:
Oracle Database 11g Enterprise Edition Release 11.2.0.4.0 - 64bit Production
With the Partitioning, Real Application Clusters, Automatic Storage Management, OLAP,
Data Mining and Real Application Testing options

SQL> select instance_name,host_name from v$instance;

INSTANCE_NAME
----------------
HOST_NAME
----------------------------------------------------------------
testdb2
node02
```

重启`node01`，服务恢复正常。

```bash
[grid@node01 ~]$ crs_stat -t
Name           Type           Target    State     Host
------------------------------------------------------------
ora.DATA.dg    ora....up.type ONLINE    ONLINE    node01
ora....ER.lsnr ora....er.type ONLINE    ONLINE    node01
ora....N1.lsnr ora....er.type ONLINE    ONLINE    node01
ora....N2.lsnr ora....er.type ONLINE    ONLINE    node02
ora....N3.lsnr ora....er.type ONLINE    ONLINE    node02
ora.asm        ora.asm.type   ONLINE    ONLINE    node01
ora.cvu        ora.cvu.type   ONLINE    ONLINE    node02
ora.gsd        ora.gsd.type   OFFLINE   OFFLINE
ora....network ora....rk.type ONLINE    ONLINE    node01
ora....SM1.asm application    ONLINE    ONLINE    node01
ora....01.lsnr application    ONLINE    ONLINE    node01
ora.node01.gsd application    OFFLINE   OFFLINE
ora.node01.ons application    ONLINE    ONLINE    node01
ora.node01.vip ora....t1.type ONLINE    ONLINE    node01
ora....SM2.asm application    ONLINE    ONLINE    node02
ora....02.lsnr application    ONLINE    ONLINE    node02
ora.node02.gsd application    OFFLINE   OFFLINE
ora.node02.ons application    ONLINE    ONLINE    node02
ora.node02.vip ora....t1.type ONLINE    ONLINE    node02
ora.oc4j       ora.oc4j.type  ONLINE    ONLINE    node02
ora.ons        ora.ons.type   ONLINE    ONLINE    node01
ora....ry.acfs ora....fs.type ONLINE    ONLINE    node01
ora.scan1.vip  ora....ip.type ONLINE    ONLINE    node01
ora.scan2.vip  ora....ip.type ONLINE    ONLINE    node02
ora.scan3.vip  ora....ip.type ONLINE    ONLINE    node02
ora.testdb.db  ora....se.type ONLINE    ONLINE    node02
```

## 2.2 load balance测试

创建多个连接

```bash
[oracle@db-server ~]$ cat lb_test.sh
#!/bin/bash
source /home/oracle/.bashrc
for i in `seq 50`;
do
nohup sqlplus -S system/oracle@cluster02.f.com/testdb<<EOF &
begin
dbms_lock.sleep(10);
end;
/

EOF
done
[oracle@db-server ~]$
```
在数据库中查看
```bash
SQL> select inst_id,count(*) from gv$session group by inst_id;

   INST_ID   COUNT(*)
---------- ----------
         1         41
         2         54
# 再创建更多的连接
SQL> /

   INST_ID   COUNT(*)
---------- ----------
         1        126
         2        123
```




# 3.问题

## 3.1 DBCA不能识别asm的磁盘组

![](/images/rac-oel-install/07a.png)

原因可有为以下任意一种：[DBCA Does Not Display ASM Disk Groups In 11.2](http://m.blog.itpub.net/161195/viewspace-1053126/)

1. `$ORACLE_HOME/bin/oracle`的权限问题；
2. `oracle`用户不在`asmdba`组中；

解决办法：

1. `chmod 6751 oracle`将oracle这个文件的权限修改为`-rwsr-s--x `；
2. 将oracle添加进`asmdba`组中；
```bash
[root@node01 ~]# id oracle
uid=54321(oracle) gid=54321(oinstall) groups=54321(oinstall),54322(dba)
[root@node01 ~]#
[root@node01 ~]# usermod -G oinstall,dba,asmdba oracle
[root@node01 ~]# id oracle
uid=54321(oracle) gid=54321(oinstall) groups=54321(oinstall),54322(dba),54325(asmdba)
```
