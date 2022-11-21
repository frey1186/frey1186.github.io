---
layout: post
title: SSH互信配置
date: 2017-10-06 21:00
author: felo
tags: centos ssh
---



# 0.环境配置


准备了三个虚拟机c01,c02,c03，配置ssh互信。

```bash
[root@c01 ~]# cat /etc/hosts
127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4
::1         localhost localhost.localdomain localhost6 localhost6.localdomain6
192.168.56.101 c01
192.168.56.102 c02
192.168.56.103 c03
[root@c01 ~]# uname -a
Linux c01 2.6.32-696.10.3.el6.x86_64 #1 SMP Tue Sep 26 18:14:22 UTC 2017 x86_64 x86_64 x86_64 GNU/Linux
[root@c01 ~]# cat /etc/redhat-release
CentOS release 6.5 (Final)
```


# 1.方法1：使用ssh-copy-id配置

```bash
# 所有节点上执行，一路回车+yes+密码
[root@c01 ~]# ssh-keygen
[root@c01 ~]# ssh-copy-id c01
[root@c01 ~]# ssh-copy-id c02
[root@c01 ~]# ssh-copy-id c03

# 测试
[root@c01 ~]# for i in 1 2 3;do ssh c0$i date;done
Fri Oct  6 18:00:29 CST 2017
Fri Oct  6 18:00:30 CST 2017
Fri Oct  6 18:00:30 CST 2017

# 如果节点很多，直接崩溃
```

更好一些的办法，如果所有节点的密码都一样的话，这里root的所有密码均为root，
然后使用expect自动交互，将秘钥复制到其他节点。

> 使用expect，可以参考[linux expect详解(ssh自动登录)](http://www.cnblogs.com/lzrabbit/p/4298794.html)。

```bash
# 所有节点上执行，删除ssh提示
sed -i "s/.*StrictHostKeyChecking.*/StrictHostKeyChecking no/" /etc/ssh/ssh_config
# 重启ssh服务
service sshd restart
# 安装expect
yum -y install expect
# 新增密钥对
ssh-keygen -q -t rsa -N "" -f ~/.ssh/id_rsa
# 复制到各个节点（这里是c01，c02，c03）
for i in 1 2 3;do expect -c "spawn ssh-copy-id c0$i;\
expect "*password:" { send "root\\r" ;exp_continue}";done

# 测试
[root@c01 ~]# for i in 1 2 3;do ssh c0$i date;done
Fri Oct  6 20:29:17 CST 2017
Fri Oct  6 20:29:18 CST 2017
Fri Oct  6 20:29:17 CST 2017
```


# 2.方法2：手动拷贝


## 2.1 配置nfs服务
```bash
# all node
[root@c01 ~]# yum list |grep -E "rpcbind|nfs-utils"
nfs-utils.x86_64                           1:1.2.3-75.el6              base
nfs-utils-lib.i686                         1.1.5-13.el6                base
nfs-utils-lib.x86_64                       1.1.5-13.el6                base
nfs-utils-lib-devel.i686                   1.1.5-13.el6                base
nfs-utils-lib-devel.x86_64                 1.1.5-13.el6                base
rpcbind.x86_64                             0.2.0-13.el6_9.1            updates
[root@c01 ~]# yum -y install rpcbind nfs-utils

# server node
[root@c01 ~]# mkdir c01ssh
[root@c01 ~]# chmod -R 777 c01ssh/
[root@c01 ~]# vi /etc/exports
[root@c01 ~]# service rpcbind restart;service nfs restart
Stopping rpcbind:                                          [  OK  ]
Starting rpcbind:                                          [  OK  ]
Shutting down NFS daemon:                                  [  OK  ]
Shutting down NFS mountd:                                  [  OK  ]
Shutting down NFS services:                                [  OK  ]
Shutting down RPC idmapd:                                  [  OK  ]
Starting NFS services:                                     [  OK  ]
Starting NFS mountd:                                       [  OK  ]
Starting NFS daemon:                                       [  OK  ]
Starting RPC idmapd:                                       [  OK  ]
[root@c01 ~]# cat /etc/exports
/root/c01ssh *(insecure,rw,async,no_root_squash)

[root@c01 ~]# showmount -e
Export list for c01:
/root/c01ssh *

# client node
[root@c02 ~]# mount -t nfs c01:/root/c01ssh/ /mnt/
[root@c02 ~]# df
Filesystem                 1K-blocks    Used Available Use% Mounted on
c01:/root/c01ssh/            6795264 1140864   5302528  18% /mnt

```

## 2.2 ssh key
```bash
在所有节点执行下面几条命令：
sed -i "s/.*StrictHostKeyChecking.*/StrictHostKeyChecking no/" /etc/ssh/ssh_config
service sshd restart
ssh-keygen -q -t rsa -N "" -f ~/.ssh/id_rsa
mount -t nfs c01:/root/c01ssh /mnt
cat /root/.ssh/id_rsa.pub >>/mnt/authorized_keys

全部执行完成后，全部节点再执行下面几条命令：
/bin/cp /mnt/authorized_keys ~/.ssh/
chmod 600 ~/.ssh/authorized_keys
umount /mnt

```

# 3.测试

```bash
[root@c02 ~]# for i in 1 2 3 ;do ssh c0$i date;done
Warning: Permanently added 'c01,192.168.56.101' (RSA) to the list of known hosts.
Fri Oct  6 17:52:26 CST 2017
Warning: Permanently added 'c02,192.168.56.102' (RSA) to the list of known hosts.
Fri Oct  6 17:52:26 CST 2017
Warning: Permanently added 'c03,192.168.56.103' (RSA) to the list of known hosts.
Fri Oct  6 17:52:26 CST 2017
```


