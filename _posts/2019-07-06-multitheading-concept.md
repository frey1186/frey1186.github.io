---
layout: post
title:  关于多线程
date: 2019-07-06 12:00
tags: multitreading 
categories: public
typora-root-url: ..

---



# 1. 概述



每个正在系统上运行的程序都是一个进程。每个进程包含一到N个线程。进程也可能是整个程序或者是部分程序的动态执行。线程是一组指令的集合，或者是程序的特殊段，它可以在程序里独立执行。也可以把它理解为代码运行的上下文。所以线程基本上是轻量级的进程，它负责在单个程序里执行多任务。通常由操作系统负责多个线程的调度和执行。线程是程序中一个单一的顺序控制流程。在单个程序中同时运行多个线程完成不同的工作,称为多线程。

线程和进程的区别在于,子进程和父进程有不同的代码和数据空间,而多个线程则共享数据空间,每个线程有自己的执行堆栈和程序计数器为其执行上下文.多线程主要是为了节约CPU时间,发挥利用,根据具体情况而定. 线程的运行中需要使用计算机的内存资源和CPU。

`同步多线程（SMT）`是一种在一个CPU 的时钟周期内能够执行来自多个线程的指令的硬件多线程技术。本质上，同步多线程是一种将线程级并行处理（多CPU）转化为指令级并行处理（同一CPU）的方法。 同步多线程是单个物理处理器从多个硬件线程上下文同时分派指令的能力。同步多线程用于在商用环境中及为周期/指令（CPI）计数较高的工作负载创造性能优势。 处理器采用超标量结构，最适于以并行方式读取及运行指令。同步多线程使您可在同一处理器上同时调度两个应用程序，从而利用处理器的超标量结构性质。

`超线程（HT, Hyper-Threading）`是英特尔研发的一种技术，于2002年发布。通过此技术，英特尔实现在一个实体CPU中，提供两个逻辑线程。

其实可以将`SMT`和`HT`理解为一个技术。



> Hyper-threading (officially called Hyper- ThreadingTechnology or HT Technology, and abbreviated as HTT orHT) is Intel's proprietary simultaneous multithreading (SMT) implementation used to improve parallelization ofcomputations (doing multiple tasks at once) performed onx86 microprocessors.
>
> 来自 <https://cn.bing.com/search?q=intel+ht&go=%E6%8F%90%E4%BA%A4&qs=ds&form=QBLHCN> 



# 2. 与多进程的区别



> "进程——资源分配的最小单位，线程——程序执行的最小单位"



实际应用中基本上都是“进程+线程”的结合方式，千万不要真的陷入一种非此即彼的误区。



| 对比维度       | 多进程                                                       | 多线程                                                       | 总结     |
| -------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | -------- |
| 数据共享、同步 | 数据共享复杂，需要用IPC；数据是分开的，同步简单              | 因为共享进程数据，数据共享简单，但也是因为这个原因导致同步复杂 | 各有优势 |
| 内存、CPU      | 占用内存多，切换复杂，CPU利用率低                            | 占用内存少，切换简单，CPU利用率高                            | 线程占优 |
| 创建销毁、切换 | 创建销毁、切换复杂，速度慢                                   | 创建销毁、切换简单，速度很快                                 | 线程占优 |
| 编程、调试     | 编程简单，调试简单                                           | 编程复杂，调试复杂                                           | 进程占优 |
| 可靠性         | 进程间不会互相影响                                           | 一个线程挂掉将导致整个进程挂掉                               | 进程占优 |
| 分布式         | 适应于多核、多机分布式；如果一台机器不够，扩展到多台机器比较简单 | 适应于多核分布式                                             | 进程占优 |





- 需要注意：

> 1）需要频繁创建销毁的优先用线程
>
> 2）需要进行大量计算的优先使用线程
>
> 3）强相关的处理用线程，弱相关的处理用进程
>
> 一般的Server需要完成如下任务：消息收发、消息处理。“消息收发”和“消息处理”就是弱相关的任务，而“消息处理”里面可能又分为“消息解码”、“业务处理”，这两个任务相对来说相关性就要强多了。因此“消息收发”和“消息处理”可以分进程设计，“消息解码”、“业务处理”可以分线程设计。当然这种划分方式不是一成不变的，也可以根据实际情况进行调整。
>
> 4）可能要扩展到多机分布的用进程，多核分布的用线程
>
> 5）都满足需求的情况下，用你最熟悉、最拿手的方式
>
> 
>
> 来自 <https://blog.csdn.net/lishenglong666/article/details/8557215> 



