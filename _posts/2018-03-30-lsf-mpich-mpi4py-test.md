---
layout: post
title: LSF & MPICH & MPI4PY 的简单例子
date: 2018-03-30 12:00
author: felo
tags: lsf mpi
categories: public
typora-root-url: ..
---

![](/images/lsf-mpi/para-compute.jpeg)

# 1.env

`lsf`基本环境：

```bash
[vagrant@lsf1 ~]$ bhosts 
HOST_NAME          STATUS       JL/U    MAX  NJOBS    RUN  SSUSP  USUSP    RSV 
lsf1               ok              -      1      0      0      0      0      0
lsf2               ok              -      1      0      0      0      0      0
lsf3               ok              -      2      0      0      0      0      0
lsf4               ok              -      1      0      0      0      0      0
[vagrant@lsf1 ~]$ lsid
IBM Platform LSF Standard 9.1.3.0, Jul 04 2014
Copyright IBM Corp. 1992, 2014. All rights reserved.
US Government Users Restricted Rights - Use, duplication or disclosure restricted by GSA ADP Schedule Contract with IBM Corp.

My cluster name is cluster1
My master name is lsf1
[vagrant@lsf1 ~]$ cat /etc/hosts
...
192.168.56.171 lsf1
192.168.56.172 lsf2
192.168.56.173 lsf3
192.168.56.174 lsf4
# 共享目录：/vagrant
[vagrant@lsf1 test_home]$ df -h
Filesystem               Size  Used Avail Use% Mounted on
...
none                     239G  182G   57G  77% /vagrant

```

`mpich`基本环境：4个节点都安装

```bash
[vagrant@lsf1 test_home]$ rpm -qa |grep mpich
mpich-autoload-3.1-4.fc22.x86_64
mpich-debuginfo-3.1-4.fc22.x86_64
mpich-devel-3.1-4.fc22.x86_64
mpich-3.1-4.fc22.x86_64
# export PATH
[vagrant@lsf1 test_home]$ export PATH=/usr/lib64/mpich/bin:$PATH
```

`mpi4py`环境：4个节点都安装好`mpi4py`

```bash
[vagrant@lsf1 test_home]$ python -m mpi4py
No path specified for execution
usage: python -m mpi4py [options] <pyfile> [arg] ...
   or: python -m mpi4py [options] -m <mod> [arg] ...
   or: python -m mpi4py [options] -c <cmd> [arg] ...
   or: python -m mpi4py [options] - [arg] ...
Try `python -m mpi4py -h` for more information.
```

# 2.test

使用python的mpi4py库，编写一个简单的脚本：

```bash
[vagrant@lsf1 test_home]$ cat test.py 
from mpi4py import MPI
import os,time

comm= MPI.COMM_WORLD
comm_rank = comm.Get_rank()
comm_size = comm.Get_size()

time.sleep(10)
hostname = os.popen('hostname')
print "I am the %d process of %d processes in host: %s" % (comm_rank,comm_size,hostname.read())
```

使用lsf来提交执行这个脚本，如下所示：

```bash
[vagrant@lsf1 test_home]$ bsub -n 4 -o 1.log 'mpiexec python /vagrant/test_home/test.py'
Job <343> is submitted to default queue <normal>.
# -n 4: 4 core
# -o 输出日志
# mpiexec python /vagrant/test_home/test.py 使用mpiexec执行脚本
[vagrant@lsf1 test_home]$ cat 1.log 
Sender: LSF System <vagrant@lsf3>
Subject: Job 343: <mpiexec python /vagrant/test_home/test.py> in cluster <cluster1> Done

Job <mpiexec python /vagrant/test_home/test.py> was submitted from host <lsf1> by user <vagrant> in cluster <cluster1>.
Job was executed on host(s) <2*lsf3>, in queue <normal>, as user <vagrant> in cluster <cluster1>.
                            <1*lsf2>
                            <1*lsf4>
# 可见分布在3个host上执行，其中lsf3两个core，2和4个1个core
</home/vagrant> was used as the home directory.
</vagrant/test_home> was used as the working directory.
Started at Sat Mar 31 11:54:50 2018
Results reported on Sat Mar 31 11:55:02 2018
# 全部用时12s
Your job looked like:

------------------------------------------------------------
# LSBATCH: User input
mpiexec python /vagrant/test_home/test.py
------------------------------------------------------------

Successfully completed.

Resource usage summary:

    CPU time :                                   0.78 sec.
    Max Memory :                                 17 MB
    Total Requested Memory :                     -
    Delta Memory :                               -

The output (if any) follows:

I am the 1 process of 4 processes in host: lsf3

I am the 3 process of 4 processes in host: lsf4

I am the 2 process of 4 processes in host: lsf2

I am the 0 process of 4 processes in host: lsf3

# 脚本居然真的并行执行了...
```

