



```bash

----------------------------------------------
1.配置网络
  ora01:
  # netadm enable -p ncp DefaultFixed
# ipadm create-ip net0
# ipadm create-ip net1
# ipadm create-ip net2
# ipadm create-ip net3
# ipadm create-ip net4
# ipadm create-ip net5
# ipadm set-ifprop -p standby=on -m ip net4
# ipadm set-ifprop -p standby=on -m ip net5
# ipadm create-ipmp -i net2 -i net4 ipmp0
# ipadm create-ipmp -i net3 -i net5 ipmp1
# ipadm create-addr -T static -a local=210.10.1.18/24 ipmp0
# ipadm create-addr -T static -a local=10.10.10.1/24 ipmp1
# route –p add default 210.10.1.250
	ora02网络配置：
# netadm enable -p ncp DefaultFixed
# ipadm create-ip net0
# ipadm create-ip net1
# ipadm create-ip net2
# ipadm create-ip net3
# ipadm create-ip net4
# ipadm create-ip net5
# ipadm set-ifprop -p standby=on -m ip net4
# ipadm set-ifprop -p standby=on -m ip net5
# ipadm create-ipmp -i net2 -i net4 ipmp0
# ipadm create-ipmp -i net3 -i net5 ipmp1
# ipadm create-addr -T static -a local=210.10.1.18/24 ipmp0
# ipadm create-addr -T static -a local=10.10.10.1/24 ipmp1
# route –p add default 210.10.1.250



2.修改host
root@ora01:~# cat /etc/hosts
#
# Copyright 2009 Sun Microsystems, Inc.  All rights reserved.
# Use is subject to license terms.
#
# Internet host table
#
#::1 ora01 localhost 
127.0.0.1  localhost loghost 
210.10.1.18     ora01   loghost
210.10.1.19     ora02   
210.10.1.20     ora01-vip
210.10.1.21     ora02-vip
10.10.10.1      ora01-priv
10.10.10.2      ora02-priv
210.10.1.40     rac-scanip
ora02节点：
root@ora02:~# cat /etc/hosts
#
# Copyright 2009 Sun Microsystems, Inc.  All rights reserved.
# Use is subject to license terms.
#
# Internet host table
#
#::1 ora01 localhost 
127.0.0.1  localhost loghost 
210.10.1.18     ora01   
210.10.1.19     ora02   loghost
210.10.1.20     ora01-vip
210.10.1.21     ora02-vip
10.10.10.1      ora01-priv
10.10.10.2      ora02-priv
210.10.1.40     rac-scanip



3.

c)	配置nsloopup进行scanip解析
如果安装时没选择GNS，在安装前需要对nslookup进行配置，否则会有如下报错：
INS-20802
INFO: Checking name resolution setup for "rac-scanip"...
INFO: ERROR:
INFO: PRVG-1101 : SCAN name "rac-scanip" failed to resolve
INFO: ERROR:
INFO: PRVF-4657 : Name resolution setup check for "rac-scanip" (IP address: 210.10.1.40) failed
INFO: ERROR:
INFO: PRVF-4664 : Found inconsistent name resolution entries for SCAN name "rac-scanip"
INFO: Verification of SCAN VIP and Listener setup failed
如果没有配置DNS但是为了能够安装11gRAC，需要手工配置使能解析, 在11gR2中，为了简化该项配置工作，引入了SCAN（Single Client Access Name）的特性，该特性的好处在于，在数据库与客户端之间，添加了一层虚拟的服务层，就是所谓的scan ip以及scan ip listener，在客户端仅需要配置scan ip的tns信息，通过scan ip listener，连接后台集群数据库。这样，不论集群数据库是否有添加或者删除节点的操作，均不会对client产生影响。官方推荐生产系统的scan ip有3个，且需要做dns做解析。但目前环境一个scan ip也能满足系统运行的需求且不需要配置专门的DNS服务器做解析，只用在/etc/hosts文件中加入相关解析条目即可。由于在Grid的安装过程中无法成功解析rac-scan的地址，所以需要手动指定解析内容。
在ora01节点上配置nslookup解析：
# mv /usr/sbin/nslookup /usr/sbin/nslookup.original
# vi /usr/sbin/nslookup
在nslookup脚本中添加一下内容：
#!/bin/bash
HOSTNAME=${1}
if [[ $HOSTNAME = "rac-scanip" ]]; then
    echo "Server:         210.10.1.20"
    echo "Address:        210.10.1.20 #53"
    echo "Non-authoritative answer:"
    echo "Name:   scanip"
    echo "Address: 210.10.1.40 "
else
   /usr/sbin/nslookup.original $HOSTNAME
fi
修改nslookup脚本权限：
# chmod 755 /usr/sbin/nslookup
# nslookup rac-scanip
在ora02节点上也需要配置nslookup解析：
# mv /usr/sbin/nslookup /usr/sbin/nslookup.original
# vi /usr/sbin/nslookup
在nslookup脚本中添加一下内容：
#!/bin/bash
HOSTNAME=${1}
if [[ $HOSTNAME = "scanip" ]]; then
    echo "Server:         210.10.1.21"
    echo "Address:        210.10.1.21 #53"
    echo "Non-authoritative answer:"
    echo "Name:   scanip"
    echo "Address: 210.10.1.40 "
else
   /usr/sbin/nslookup.original $HOSTNAME
fi
修改nslookup脚本权限：
# chmod 755 /usr/sbin/nslookup
# nslookup rac-scanip
解释：这里的210.10.1.20  ip是ora01上面的vip地址，而210.10.1.40 这个ip就是在/etc/hosts里面添加的rac-scanip地址，必须是没有使用的ip，意思类似于rac中的vip地址。只是11.2中把这个vip也再绑定了一个ip，其实也是一个vip地址。rac-scanip是host文件里面对应的域名，安装rac时候提示要填写，安装时候请注意！！！

-----------------------------
2.1.2	创建用户组和安装目录
在2个节点上创建集群软件安装用户grid和数据库软件安装用户oracle：
# groupadd -g 1000 oinstall
# groupadd -g 1020 asmadmin
# groupadd -g 1021 asmdba
# groupadd -g 1022 asmoper
# groupadd -g 1031 dba
# groupadd -g 1032 oper
# useradd -u 1100 -g oinstall -G dba,asmoper,asmadmin,asmdba -d /export/home/grid -m grid
# useradd -u 1101 -g oinstall -G oper,dba,asmdba -d /export/home/oracle -m oracle
# passwd grid
# passwd oracle
在2个节点上创建安装目录：
# mkdir -p /u01/app/grid
# mkdir -p /u01/app/11.2.0/grid
# chown -R grid:oinstall /u01
# mkdir -p /u01/app/oracle
# chown oracle:oinstall /u01/app/oracle
# chmod -R 775 /u01

-------------------------------------------

配置grid用户环境变量：
登录主机ora01的grid用户配置环境变量:
# su - grid
$ vi /export/home/grid/.profile
在.profile文件末尾加上以下内容：
ORACLE_SID=+ASM1; export ORACLE_SID
ORACLE_BASE=/u01/app/grid; export ORACLE_BASE
ORACLE_HOME=/u01/app/11.2.0/grid; export ORACLE_HOME
JAVA_HOME=$ORACLE_HOME/jdk; export JAVA_HOME
ORACLE_PATH=/u01/app/oracle/common/oracle/sql; export ORACLE_PATH
ORACLE_TERM=xterm; export ORACLE_TERM
NLS_DATE_FORMAT="DD-MON-YYYY HH24:MI:SS"; export NLS_DATE_FORMAT
TNS_ADMIN=$ORACLE_HOME/network/admin; export TNS_ADMIN
ORA_NLS11=$ORACLE_HOME/nls/data; export ORA_NLS11
PATH=.:${JAVA_HOME}/bin:${PATH}:$HOME/bin:$ORACLE_HOME/bin
PATH=${PATH}:/usr/bin:/bin:/usr/bin/X11:/usr/local/bin
PATH=${PATH}:/u01/app/common/oracle/bin
export PATH
LD_LIBRARY_PATH=$ORACLE_HOME/lib
LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:$ORACLE_HOME/oracm/lib
LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/lib:/usr/lib:/usr/local/lib
export LD_LIBRARY_PATH
CLASSPATH=$ORACLE_HOME/JRE
CLASSPATH=${CLASSPATH}:$ORACLE_HOME/jlib
CLASSPATH=${CLASSPATH}:$ORACLE_HOME/rdbms/jlib
CLASSPATH=${CLASSPATH}:$ORACLE_HOME/network/jlib
export CLASSPATH
THREADS_FLAG=native; export THREADS_FLAG
export TEMP=/tmp
export TMPDIR=/tmp
umask 022
ulimit -t unlimited
ulimit -f unlimited
ulimit -d unlimited
ulimit -s unlimited
ulimit -v unlimited
if [ -t 0 ]; then
stty intr ^C
fi
登录主机ora02的grid用户并配置环境变量:
# su - grid
$ vi /export/home/grid/.profile
在.profile文件末尾加上以下内容：
ORACLE_SID=+ASM2; export ORACLE_SID
ORACLE_BASE=/u01/app/grid; export ORACLE_BASE
ORACLE_HOME=/u01/app/11.2.0/grid; export ORACLE_HOME
JAVA_HOME=$ORACLE_HOME/jdk; export JAVA_HOME
ORACLE_PATH=/u01/app/oracle/common/oracle/sql; export ORACLE_PATH
ORACLE_TERM=xterm; export ORACLE_TERM
NLS_DATE_FORMAT="DD-MON-YYYY HH24:MI:SS"; export NLS_DATE_FORMAT
TNS_ADMIN=$ORACLE_HOME/network/admin; export TNS_ADMIN
ORA_NLS11=$ORACLE_HOME/nls/data; export ORA_NLS11
PATH=.:${JAVA_HOME}/bin:${PATH}:$HOME/bin:$ORACLE_HOME/bin
PATH=${PATH}:/usr/bin:/bin:/usr/bin/X11:/usr/local/bin
PATH=${PATH}:/u01/app/common/oracle/bin
export PATH
LD_LIBRARY_PATH=$ORACLE_HOME/lib
LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:$ORACLE_HOME/oracm/lib
LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/lib:/usr/lib:/usr/local/lib
export LD_LIBRARY_PATH
CLASSPATH=$ORACLE_HOME/JRE
CLASSPATH=${CLASSPATH}:$ORACLE_HOME/jlib
CLASSPATH=${CLASSPATH}:$ORACLE_HOME/rdbms/jlib
CLASSPATH=${CLASSPATH}:$ORACLE_HOME/network/jlib
export CLASSPATH
THREADS_FLAG=native; export THREADS_FLAG
export TEMP=/tmp
export TMPDIR=/tmp
umask 022
ulimit -t unlimited
ulimit -f unlimited
ulimit -d unlimited
ulimit -s unlimited
ulimit -v unlimited
if [ -t 0 ]; then
stty intr ^C
fi
登录主机ora01的oracle用户配置环境变量:
# su - oracle
$ vi /export/home/oracle/.profile
在.profile文件末尾加上以下内容：
ORACLE_SID=hisd1; export ORACLE_SID
ORACLE_UNQNAME=hisd; export ORACLE_UNQNAME
ORACLE_BASE=/u01/app/oracle; export ORACLE_BASE
ORACLE_HOME=$ORACLE_BASE/product/11.2.0/dbhome_1; export ORACLE_HOME
JAVA_HOME=$ORACLE_HOME/jdk; export JAVA_HOME
ORACLE_PATH=/u01/app/common/oracle/sql; export ORACLE_PATH
ORACLE_TERM=xterm; export ORACLE_TERM
NLS_DATE_FORMAT="DD-MON-YYYY HH24:MI:SS"; export NLS_DATE_FORMAT
TNS_ADMIN=$ORACLE_HOME/network/admin; export TNS_ADMIN
ORA_NLS11=$ORACLE_HOME/nls/data; export ORA_NLS11
PATH=.:${JAVA_HOME}/bin:${PATH}:$HOME/bin:$ORACLE_HOME/bin
PATH=${PATH}:/usr/bin:/bin:/usr/bin/X11:/usr/local/bin
PATH=${PATH}:/u01/app/common/oracle/bin
export PATH
LD_LIBRARY_PATH=$ORACLE_HOME/lib
LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:$ORACLE_HOME/oracm/lib
LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/lib:/usr/lib:/usr/local/lib
export LD_LIBRARY_PATH
CLASSPATH=$ORACLE_HOME/JRE
CLASSPATH=${CLASSPATH}:$ORACLE_HOME/jlib
CLASSPATH=${CLASSPATH}:$ORACLE_HOME/rdbms/jlib
CLASSPATH=${CLASSPATH}:$ORACLE_HOME/network/jlib
export CLASSPATH
THREADS_FLAG=native; export THREADS_FLAG
export TEMP=/tmp
export TMPDIR=/tmp
umask 022
stty erase ^H
登录主机ora02的oracle用户配置环境变量:
# su - oracle
$ vi /export/home/oracle/.profile
在.profile文件末尾加上以下内容：
ORACLE_SID=hisd2; export ORACLE_SID
ORACLE_UNQNAME=hisd; export ORACLE_UNQNAME
ORACLE_BASE=/u01/app/oracle; export ORACLE_BASE
ORACLE_HOME=$ORACLE_BASE/product/11.2.0/dbhome_1; export ORACLE_HOME
JAVA_HOME=$ORACLE_HOME/jdk; export JAVA_HOME
ORACLE_PATH=/u01/app/common/oracle/sql; export ORACLE_PATH
ORACLE_TERM=xterm; export ORACLE_TERM
NLS_DATE_FORMAT="DD-MON-YYYY HH24:MI:SS"; export NLS_DATE_FORMAT
TNS_ADMIN=$ORACLE_HOME/network/admin; export TNS_ADMIN
ORA_NLS11=$ORACLE_HOME/nls/data; export ORA_NLS11
PATH=.:${JAVA_HOME}/bin:${PATH}:$HOME/bin:$ORACLE_HOME/bin
PATH=${PATH}:/usr/bin:/bin:/usr/bin/X11:/usr/local/bin
PATH=${PATH}:/u01/app/common/oracle/bin
export PATH
LD_LIBRARY_PATH=$ORACLE_HOME/lib
LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:$ORACLE_HOME/oracm/lib
LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/lib:/usr/lib:/usr/local/lib
export LD_LIBRARY_PATH
CLASSPATH=$ORACLE_HOME/JRE
CLASSPATH=${CLASSPATH}:$ORACLE_HOME/jlib
CLASSPATH=${CLASSPATH}:$ORACLE_HOME/rdbms/jlib
CLASSPATH=${CLASSPATH}:$ORACLE_HOME/network/jlib
export CLASSPATH
THREADS_FLAG=native; export THREADS_FLAG
export TEMP=/tmp
export TMPDIR=/tmp
umask 022
stty erase ^H

-------------------------------------

2.1.4	配置Solaris内核参数

在ora01和ora02节点上配置同样的Solaris内核参数。
a)	为grid用户和oracle用户创建projects，配置共享内存参数：
# /usr/sbin/projadd -U grid -K "project.max-shm-memory=(priv,28g,deny)" user.grid
# /usr/sbin/projmod -sK "project.max-sem-nsems=(priv,512,deny)" user.grid
# /usr/sbin/projmod -sK "project.max-sem-ids=(priv,128,deny)" user.grid
# /usr/sbin/projmod -sK "project.max-shm-ids=(priv,128,deny)" user.grid
# /usr/sbin/projmod -sK "project.max-shm-memory=(priv,6g,deny)" user.grid
# /usr/sbin/projadd -U oracle -K "project.max-shm-memory=(priv,28g,deny)" user.oracle
# /usr/sbin/projmod -sK "project.max-sem-nsems=(priv,512,deny)" user.oracle
# /usr/sbin/projmod -sK "project.max-sem-ids=(priv,128,deny)" user.oracle
# /usr/sbin/projmod -sK "project.max-shm-ids=(priv,128,deny)" user.oracle
# /usr/sbin/projmod -sK "project.max-shm-memory=(priv,28g,deny)" user.oracle
# /usr/sbin/projmod -sK "process.max-file-descriptor=(priv,65536,deny)" user.oracle
# /usr/sbin/projmod -sK "process.max-file-descriptor=(priv,65536,deny)" user.grid
# /usr/sbin/prctl -n project.max-shm-memory -r -v 28G -i project system
# /usr/sbin/projmod -s -K "project.max-shm-memory=(priv,28G,deny)" system
# /usr/sbin/projmod -s -K "project.max-shm-memory=(priv,28G,deny)" default
编辑/etc/user_attr文件添加以下内容，中给root的用户加上project=system：
root::::type=normal;auths=solaris.*,solaris.grant;profiles=Web Console Management,All;lock_after_retries=no;clearance=admin_high;min_label=admin_low;project=system
b)	配置TCP和UDP内核参数
	通过使用ipadm命令配置如下：
# ipadm set-prop -p smallest_anon_port=9000 tcp
# ipadm set-prop -p largest_anon_port=65500 tcp
# ipadm set-prop -p smallest_anon_port=9000 udp
# ipadm set-prop -p largest_anon_port=65500 udp
c)	调整2个节点的swap空间大小
# zfs set volsize=20G rpool/swap
# zfs get volsize rpool/swap
NAME        PROPERTY  VALUE  SOURCE
rpool/swap  volsize   20G    local
d)	修改/etc/system文件，添加进程数软硬限制
set rlim_fd_cur = 65536
set rlim_fd_max = 65536

----------------------

2.1.5	关闭ntp服务和sendmail服务
Oracle 11g R2 中新添加了时间同步服务Cluster Time Synchronization Service(CTSS)，要想使用该功能，就必须先关闭ntp服务。
在2个节点上关闭NTP服务和sendmail服务：
# svcadm disable ntp
# svcadm disable sendmail



------------------------------

2.1.6	系统软件包检查安装
在2个节点上配置本地映像库，用于oracle安装环境所需安装包安装，上传映像库文件到节点，映像库文件可以在oracle官网下载，映像库文件为：
sol-11_1-repo-full.iso-a
sol-11_1-repo-full.iso-b
建立映像存放目录/inspur，将映像库上传到/inspur目录，完成后将2个文件合并：
# mkdir /inspur
# cat sol-11_1-repo-full.iso-a sol-11_1-repo-full.iso-b > sol-11_1-repo-full.iso
创建映像挂载目录：
# mkdir /iso
挂载映像库文件
# mount –F hsfs /inspur/ sol-11_1-repo-full.iso /iso
建立本地映像库：
#pkg set-publisher -G '*' -g  file:///iso/repo solaris
	如果安装操作系统时未安装图形界面，可通过以下命令安装图形界面：
# pkg install  solaris-desktop
	安装集群所需安装包：
# pkg install compatibility/packages/SUNWxwplt SUNWmfrun SUNWarc SUNWhea SUNWlibm

----------------------

2.1.7	建立ssh信任
	Oracle 11G RAC安装需要grid用户和oracle用户对应的2个节点都要做ssh信任关系。
1.	配置oracle用户的信任关系步骤如下：
	)	在2个节点都要执行以下命令，创建公钥和私钥
# su – oracle
$ ssh-keygen -t rsa
$ ssh-keygen -t dsa
$ cd /export/home/oracle/.ssh
$ cat *.pub >> authorized_keys
b)	将ora01上的authorized_keys拷贝到ora02节点相应目录并改名
$ scp /export/home/oracle/.ssh/authorized_keys ora02: /export/home/oracle/.ssh/keys
c)	在节点2上将keys内容合并到authorized_keys，并将此文件拷贝节点1上：
$ cat keys >> authorized_keys
$ scp authorized_keys ora01: /export/home/oracle/.ssh/
d)	在所有节点上测试验证信任关系
$ ssh ora01 date
$ ssh ora02 date
$ ssh ora01-priv date
$ ssh ora02-priv date
2.	配置grid用户的信任关系步骤与配置oracle用户信任关系一致：
	)	在2个节点都要执行以下命令，创建公钥和私钥
# su – grid
$ ssh-keygen -t rsa
$ ssh-keygen -t dsa
$ cd /export/home/grid/.ssh
$ cat *.pub >> authorized_keys
b)	将ora01上的authorized_keys拷贝到ora02节点相应目录并改名
$ scp /export/home/grid/.ssh/authorized_keys ora02: /export/home/grid/.ssh/keys
c)	在节点2上将keys内容合并到authorized_keys，并将此文件拷贝节点1上：
$ cat keys >> authorized_keys
$ scp authorized_keys ora01: /export/home/grid/.ssh/
d)	在所有节点上测试验证信任关系
$ ssh ora01 date
$ ssh ora02 date
$ ssh ora01-priv date
$ ssh ora02-priv date

------------------------------------

2.1.8	配置共享磁盘分区
存储为Inspur AS500H映射在TS850机器上为多路径，而在基于x86的Solaris 11操作系统上默认是启动了多路径功能。
1.	配置操作系统多路径功能
确认多路径是否启用：
# prtconf -vc /devices/scsi_vhci |grep dev_link.*s2
命令返回多路径信息确定已经启用了多路径功能，若未启用则使用命令启用即可。
确认多路径安装包是否安装：
# pkg info system/storage/multipath-utilities
          Name: system/storage/multipath-utilities
       Summary: Solaris Multipathing CLI
   Description: Path Administration Utility for a Solaris Multipathing device
      Category: Applications/System Utilities
         State: Installed
     Publisher: solaris
       Version: 0.5.11
 Build Release: 5.11
        Branch: 0.175.0.0.0.0.0
Packaging Date: Tue Sep 27 01:40:01 2011
          Size: 77.29 kB
          FMRI: pkg://solaris/system/storage/multipath-utilities@
0.5.11,5.11-0.175.0.0.0.0.0:20110927T014001Z
安装多路径软件包，需要配置Solaris本地映像库，以后章节会讲解配置本地映像库：
# pkg install system/storage/multipath-utilities

启动多路径设备：
# stmsboot -e
禁用多路径设备：
# stmsboot -d


2.	磁盘分区
磁盘分区只需要在一个节点做即可，这里针对一个磁盘分区进行说明，其他磁盘分区与其配置方法一致，使用format命令进行分区：
root@ora01:~# format
Searching for disks...done
AVAILABLE DISK SELECTIONS:
       0. c0t60080E50003EA0E60000050B52CBA01Ad0 <LSI-INF-01-00-0784 cyl 44555 alt 2 hd 255 sec 189>
          /scsi_vhci/disk@g60080e50003ea0e60000050b52cba01a
       1. c0t60080E50003EA0E60000050D52CBA03Cd0 <LSI-INF-01-00-0784 cyl 44555 alt 2 hd 255 sec 189>
          /scsi_vhci/disk@g60080e50003ea0e60000050d52cba03c
	2. c0t60080E50003EA0E60000050F52CBA107d0 <LSI-INF-01-00-0784 cyl 44555 alt 2 hd 255 sec 189>
          /scsi_vhci/disk@g60080e50003ea0e60000050f52cba107
       3. c0t60080E50003EA0E60000050752CB9FBCd0 <LSI-INF-01-00-0784 cyl 1021 alt 2 hd 128 sec 32>
          /scsi_vhci/disk@g60080e50003ea0e60000050752cb9fbc
       4. c0t60080E50003EA0E60000050952CB9FF9d0 <LSI-INF-01-00-0784 cyl 44556 alt 2 hd 255 sec 189>
          /scsi_vhci/disk@g60080e50003ea0e60000050952cb9ff9
       5. c0t60080E50003EA0E60000053152D59D24d0 <LSI-INF-01-00-0784 cyl 1022 alt 2 hd 128 sec 32>
          /scsi_vhci/disk@g60080e50003ea0e60000053152d59d24
       6. c0t60080E50003EA0E60000054752D6259Ad0 <LSI-INF-01-00-0784 cyl 44556 alt 2 hd 255 sec 189>
          /scsi_vhci/disk@g60080e50003ea0e60000054752d6259a
       7. c0t60080E50003EA3740000051A52CB9FF5d0 <LSI-INF-01-00-0784 cyl 44556 alt 2 hd 255 sec 189>
          /scsi_vhci/disk@g60080e50003ea3740000051a52cb9ff5
       8. c0t60080E50003EA3740000051C52CBA015d0 <LSI-INF-01-00-0784 cyl 44556 alt 2 hd 255 sec 189>
          /scsi_vhci/disk@g60080e50003ea3740000051c52cba015
       9. c0t60080E50003EA3740000051652CB9F99d0 <LSI-INF-01-00-0784 cyl 1022 alt 2 hd 128 sec 32>
          /scsi_vhci/disk@g60080e50003ea3740000051652cb9f99
      10. c0t60080E50003EA3740000051852CB9FB2d0 <LSI-INF-01-00-0784 cyl 1022 alt 2 hd 128 sec 32>
          /scsi_vhci/disk@g60080e50003ea3740000051852cb9fb2
      11. c0t60080E50003EA3740000055D52D62553d0 <LSI-INF-01-00-0784 cyl 44556 alt 2 hd 255 sec 189>
          /scsi_vhci/disk@g60080e50003ea3740000055d52d62553
      12. c0t60080E50003EA3740000054452D59D06d0 <LSI-INF-01-00-0784 cyl 1022 alt 2 hd 128 sec 32>
          /scsi_vhci/disk@g60080e50003ea3740000054452d59d06
      13. c0t60080E50003EA3740000051E52CBA0E3d0 <LSI-INF-01-00-0784 cyl 44556 alt 2 hd 255 sec 189>
          /scsi_vhci/disk@g60080e50003ea3740000051e52cba0e3
      14. c0t60080E50003EA3740000055F52D62597d0 <LSI-INF-01-00-0784 cyl 65268 alt 2 hd 255 sec 63>
          /scsi_vhci/disk@g60080e50003ea3740000055f52d62597
      15. c7t0d0 <LSI-MR9271-8i-3.19-278.88GB>
          /pci@0,0/pci8086,3410@9/pci1000,9271@0/sd@0,0
Specify disk (enter its number): 1     
selecting c0t60080E50003EA0E60000050D52CBA03Cd0
[disk formatted]

FORMAT MENU:
        disk       - select a disk
        type       - select (define) a disk type
        partition  - select (define) a partition table
        current    - describe the current disk
        format     - format and analyze the disk
        fdisk      - run the fdisk program
        repair     - repair a defective sector
        label      - write label to the disk
        analyze    - surface analysis
        defect     - defect list management
        backup     - search for backup labels
        verify     - read and display labels
        save       - save new disk/partition definitions
        inquiry    - show disk ID
        volname    - set 8-character volume name
        !<cmd>     - execute <cmd>, then return
        quit
format> p
PARTITION MENU:
        0      - change `0' partition
        1      - change `1' partition
        2      - change `2' partition
        3      - change `3' partition
        4      - change `4' partition
        5      - change `5' partition
        6      - change `6' partition
        7      - change `7' partition
        select - select a predefined table
        modify - modify a predefined partition table
        name   - name the current table
        print  - display the current table
        label  - write partition map and label to the disk
        !<cmd> - execute <cmd>, then return
        quit
partition> 6
Part      Tag    Flag     Cylinders         Size            Blocks
  6 unassigned    wm       0                0         (0/0/0)              0

Enter partition id tag[unassigned]: usr
Enter partition permission flags[wm]: 
Enter new starting cyl[1]: 3
Enter partition size[0b, 0c, 3e, 0.00mb, 0.00gb]: $

partition> p
Current partition table (unnamed):
Total disk cylinders available: 44555 + 2 (reserved cylinders)

Part      Tag    Flag     Cylinders         Size            Blocks
  0 unassigned    wm       0                0         (0/0/0)              0
  1 unassigned    wm       0                0         (0/0/0)              0
  2     backup    wu       0 - 44554     1023.93GB    (44555/0/0) 2147328225
  3 unassigned    wm       0                0         (0/0/0)              0
  4 unassigned    wm       0                0         (0/0/0)              0
  5 unassigned    wm       0                0         (0/0/0)              0
  6        usr    wm       3 - 44554     1023.86GB    (44552/0/0) 2147183640
  7 unassigned    wm       0                0         (0/0/0)              0
  8       boot    wu       0 -     0       23.53MB    (1/0/0)          48195
  9 unassigned    wm       0                0         (0/0/0)              0

partition> label
Ready to label disk, continue? yes
partition> q
磁盘分区结果如下：
/dev/rdsk/c0t60080E50003EA0E60000050B52CBA01Ad0s6 
/dev/rdsk/c0t60080E50003EA0E60000050D52CBA03Cd0s6 /dev/rdsk/c0t60080E50003EA0E60000050F52CBA107d0s6 /dev/rdsk/c0t60080E50003EA0E60000050752CB9FBCd0s6 
/dev/rdsk/c0t60080E50003EA0E60000050952CB9FF9d0s6 
/dev/rdsk/c0t60080E50003EA0E60000053152D59D24d0s6 
/dev/rdsk/c0t60080E50003EA0E60000054752D6259Ad0s6 
/dev/rdsk/c0t60080E50003EA3740000051A52CB9FF5d0s6 
/dev/rdsk/c0t60080E50003EA3740000051C52CBA015d0s6 
/dev/rdsk/c0t60080E50003EA3740000051652CB9F99d0s6 
/dev/rdsk/c0t60080E50003EA3740000051852CB9FB2d0s6 
/dev/rdsk/c0t60080E50003EA3740000055D52D62553d0s6 
/dev/rdsk/c0t60080E50003EA3740000054452D59D06d0s6 
/dev/rdsk/c0t60080E50003EA3740000051E52CBA0E3d0s6

3.	建立共享磁盘分区软连接
建立软连接的目的是把本地磁盘名称映射为相同的名称，另外，映射之后的设备名称比较直观，便与管理。创建磁盘软链接目录并建立软链接：
# mkdir /sharedisk
# chmod 775 /sharedisk
# ln -s /dev/rdsk/c0t60080E50003EA0E60000050B52CBA01Ad0s6 /sharedisk/asm1
# ln -s /dev/rdsk/c0t60080E50003EA0E60000050D52CBA03Cd0s6 /sharedisk/asm2
# ln -s /dev/rdsk/c0t60080E50003EA0E60000050F52CBA107d0s6 /sharedisk/asm3
# ln -s /dev/rdsk/c0t60080E50003EA0E60000050752CB9FBCd0s6 /sharedisk/crs1
# ln -s /dev/rdsk/c0t60080E50003EA0E60000050952CB9FF9d0s6 /sharedisk/asm4
# ln -s /dev/rdsk/c0t60080E50003EA0E60000053152D59D24d0s6 /sharedisk/crs2
# ln -s /dev/rdsk/c0t60080E50003EA0E60000054752D6259Ad0s6 /sharedisk/asm5
# ln -s /dev/rdsk/c0t60080E50003EA3740000051A52CB9FF5d0s6 /sharedisk/asm6
# ln -s /dev/rdsk/c0t60080E50003EA3740000051C52CBA015d0s6 /sharedisk/asm7
# ln -s /dev/rdsk/c0t60080E50003EA3740000051652CB9F99d0s6 /sharedisk/crs3
# ln -s /dev/rdsk/c0t60080E50003EA3740000051852CB9FB2d0s6 /sharedisk/crs4
# ln -s /dev/rdsk/c0t60080E50003EA3740000055D52D62553d0s6 /sharedisk/fra1
# ln -s /dev/rdsk/c0t60080E50003EA3740000054452D59D06d0s6 /sharedisk/crs5
# ln -s /dev/rdsk/c0t60080E50003EA3740000051E52CBA0E3d0s6 /sharedisk/fra2
4.	修改磁盘用户组、所属组以及权限
# chmod -R 660 /dev/rdsk/c0t60080E50003EA0E60000050B52CBA01Ad0s6 
# chmod -R 660 /dev/rdsk/c0t60080E50003EA0E60000050D52CBA03Cd0s6 
# chmod -R 660 /dev/rdsk/c0t60080E50003EA0E60000050F52CBA107d0s6 
# chmod -R 660 /dev/rdsk/c0t60080E50003EA0E60000050752CB9FBCd0s6 
# chmod -R 660 /dev/rdsk/c0t60080E50003EA0E60000050952CB9FF9d0s6 
# chmod -R 660 /dev/rdsk/c0t60080E50003EA0E60000053152D59D24d0s6 
# chmod -R 660 /dev/rdsk/c0t60080E50003EA0E60000054752D6259Ad0s6 
# chmod -R 660 /dev/rdsk/c0t60080E50003EA3740000051A52CB9FF5d0s6 
# chmod -R 660 /dev/rdsk/c0t60080E50003EA3740000051C52CBA015d0s6 
# chmod -R 660 /dev/rdsk/c0t60080E50003EA3740000051652CB9F99d0s6 
# chmod -R 660 /dev/rdsk/c0t60080E50003EA3740000051852CB9FB2d0s6 
# chmod -R 660 /dev/rdsk/c0t60080E50003EA3740000055D52D62553d0s6 
# chmod -R 660 /dev/rdsk/c0t60080E50003EA3740000054452D59D06d0s6 
# chmod -R 660 /dev/rdsk/c0t60080E50003EA3740000051E52CBA0E3d0s6
# chown -R grid:asmadmin /dev/rdsk/c0t60080E50003EA0E60000050B52CBA01Ad0s6
# chown -R grid:asmadmin /dev/rdsk/c0t60080E50003EA0E60000050D52CBA03Cd0s6
# chown -R grid:asmadmin /dev/rdsk/c0t60080E50003EA0E60000050F52CBA107d0s6
# chown -R grid:asmadmin /dev/rdsk/c0t60080E50003EA0E60000050752CB9FBCd0s6
# chown -R grid:asmadmin /dev/rdsk/c0t60080E50003EA0E60000050952CB9FF9d0s6
# chown -R grid:asmadmin /dev/rdsk/c0t60080E50003EA0E60000053152D59D24d0s6
# chown -R grid:asmadmin /dev/rdsk/c0t60080E50003EA0E60000054752D6259Ad0s6
# chown -R grid:asmadmin /dev/rdsk/c0t60080E50003EA3740000051A52CB9FF5d0s6
# chown -R grid:asmadmin /dev/rdsk/c0t60080E50003EA3740000051C52CBA015d0s6
# chown -R grid:asmadmin /dev/rdsk/c0t60080E50003EA3740000051652CB9F99d0s6
# chown -R grid:asmadmin /dev/rdsk/c0t60080E50003EA3740000051852CB9FB2d0s6
# chown -R grid:asmadmin /dev/rdsk/c0t60080E50003EA3740000055D52D62553d0s6
# chown -R grid:asmadmin /dev/rdsk/c0t60080E50003EA3740000054452D59D06d0s6
# chown -R grid:asmadmin /dev/rdsk/c0t60080E50003EA3740000051E52CBA0E3d0s6	

# chmod -R 660 /sharedisk/*
# chown -R grid:asmadmin /sharedisk/*

-----------------------------

2.1.9	集群软件安装前检查
重启2个节点操作系统后进行集群软件安装前检查工作，上传安装包到/inspur目录，解压安装包：
# cd /inspur
# unzip p10404530_112030_Solaris86-64_1of6.zip
# unzip p10404530_112030_Solaris86-64_1of6.zip
# unzip p10404530_112030_Solaris86-64_1of6.zip
进入解压出来的grid安装包，执行命令检查安装环境配置情况：
# su – grid
$ cd /inspur/grid
$ ./runcluvfy.sh stage -pre crsinst -n ora01,ora02 -fixup –verbose


。。。。。。

-------------------------

2.2	安装集群软件
	集群软件安装只需要在一个节点使用grid用户安装即可，登录grid用户进入集群安装包目录执行：
$ cd /inspur/grid
$ ./runInstaller



在安装的最后，会弹出执行脚本对话框要执行配置脚本，一定要按提示的顺序操作
以root用户执行脚本： 
a)	在RAC节点ora01上执行orainstRoot.sh： 
# /u01/app/oraInventory/orainstRoot.sh 

Changing permissions of /u01/app/oraInventory.
Adding read,write permissions for group.

Removing read,write,execute permissions for world.
Changing groupname of /u01/app/oraInventory to oinstall.
The execution of the script is complete.
b)	在RAC节点ora02上执行orainstRoot.sh： 
# /u01/app/oraInventory/orainstRoot.sh 



c)	在RAC节点ora01上执行root.sh： 
# /u01/app/11.2.0/grid/root.sh 

Performing root user operation for Oracle 11g 

The following environment variables are set as:
    ORACLE_OWNER= grid
    ORACLE_HOME=  /u01/app/11.2.0/grid

Enter the full pathname of the local bin directory: [/usr/local/bin]: 
Creating /usr/local/bin directory...
   Copying dbhome to /usr/local/bin ...
   Copying oraenv to /usr/local/bin ...
   Copying coraenv to /usr/local/bin ...


Creating /var/opt/oracle/oratab file...
Entries will be added to the /var/opt/oracle/oratab file as needed by
Database Configuration Assistant when a database is created
Finished running generic part of root script.
Now product-specific root actions will be performed.
Using configuration parameter file: /u01/app/11.2.0/grid/crs/install/crsconfig_params
Creating trace directory
User ignored Prerequisites during installation
OLR initialization - successful
  root wallet
  root wallet cert
  root cert export
  peer wallet
  profile reader wallet
  pa wallet
  peer wallet keys
  pa wallet keys
  peer cert request
  pa cert request
  peer cert
  pa cert
  peer root cert TP
  profile reader root cert TP
  pa root cert TP
  peer pa cert TP
  pa peer cert TP
  profile reader pa cert TP
  profile reader peer cert TP
  peer user cert
  pa user cert
Adding Clusterware entries to inittab
CRS-2672: Attempting to start 'ora.mdnsd' on 'ora01'
CRS-2676: Start of 'ora.mdnsd' on 'ora01' succeeded
CRS-2672: Attempting to start 'ora.gpnpd' on 'ora01'
CRS-2676: Start of 'ora.gpnpd' on 'ora01' succeeded
CRS-2672: Attempting to start 'ora.cssdmonitor' on 'ora01'
CRS-2672: Attempting to start 'ora.gipcd' on 'ora01'
CRS-2676: Start of 'ora.cssdmonitor' on 'ora01' succeeded
CRS-2676: Start of 'ora.gipcd' on 'ora01' succeeded
CRS-2672: Attempting to start 'ora.cssd' on 'ora01'
CRS-2672: Attempting to start 'ora.diskmon' on 'ora01'
CRS-2676: Start of 'ora.diskmon' on 'ora01' succeeded
CRS-2676: Start of 'ora.cssd' on 'ora01' succeeded

ASM created and started successfully.

Disk Group CRS created successfully.

clscfg: -install mode specified
Successfully accumulated necessary OCR keys.
Creating OCR keys for user 'root', privgrp 'root'..
Operation successful.
CRS-4256: Updating the profile
Successful addition of voting disk 0e12cbd251d34f75bfd7dfc27b639d42.
Successful addition of voting disk 0da64751d2944f92bff9796e99d56bab.
Successful addition of voting disk 85e7ab70f9794f6ebf733ae56a99d475.
Successfully replaced voting disk group with +CRS.
CRS-4256: Updating the profile
CRS-4266: Voting file(s) successfully replaced
##  STATE    File Universal Id                File Name Disk group
--  -----    -----------------                --------- ---------
 1. ONLINE   0e12cbd251d34f75bfd7dfc27b639d42 (/sharedisk/crs1) [CRS]
 2. ONLINE   0da64751d2944f92bff9796e99d56bab (/sharedisk/crs2) [CRS]
 3. ONLINE   85e7ab70f9794f6ebf733ae56a99d475 (/sharedisk/crs3) [CRS]
Located 3 voting disk(s).
CRS-2672: Attempting to start 'ora.asm' on 'ora01'
CRS-2676: Start of 'ora.asm' on 'ora01' succeeded
CRS-2672: Attempting to start 'ora.CRS.dg' on 'ora01'
CRS-2676: Start of 'ora.CRS.dg' on 'ora01' succeeded
Configure Oracle Grid Infrastructure for a Cluster ... succeeded


d)	RAC节点ora02： 
# /u01/app/11.2.0/grid/root.sh 

。。。。。



----------------------


2.2.16	集群软件校验
通过命令检查集群状态信息：

grid@ora01:~$ crsctl check cluster -all



grid@ora01:~$ crs_stat -t -v

-----------------------
2.2.17	创建ASM磁盘组
创建2个ASM磁盘组，DATA磁盘组用于存放数据文件，FRA磁盘组用于系统的闪回区，磁盘组创建需要使用grid用户，具体步骤如下：
	登录到grid用户，执行asmca命令：


------------------------------
2.3	安装数据库软件

登录oracle用户，进入到database介质目录，创建数据库软件，只安装数据库软件，不进行建库。
$ cd /inspur/database
$ ./runInstaller



..............

根据提示信息，使用root用户分别在2个节点上执行脚本：
# /u01/app/oracle/product/11.2.0/dbhome_1/root.sh


完成数据库软件安装



----------------------------

2.4	创建数据库
	登录到oracle用户，使用dbca命令创建数据库：


注意点：将字符集调整为ZHS16GBK

调整Redo Log Groups，创建或者修改redo log组和大小

----------------------------------------
集群数据库验证维护
3.1	集群数据库验证维护
A.	检查集群服务资源状态
grid@ora01:~$ crs_stat -t -v
Name           Type           R/RA   F/FT   Target    State     Host        
----------------------------------------------------------------------
ora.CRS.dg     ora....up.type 0/5    0/     ONLINE    ONLINE    ora01       
ora.DATA.dg    ora....up.type 0/5    0/     ONLINE    ONLINE    ora01       
ora.FRA.dg     ora....up.type 0/5    0/     ONLINE    ONLINE    ora01       
ora....ER.lsnr ora....er.type 0/5    0/     ONLINE    ONLINE    ora01       
ora....N1.lsnr ora....er.type 0/5    0/0    ONLINE    ONLINE    ora01       
ora.asm        ora.asm.type   0/5    0/     ONLINE    ONLINE    ora01       
ora.cvu        ora.cvu.type   0/5    0/0    ONLINE    ONLINE    ora01       
ora.gsd        ora.gsd.type   0/5    0/     OFFLINE   OFFLINE               
ora.hisd.db    ora....se.type 0/2    0/1    ONLINE    ONLINE    ora01       
ora....network ora....rk.type 0/5    0/     ONLINE    ONLINE    ora01       
ora.oc4j       ora.oc4j.type  0/1    0/2    OFFLINE   OFFLINE               
ora.ons        ora.ons.type   0/3    0/     ONLINE    ONLINE    ora01       
ora....SM1.asm application    0/5    0/0    ONLINE    ONLINE    ora01       
ora....01.lsnr application    0/5    0/0    ONLINE    ONLINE    ora01       
ora.ora01.gsd  application    0/5    0/0    OFFLINE   OFFLINE               
ora.ora01.ons  application    0/3    0/0    ONLINE    ONLINE    ora01       
ora.ora01.vip  ora....t1.type 0/0    0/0    ONLINE    ONLINE    ora01       
ora....SM2.asm application    0/5    0/0    ONLINE    ONLINE    ora02       
ora....02.lsnr application    0/5    0/0    ONLINE    ONLINE    ora02       
ora.ora02.gsd  application    0/5    0/0    OFFLINE   OFFLINE               
ora.ora02.ons  application    0/3    0/0    ONLINE    ONLINE    ora02       
ora.ora02.vip  ora....t1.type 0/0    0/0    ONLINE    ONLINE    ora02       
ora.scan1.vip  ora....ip.type 0/0    0/0    ONLINE    ONLINE    ora01            
B.	检查集群状态
grid@ora01:~$ crsctl check cluster -all
**************************************************************
ora01:
CRS-4537: Cluster Ready Services is online
CRS-4529: Cluster Synchronization Services is online
CRS-4533: Event Manager is online
**************************************************************
ora02:
CRS-4537: Cluster Ready Services is online
CRS-4529: Cluster Synchronization Services is online
CRS-4533: Event Manager is online
**************************************************************
C.	检查所有实例状态
grid@ora01:~$ srvctl status database -d hisd
Instance hisd1 is running on node ora01
Instance hisd2 is running on node ora02
D.	检查节点应用程序状态
grid@ora01:~$ srvctl status nodeapps
VIP ora01-vip is enabled
VIP ora01-vip is running on node: ora01
VIP ora02-vip is enabled
VIP ora02-vip is running on node: ora02
Network is enabled
Network is running on node: ora01
Network is running on node: ora02
GSD is disabled
GSD is not running on node: ora01
GSD is not running on node: ora02
ONS is enabled
ONS daemon is running on node: ora01
ONS daemon is running on node: ora02
E.	列出所有数据库配置
grid@ora01:~$ srvctl config database
hisd

grid@ora01:~$ srvctl config database -d hisd -a
Database unique name: hisd
Database name: hisd
Oracle home: /u01/app/oracle/product/11.2.0/dbhome_1
Oracle user: oracle
Spfile: +DATA/hisd/spfilehisd.ora
Domain: 
Start options: open
Stop options: immediate
Database role: PRIMARY
Management policy: AUTOMATIC
Server pools: hisd
Database instances: hisd1,hisd2
Disk Groups: DATA,FRA
Mount point paths: 
Services: 
Type: RAC
Database is enabled
Database is administrator managed
F.	查询ASM状态与配置
grid@ora01:~$ srvctl status asm
ASM is running on ora01,ora02

grid@ora01:~$ srvctl config asm -a
ASM home: /u01/app/11.2.0/grid
ASM listener: LISTENER
ASM is enabled.
G.	TNS监听器状态以及配置
grid@ora01:~$ srvctl status listener
Listener LISTENER is enabled
Listener LISTENER is running on node(s): ora01,ora02

grid@ora01:~$ srvctl config listener -a
Name: LISTENER
Network: 1, Owner: grid
Home: <CRS home>
  /u01/app/11.2.0/grid on node(s) ora02,ora01
End points: TCP:1521
H.	SCAN状态以及配置
grid@ora01:~$ srvctl status scan
SCAN VIP scan1 is enabled
SCAN VIP scan1 is running on node ora01

grid@ora01:~$ srvctl config scan
SCAN name: rac-scanip, Network: 1/210.10.1.0/255.255.255.0/ipmp0
SCAN VIP name: scan1, IP: /rac-scanip/210.10.1.40
I.	VIP各个节点的状态以及配置
grid@ora01:~$ srvctl status vip -n ora01
VIP ora01-vip is enabled
VIP ora01-vip is running on node: ora01

grid@ora01:~$ srvctl status vip -n ora02
VIP ora02-vip is enabled
VIP ora02-vip is running on node: ora02

grid@ora01:~$ srvctl config vip -n ora01
VIP exists: /ora01-vip/210.10.1.20/210.10.1.0/255.255.255.0/ipmp0, hosting node ora01

grid@ora01:~$ srvctl config vip -n ora02
VIP exists: /ora02-vip/210.10.1.21/210.10.1.0/255.255.255.0/ipmp0, hosting node ora02
J.	节点应用程序配置 —（VIP、GSD、ONS、监听器）
grid@ora01:~$ srvctl config nodeapps -a -g -s -l
Warning:-l option has been deprecated and will be ignored.
Network exists: 1/210.10.1.0/255.255.255.0/ipmp0, type static
VIP exists: /ora01-vip/210.10.1.20/210.10.1.0/255.255.255.0/ipmp0, hosting node ora01
VIP exists: /ora02-vip/210.10.1.21/210.10.1.0/255.255.255.0/ipmp0, hosting node ora02
GSD exists
ONS exists: Local port 6100, remote port 6200, EM port 2016
Name: LISTENER
Network: 1, Owner: grid
Home: <CRS home>
  /u01/app/11.2.0/grid on node(s) ora02,ora01
End points: TCP:1521
K.	验证所有集群节点间的时钟同步
grid@ora01:~$ cluvfy comp clocksync -verbose
Verifying Clock Synchronization across the cluster nodes 

Checking if Clusterware is installed on all nodes...
Check of Clusterware install passed

Checking if CTSS Resource is running on all nodes...
Check: CTSS Resource running on all nodes
  Node Name                             Status                  
------------------------------------  ------------------------
  ora01                                 passed                  
Result: CTSS resource check passed


Querying CTSS for time offset on all nodes...
Result: Query of CTSS for time offset passed

Check CTSS state started...
Check: CTSS state
  Node Name                             State                   
------------------------------------  ------------------------
  ora01                                 Active                  
CTSS is in Active state. Proceeding with check of clock time offsets on all nodes...
Reference Time Offset Limit: 1000.0 msecs
Check: Reference Time Offset
  Node Name     Time Offset               Status                  
------------  ------------------------  ------------------------
  ora01         0.0                       passed                  

Time offset is within the specified limits on the following set of nodes: 
"[ora01]" 
Result: Check of clock time offsets passed


Oracle Cluster Time Synchronization Services check passed

Verification of Clock Synchronization across the cluster nodes was successful.
L.	数据库状态验证
oracle@ora01:~$ sqlplus / as sysdba

SQL*Plus: Release 11.2.0.3.0 Production on Mon Jan 20 10:21:58 2014

Copyright (c) 1982, 2011, Oracle.  All rights reserved.


Connected to:
Oracle Database 11g Enterprise Edition Release 11.2.0.3.0 - 64bit Production
With the Partitioning, Real Application Clusters, Automatic Storage Management, OLAP,
Data Mining and Real Application Testing options

SQL> SELECT inst_id , instance_number inst_no , instance_name inst_name , parallel , status , database_status db_status , active_state state , host_name host FROM gv$instance ORDER BY inst_id; 

INST_ID    INST_NO INST_NAME  PAR STATUS       DB_STATUS         STATE     HOST
------- ---------- ---------- --- ------------ ----------------- --------- ----------
      1          1 hisd1      YES OPEN         ACTIVE            NORMAL    ora01
      2          2 hisd2      YES OPEN         ACTIVE            NORMAL    ora02

SQL>

```