# 3. 如何使用？



需要CPU、BIOS、操作系统、应用软件都支持多线程技术才可以。



# 4. 支持多线程的`CPU`

`Power CPU `支持的`SMT`技术：

> Simultaneous multithreading (SMT) is a processor technology that allows multiple instruction streams (threads) to run concurrently on the same physical processor, improving overall throughput. To the operating system, each hardware thread is treated as an independent logical processor. Single-threaded (ST) execution mode is also supported.
>
> 来自 <https://www.ibm.com/support/knowledgecenter/SSFHY8_6.2/reference/am5gr_f0106.html?view=embed> 

`Intel CPU `支持的`HT`技术：

> Intel® Hyper-Threading Technology (Intel® HT Technology) uses processor resources more efficiently, enabling multiple threads to run on each core. As a performance feature, it also increases processor throughput, improving overall performance on threaded software.
> Intel® HT Technology is available on the latest Intel® Core™ vPro™ processors, the Intel® Core™ processor family, the Intel® Core™ M processor family, and the Intel® Xeon® processor family. 
> By combining one of these Intel® processors and chipsets with an operating system and BIOS supporting Intel® HT Technology.
>
> 来自 <https://www.intel.com/content/www/us/en/architecture-and-technology/hyper-threading/hyper-threading-technology.html> 



# 5. `SMT/HT`支持情况

- Intel CPU : 2 Thread/Core
- Power9 CPU： 8 Thread /Core
- Sparc: 8 Thread /Core

## 5.1 `RHEL7/CentOS7 & Intel CPU`

`BIOS `中修改`SMT/HT` 的设置，使用这种方式`Enable`或者`Disable`后，将永久生效，需要重启。

```

Hyper-Threading Technology BIOS Setup Options

For Intel® Desktop/Server Boards setup option location is the main menu of the BIOS setup program.

 • Located on the same menu screen that already had Processor Type, Processor Speed, System Bus Speed, and other related processor fields.

 • Setup Option Text

  ○ The field is called Hyper-Threading Technology.

 • Setup Option Values

  ○ The setup option values are Enabled and Disabled.

 • Setup Option Help Text

来自 <https://www.intel.com/content/www/us/en/support/articles/000007645/boards-and-kits/desktop-boards.html> 

```



`RHEL/CentOS`操作系统中查看多线程情况：（更多信息：https://access.redhat.com/solutions/rhel-smt）



```bash
# lscpu | grep -e Socket -e Core -e Thread
Thread(s) per core: 2 # 线程数
Core(s) per socket: 6 # core 数量
Socket(s): 2
```



或者



```bash
# grep -H . /sys/devices/system/cpu/cpu*/topology/thread_siblings_list | sort -n -t ':' -k 2 -u

# 显示 /sys/devices/system/cpu/cpu0/topology/thread_siblings_list:0 # 表示HT关闭
# 显示 /sys/devices/system/cpu/cpu0/topology/thread_siblings_list:0-1 # 表示 HT 启用
```



操作系统层关闭多线程有几种办法：



- 方法一：使用`nosmt`启动参数，需要新的`x86 CPU`，需要重启

```bash
# grubby --args=nosmt --update-kernel=DEFAULT
# grub2-mkconfig -o  /boot/grub/grub.conf   # 创建新的grub.conf
# reboot  #重启
```

- 方法二：临时关闭，重启后失效

```bash
# echo off > /sys/devices/system/cpu/smt/control
```

```bash
 /sys/devices/system/cpu/smt/control:
This file allows to read out the SMT control state and provides the
     ability to disable or (re)enable SMT. The possible states are:
============== ===================================================
        on SMT is supported by the CPU and enabled. All
                        logical CPUs can be onlined and offlined without
                        restrictions.
off SMT is supported by the CPU and disabled. Only
                        the so called primary SMT threads can be onlined
                        and offlined without restrictions. An attempt to
                        online a non-primary sibling is rejected
forceoff Same as 'off' but the state cannot be controlled.
                        Attempts to write to the control file are rejected.
notsupported The processor does not support SMT. It's therefore
                        not affected by the SMT implications of L1TF.
                        Attempts to write to the control file are rejected.
        ============== ===================================================
The possible states which can be written into this file to control SMT
     state are:
     - on
     - off
     - forceoff
/sys/devices/system/cpu/smt/active:
This file reports whether SMT is enabled and active, i.e. if on any
     physical core two or more sibling threads are online.
```



