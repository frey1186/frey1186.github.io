https://blog.csdn.net/xuensong520/article/details/48269477

## 项目背景介绍

本次项目目的在于构建一个具有高性能、支持高并发读写、文件共享的存储系统。Lustre在HPC领域被广泛使用，本次项目建设也是在调研了其他诸多文件系统之后，最终选择Lustre文件系统作为软件部分，由于Lustre文件系统本身无数据安全机制，必须构建于稳定的磁盘阵列之上，通过硬件的稳定性来解决数据的安全性。

硬件层面可以从两个方面来保证数据的安全性。

- RAID组
- 节点冗余

这里节点冗余包括MDS和OSS节点，2个MDS节点互为active/stanby模式，两个OSS节点均为active模式。基本上实现数据访问不中断。

## 软件安装

这里使用的是DDN打包好的es-hpc-2.1.2-Cent-r41-x86_64-DVD.iso镜像文件，直接作为操作系统的ISO文件安装操作系统即可。系统安装完毕后，所有相关软件均会同步安装完毕。安装的过程中若原先系统盘中有数据会提示你是否将原先数据格式清除，在系统盘引导界面需选择相应的安装项，按e键进入编辑模式，添加skip-sda-check参数，跳过安全检查，即可直接安装。

系统安装完毕后，需配置好一些准备工作：

- 确保TCP和IB网络正常
- 添加主机名-IP地址隐射关系
- 关闭防火墙和selinux
- 确保时间同步

确认完成以上内容后，即可开始文件系统创建。

## MDS节点部署

MDS节点即为lustre的元数据节点，一般采用2台服务器作为mds节点进行部署，一个处于avtive状态，另一个处于standby状态。MDS节点安装配置分为几步：

- 格式化磁盘
- 配置lustre.conf文件
- 加载lustre内核模块
- 挂载磁盘

### 格式化磁盘

MDT

```
mkfs.lustre --mdt --index=0 --fsname=lustre --failnode=11.11.11.35@o2ib --failnode=192.168.242.35@tcp --mgsnode=11.11.11.34@o2ib --mgsnode=11.11.11.35@o2ib --mgsnode=192.168.242.34@tcp --mgsnode=192.168.242.35@tcp  --mkfsoptions="-m 1 -J size=4096"  --reformat --verbose /dev/mapper/mdt
12
```

MGT

```
mkfs.lustre --mgs --fsname=lustre --failnode=11.11.11.35@o2ib --failnode=192.168.242.35@tcp --reformat --verbose  /dev/mapper/mgt
12
```

命令比较长，不做过多解释，从字面上基本上都能理解各个参数的含义。

### lustre.conf

lustre.conf为luster的配置文件，文件内容只有一项，是关于文件系统网络的配置：

```
[root@mds00 new]# cat /etc/modprobe.d/lustre.conf
options lnet networks=o2ib(bond0),tcp(eth2)
123
```

这里有两套网络，用逗号各个，注意语法规则，前面的为IB网络，后面的为tcp网络，括号里面的是网络设备名称，必须与当前处于up状态的网卡进行对应。这里ib网络用了2个端口进行绑定，所以用的是bond0，以太网为eth2网卡。

### 加载lustre内核模块

默认操作系统安装好后，系统启动不会加载lustre模块，可通过命令

```
lsmod|grep lustre
12
```

进行查看是否加载了lustre模块。

手动加载lustre模块：

```
modprobe lustre
12
```

整个文件系统创建最关键的一步就在这里，lustre内核模块加载成功后，后面基本上不有什么大的问题。因为lustre模块对操作系统的内核以及IB驱动的版本均有很强的依赖关系，有一个不匹配就会加载不上，如果报错，先检查lustre.conf文件格式是否正确，如果确认lustre.conf内容无误，再取查看具体messages日志信息。

### 挂载MDT、MGT

完成上面几步之后，即可进行MDT和MGT挂载.

MGT

