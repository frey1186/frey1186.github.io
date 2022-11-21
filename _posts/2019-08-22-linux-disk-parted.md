---
layout: post
title:  磁盘的分区
date: 2019-08-22 12:00
tags: linux
categories: linux-basics 
typora-root-url: ..
---



# 1. 分区模式

MBR分区

- 硬盘主引导记录MBR由4个部分组成
- 主引导程序（偏移地址0000H--0088H），它负责从活动分区中装载，并运行系统引导程序。
- 出错信息数据区，偏移地址0089H--00E1H为出错信息，00E2H--01BDH全为0字节。
- 分区表（DPT,Disk Partition Table）含4个分区项，偏移地
- 址01BEH--01FDH,每个分区表项长16个字节，共64字节为分区项1、分区项2、分区项3、分区项4
- 结束标志字，偏移地址01FE--01FF的2个字节值为结束标志55AA

GPT分区

- GPT:GUID（Globals Unique Identifiers） partitiontable 支持128个分区，使用64位，支持8Z（512Byte/block ）64Z （ 4096Byte/block）
- 使用128位UUID(Universally Unique Identifier) 表示磁盘和分区 GPT分区表自动备份在头和尾两份，并有CRC校验位
- UEFI (统一扩展固件接口)硬件支持GPT，使操作系统启动

# 2. 分区工具


- cfdisk	字符交互式分区工具，比较简单好用但是不常用
- cgdisk	与cfdisk类似，支持GPT分区
- fdisk 	命令行分区工具，最常用工具（Centos6中的fdisk不支持gpt分区，Centos7的fdisk是支持的）
- gdisk 	与fdisk类似，支持GPT分区
- parted	支持非交互式划分区，支持GPT，常用工具
- sfdisk	不常用
- sgdisk	不常用

# 3. fdisk

```bash
a toggle a bootable flag   # 切换可启动标志
b edit bsd disklabel
c toggle the dos compatibility flag　　　 # 切换dos兼容标志
d delete a partition    　　　　　　　　　　 # 删除一个分区
g create a new empty GPT partition table    # 创建一个空的GPT分区表
G create an IRIX (SGI) partition table
l list known partition types
m print this menu
n add a new partition    # 添加一个分区
o create a new empty DOS partition table    # 创建一个空的DOS分区表
p print the partition table    # 打印分区表
q quit without saving changes
s create a new empty Sun disklabel
t change a partition's system id    # 改变一个分区的类型
u change display/entry units
v verify the partition table
w write table to disk and exit    # 写分区表并退出
x extra functionality (experts only)
```

常规用法是交互式的划分分区，也可以使用非交互式，如下：

```bash
# 创建一个文件模拟硬盘
[root@vm-centos7 ~]# qemu-img create -f raw cn5.img 500M
Formatting 'cn5.img', fmt=raw size=524288000 
[root@vm-centos7 ~]# fdisk cn5.img << EOF
> n
> p
> 1
>
> +100M
> n
> p
> 2
>
>
> w
> EOF
[root@vm-centos7 ~]# fdisk -l cn5.img
Disk cn5.img: 524 MB, 524288000 bytes, 1024000 sectors
Units = sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disk label type: dos
Disk identifier: 0x000cfa15
  Device Boot      Start         End      Blocks   Id  System
cn5.img1            2048      206847      102400   83  Linux
cn5.img2          206848     1023999      408576   83  Linux
```

# 4.parted 

```bash
align-check TYPE N                        check partition N for TYPE(min|opt) alignment
help [COMMAND]                           print general help, or help on COMMAND
mklabel,mktable LABEL-TYPE               create a new disklabel (partition table)    # 常用gpt,msdos
mkpart PART-TYPE [FS-TYPE] START END     make a partition   # 常用
name NUMBER NAME                         name partition NUMBER as NAME
print [devices|free|list,all|NUMBER]     display the partition table, available devices, free space, all found partitions, or a particular partition
quit                                     exit program
rescue START END                         rescue a lost partition near START and END

resizepart NUMBER END                    resize partition NUMBER
rm NUMBER                                delete partition NUMBER
select DEVICE                            choose the device to edit
disk_set FLAG STATE                      change the FLAG on selected device
disk_toggle [FLAG]                       toggle the state of FLAG on selected device
set NUMBER FLAG STATE                    change the FLAG on partition NUMBER   # 常用设置boot,lvm,swap
toggle [NUMBER [FLAG]]                   toggle the state of FLAG on partition NUMBER
unit UNIT                                set the default unit to UNIT
version                                  display the version number and copyright information of GNU Parted
```

可以查看[parted帮助]( https://www.gnu.org/software/parted/manual/parted.html)

一条命令划分区:

```bash
# 查看分区情况
[root@vm-centos7 ~]# parted -s cn5.img print
# 划分区
[root@vm-centos7 ~]# parted -s cn5.img mklabel msdos mkpart primary ext4  1024kb 100m  mkpart primary ext4 100m 100%  set 1 boot
```

也可以分步执行(参考[Linux下三种分区工具](https://www.cnblogs.com/zhaojiedi1992/p/zhaojiedi_linux_039_fdisk_gdisk_parted.html)):

```bash
[root@centos7 mnt]$ parted -s /dev/sdb mklabel gpt 
[root@centos7 mnt]$ parted -s /dev/sdb unit GB mkpart primary 1 30 set 1 lvm on
[root@centos7 mnt]$ parted -s /dev/sdb unit GB mkpart primary 30 50 set 2 swap on
[root@centos7 mnt]$ parted -s /dev/sdb unit GB mkpart primary 50 60
[root@centos7 mnt]$ parted -s /dev/sdb unit GB mkpart primary 60 70
[root@centos7 mnt]$ parted -s /dev/sdb print
```

# 参考

- [parted帮助]( https://www.gnu.org/software/parted/manual/parted.html)
- [Linux下三种分区工具](https://www.cnblogs.com/zhaojiedi1992/p/zhaojiedi_linux_039_fdisk_gdisk_parted.html)
- [GNU Manuals Online](https://www.gnu.org/manual/)










