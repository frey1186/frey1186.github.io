---
layout: post
title: multipath.conf配置
date: 2017-11-04 12:00
author: felo
tags: multipath
---

绝大部分内容摘至https://zhuanlan.zhihu.com/p/26714897；

# 0.准备工作

```bash
#查看主机或者存储交换机上的WWN号，在存储上将LUN映射给需要的主机
cat /sys/class/fc_host/host*/port_name
0x2002d0431efb7f5d
0x2001d0431efb7f5d

#在系统内执行扫盘命令，没有命令先安装sg3_utils
yum install sg3_utils
rescan-scsi-bus.sh

#查看是否映射到对应的
fdisk -l
lsblk

#查看是否安装了multipath
yum install device-mapper-multipath

rpm -qa | grep device-mapper
device-mapper-libs-1.02.107-5.el7_2.2.x86_64
device-mapper-persistent-data-0.5.5-1.el7.x86_64
device-mapper-multipath-0.4.9-85.el7_2.4.x86_64
device-mapper-1.02.107-5.el7_2.2.x86_64
device-mapper-event-libs-1.02.107-5.el7_2.2.x86_64
device-mapper-event-1.02.107-5.el7_2.2.x86_64
device-mapper-multipath-libs-0.4.9-85.el7_2.4.x86_64
```

# 1.multipath.conf配置

```bash

#拷贝默认的multipath.conf到/etc目录下，也可以使用mpathconf命令创建默认模板
cp /usr/share/doc/device-mapper-multipath-0.4.9/multipath.conf /etc/multipath.conf
mpathconf --enable --with_multipathd y

#查看本地存储wwid
/lib/udev/scsi_id --whitelisted --device=/dev/sda
36141877030bcca001d9c4d52106b9d90

#查看存储参数
cat /sys/block/sdb/device/vendor 
3PARdata
cat /sys/block/sdb/device/model
VV

#添加本地盘到blacklist内,不同的存储和系统参考官方的最佳实践
vim /etc/multipath.conf

defaults {
polling_interval 10
user_friendly_names no
find_multipaths yes
}
blacklist {
wwid "<wwid_of_the_local_disk>"
}
devices {
device {
vendor "3PARdata"
product "VV"
path_grouping_policy group_by_prio
path_selector "round-robin 0"
path_checker tur
features "0"
hardware_handler "1 alua"
prio alua
failback immediate
rr_weight uniform
no_path_retry 18
rr_min_io_rq 1
detect_prio yes
# fast_io_fail_tmo 10
# dev_loss_tmo 14
}
}
```
```bash
#固定设备的别名
cat /etc/multipath/bindings 
# Multipath bindings, Version : 1.0
# NOTE: this file is automatically maintained by the multipath program.
# You should not need to edit this file in normal circumstances.
#
# Format:
# alias wwid
#
mpatha 360002ac000000000000000260001a945
mpathb 360002ac000000000000000270001a945
mpathc 360002ac000000000000000280001a945
mpathd 360002ac000000000000000290001a945
mpathe 360002ac0000000000000002a0001a945

#编辑multipath.conf，增加以下字段
vim /etc/multipath.conf

multipaths {
  multipath {
  wwid 360002ac000000000000000260001a945
  alias 3PAR8400_DEV_LUN26
  }
  multipath {
  wwid 360002ac000000000000000270001a945
  alias 3PAR8400_DEV_LUN27
  }
  multipath {
  wwid 360002ac000000000000000280001a945
  alias 3PAR8400_DEV_LUN28
  }
  multipath {
  wwid 360002ac000000000000000290001a945
  alias 3PAR8400_DEV_LUN29
  }
  multipath {
  wwid 360002ac0000000000000002a0001a945
  alias 3PAR8400_DEV_LUN30
  }
}
```
```bash
#清空已有的multipath记录
multipath -F
#打印诊断信息
multipath -v3
#启用多路径守护程序以在引导时启动
mpathconf --enable
#启动多路径服务
service multipathd start
#如果在启动 multipath 守护程序后更改多路径配置文件，请运行以下命令以使更改生效。
service multipathd reload 
#重启系统测试
init 6
#查看多路径当前状态
multipath -ll

#Enable extended logging on the qla2xxx driver
chmod u+x /sys/module/qla2xxx/parameters/ql2xextended_error_logging
echo "1" > /sys/module/qla2xxx/parameters/ql2xextended_error_logging
cat /sys/module/qla2xxx/parameters/ql2xextended_error_logging

#重启lvm服务是识别共享存储vg信息
systemctl restart lvm2-lvmetad.service
pvs


```
# 2.lvm.conf配置