```
mount -t lustre /dev/mapper/mgt /lustre/mgt/
12
```

MDT

```
mount -t lustre /dev/mapper/mdt /lustre/mdt/
12
```

挂载时间会比较长，大概1-2分钟，需要多等一会。

到这里就完成了lustre的mds节点部署。

## OSS节点部署

oss节点即为lustre的数据存储节点，影响oss节点数量的因素有以下几个：

- 磁盘阵列的规模及聚合带宽
- 单个oss节点的网络带宽

为保障节点间高可用，原则上集群中oss节点数量应为偶数，两两互为备份。ost的数量也要求为偶数，互为备份的两个oss节点上挂载数目相同的ost。本次项目环境中仅有2个oss节点、14个ost，每组ost为8+2 Raid6，4块盘作为热备盘，磁盘阵列共144*6T 7.2k SAS盘.

部署oss节点与mds节点过程类似，步骤如下：

### 格式化磁盘

这里每个oss节点上共有7个ost

```
mkfs.lustre --ost --index=0 --fsname=lustre --failnode=11.11.11.37@o2ib --failnode=192.168.242.37@tcp --mgsnode=11.11.11.34@o2ib --mgsnode=11.11.11.35@o2ib --mgsnode=192.168.242.34@tcp --mgsnode=192.168.242.35@tcp --mkfsoptions="-m 1 -i 131072" --reformat --verbose /dev/mapper/360001ff0a101a0000000000089c50000

mkfs.lustre --ost --index=1 --fsname=lustre --failnode=11.11.11.37@o2ib --failnode=192.168.242.37@tcp --mgsnode=11.11.11.34@o2ib --mgsnode=11.11.11.35@o2ib --mgsnode=192.168.242.34@tcp --mgsnode=192.168.242.35@tcp --mkfsoptions="-m 1 -i 131072" --reformat --verbose /dev/mapper/360001ff0a101a0000000000189c60001

mkfs.lustre --ost --index=2 --fsname=lustre --failnode=11.11.11.37@o2ib --failnode=192.168.242.37@tcp --mgsnode=11.11.11.34@o2ib --mgsnode=11.11.11.35@o2ib --mgsnode=192.168.242.34@tcp --mgsnode=192.168.242.35@tcp --mkfsoptions="-m 1 -i 131072" --reformat --verbose /dev/mapper/360001ff0a101a0000000000289c70002

mkfs.lustre --ost --index=3 --fsname=lustre --failnode=11.11.11.37@o2ib --failnode=192.168.242.37@tcp --mgsnode=11.11.11.34@o2ib --mgsnode=11.11.11.35@o2ib --mgsnode=192.168.242.34@tcp --mgsnode=192.168.242.35@tcp --mkfsoptions="-m 1 -i 131072" --reformat --verbose /dev/mapper/360001ff0a101a0000000000389c80003

mkfs.lustre --ost --index=4 --fsname=lustre --failnode=11.11.11.37@o2ib --failnode=192.168.242.37@tcp --mgsnode=11.11.11.34@o2ib --mgsnode=11.11.11.35@o2ib --mgsnode=192.168.242.34@tcp --mgsnode=192.168.242.35@tcp --mkfsoptions="-m 1 -i 131072" --reformat --verbose /dev/mapper/360001ff0a101a0000000000489c90004

mkfs.lustre --ost --index=5 --fsname=lustre --failnode=11.11.11.37@o2ib --failnode=192.168.242.37@tcp --mgsnode=11.11.11.34@o2ib --mgsnode=11.11.11.35@o2ib --mgsnode=192.168.242.34@tcp --mgsnode=192.168.242.35@tcp --mkfsoptions="-m 1 -i 131072" --reformat --verbose /dev/mapper/360001ff0a101a0000000000589ca0005

mkfs.lustre --ost --index=6 --fsname=lustre --failnode=11.11.11.37@o2ib --failnode=192.168.242.37@tcp --mgsnode=11.11.11.34@o2ib --mgsnode=11.11.11.35@o2ib --mgsnode=192.168.242.34@tcp --mgsnode=192.168.242.35@tcp --mkfsoptions="-m 1 -i 131072" --reformat --verbose /dev/mapper/360001ff0a101a0000000000689cb0006
1234567891011121314
```

