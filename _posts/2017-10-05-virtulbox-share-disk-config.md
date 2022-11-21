---
layout: post
title: virtualbox配置共享磁盘
date: 2017-10-05 21:00
author: felo
tags: centos virtualbox
---


# 0.环境准备

准备了三个虚拟机c01,c02,c03，为这三个虚拟机分配3个共享的磁盘。

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

# 1.配置共享磁盘

两个重要的方面：
- 该磁盘需要直接分配空间，即“**固定大小（Fixed）**”，不可使用“动态分配”；
- 需要将该磁盘的类型改为“**可共享（shareable）**”；


## 方法一：使用图形界面操作，几个虚拟机的情况下使用

简单步骤如下：
- 关闭虚拟机；
- 在虚拟机设置中一个控制器下增加一个磁盘，注意选择直接分配空间；
- 在虚拟介质管理器中，将这个磁盘修改为“可共享”；
- 将此磁盘分配给其他虚拟机，注意顺序一致；

完成后状态如下：

![](/images/vb_share_disk/新增磁盘.png)


![](/images/vb_share_disk/修改磁盘属性.png)




## 方法二：使用命令行来创建硬盘和挂载，可在大量虚拟机的情况下使用

```bash
localhost:~$ cd VirtualBox\ VMs/
localhost:VirtualBox VMs$ ls
c01	c02	c03
# 创建一个磁盘
localhost:VirtualBox VMs$ VBoxManage createmedium disk --filename gpfs04.vdi \
--size 1024 --variant Fixed 
0%...10%...20%...30%...40%...50%...60%...70%...80%...90%...100%
Medium created. UUID: 538ac09e-1018-4c89-a186-2232aeb18a2d
# --size：单位M
# --variant：Fixed表示预先分配
# --fielname：注意路径

# 挂载到虚拟机，注意需要在虚拟机关闭的情况下挂载
localhost:VirtualBox VMs$ VBoxManage storageattach c01 --storagectl "SATA" \
--port 4 --device 0 --type hdd --mtype shareable --medium gpfs04.vdi 
localhost:VirtualBox VMs$ VBoxManage storageattach c02 --storagectl "SATA" \
--port 4 --device 0 --type hdd --mtype shareable --medium gpfs04.vdi 
localhost:VirtualBox VMs$ VBoxManage storageattach c03 --storagectl "SATA" \
--port 4 --device 0 --type hdd --mtype shareable --medium gpfs04.vdi 

# 有几个注意的地方：
# --mtype：选择shareable，可共享的；
# --port：使用虚拟机中未使用的端口；
# --device：可以直接使用现有的设备；

```

完成后状态如下：

![](/images/vb_share_disk/虚拟机中的磁盘属性.png)



# 2.在虚拟机中检查


在linux中检查磁盘对应情况

```bash
# 未使用的磁盘看不到
[root@c01 ~]# blkid
/dev/sda1: UUID="294e19f8-4974-48a5-b63b-1bf4a48d917d" TYPE="ext4"
/dev/sda2: UUID="NUVWTX-VXvj-FD1P-4PYt-bJlZ-wSKg-c5j1R8" TYPE="LVM2_member"
/dev/mapper/vg_c01-lv_root: UUID="7e963d1e-d294-4807-97bf-0d3bff8a0eff" TYPE="ext4"
/dev/mapper/vg_c01-lv_swap: UUID="e4aa1894-770e-481a-88ae-0af0152461b4" TYPE="swap"
[root@c01 ~]# ll /dev/disk/by-uuid/
total 0
lrwxrwxrwx 1 root root 10 Oct  5 23:12 294e19f8-4974-48a5-b63b-1bf4a48d917d -> ../../sda1
lrwxrwxrwx 1 root root 10 Oct  5 23:12 7e963d1e-d294-4807-97bf-0d3bff8a0eff -> ../../dm-0
lrwxrwxrwx 1 root root 10 Oct  5 23:12 e4aa1894-770e-481a-88ae-0af0152461b4 -> ../../dm-1

# 看到sdx对应的ID
[root@c01 ~]# ll /dev/disk/by-id/
total 0
lrwxrwxrwx 1 root root  9 Oct  5 23:12 ata-VBOX_HARDDISK_VB2c219235-b5342f0a -> ../../sdd
lrwxrwxrwx 1 root root  9 Oct  5 23:12 ata-VBOX_HARDDISK_VB8be33791-dbd131d9 -> ../../sdc
lrwxrwxrwx 1 root root  9 Oct  5 23:12 ata-VBOX_HARDDISK_VBd1f49c4d-f7d10830 -> ../../sdb
lrwxrwxrwx 1 root root  9 Oct  5 23:12 ata-VBOX_HARDDISK_VBe837dfd9-75743ee5 -> ../../sda
lrwxrwxrwx 1 root root 10 Oct  5 23:12 ata-VBOX_HARDDISK_VBe837dfd9-75743ee5-part1 -> ../../sda1
lrwxrwxrwx 1 root root 10 Oct  5 23:12 ata-VBOX_HARDDISK_VBe837dfd9-75743ee5-part2 -> ../../sda2
lrwxrwxrwx 1 root root 10 Oct  5 23:12 dm-name-vg_c01-lv_root -> ../../dm-0
lrwxrwxrwx 1 root root 10 Oct  5 23:12 dm-name-vg_c01-lv_swap -> ../../dm-1
lrwxrwxrwx 1 root root 10 Oct  5 23:12 
dm-uuid-LVM-TE5oTnS0nytbFWgPeKlSCFZuYxcCgPk80DjcBzJyQbULlWfG3QSa8DgSJO1MncCc -> ../../dm-1
lrwxrwxrwx 1 root root 10 Oct  5 23:12 
dm-uuid-LVM-TE5oTnS0nytbFWgPeKlSCFZuYxcCgPk8jEuJ9InDraGakO6okGxG7OUaZXJVazHy -> ../../dm-0
lrwxrwxrwx 1 root root  9 Oct  5 23:12 scsi-SATA_VBOX_HARDDISK_VB2c219235-b5342f0a -> ../../sdd
lrwxrwxrwx 1 root root  9 Oct  5 23:12 scsi-SATA_VBOX_HARDDISK_VB8be33791-dbd131d9 -> ../../sdc
lrwxrwxrwx 1 root root  9 Oct  5 23:12 scsi-SATA_VBOX_HARDDISK_VBd1f49c4d-f7d10830 -> ../../sdb
lrwxrwxrwx 1 root root  9 Oct  5 23:12 scsi-SATA_VBOX_HARDDISK_VBe837dfd9-75743ee5 -> ../../sda
lrwxrwxrwx 1 root root 10 Oct  5 23:12 scsi-SATA_VBOX_HARDDISK_VBe837dfd9-75743ee5-part1 -> ../../sda1
lrwxrwxrwx 1 root root 10 Oct  5 23:12 scsi-SATA_VBOX_HARDDISK_VBe837dfd9-75743ee5-part2 -> ../../sda2

# 检查一下各个虚拟机中的对应位置和情况一致即可，如果前面按照顺序挂载应该不会出现不一致的情况。

```