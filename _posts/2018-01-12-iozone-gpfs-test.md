---
layout: post
title: iozone test for gpfs
date: 2018-01-12 12:00
author: felo
tags: gpfs iozone
categories: public
typora-root-url: ..
---





使用iozone对gpfs集群进行读写性能测试。

# 1.测试方法

在iozone里有一个`-+m`的选项可以测试集群文件系统的性能。
```bash
# -+m
-+m  filename
              Used  to  specify  a  filename that will be used to specify the
              clients in a distributed measurement.  The  file  contains  one
              line  for  each client. The fields are space delimited. Field 1
              is the client name. Field 2 is the working  directory,  on  the
              client,  where Iozone will run. Field 3 is the path to the exe-
              cutable Iozone on the client.
```
测试步骤：

- 集群各节点之间配置SSH无密码访问；
- 将iozone默认rsh指定为ssh；
- 编写集群测试配置文件；
- 使用iozone进行测试；




# 2.测试环境

虚拟机环境，测试结果没有太大的意义，只是记录下测试的方法。

```bash
# gpfs 环境，三个节点
 Node  Daemon node name  IP address      Admin node name  Designation
----------------------------------------------------------------------
   1   c01               192.168.56.101  c01              quorum-manager
   2   c02               192.168.56.102  c02              quorum
   3   c03               192.168.56.103  c03
# 节点OS版本
[root@c01 ~]# cat /etc/redhat-release
CentOS release 6.5 (Final)
[root@c01 ~]# uname -a
Linux c01 2.6.32-696.10.3.el6.x86_64 #1 SMP Tue Sep 26 18:14:22 UTC 2017 x86_64 x86_64 x86_64 GNU/Linux
# 挂载文件系统/gpfs2
Filesystem                  Size  Used Avail Use% Mounted on
/dev/gpfs2                  2.0G  171M  1.9G   9% /gpfs2
```

# 3.测试步骤

## 3.1 安装iozone