格式化磁盘后，配置lustre.conf文件及加载lustre模块，过程与mds相同，这里不做过多说明，下面进行磁盘挂载。

### 挂载OST

```
mount -t lustre /dev/mapper/360001ff0a101a0000000000089c50000 /lustre/ost00/
mount -t lustre /dev/mapper/360001ff0a101a0000000000189c60001 /lustre/ost01/
mount -t lustre /dev/mapper/360001ff0a101a0000000000289c70002 /lustre/ost02/
mount -t lustre /dev/mapper/360001ff0a101a0000000000389c80003 /lustre/ost03/
mount -t lustre /dev/mapper/360001ff0a101a0000000000489c90004 /lustre/ost04/
mount -t lustre /dev/mapper/360001ff0a101a0000000000589ca0005 /lustre/ost05/
mount -t lustre /dev/mapper/360001ff0a101a0000000000689cb0006 /lustre/ost06/
12345678
```

以上完成了其中一个oss节点的部署，另外一个节点操作与此类似。

完成以上配置后，lustre文件系统的配置基本结束，客户端安装lustre客户端软件包并加载lustre模块即可挂载使用了。客户端配置后面再详细说明。

## HA实现说明

上面的操作只完成了基本的lustre的文件系统创建，若想实现文件系统的高可用，还需进一步配置才行。本次项目使用的是基于corosync+pacemaker进行资源和节点间心跳管理。这里创建2组资源，一组为MDS，一组为OSS。也可将2组资源合并到一起，这里为了方便管理和后期扩容，将MDS和OSS进行分离，创建两组秘钥。

### 节点HA

corosync.conf具体配置如下：

```
[root@mds00 ~]# cat /etc/corosync/corosync.conf
compatibility: none

totem {
    version: 2
    secauth: off
    threads: 0

    # Tuning for highly congested networks
    # token:
    # This timeout specifies in milliseconds until a token loss is
    # declared after not receiving a token. This is the time spent
    # detecting a failure of a processor in the current configuration.
    # Reforming a new configuration takes about 50 milliseconds in
    # addition to this timeout.
    # The default is 1000 milliseconds.
    token: 10000
    # retransmits_before_loss:
    # This  value  identifies  how  many  token  retransmits should be
    # attempted before forming a new configuration.  If this value  is
    # set,  retransmit  and hold will be automatically calculated from
    # retransmits_before_loss and token.
    # The default is 4 retransmissions.
    retransmits_before_loss: 25
    # consensus:
    # This  timeout  specifies  in  milliseconds  how long to wait for
    # consensus  to  be  achieved  before  starting  a  new  round  of
    # membership configuration.
    # The default is 200 milliseconds.
    consensus: 12000
    # join:
    # This timeout specifies in milliseconds how long to wait for join
    # messages in the membership protocol.
    # The default is 100 milliseconds.
    join: 1000
    # merge:
    # This  timeout  specifies in milliseconds how long to wait before
    # checking for a partition when  no  multicast  traffic  is  being
    # sent.   If  multicast traffic is being sent, the merge detection
    # happens automatically as a function of the protocol.
    # The default is 200 milliseconds.
    merge: 400
    # downcheck:
    # This timeout specifies in milliseconds how long to  wait  before
    # checking  that  a network interface is back up after it has been
    # downed.
    # The default is 1000 millseconds.
    downcheck: 2000

    rrp_mode: passive

    interface {
            member {
                    memberaddr: 192.168.242.34
            }
            member {
                    memberaddr: 192.168.242.35
            }
            ringnumber: 0
            #bindnetaddr: 226.94.1.1
            bindnetaddr: 192.168.242.0
            mcastport: 5401
            ttl: 1
    }
    transport: udpu
}


logging {
    fileline: off
    to_stderr: no
    to_logfile: yes
    to_syslog: yes
    logfile: /var/log/cluster/corosync.log
    debug: off
    timestamp: on
    logger_subsys {
            subsys: AMF
            debug: off
    }
}

amf {
    mode: disabled
}
```