```bash

#屏蔽WARNING: duplicate提示信息
vim /etc/lvm/lvm.conf

    # Configuration option devices/filter.
    # Limit the block devices that are used by LVM commands.
    # This is a list of regular expressions used to accept or reject block
    # device path names. Each regex is delimited by a vertical bar '|'
    # (or any character) and is preceded by 'a' to accept the path, or
    # by 'r' to reject the path. The first regex in the list to match the
    # path is used, producing the 'a' or 'r' result for the device.
    # When multiple path names exist for a block device, if any path name
    # matches an 'a' pattern before an 'r' pattern, then the device is
    # accepted. If all the path names match an 'r' pattern first, then the
    # device is rejected. Unmatching path names do not affect the accept
    # or reject decision. If no path names for a device match a pattern,
    # then the device is accepted. Be careful mixing 'a' and 'r' patterns,
    # as the combination might produce unexpected results (test changes.)
    # Run vgscan after changing the filter to regenerate the cache.
    # See the use_lvmetad comment for a special case regarding filters.
    # 
    # Example
    # Accept every block device:
    # filter = [ "a|.*/|" ]
    # Reject the cdrom drive:
    # filter = [ "r|/dev/cdrom|" ]
    # Work with just loopback devices, e.g. for testing:
    # filter = [ "a|loop|", "r|.*|" ]
    # Accept all loop devices and ide drives except hdc:
    # filter = [ "a|loop|", "r|/dev/hdc|", "a|/dev/ide|", "r|.*|" ]
    # Use anchors to be very specific:
    # filter = [ "a|^/dev/hda8$|", "r|.*/|" ]
    # 
    # This configuration option has an automatic default value.
    # filter = [ "a|.*/|" ]
    filter = ["a/sda/","a/mapper/3PAR8400_DEV_LUN26p1/","r/.*/"]
#filter = ["a/sda/","r/.*/"]

    # Configuration option devices/global_filter.
    # Limit the block devices that are used by LVM system components.
    # Because devices/filter may be overridden from the command line, it is
    # not suitable for system-wide device filtering, e.g. udev and lvmetad.
    # Use global_filter to hide devices from these LVM system components.
    # The syntax is the same as devices/filter. Devices rejected by
    # global_filter are not opened by LVM.
    # This configuration option has an automatic default value.
    # global_filter = [ "a|.*/|" ]
    global_filter = ["a/sda/","a/mapper/3PAR8400_DEV_LUN26p1/","r/.*/"]


```

