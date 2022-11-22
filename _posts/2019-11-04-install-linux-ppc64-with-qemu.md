---
layout: post
title: 使用QEMU模拟Linux-ppc64le
date: 2019-11-04 12:00
tags: linux qemu
categories: public
typora-root-url: ..
---

# 一、下载并编译QEMU

https://www.qemu.org/download/

QEMU可以支持模拟的硬件架构有：  

```bash
  --target-list=LIST       set target list (default: build everything)
                           Available targets: aarch64-softmmu alpha-softmmu
                           arm-softmmu cris-softmmu hppa-softmmu i386-softmmu
                           lm32-softmmu m68k-softmmu microblazeel-softmmu
                           microblaze-softmmu mips64el-softmmu mips64-softmmu
                           mipsel-softmmu mips-softmmu moxie-softmmu
                           nios2-softmmu or1k-softmmu ppc64-softmmu ppc-softmmu
                           riscv32-softmmu riscv64-softmmu s390x-softmmu
                           sh4eb-softmmu sh4-softmmu sparc64-softmmu
                           sparc-softmmu tricore-softmmu unicore32-softmmu
                           x86_64-softmmu xtensaeb-softmmu xtensa-softmmu
                           aarch64_be-linux-user aarch64-linux-user
                           alpha-linux-user armeb-linux-user arm-linux-user
                           cris-linux-user hppa-linux-user i386-linux-user
                           m68k-linux-user microblazeel-linux-user
                           microblaze-linux-user mips64el-linux-user
                           mips64-linux-user mipsel-linux-user mips-linux-user
                           mipsn32el-linux-user mipsn32-linux-user
                           nios2-linux-user or1k-linux-user
                           ppc64abi32-linux-user ppc64le-linux-user
                           ppc64-linux-user ppc-linux-user riscv32-linux-user
                           riscv64-linux-user s390x-linux-user sh4eb-linux-user
                           sh4-linux-user sparc32plus-linux-user
                           sparc64-linux-user sparc-linux-user
                           tilegx-linux-user x86_64-linux-user
                           xtensaeb-linux-user xtensa-linux-user
```

编译qemu：

```bash
wget https://download.qemu.org/qemu-4.1.0.tar.xz
tar xvJf qemu-4.1.0.tar.xz
cd qemu-4.1.0
./configure
make
```

或者

```bash
git clone https://git.qemu.org/git/qemu.git
cd qemu
git submodule init
git submodule update --recursive
./configure
make
```

这种方式比较慢，可以选择指定的类型进行编译，这样只是为ppc64配置

```bash
./configure --target-list=ppc64-softmmu && make
./configure --target-list=ppc64-softmmu --enable-spice && make   # 要用virt-manager的话需要使用spice
```

比如要编译x86的，并启用KVM

```bash
./configure --target-list=x86_64-softmmu --enable-kvm  && make
```

# 二、启动已有虚拟机

这里有个已经安装好的虚拟机镜像c7u5le.img.gz，解压后可以直接使用。这个虚拟机是centos7 for PPC64le。

```bash
[root@vm-centos7 cn4]# qemu-system-ppc64 -cpu POWER9 -machine pseries -m  1024 -drive file=cn4.img -serial stdio
[root@vm-centos7 cn4]# qemu-system-ppc64 -cpu POWER9 -machine pseries -m  1024 -drive file=cn4.img -serial stdio -vnc :1
```

其中有几个参数需要注意的：

-cpu：后面跟POWER9
-machine：pseries
-m：内存，以MB为单位
-drive：镜像文件
-serial：标准输出来处理串口输出的问题另外，

还有vnc，默认:1输出



![](/images/2019-11-04-install-linux-ppc64-with-qemu/centos7-vm-with-qemu.png)


# 三、关于模拟AIX

看了几篇文章，据说是可以模拟AIX的，这里测试一下，貌似不行。
这里用了一个aix7.2的镜像挂载到cdrom上，执行下面的命令：

```bash
[root@vm-centos7 vm]# qemu-system-ppc64 -cpu POWER8 -machine pseries -m  2G -serial stdio -cdrom /dev/sr0 -drive  file=cn5.img,if=none,id=drive-virtio-disk0 -device  virtio-scsi-pci,id=scsi -device scsi-hd,drive=drive-virtio-disk0 -net  nic -net user,hostfwd=tcp::2222-:22 -prom-env boot-command='boot cdrom:  -s verbose' -vnc :1
```

其中：

-prom-env boot-command='boot cdrom:  -s verbose'    是必须选项
-m 2G   最小必须2GB内存
-serial mon:stdio   串口输出信息，并且不能使用CTRL+C直接杀死虚拟机
-serial stdio   串口输出信息，可以使用CTRL+C直接杀死虚拟机

由于虚拟机里测试，不知道什么情况，一直卡在下面的界面：

![](/images/2019-11-04-install-linux-ppc64-with-qemu/error-of-aix.png)


四、关于虚拟机网络

这里是使用tap网络的一种方法：

```bash
[root@vm-centos7 cn4]# qemu-system-ppc64 -cpu POWER9 -machine pseries -m  1024 -drive file=cn4.img -serial stdio -vnc :1  -net nic -net tap,fname=tap0,script=no,downscript=no
```

待续...


# X、参考资料

- [1]  https://qemu.weilnetz.de/doc/qemu-doc.html
- [2]  https://www.qemu.org/documentation/
- [3] https://worthdoingbadly.com/aixqemu/
- [4] https://www.ibm.com/developerworks/community/blogs/cgaix/entry/AIX_7_2_running_on_my_Macbook?lang=en
- [5] https://virtuallyfun.com/wordpress/2019/04/22/installing-aix-on-qemu/
- [6] https://www.ibm.com/developerworks/community/blogs/cgaix/resource/AIX_QEMU_blog.pdf?lang=en