这里只列出了MDS节点的配置文件，OSS节点与此类似。

生成秘钥文件 
命令：

```
corosync-keygen
```

执行该命令后会，在/etc/corosync/目录下会生成authkey文件，将该文件和corosync.conf一起拷贝到另外一个mds节点上。

配置文件都准备好之后将corosync服务重启一下,然后执行crm_mon命令查看集群状态

```
Last updated: Sun Sep  6 02:37:16 2015
Last change: Tue Aug 25 23:12:18 2015 via crmd on oss00
Stack: classic openais (with plugin)
Current DC: oss01 - partition with quorum
Version: 1.1.10-14.el6_5.3-368c726
2 Nodes configured, 2 expected votes
14 Resources configured


Online: [ oss00 oss01 ]

res_Filesystem_ost07    (ocf::heartbeat:Filesystem):    Started oss01
res_Filesystem_ost08    (ocf::heartbeat:Filesystem):    Started oss01
res_Filesystem_ost09    (ocf::heartbeat:Filesystem):    Started oss01
res_Filesystem_ost0a    (ocf::heartbeat:Filesystem):    Started oss01
res_Filesystem_ost0b    (ocf::heartbeat:Filesystem):    Started oss01
res_Filesystem_ost0c    (ocf::heartbeat:Filesystem):    Started oss01
res_Filesystem_ost0d    (ocf::heartbeat:Filesystem):    Started oss01
res_Filesystem_ost00    (ocf::heartbeat:Filesystem):    Started oss00
res_Filesystem_ost01    (ocf::heartbeat:Filesystem):    Started oss00
res_Filesystem_ost02    (ocf::heartbeat:Filesystem):    Started oss00
res_Filesystem_ost03    (ocf::heartbeat:Filesystem):    Started oss00
res_Filesystem_ost04    (ocf::heartbeat:Filesystem):    Started oss00
res_Filesystem_ost05    (ocf::heartbeat:Filesystem):    Started oss00
res_Filesystem_ost06    (ocf::heartbeat:Filesystem):    Started oss00
```

看到有2个节点在线oss00和oss01。下面是这两个节点的资源分配情况，这里借助的是图形化工具lcmc，进行资源添加和分配，并设置优先级，也可通过命令行来操作，但较为麻烦。借助图形化工具划分好资源后，我们可通过命令行进行配置文件查看，具体方法如下：

```
[root@oss00 ~]# crm
crm(live)# configure
crm(live)configure# show
```

执行前面2条命令后，查看配置文件可执行show，通过LCMC添加完资源后，我们可通过命令行的方式进行参数编辑，若想编辑配置文件可执行edit，进入后，同vim编辑器操作相同。

### 磁盘HA

磁盘与节点间使用的是多路径软件multipath来实现，将所有OST或MDT磁盘阵列同时映射给相应的OSS节点或MDS节点。

```
[root@mds00 ~]# multipath -ll
mdt (3600c0ff0001e1c81cb32d75501000000) dm-2 DotHill,DH3824
size=540G features='0' hwhandler='0' wp=rw
|-+- policy='round-robin 0' prio=1 status=active
| `- 11:0:0:0 sdb 8:16 active ready running
`-+- policy='round-robin 0' prio=1 status=enabled
`- 12:0:0:0 sdd 8:48 active ready running
mgt (3600c0ff0001e1c812233d75501000000) dm-3 DotHill,DH3824
size=19G features='0' hwhandler='0' wp=rw
|-+- policy='round-robin 0' prio=1 status=active
| `- 11:0:0:1 sdc 8:32 active ready running
`-+- policy='round-robin 0' prio=1 status=enabled
  `- 12:0:0:1 sde 8:64 active ready running
```