## 5.2 AIX & Power：

`Power9 CPU`默认支持8线程，使用`smtctl`命令可以查看和修改` smt`级别。更多内容查看https://www.ibm.com/support/knowledgecenter/ssw_aix_72/com.ibm.aix.cmds5/smtctl.htm

- 查看` SMT level`

```bash
smtctl
```

- 临时修改 `SMT level`, # 可以是 `1, 2, 4 or 8`，重启后将恢复原来的`smt level`

```bash
smtctl -t 2 -w now
```

- 修改 `SMT level`永久生效，# 可以是 `1, 2, 4 or 8`，完成后需要使用`bosboot`创建启动设备

```bash
 smtctl -t 4 -w boot
 bosboot -a # Creates complete boot image and device.
```



## 5.3 RHEL7 & Power：

`OpenPower CPU` 默认支持4线程，安装`RHEL`后可以使用开源的工具 `ppc64_cpu`进行查看和修改多线程（更多查看 https://github.com/ibm-power-utilities/powerpc-utils）。

```bash
ppc64_cpu
---------

This allows users to set the smt state, smt-snooze-delay and other settings

on ppc64 processors. It also allows users to control the number of processor

cores which are online (not in the sleep state).
来自 <https://github.com/ibm-power-utilities/powerpc-utils> 
```

1，查看 `SMT level`

```bash
ppc64_cpu --smt
```

2，修改 `SMT `级别， `# is 1, 2, 4 or on` 

```bash
ppc64_cpu --smt=#
```

3， 关闭 `smt`支持

```bash
ppc64_cpu --smt=off
```



# 6. 其他

## 6.1 `oracle`数据库

`Oracle Database` 在12c之前`windows`平台下支持多线程，`Unix`和`Linux`只支持多进程模式。在`Oracle Database 12c`中，`Oracle`引入了多线程模式，允许在`Windows`平台之外的`Unix`、`Linux`系统使用多线程模式，结合多进程与多线程模式，`Oracle`可以改进进程管理与性能。

通过设置初始化参数` threaded_execution `，可以启用或关闭多线程模式，该参数缺省值为`False`，设置为`TRUE`启用12c的这个新特性：

``` sql
SQL> show parameter threaded_exec

NAME TYPE VALUE

---

threaded_execution boolean FALSE

SQL> alter system set threaded_execution=true scope=spfile;

System altered.

```

该参数重新启动数据库后生效，但是注意，多线程模式，不支持操作系统认证，不能直接启动数据库，需要提供`SYS`的密码认证后方能启动数据库：

``` sql
SQL> shutdown immediate;

SQL> startup

ORA-01017: invalid username/password; logon denied

# 需要通过用户名和密码登录数据库。

```

用`ps -ef` 检查一下进程/线程：

```bash
[oracle@enmocoredb dbs]$ ps -ef|grep ora_
oracle 27404 1 0 17:00 ? 00:00:00 ora_pmon_core
oracle 27406 1 0 17:00 ? 00:00:00 ora_psp0_core
oracle 27408 1 3 17:00 ? 00:00:05 ora_vktm_core
oracle 27412 1 0 17:00 ? 00:00:00 ora_u004_core
oracle 27418 1 0 17:00 ? 00:00:00 ora_u005_core
oracle 27424 1 0 17:00 ? 00:00:00 ora_dbw0_core
其中U<NNN>进程是共享线程的"容器进程"，每个进程可以容纳100个线程。
来自 https://www.eygle.com/archives/2013/07/oracle_database_12c_multithreaded_model.html 
```

# 参考

1，smt，https://www.cnblogs.com/idorax/p/6884088.html

2，intel-ht，https://www.intel.com/content/www/us/en/architecture-and-technology/hyper-threading/hyper-threading-technology.html

3，rhel-smt，https://access.redhat.com/solutions/rhel-smt

4，smt，https://blog.csdn.net/xlinsist/article/details/54562571

5，smtctl，https://www.ibm.com/support/knowledgecenter/ssw_aix_72/com.ibm.aix.cmds5/smtctl.htm

6，ppc64_cpu，https://github.com/ibm-power-utilities/powerpc-utils

7，bosboot，http://www.regatta.cs.msu.su/doc/usr/share/man/info/ru_RU/a_doc_lib/cmds/aixcmds1/bosboot.htm

8，https://blog.csdn.net/ashic/article/details/53810450

9，https://www.eygle.com/archives/2013/07/oracle_database_12c_multithreaded_model.html

