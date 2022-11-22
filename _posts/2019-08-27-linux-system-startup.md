---
layout: post
title:  系统启动
date: 2019-08-27 12:00
tags: linux
categories: linux-basics 
typora-root-url: ..
---

系统启动其实很复杂，要想每个过程都了解感觉还是很难的。

这里记录一下主要过程吧，将来水平提升了再来补充。

# 0. 概述

总的来说分成下面几步吧：

- 按下电源，启动自检
- 进入BIOS，选择从硬盘启动
- 硬盘引导起来后，由grub接管
- 加载内核，进入系统

有几种常见的组合：

```
- BIOS legacy & MBR & grub legacy & sysvinit  & initrd.img   --> Centos5
- BIOS legacy & MBR & grub legacy & upstart   & initramfs    --> Centos6
- UEFI        & GPT & grub legacy & upstart   & initramfs    --> Centos6
- BIOS legacy & MBR & grub2       & systemd   & initramfs    --> Centos7
- BIOS legacy & GPT & grub2       & systemd   & initramfs    --> Centos7   # 可选
- UEFI        & GPT & grub2       & systemd   & initramfs    --> Centos7
```

# 1. 按下电源

在没按下电源之前，在机器已经通电的情况下，已经有一个bmc模块已经在运行了。通过bmc可以模拟开机的动作，也可以查看机器的状况。

在按下电源的时候，就会进入开机自检的状态，检查设备的CPU、硬盘等，如果发现严重的硬件故障，就会停止启动。

# 2. `BIOS`


BIOS有两种模式：

- legacy模式，也就是传统的BIOS模式，或者说UEFI固件的传统BIOS兼容模式；
- UEFI模式，这才是UEFI固件的主流模式；

创建的组合是：传统BIOS和MBR，传统BIOS和GPT，UEFI固件和GPT。


通常启动到一定时候就会出现 Press F1 xxxx, F12 xxxxx的字样，选择怎样的启动方式：

- 硬盘
- usb
- dvd
- network
- ...


一般对硬盘来说，传统BIOS模式和原生UEFI固件启动时候的区别在于：

- 传统BIOS模式，启动后只是寻找硬盘中的固定位置（第一个扇区的前446字节）代码，并运行；
- UEFI模式，启动后寻找FAT32分区中的某个efi文件，并运行。

因为硬盘的第一个扇区太小了，根本干不了啥，所以只能让446字节的这段代码在指向另外一个位置（如果是MBR硬盘的话，就会指向MBR和第一个分区之间的缝隙区域，好尴尬的设置），让它来识别/boot分区，启动GRUB程序；这也是UEFI模式出现的原因之一，它让启动更加的简单了。

# 3. `BootLoader`

不管是硬盘还是光驱，都需要BootLoader来启动。

这里就说硬盘了，硬盘不同的分区，还是有点区别的，mbr不支持2TB以上的磁盘，因此，现在GPT分区的硬盘也越来越多了。

## 3.1 `mbr BootLoader`


第一个扇区，512字节中的前446个字节就是`Boot`程序，是一段汇编代码，因为空间只有446个字节，太少了，它的基本思想就是指向其他位置。

```bash

# 这三个是硬盘上的位置是系统启动的关键位置。
mbr --->  mbr gap ---> /boot

# 1.mbr 主引导分区，512字节的第一扇区
# 2.mbr gap  主引导分区和第一个分区之间的空隙
# 3./boot分区，一般是第一个分区

```

使用`grub`工具可以简单的部署上面说的这些东西，其实就是一些文件。但是使用`grub`和`grub2`有点区别，需要注意一下。

### 3.1.1 `grub`

`grub`，一般指的是`grub legacy`，版本号为`0.97`。`Centos6`以及之前的版本使用。

`grub`把启动需要的阶段分成了3个步骤，`stage1`、`stage1_5`、`stage2`。简单的来说，