这里列出的是MDS节点上的mdt存储磁盘，这里有2个设备：mdt与mgt，也可将mgt与mdt合并，我这里磁盘比较富裕，就单独为mgt创建了一块分区作为mgt存储区域。同时再另外一台备份节点上也可发现相同的2个设备，如下：

```
[root@mds01 ~]# multipath -ll
mdt (3600c0ff0001e1c81cb32d75501000000) dm-2 DotHill,DH3824
size=540G features='0' hwhandler='0' wp=rw
|-+- policy='round-robin 0' prio=1 status=active
| `- 11:0:0:0 sdb 8:16 active ready running
`-+- policy='round-robin 0' prio=1 status=enabled
  `- 12:0:0:0 sdd 8:48 active ready running
mgt (3600c0ff0001e1c812233d75501000000) dm-3 DotHill,DH3824
size=19G features='0' hwhandler='0' wp=rw
|-+- policy='round-robin 0' prio=1 status=active
| `- 11:0:0:1 sdc 8:32 active ready running
`-+- policy='round-robin 0' prio=1 status=enabled
 `- 12:0:0:1 sde 8:64 active ready running
```

### 网络HA

这里IO节点的IB网卡均配置了双网卡，绑定提高网卡的稳定性。步骤如下：

配置IP地址

```
[root@mds00 ~]# cat /etc/sysconfig/network-scripts/ifcfg-ib0
DEVICE=ib0
TYPE=InfiniBand
BOOTPROTO=none
ONBOOT=yes
USERCTL=no
MASTER=bond0
SLAVE=yes
PRIMARY=yes


[root@mds00 ~]# cat /etc/sysconfig/network-scripts/ifcfg-ib1
DEVICE=ib1
TYPE=InfiniBand
BOOTPROTO=none
ONBOOT=yes
USERCTL=no
MASTER=bond0
SLAVE=yes
PRIMARY=no


[root@mds00 ~]# cat /etc/sysconfig/network-scripts/ifcfg-bond0
DEVICE=bond0
#TYPE=InfiniBand
IPADDR=11.11.11.34
NETMASK=255.255.255.0
USERCTL=no
BOOTPROTO=static
ONBOOT=yes
```

新建bond.conf文件，内容如下：

```
[root@mds00 ~]# cat /etc/modprobe.d/bond.conf
alias bond0 bonding
options bond0 mode=1 miimon=100
```

加载该配置文件

```
modprobe bonding
```

重启网卡后，查看网卡状态：

```
[root@oss00 ~]# cat /proc/net/bonding/bond0
Ethernet Channel Bonding Driver: v3.6.0 (September 26, 2009)

Bonding Mode: fault-tolerance (active-backup) (fail_over_mac active)
Primary Slave: None
Currently Active Slave: ib0
MII Status: up
MII Polling Interval (ms): 100
Up Delay (ms): 0
Down Delay (ms): 0

Slave Interface: ib0
MII Status: up
Speed: 56000 Mbps
Duplex: full
Link Failure Count: 0
Permanent HW addr: a0:04:02:20:fe:80
Slave queue ID: 0

Slave Interface: ib1
MII Status: up
Speed: 56000 Mbps
Duplex: full
Link Failure Count: 0
Permanent HW addr: a0:04:03:00:fe:80
Slave queue ID: 0
```

这里绑定模式选择的是1，即active-backup模式。

## 客户端配置

客户端安装首先需要编译适合当前生产环境版本的lustre-clinet安装包，可使用lustre源码包进行编译。

首先将 lustre 的源码 copy 到 本地,然后解压缩源码文件。进入到源码的路径下。 
因为是 lustre 客户端的编译,所以和 IO server 端的编译不同。我们在 
编译的过程中不需要很多复杂的工具,所以在指定编译命令的时候需要增加一 
些相应的参数。 编译命令如下:

