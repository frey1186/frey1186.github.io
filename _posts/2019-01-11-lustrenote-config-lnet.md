---
layout: post
title: Lustre学习笔记（3）-配置LNet
date: 2019-01-11 12:00
tags: lustre
categories: public
typora-root-url: ..

---



配置Lnet可以使用两种方式，静态配置（支持所有版本）和动态配置（仅支持2.7.0以上版本）

# 1 静态配置

静态配置通过修改modprobe配置文件的方式实现，一般在/etc/modprobe.d/下添加一个lustre.conf的文件，有networks和ip2nets两种语法可以二选一进行配置。一般情况下，一台主机只能包含一个lustre.conf的配置。

## 1.1 networks语法

简单明了，适合一般场景，有几个注意的地方：
- 如果在配置文件中存在多个条目的networks或者ip2nets配置，最后条目将被内核模块加载。确保在modprobe目录中（/etc/modprobe.d in RHEL and CentOS）不超过1个LNet配置。
- 内核加载选项只在内核模块被加载的时候读取，被模块加载器加载到内核中。所以，修改配置文件后，需要从内核卸载模块，再重新加载。

语法如下：

```bash
options lnet networks="<lnd><#>(<dev>)[,…]"
```

常见的例子如下：

```bash
options lnet networks="tcp0(eth1)"
```

复杂一点的例子

```bash
options lnet networks="tcp0(eth1),o2ib0(ib0),o2ib1(ib1)"
```


## 1.2 ip2nets语法

适合复杂场景，注意点如下：
- ip2nets配置语法使用正则表达式来创建一个主机的LNet配置，基于IPv4；
- ip2nets配置比networks配置更加灵活，但是灵活性会降低简易型和可读性；
- 规则从左到右匹配，匹配到第一条规则后即停止匹配；
- 规格中没有指定明确接口的ethx，只匹配不是loopback接口的第一个接口（如eth0）；
- 可以编写注释，但是必须在分号内进行注释（http://wiki.lustre.org/Static_LNet_Configuration）；

通常语法：

```bash
options lnet ip2nets="<lnd>[<#>][(<dev>)][, <lnd>[<#>][(<dev>)]] <pattern>[; …]"
```

常见例子如下：
```bash
options lnet ip2nets="tcp0(eth1) 10.10.100.*; o2ib0(ib0) 192.168.200.*"
options lnet ip2nets="tcp0(eth0) 10.10.100.[1-50]; tcp0(eth1) 10.10.100.[100-200]"
```
复杂例子：

```bash
# 下面的匹配规则是11和12两台主机匹配tcp0(eth1)，21-24主机匹配tcp0(eth2)，其他主机匹配第一个非回环网卡且地址10.70.*.*
options lnet ip2nets="tcp0(eth1) 10.70.207.[11,12]; \
    tcp0(eth2) 10.70.207.[21-24]; \
    tcp0 10.70.*.*"
```


# 2 动态配置

使用lnetctl工具进行配置，使得LNet能够在内核模块运行的情况下更新，这个特性叫做动态LNet 配置（DLC）。
- 该工具必须在lnet内核模块加载的情况下运行（modprobe lnet）；
- 加载内核后，需要使用lnetctl lnet configure命令进行初始化配置工作；
- lnetctl lnet configure [--all]，如果--all选项被使用，lnetctl会尝试加载任何由modprobe配置文件中networks或者ip2nets选项配置的Lnet接口。否则，lnetctl lnet configure将不会尝试初始化任何网络。当使用动态LNet配置来管理LNet接口时，使用--all标签是不被推荐的，除非需要迁移复杂的旧配置。
- lnetctl可以使用交互式和非交互式两种方式进行配置；
- lnetctl net 配置主要有 add，del，show等几个操作；
- systemd维护的rhel或者centos系统有一个lnet.service可以进行LNet配置的自动管理，配置文件一般使用/etc/lnet.conf（使用YAML格式编写）,通过编写lnet.conf文件即可使用systemd来管理LNet服务。

简单的例子

```bash
# 创建tcpip sockect LND：

lnetctl net add --net tcp1 --if eth1
# 创建一个基于infiniband的NID：

lnetctl net add --net o2ib0 --if ib0
# 查看主机当前配置
lnetctl net show
```

# 3. 举例

配置enp0s8为tcp0的方法，两种方法二选一。

- 静态配置方法
```bash
# 修改配置文件
echo "options lnet networks=tcp0(enp0s8)" > /etc/modprobe.d/lustre.conf
# 加载lnet内核，重启后需要手动重载lnet内核模块
modprobe -v lnet
```

- 动态配置方法：
```bash
# 加载lnet内核模块
modprobe -v lnet
# 初始化配置lnet
lnetctl lnet configure
# 添加tcp0
lnetctl net add --net tcp0 --if enp0s8
# 保存到配置文件
lnetctl net show --net tcp0 > /etc/lnet.conf
# 配置开机自启动，默认读取/etc/lnet.conf配置文件
systemctl enable lnet
```

## 3.1 本例中配置方法

这上一篇中的io1-io4这4个节点中，我们采用lnetctl进行动态配置如下：
```bash
# 在io1中操作即可
## 加载lnet内核模块
modprobe -v lnet
## 初始化配置lnet
lnetctl lnet configure
## 添加tcp0
lnetctl net add --net tcp0 --if enp0s8
## 保存到配置文件
lnetctl net show --net tcp0 > /etc/lnet.conf
[root@io1 ~]# cat /etc/lnet.conf 
net:
    - net type: tcp
      local NI(s):
        - nid: 192.168.56.11@tcp
          status: up
          interfaces:
              0: enp0s8
## 将配置文件复制到其他节点，因为四个节点配置完全一致，不需要单独修改配置
for i in 2 3 4;do scp /etc/lnet.conf io$i:/etc/;done
## 开机自启动 lnet 服务
for i in 1 2 3 4;do ssh io$i systemctl enable lnet ;done
## 启动lnet 服务
for i in 1 2 3 4;do ssh io$i systemctl start lnet ;done
# 使用lctl ping 测试一下各个节点nid连通性
[root@io1 ~]# for i in 1 2 3 4 ;do lctl ping io$i@tcp0 ;done
12345-0@lo
12345-192.168.56.11@tcp
12345-0@lo
12345-192.168.56.12@tcp
12345-0@lo
12345-192.168.56.13@tcp
12345-0@lo
12345-192.168.56.14@tcp
```