- `stage1`就是`mbr`的第一个分区的446字节二进制文件，作用是指向`stage1_5`。
- `stage1_5`,主要任务就是识别文件系统，包含了很多文件系统的驱动。保存在`mbr gap` 缝隙之中，作用是指向`stage2`。
- `stage2`，作用是加载`grub`配置文件，进入加载内核等。保存在`/boot`目录下。

其实三个阶段设计的文件都保存在`/boot`下，当指定`setup`命令安装`grub`的时候，会将相应的文件写到指定的位置上。

```bash
#大概步骤就是这样了：

stage1 ---> stage1_5 ---> stage2    ---> vmlinuz&initrd ---> ...
启动   ---> fs驱动   ---> grub配置  ---> 内核&更多驱动  ---> ...

MBR --> stage1_5( mbr gap ) --> /boot/grub/menu.lst --> vmlinuz --> ...

```

这个步骤是固定的，基本需要调整的就是`grub`的配置文件`/boot/grub/menu.lst`。


### 3.1.2 `grub2`

`grub 2.x`的版本，`RHEL7/Centos7`以后开始使用，替换了原先的`grub legacy`。

`grub2`的方式基本和`grub`差不多，毕竟一脉相承，但是不再使用`stage`文件，而是用`boot.img,core.img`代替。

- `boot.img`：这个文件基本跟`stage1`作用是一样的,作用就是跳转到`core.img`上；
- `core.img`：跟`stage1_5`基本差不多,在mbr的磁盘分区方式下，会放在`mbr gap` 缝隙中。`core.img`内会包含一些必要的模块，以便能够grub访问到`/boot/grub`目录。因为`grub2`使用了大量动态模块，`core.img`会足够小。当然，`core.img`里面还有不同，不细说了。

```bash
所以启动的步骤也基本类似的：
1，读取硬盘第一扇区，也就是加载了boot.img
2，跳转到mbr和第一个分区的缝隙中的core.img，加载必要的模块，启动grub2
3，跳转到/boot下，grub2启动并加载grub2.cfg的配置文件
4，加载vmlinuz内核等...

简单来说就是： BIOS --> MBR --> core.img ( mbr gap ) --> grub.cfg --> vmlinuz --> ...

```

同样的，常见的调整就是修改`grub2`的配置，不过`grub2`的配置文件相对复杂一些，一般不再直接修改`/boot/grub2/grub.cfg`文件，而是通过修改`/etc/grub/default`和`grub-mkconfig`来自动生成配置。

## 3.2 `GPT BootLoader`

对于`GPT`硬盘，一般会使用`UEFI`进行启动，有时候也会使用`BIOS legacy`方式。

### 3.2.1` grub`

- BIOS+GPT 模式：貌似不可行。
- UEFI + GPT模式

Centos6系统下的分区如下：

```bash
[root@cn4 ~]# df -hT
Filesystem           Type   Size  Used Avail Use% Mounted on
/dev/mapper/vg_cn4-lv_root
                     ext4    17G  675M   16G   5% /
tmpfs                tmpfs  490M     0  490M   0% /dev/shm
/dev/sda2            ext4   477M   27M  425M   6% /boot
/dev/sda1            vfat   200M  264K  200M   1% /boot/efi
```

启动过程中UEFI直接指向了/boot/efi这个文件系统中的grub.efi文件。

```bash
[root@cn4 ~]# cd /boot/efi/EFI/redhat/
[root@cn4 redhat]# ls -l
total 256
-rwx------ 1 root root    880 Aug 28 23:17 grub.conf    # 配置文件
-rwx------ 1 root root 254317 Mar 23  2017 grub.efi     # 加载grub，指向grub.cfg
```

启动顺序：

```bash
UEFI --> grub.efi --> grub.cfg --> vmlinuz --> ...
```

### 3.2.2 `grub2`

- BIOS + GPT 模式

在`BIOS&GPT`硬盘下的`grub2`与`mbr`方式只有一点区别，就是`core.img`的位置，它放在了一个专用的分区之中，使用不同工具划分分区，需要添加不同的标签，这个分区大小`1M`即可。