```
./configure --with-o2ib=/usr/src/ofa_kernel/default/ --with-linux=/usr/src/kernels/2.6.32-504.el6.x86_64/ --disable- server
```

–with-o2ib 参数指定了 lustre 所支持的网络为 IB 网络,如果 lustre 环 境并没有 IB 的网络,而是仅有 tcp 的网络(千兆网络,万兆网络),那么就可 以不使用这个参数了。 
–with-linux 参数指定了但前的操作系统的 kernel 信息。 –disable-server 参数指定了当前是针对lustre 的客户端进行编译。 
系统编译完成后,执行如下命令:

```
# make -j8
```

系统会继续执行,知道编译过程中没有任何错误信息后,通过

```
# make rpms
```

命令生成 lustre 客户端的 rpm 安装包。 
命令完成后,会在系统的/root/rpmbuild/RPMS/x86_64 目录下生成 lustre 客户端的 rpm 包。 然后安装所有 rpm 包即可。

在安装的过程中可能会出现如下的错误信息:

```
# rpm -ivh lustre-client-*
error: Failed dependencies:
/usr/bin/expect is needed by lustre-client-source-
2.5.29.ddnpf5-2.6.32_504.el6.x86_64_g2139632.x86_64 lustre-iokit is needed by lustre-client-tests-2.5.29.ddnpf5-2.6.32_504.el6.x86_64_g2139632.x86_64
```

提示信息为操作系统的系统关联,也就是说在安装 lustre 软件包的时候 需要依赖 expect 软件包才能继续进行安装。 手动安装 expect。

```
# yum install expect sg3_utils
```

这里我把sg3_utils也安装了，不然后面还会提示缺少这个包。

再次执行 lustre 的软件包安装。

```
#rpm -ivh lustre-*  
```

### Lnet 设置

安装完相应客户端软件之后，配置下lustre.conf，配置方式同server端的配置类似，这里不做过多说明，注意修改网卡设备名称即可。配置完Lnet之后，执行lustre模块加载

```
modprobe lustre
```

加载成功后，查看 lnet 信息

```
# lctl list_nids
11.11.11.161@o2ib
```

查看与 mgs 之间的通讯

```
# lctl ping 11.11.11.34@o2ib
12345-0@lo 12345-11.11.11.34@o2ib
```

通过上面的输出可以确认该节点的 lnet 与 mgs 之间的通讯正常。

### 客户端挂载

lustre 客户端的安装和配置完成之后,就可以对文件系统进行挂载了。 挂载命令如下:

```
mount -t lustre 11.11.11.34@o2ib:11.11.11.35@o2ib:/lustre /lustre/
```

看是很长的一条命令,也非常不容易记忆。但是等知道这条命令的具体意义的话,就会非常容易理解和记忆这条命令了。

-t lustre 参数 指定了挂载的文件系统类型为 lustre 文件系统。 
11.11.11.34@o2ib 参数指定了互为主备的 mgs1 的 lnet 地址 11.11.11.35@o2ib 参数指定了互为主备的 mgs2 的 lnet 地址,两个 mgs 
的 lnet 地址中间用:隔开

:/lustre 参数指定了在文件系统创建的时候指定的文件系统的名称。

/lustre 参数指定了,操作系统的挂载路径。

## 总结

以上为lustre部署过程中所有步骤，性能测试后期再进行补充，因为初始环境不同，部署过程中可能会遇到各种各样的问题，根据错误提示，google搜索应该都能解决。

总体来看，lustre的部署过程相对来说还是比较复杂的，这里server段的安装直接固化到操作系统中了，省了很多事情。因为lustre的基于内核态的文件系统，相对系统版本及各种依赖软件版本要求较高，安装过程中也容易出错。且lustre本身无数据冗余机制，这里通过软件+硬件的方式来保障lustre文件系统的稳定运行。但一旦出现问题，可能会造成所有数据故障期间无法访问，影响范围较广，所以对运维人员的技能要求也较高。