# 3. 一个配置
```bash

#一个简单的multipath.conf配置文件
[root@controller01 ~]# cat /etc/multipath.conf
# This is a basic configuration file with some examples, for device mapper
# multipath.
#
# For a complete list of the default configuration values, run either
# multipath -t
# or
# multipathd show config
#
# For a list of configuration options with descriptions, see the multipath.conf
# man page

## By default, devices with vendor = "IBM" and product = "S/390.*" are
## blacklisted. To enable mulitpathing on these devies, uncomment the
## following lines.
#blacklist_exceptions {
#    device {
#        vendor    "IBM"
#        product    "S/390.*"
#    }
#}

## Use user friendly names, instead of using WWIDs as names.
defaults {
    user_friendly_names yes
    find_multipaths yes
}
##
## Here is an example of how to configure some standard options.
##
#
#defaults {
#    polling_interval     10
#    path_selector        "round-robin 0"
#    path_grouping_policy    multibus
#    uid_attribute        ID_SERIAL
#    prio            alua
#    path_checker        readsector0
#    rr_min_io        100
#    max_fds            8192
#    rr_weight        priorities
#    failback        immediate
#    no_path_retry        fail
#    user_friendly_names    yes
#}
##
## The wwid line in the following blacklist section is shown as an example
## of how to blacklist devices by wwid.  The 2 devnode lines are the
## compiled in default blacklist. If you want to blacklist entire types
## of devices, such as all scsi devices, you should use a devnode line.
## However, if you want to blacklist specific devices, you should use
## a wwid line.  Since there is no guarantee that a specific device will
## not change names on reboot (from /dev/sda to /dev/sdb for example)
## devnode lines are not recommended for blacklisting specific devices.
##
#blacklist {
#       wwid 26353900f02796769
#    devnode "^(ram|raw|loop|fd|md|dm-|sr|scd|st)[0-9]*"
#    devnode "^hd[a-z]"
#}
#multipaths {
#    multipath {
#        wwid            3600508b4000156d700012000000b0000
#        alias            yellow
#        path_grouping_policy    multibus
#        path_selector        "round-robin 0"
#        failback        manual
#        rr_weight        priorities
#        no_path_retry        5
#    }
#    multipath {
#        wwid            1DEC_____321816758474
#        alias            red
#    }
#}
#devices {
#    device {
#        vendor            "COMPAQ  "
#        product            "HSV110 (C)COMPAQ"
#        path_grouping_policy    multibus
#        path_checker        readsector0
#        path_selector        "round-robin 0"
#        hardware_handler    "0"
#        failback        15
#        rr_weight        priorities
#        no_path_retry        queue
#    }
#    device {
#        vendor            "COMPAQ  "
#        product            "MSA1000         "
#        path_grouping_policy    multibus
#    }
#}
multipaths {
  multipath {
  wwid 360002ac000000000000000260001a945
  alias 3PAR8400_DEV_LUN26
  }
  multipath {
  wwid 360002ac000000000000000270001a945
  alias 3PAR8400_DEV_LUN27
  }
  multipath {
  wwid 360002ac000000000000000280001a945
  alias 3PAR8400_DEV_LUN28
  }
  multipath {
  wwid 360002ac000000000000000290001a945
  alias 3PAR8400_DEV_LUN29
  }
  multipath {
  wwid 360002ac0000000000000002a0001a945
  alias 3PAR8400_DEV_LUN30
  }
  multipath {
  wwid 360002ac0000000000000002b0001a945
  alias 3PAR8400_DEV_LUN31
  }
  multipath {
  wwid 360002ac0000000000000002c0001a945
  alias 3PAR8400_DEV_LUN32
  }
  multipath {
  wwid 360002ac0000000000000002d0001a945
  alias 3PAR8400_DEV_LUN33
  }
  multipath {
  wwid 360002ac0000000000000002e0001a945
  alias 3PAR8400_DEV_LUN34
  }
  multipath {
  wwid 360002ac0000000000000002f0001a945
  alias 3PAR8400_DEV_LUN35
  }
  multipath {
  wwid 360002ac000000000000000320001a945
  alias 3PAR8400_DEV_LUN36
  }
  multipath {
  wwid 360002ac000000000000000330001a945
  alias 3PAR8400_DEV_LUN37
  }
  multipath {
  wwid 360002ac000000000000000340001a945
  alias 3PAR8400_DEV_LUN38
  }
  multipath {
  wwid 360002ac000000000000000350001a945
  alias 3PAR8400_DEV_LUN39
  }
  multipath {
  wwid 360002ac000000000000000360001a945
  alias 3PAR8400_DEV_LUN40
  }
  multipath {
  wwid 360002ac000000000000000370001a945
  alias 3PAR8400_DEV_LUN41
  }
  multipath {
  wwid 360002ac000000000000000380001a945
  alias 3PAR8400_DEV_LUN42
  }
  multipath {
  wwid 360002ac000000000000000390001a945
  alias 3PAR8400_DEV_LUN43
  }
  multipath {
  wwid 360002ac0000000000000003a0001a945
  alias 3PAR8400_DEV_LUN44
  }
  multipath {
  wwid 360002ac0000000000000003b0001a945
  alias 3PAR8400_DEV_LUN45
  }
  multipath {
  wwid 360002ac0000000000000003d0001a945
  alias 3PAR8400_DEV_LUN46
  }
  multipath {
  wwid 360002ac0000000000000003e0001a945
  alias 3PAR8400_DEV_LUN47
  }
  multipath {
  wwid 360002ac0000000000000003f0001a945
  alias 3PAR8400_DEV_LUN48
  }
  multipath {
  wwid 360002ac000000000000000400001a945
  alias 3PAR8400_DEV_LUN49
  }
  multipath {
  wwid 360002ac000000000000000410001a945
  alias 3PAR8400_DEV_LUN50
  }
}

```