```bash
# parted   -->  bios_grub
# gdisk    -->  ef02
# anconda图形界面  --> 需要指定为 BIOS Boot 的Filesystem
```

使用下面的命令可以修改一个分区为bios_grub模式

```bash
parted /dev/sda set 1 bios_grub on
```

启动顺序为：

```bash
BIOS --> MBR --> core.img (EF02 partition) --> grub.cfg --> vmlinuz --> ...
```

下图显示了GRUB2在MBR和GPT两种格式下的不同之处，来之wikipedia

![](/images/2019-08-27-linux-system-startup/GNU_GRUB_components.svg.png)



- UEFI + GPT 模式

在UEFI&GPT的模式下，因为UEFI能够直接读取文件系统，不需要直接读取某个扇区中的内容，因此直接指向类似core.img的一个grub.efi文件来启动grub2程序，加载grub.cfg这个配置文件。

这个文件的位置是：`/boot/efi/EFI/centos/grubx64.efi`。

这种模式下的分区也有些区别，需要额外增加一个专用`efi`分区，格式为`fat32`，挂载位置是`/boot/efi`，大小自定默认200M。

```bash
# 这种模式下的分区，是这样的：
[root@cn2 ~]# df -hT |grep -v tmpfs
Filesystem              Type      Size  Used Avail Use% Mounted on
/dev/mapper/centos-root xfs        17G  1.2G   16G   7% /
/dev/sda2               xfs      1014M  138M  877M  14% /boot
/dev/sda1               vfat      200M   12M  189M   6% /boot/efi
```

启动顺序：

```bash
启动顺序为：UEFI --> grubx64.efi --> grub.cfg --> vmlinuz --> ...
```


# 4. `kernel & initrd`

现在grub或者grub2的工作就完成了，把内核vmlinuz加载到了内存，并传递了执行的参数以及initrd的位置，就是grub.cfg参数中所写的那些。

vmlinuz&initrd  --->  0#  ---> 1# ---> 2# ---> ...

## 4.1 vmlinuz 

vmlinuz文件是一个bzImage压缩文件，

```bash
# 这是centos7.6的vmlinuz文件属性和文件大小
[root@cn2 boot]# file vmlinuz-3.10.0-957.el7.x86_64
vmlinuz-3.10.0-957.el7.x86_64: Linux kernel x86 boot executable bzImage, version 3.10.0-957.el7.x86_64 (mockbuild@kbuilder.bsys.centos.org) #1 S, RO-rootFS, swap_dev 0x6, Normal VGA
[root@cn2 boot]# du -h vmlinuz-3.10.0-957.el7.x86_64
6.4M    vmlinuz-3.10.0-957.el7.x86_64
```

运行后创建0号进程，然后创建1号和2号进程。

```bash
# 这是CentOS7.6 的1号和2号进程
[root@cn2 boot]# ps -ef |head -n 3
UID         PID   PPID  C STIME TTY          TIME CMD
root          1      0  0 22:03 ?        00:00:01 /usr/lib/systemd/systemd --switched-root --system --deserialize 22
root          2      0  0 22:03 ?        00:00:00 [kthreadd]
```

但是呢，有一个前提，1号进程执行的程序放在了/usr目录下面（或者说是根目录下面），那么就要求vmlinuz内核必须要先加载根文件系统，为了应对不同类型的根文件系统内核就会越来越大，因此采用了另外一种折中方案，附带一个initrd来放驱动之类的系统专有文件。vmlinuz中只包含一些必要的共性文件。

## 4.2 initrd.img & initramfs

initrd.img适用于centos5，initramfs适用于centos6和centos7。目的是一样的，但是实际上有很大的区别。

### 4.2.1 initrd.img

initrd是一个镜像文件系统，被加载到内存中，实现找到真正的根文件系统、加载必要的驱动、收集内核运行状态、设备信息等。其中/sys,/proc,/dev等目录中的信息就是它收集的。另外，完成这些工作后，它将会切换到真正的根文件系统中，将权限正式交给用户空间。