下载[iozone](http://www.iozone.org/src/current/iozone-3-471.src.rpm)，上传至三个节点中，并使用源码安装64位iozone。

```bash
[root@c01 ~]# ls -l iozone-3-471.src.rpm
-rwxr-xr-x 1 root root 830196 Jan 11 20:48 iozone-3-471.src.rpm
[root@c01 ~]# rpm -ivh iozone-3-471.src.rpm
   1:iozone                 ########################################### [100%]
[root@c01 ~]# cd rpmbuild/SOURCES/
[root@c01 SOURCES]# ls
iozone3_471.tar
[root@c01 SOURCES]# tar -xvf iozone3_471.tar
[root@c01 SOURCES]# cd iozone3_471/src/current/
[root@c01 current]# make linux-AMD64
[root@c01 current]# ./iozone -h
iozone: help mode
    Usage: iozone [-s filesize_kB] [-r record_size_kB] [-f [path]filename] [-h]
                  [-i test] [-E] [-p] [-a] [-A] [-z] [-Z] [-m] [-M] [-t children]
                  [-l min_number_procs] [-u max_number_procs] [-v] [-R] [-x] [-o]
                  [-d microseconds] [-F path1 path2...] [-V pattern] [-j stride]
                  [-T] [-C] [-B] [-D] [-G] [-I] [-H depth] [-k depth] [-U mount_point]
                  [-S cache_size] [-O] [-L cacheline_size] [-K] [-g maxfilesize_kB]
                  [-n minfilesize_kB] [-N] [-Q] [-P start_cpu] [-e] [-c] [-b Excel.xls]
                  [-J milliseconds] [-X write_telemetry_filename] [-w] [-W]
                  [-Y read_telemetry_filename] [-y minrecsize_kB] [-q maxrecsize_kB]
                  [-+u] [-+m cluster_filename] [-+d] [-+x multiplier] [-+p # ]
                  [-+r] [-+t] [-+X] [-+Z] [-+w percent dedupable] [-+y percent_interior_dedup]
                  [-+C percent_dedup_within]
                  ...
```

## 3.2 测试集群性能

```bash
# 编写配置文件
# 1，主机名或者ip地址
# 2，文件系统
# 3，iozone所在位置
# 4，临时文件生成位置
[root@c01 ~]# echo "c01 /gpfs2 /root/iozone /gpfs2/test_c01" >>/tmp/nodelist
[root@c01 ~]# echo "c02 /gpfs2 /root/iozone /gpfs2/test_c02" >>/tmp/nodelist
[root@c01 ~]# echo "c03 /gpfs2 /root/iozone /gpfs2/test_c03" >>/tmp/nodelist
[root@c01 ~]# cat /tmp/nodelist
c01 /gpfs2 /root/iozone /gpfs2/test_c01
c02 /gpfs2 /root/iozone /gpfs2/test_c02
c03 /gpfs2 /root/iozone /gpfs2/test_c03
# 改用ssh
[root@c01 ~]# export RSH=ssh
[root@c01 ~]# export rsh=ssh
# 开始测试
# -i 0 -i 1  测试读写性能，其中0表示测试写性能，会测试write和re-write两个，同样的1表示读性能，也会测试read和re-read两个。
# -s 测试文件大小，最好是内存的两倍
# -r 块大小
# -t 线程数，几个节点使用几个线程
# -+m 集群配置文件
# -C 显示子节点吞吐量
[root@c01 ~]# ./iozone -i 0 -i 1 -s 200M -r 4k -t 3  -+m /tmp/nodelist -C
        Iozone: Performance Test of File I/O
                Version $Revision: 3.471 $
                Compiled for 64 bit mode.
                Build: linux-AMD64

        Contributors:William Norcott, Don Capps, Isom Crawford, Kirby Collins
                     Al Slater, Scott Rhine, Mike Wisner, Ken Goss
                     Steve Landherr, Brad Smith, Mark Kelly, Dr. Alain CYR,
                     Randy Dunlap, Mark Montague, Dan Million, Gavin Brebner,
                     Jean-Marc Zucconi, Jeff Blomberg, Benny Halevy, Dave Boone,
                     Erik Habbinga, Kris Strecker, Walter Wong, Joshua Root,
                     Fabrice Bacchella, Zhenghua Xue, Qin Li, Darren Sawyer,
                     Vangel Bojaxhi, Ben England, Vikentsi Lapa,
                     Alexey Skidanov.

        Run began: Thu Jan 11 21:22:40 2018

        File size set to 204800 kB
        Record Size 4 kB
        Network distribution mode enabled.
        Command line used: ./iozone -i 0 -i 1 -s 200M -r 4k -t 3 -+m /tmp/nodelist -C
        Output is in kBytes/sec
        Time Resolution = 0.000001 seconds.
        Processor cache size set to 1024 kBytes.
        Processor cache line size set to 32 bytes.
        File stride size set to 17 * record size.
        Throughput test with 3 processes
        Each process writes a 204800 kByte file in 4 kByte records

        Test running:
        Children see throughput for  3 initial writers  =  393197.84 kB/sec
        Min throughput per process                      =  121949.16 kB/sec
        Max throughput per process                      =  136219.47 kB/sec
        Avg throughput per process                      =  131065.95 kB/sec
        Min xfer                                        =  183548.00 kB
        Child[0] xfer count =  204116.00 kB, Throughput =  135029.22 kB/sec
        Child[1] xfer count =  204800.00 kB, Throughput =  136219.47 kB/sec
        Child[2] xfer count =  183548.00 kB, Throughput =  121949.16 kB/sec

        Test running:
        Children see throughput for  3 rewriters        =  938180.25 kB/sec
        Min throughput per process                      =  245367.28 kB/sec
        Max throughput per process                      =  440644.44 kB/sec
        Avg throughput per process                      =  312726.75 kB/sec
        Min xfer                                        =  116732.00 kB
        Child[0] xfer count =  204800.00 kB, Throughput =  440644.44 kB/sec
        Child[1] xfer count =  119804.00 kB, Throughput =  252168.53 kB/sec
        Child[2] xfer count =  116732.00 kB, Throughput =  245367.28 kB/sec

        Test running:
        Children see throughput for  3 readers          = 4044318.38 kB/sec
        Min throughput per process                      = 1125264.00 kB/sec
        Max throughput per process                      = 1608165.88 kB/sec
        Avg throughput per process                      = 1348106.12 kB/sec
        Min xfer                                        =  163780.00 kB
        Child[0] xfer count =  163780.00 kB, Throughput = 1125264.00 kB/sec
        Child[1] xfer count =  204800.00 kB, Throughput = 1608165.88 kB/sec
        Child[2] xfer count =  183236.00 kB, Throughput = 1310888.50 kB/sec

        Test running:
        Children see throughput for 3 re-readers        = 3972303.62 kB/sec
        Min throughput per process                      = 1172565.25 kB/sec
        Max throughput per process                      = 1406844.12 kB/sec
        Avg throughput per process                      = 1324101.21 kB/sec
        Min xfer                                        =  181804.00 kB
        Child[0] xfer count =  204800.00 kB, Throughput = 1392894.25 kB/sec
        Child[1] xfer count =  181804.00 kB, Throughput = 1172565.25 kB/sec
        Child[2] xfer count =  204800.00 kB, Throughput = 1406844.12 kB/sec

        Test cleanup:


iozone test complete.
```

结果说明：
- Write:测试向一个新文件写入的性能。当一个新文件被写入时，不仅仅是那些文件中的数据需要被存储，还包括那些用于定位数据存储在存储介质的具体位置的额外信息。这些额外信息被称作“元数据”。它包括目录信息，所分配的空间和一些与该文件有关但又并非该文件所含数据的其他数据。拜这些额外信息所赐，Write的性能通常会比Re-write的性能低。
- Re-write:测试向一个已存在的文件写入的性能。当一个已存在的文件被写入时，所需工作量较少，因为此时元数据已经存在。Re-write的性能通常比Write的性能高。
- Read: 测试读一个已存在的文件的性能。
- Re-Read:测试读一个最近读过的文件的性能。Re-Read性能会高些，因为操作系统通常会缓存最近读过的文件数据。这个缓存可以被用于读以提高性能。

## 3.3 其他

```bash
# 输出到xls文件中
[root@c01 ~]# ./iozone -i 0 -i 1 -s 200M -Rb /tmp/test.xls -r 4k -t 3  -+m /tmp/nodelist -C
# 保存日志
[root@c01 ~]# ./iozone -i 0 -i 1 -s 200M -r 4k -t 3  -+m /tmp/nodelist -C |tee /tmp/test.log
```



# 4.参考

- http://www.iozone.org/src/current/iozone-3-471.src.rpm
- https://wenku.baidu.com/view/65d861cec850ad02de8041f8.html
- http://www.iozone.org/
- https://yq.aliyun.com/articles/27834?spm=5176.100239.blogcont15231.15.351824aeu6k3Zi