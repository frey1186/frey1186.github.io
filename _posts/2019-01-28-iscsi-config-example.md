---

layout: post

title: Lustre学习笔记（4.1）-ISCSI配置示例

date: 2019-01-28 12:00

tags: iscsi lustre 
categories: public

typora-root-url: ..



---









![](/images/2019-01-28-iscsi-config-example/top.jpg)





## 服务端配置



准备一个200M的磁盘作为MGT：



```bash

[root@iscsi ~]# lsblk /dev/sdb 

NAME MAJ:MIN RM SIZE RO TYPE MOUNTPOINT

sdb 8:16 0 200M 0 disk 

```



iscsi服务端配置如下：



```bash

[root@iscsi ~]# yum install targetcli

[root@iscsi ~]# systemctl enable targetd

[root@iscsi ~]# targetcli 

# 创建一个块设备的磁盘，如果是文件img的话需要使用/backstores/fileio

/> /backstores/block create mgt /dev/sdb 

# 创建一个空的iqn

/> /iscsi create iqn.2019-01.f.com:mgt

# 在下面创建可以访问“mgt”的iqn，这里是io1和io2的两个主机

/> /iscsi/iqn.2019-01.f.com:mgt/tpg1/acls create iqn.2019-01.f.cm:io1

/> /iscsi/iqn.2019-01.f.com:mgt/tpg1/acls create iqn.2019-01.f.cm:io2

# 为“mgt”创建lun

/> /iscsi/iqn.2019-01.f.com:mgt/tpg1/luns create /backstores/block/mgt 

# 退出后自动保存

/> exit

Global pref auto_save_on_exit=true

Last 10 configs saved in /etc/target/backup/.

Configuration saved to /etc/target/saveconfig.json

```



完成配置如下：





![](/images/2019-01-28-iscsi-config-example/iscsi-config.png)





## 客户端配置



- io1配置：



```bash

[root@io1 ~]# yum install iscsi-initiator-utils

# 修改本机iqn，必须与注册在iscsi服务器上的iqn完全一致

[root@io1 ~]# echo "InitiatorName=iqn.2019-01.f.com:io1" > /etc/iscsi/initiatorname.iscsi 

[root@io1 ~]# systemctl start iscsi

[root@io1 ~]# systemctl enable iscsi

# 发现目标端的iscsi磁盘

[root@io1 ~]# iscsiadm -m discovery -t sendtargets -p 192.168.56.130

# 登录，下面的命令是登录发现的所有磁盘

[root@io1 ~]# iscsiadm -m node -L all

# 也可以指定登录

# iscsiadm -m node -T iqn.2019-01.f.com:mgt -l 

# 取消登录使用：

# iscsiadm -m node -T iqn.2019-01.f.com:mgt -u

[root@io1 ~]# ls -l /dev/disk/by-id/ |grep sdc

lrwxrwxrwx 1 root root 9 Jan 28 15:05 scsi-36001405a6e718219a59410a82aa3069f -> ../../sdc

lrwxrwxrwx 1 root root 9 Jan 28 15:05 wwn-0x6001405a6e718219a59410a82aa3069f -> ../../sdc

```



- io2配置：



```bash

[root@io2 ~]# yum install iscsi-initiator-utils

[root@io2 ~]# echo "InitiatorName=iqn.2019-01.f.com:io2" > /etc/iscsi/initiatorname.iscsi 

[root@io2 ~]# systemctl start iscsi

[root@io2 ~]# systemctl enable iscsi

[root@io2 ~]# iscsiadm -m discovery -t sendtargets -p 192.168.56.130

[root@io2 ~]# iscsiadm -m node -L all

[root@io2 ~]# ls -l /dev/disk/by-id/ |grep sdc

lrwxrwxrwx 1 root root 9 Jan 28 15:05 scsi-36001405a6e718219a59410a82aa3069f -> ../../sdc

lrwxrwxrwx 1 root root 9 Jan 28 15:05 wwn-0x6001405a6e718219a59410a82aa3069f -> ../../sdc

```



## 参考

- https://blog.csdn.net/zhongbeida_xue/article/details/70921167

- http://blog.51cto.com/12227558/2096433

- https://blog.csdn.net/qq_40385970/article/details/78786023

