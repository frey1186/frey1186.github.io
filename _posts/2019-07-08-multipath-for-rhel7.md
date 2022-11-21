---
layout: post
title:  RHEL7 DM Multipath
date: 2019-07-08 12:00
tags: multipath 
categories: linux-basics
typora-root-url: ..

---



设备映射多路径（`Device mapper multipathing` (`DM Multipath`)），用于合并服务器和存储阵列之间的多`IO`路径。

# 1 `DM Multipath`

`DM Multipath`有两个功能：

- 增加冗余性，`Multipath`提供了`active/passive`的模式；
- 增加性能，`Multipath`提供了`active/active`的模式；


## 1.1 存储阵列支持情况

默认情况下，`DM-Multipath`已经支持了绝大部分的存储阵列，通过下面的命令可以查看。

```bash
# 下面两个命令都可以
# multipathd show config
# multipath -t
```

如果确实没有包含在列表中，需要手动在`multipath.conf`中增加。有一些存储阵列还需要一些特殊的IO错误和路径交换。


## 1.2 `dm-multipath`组成

- `dm_multipath`：内核模块，负责路径切换和IO路由；
- `mpathconf`：启动和配置多路径；
- `multipath`：配置多路径设备的命令；
- `multipathd`：路径监控进程，修改配置文件后要重启这个进程；
- `kpartx`：分区工具，device-mapper-multipath依赖这个包；




# 2  多路径设备

## 2.1 关于多路径设备的名称问题 

每一个多路径设备都会有一个`World Wide Identifier (WWID)`，是唯一的标识该设备的ID。默认情况下系统会使用WWID作为设备的名称。
该多路径设备在系统中的每条路径都会显示为一个设备，如sdb，sdc ...  这些设备不能直接使用，同一个设备的不同路径的WWID是一致的；
使用`user_friendly_names`配置选项，可以让名字更加具有可读性和友好性。当配置为`yes`，路径聚合后系统中显示的设备名称为：`mpathn`，其中n为从a开始的字母，超过26个的话，会显示如`mpathaa`，`mpathab`;
多路径设备聚合后，会在两个不同地方显示设备`/dev/mapper/mpathn` 和` /dev/dm-n`，其中`mpathn`可以为管理员使所用，`dm-n`为系统内部调用不建议管理员直接使用它。
也可以自定义多路径设备的名称，可以使用`alias`;

## 2.2 集群中的多路径设备

要求集群中每个节点如果使用`user_friendly_names`配置选项，每个主机识别的多路径设备名称可能不一致。
保持一致的多路径名称有下面几个办法：
- 方法1，使用wwid作为设备名称，这种方法不存在不一致；
- 方法2，同步集群中各个节点的`/etc/multipath/bindings`文件，每增加一个设备需要执行一次下面的步骤

```bash
# 1，在一个节点中设置好多路径设备
# 2，停止其他节点多路径服务
systemctl stop multipathd.service
multipath -F
# 3，复制/etc/multipath/bindings文件到其他节点
# 4，启动multipathd服务
```

- 方法3，同步集群中各个节点的`/etc/multipah.conf`文件，每增加一个设备需要执行一次下面的步骤

```bash
# 1，在一个节点中设置好多路径设备
# 2，停止其他节点多路径服务
systemctl stop multipathd.service
multipath -F
# 3，复制/etc/multipath.conf文件到其他节点
# 4，启动multipathd服务
```


# 3 设置`DM-Multipath`

## 3.1 使用mpathconf命令设置

mpathconf命令可以创建或修改/etc/multipath.conf配置文件，如果当前系统不存在/etc/multipath.conf，就会从/usr/share/doc/device-mapper-multipath-0.4.9/multipath.conf复制一份；

```bash
# 不修改配置文件，创建一个默认的配置文件
mpathconf --enable --with_multipathd y  # 并启动multipathd服务
# mpathconf -h
usage: /usr/sbin/mpathconf <command>

Commands:
Enable: --enable
Disable: --disable
Only allow certain wwids (instead of enable): --allow <WWID>  # 允许特定的wwid
Set user_friendly_names (Default y): --user_friendly_names <y|n>  # 使用友好的名称，会被写到/etc/multipath.conf中
Set find_multipaths (Default y): --find_multipaths <y|n>  # 忽略本地设备，会被写到/etc/multipath.conf中
Load the dm-multipath modules on enable (Default y): --with_module <y|n> # 加载内核，手动加载命令modprobe dm-multipath
start/stop/reload multipathd (Default n): --with_multipathd <y|n>  # 启动multipath服务，默认不启动
select output file (Default /etc/multipath.conf): --outfile <FILE>  # 配置问价路径

# 如果需要不需要user_friendly_names参数
mpathconf --enable --user_friendly_names n
```
```bash
# 如果需要修改配置文件的情况下
# 1，创建配置文件
mpathconf --enable
# 2，修改配置文件并保存
vi /etc/multipath.conf
# 3，重启服务
```

## 3.2 忽略本地设备

`find_multipaths`参数默认会被配置为`yes`，所以默认情况下，本地设备是不会被`multipath`来管理的。
如果该参数被配置为`no`，那么使用下面命令可以查看未被`multipath`管理的本地设备

```bash
multipath -v2 -d 
```

将查询到wwid写入黑名单(/etc/multipath.conf文件中的blacklist)中，就可以手动实现忽略本地设备

```bash
blacklist {
    wwid 36xxxx0072xxxx428BX1xxxx
}
```

如果需要在initramfs 中使用multipath设备，那么需要执行如下命令：

```bash
# dracut --force --add multipath --include /etc/multipath
```

# 4 常见安装和配置步骤

- 安装包`device-mapper-multipath`，会一起安装lib包；
- 使用`mpathconf`命令配置多路径；
- 必要的情况下，修改`multipath.conf`配置文件；
- 启动或重启监控进程；

## 4.1 使用默认配置

```bash
# 安装 & 配置 & 启服务
yum -y install device-mapper-multipath 
mpathconf --enable --with_multipathd y
```

# 4.2 使用alias

其他的步骤没啥区别，就是修改`/etc/multipath.conf`：

```bash
# cat /etc/multipath.conf |grep -v -E "^$|^#"

defaults {
    user_friendly_names yes
    find_multipaths yes
}

multipaths {
    multipath {
        wwid WWID_of_swap_device
        alias dev_alias
    }
}

blacklist {
}

```


# 参考

- https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/dm_multipath/index
