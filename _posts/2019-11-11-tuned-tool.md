---
layout: post
title: RHEL tuned
date: 2019-11-11 12:00
tags: linux 
categories: linux-basics
typora-root-url: ..
---

# 1. tuned

tuned从rhel6.3开始引入，可以针对不同的业务类型来实施优化，内置了部分优化脚本也可以自己定制脚本。

主要用于简化调优的管理，充分利用资源。

tuned以服务的形式运行。从RHEL7.2开始可以使用非服务的方式运行，但是有一些局限性。如果将 /etc/tuned/tuned-main.conf 文件中将dynamic_tuning 设置为 1，可以开启动态调整模式，默认关闭。


# 2. 安装服务

```bash
# 安装
yum install tuned

# 启动服务
systemctl start tuned
systemctl enable tuned
```
# 3. 系统默认的profile

```bash
Available profiles:
- balanced                    - General non-specialized tuned profile
- desktop                     - Optimize for the desktop use-case
- hpc-compute                 - Optimize for HPC compute workloads
- latency-performance         - Optimize for deterministic performance at the cost of increased power consumption
- network-latency             - Optimize for deterministic performance at the cost of increased power consumption, focused on low latency network performance
- network-throughput          - Optimize for streaming network throughput, generally only necessary on older CPUs or 40G+ networks
- powersave                   - Optimize for low power consumption
- throughput-performance      - Broadly applicable tuning that provides excellent performance across a variety of common server workloads
- virtual-guest               - Optimize for running inside a virtual guest
- virtual-host                - Optimize for running KVM guests
```

这些脚本对应的就是在/usr/lib/tuned/目录下的各个同名文件夹，下面各有一个tuned.conf的调优配置文件，比如virtual-host:

```bash
[root@vm-centos7 tuned]# pwd
/usr/lib/tuned
[root@vm-centos7 tuned]# cat virtual-host/tuned.conf
#
# tuned configuration
#

[main]
summary=Optimize for running KVM guests    # 备注
include=throughput-performance             # 包含的其他profile

[sysctl]
# Start background writeback (via writeback threads) at this percentage (system
# default is 10%)  
# 针对sysctl的内核参数调整
vm.dirty_background_ratio = 5

# The total time the scheduler will consider a migrated process
# "cache hot" and thus less likely to be re-migrated
# (system default is 500000, i.e. 0.5 ms)
kernel.sched_migration_cost_ns = 5000000

[cpu]
# Setting C3 state sleep mode/power savings    # 针对CPU的参数调整
force_latency=70

```

# 4.编写自己的tuned.conf

可以和系统默认的位置上/usr/lib/tuned/下面直接创建,也可以在/etc/tuned/下创建。

```bash
[root@vm-centos7 tuned]# pwd
/usr/lib/tuned
[root@vm-centos7 tuned]# mkdir my-test
[root@vm-centos7 tuned]# vim my-test/tuned.conf
[root@vm-centos7 tuned]# cat my-test/tuned.conf
#
# tuned configuration
#

[main]
summary=my test tuned profile.
include=network-throughput

[sysctl]
net.ipv4.tcp_rmem="4096 87380 16777216"
net.ipv4.tcp_wmem="4096 16384 16777216"
net.ipv4.udp_mem="3145728 4194304 16777216"
[root@vm-centos7 tuned]#
Current active profile: virtual-guest
[root@vm-centos7 tuned]# tuned-adm list |grep my-test
- my-test                     - my test tuned profile.

```

编写tuned.conf可以参考man手册`man tuned.conf`.

# 5. 启用和停止tuned

```bash
# 启用一个profile
[root@vm-centos7 ~]# tuned-adm profile my-test

# 激活启用的profile
[root@vm-centos7 ~]# tuned-adm active
Current active profile: my-test

# 系统推荐的profile
[root@vm-centos7 ~]# tuned-adm recommend
virtual-guest

# 列举当前profile的状态，末尾会显示启用的profile
[root@vm-centos7 ~]# tuned-adm list
Available profiles:
- balanced                    - General non-specialized tuned profile
- desktop                     - Optimize for the desktop use-case
- hpc-compute                 - Optimize for HPC compute workloads
- latency-performance         - Optimize for deterministic performance at the cost of increased power consumption
- my-test                     - my test tuned profile.
- network-latency             - Optimize for deterministic performance at the cost of increased power consumption, focused on low latency network performance
- network-throughput          - Optimize for streaming network throughput, generally only necessary on older CPUs or 40G+ networks
- powersave                   - Optimize for low power consumption
- throughput-performance      - Broadly applicable tuning that provides excellent performance across a variety of common server workloads
- virtual-guest               - Optimize for running inside a virtual guest
- virtual-host                - Optimize for running KVM guests
Current active profile: my-test

# 关闭
[root@vm-centos7 ~]# tuned-adm off
```


# X、参考资料

- [1] https://www.tecmint.com/tuned-automatic-performance-tuning-of-centos-rhel-servers/
- [2] https://blog.csdn.net/chalefly/article/details/71216449 
- [3] https://www.rcannings.com/centos-7-tuned-parameters-misinterpreted/
- [4] [RHEL7 Chapter 3. Tuned](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/performance_tuning_guide/chap-red_hat_enterprise_linux-performance_tuning_guide-tuned)