```bash
# centos 5.8 中的initrd 文件
[root@localhost ~]# cp /boot/initrd-2.6.18-308.el5.img /tmp/initrd.gz
[root@localhost tmp]# gunzip initrd.gz
[root@localhost tmp]# cpio -id < initrd 

[root@localhost tmp]# ls
bin  dev  etc  init  initrd  lib  proc  sbin  sys  sysroot
```

### 4.2.2 initramfs

initramfs是initrd的改进版本，它将进程为1的init文件直接放在了initramfs中，先运行init，再挂载根目录。解压后就可以直接看到init执行文件。如果是centos7版本，可以发现init是一个软连接，目标就是systemd命令。

## 4.3 `sysvinit` & `upstart` & `systemd`

```bash
sysvinit ---> centos5
upstart ---> centos6
systemd ---> centos7 ...
```

### 4.3.1 sysvinit

sysvinit启动风格，特点是：单线程的，顺序执行，后面的进程启动必须等待前面进程；同时，不是基于事件的启动方式，在centos5中使用。

它的管理方式就是运行级别体系，运行级别1至6共6个级别，不同的级别使用不同的rc目录中的脚本来启动或者停止相关服务。

### 4.3.2 upstart

sysvinit的替代品，更优。并行的，只要事件发生，就能够启动服务。比如，光驱或USB设备的的自动识别。其操作和配置方法与sysvinit风格一致。

```bash
# 启停服务
service sshd start|stop|restart|status
# 开机自启动
chkconfig --list sshd
chkconfig sshd on|off
# 通过运行级别可以关机
init 0 
# 重启
init 6
```

### 4.3.3 systemd

更好更加完善的启动风格，但是及其庞大和复杂，也经常被人诟病。

详细内容可以参看[systemd 中文手册](http://www.jinbuguo.com/systemd/systemd.html)。

```bash
# 启停服务
systemctl start|stop|status|restart sshd.service
# 开机自启动
systemctl disable|enable sshd
# 关机和重启
systemctl poweroff   
systemctl reboot
# 照顾大家习惯沿用了 init 0 和init 6

# 日志的管理
journalctl -f -u sshd
journalctl -u sshd
```

关于网络服务，centos7里也保留了network服务，并且是sysvinit风格的。未来版本将会取消（RHEL8中已经取消了），使用NetworkManager.service来管理。

```bash
# 可以使用原有的风格来管理网络服务
[root@cn2 ~]# chkconfig --list |grep network   # 不确定是否失效
network         0:off   1:off   2:on    3:on    4:on    5:on    6:off
[root@cn2 ~]# service network restart
Restarting network (via systemctl):                        [  OK  ]

# 用systemctl管理的network服务也是调用了rc脚本
[root@cn2 ~]# systemctl cat network
...
ExecStart=/etc/rc.d/init.d/network start
ExecStop=/etc/rc.d/init.d/network stop
```

systemd 启动过程，还是相当比较复杂的。

![](/images/2019-08-27-linux-system-startup/systemd-startup.png)

# x 参考资料

- [GRUB2配置文件"grub.cfg"详解(GRUB2实战手册)](http://www.jinbuguo.com/linux/grub.cfg.html)
- [GPT 分区详解](http://www.jinbuguo.com/storage/gpt.html)
- [第14章 Linux开机详细流程](https://www.cnblogs.com/f-ck-need-u/p/7100336.html)
- [grub2详解(翻译和整理官方手册)](https://www.cnblogs.com/f-ck-need-u/p/7094693.html)
- [systemd 中文手册](http://www.jinbuguo.com/systemd/systemd.html)
- [An introduction to the Linux boot and startup processes](https://opensource.com/article/17/2/linux-boot-and-startup)
- [OS boot partition](https://en.wikipedia.org/wiki/BIOS_boot_partition)
