

https://www.jianshu.com/p/7c8b44d03edc





## 前续

有时候想写一些文章，这样可以整理一些思路，加深对一些技能的理解。但有时候又不想写，毕竟网上有好多这样的资料，感觉写了也不会有人看。所以现在好多东西都在印象笔记上记着，记录的比较乱，也就自己能看懂。写东西好像缺少了动力，唉，不说了，今天整理一下ipxe的使用方法，包括支持UEFI启动。
UEFI统一可扩展固件接口（英语：Unified Extensible Firmware Interface）是一种个人计算机系统规格，用来定义操作系统与系统固件之间的软件界面接口程序设计，作为BIOS的替代方案。据说Intel宣布2020年完全封闭UEFI 相容传统BIOS 模式。

## IPXE简介

官方地址：<http://ipxe.org/>
从官网文档中可以看出，ipxe很强大，也确实强大。大致意思是pxe进化gpxe，gpxe进化ipxe（<http://ipxe.org/faq>）。支持更多的协议，兼容性更好，不挑网卡。不过也可以给网卡刷一下rom，让网卡更好的支持ipxe启动（<http://ipxe.org/howto/romburning>）。

## DHCP服务器端配置

1. 加入ipxe指定的一些参数（<http://ipxe.org/howto/dhcpd>）。这些参数对于传统的dhcp服务是不识别的，所以放心加吧，不会对dhcp服务有其他影响。
   如果感觉这些参数太多，加到/etc/dhcpd.conf文件里会有些乱，使配置文件的可读性变差，那么你可以单独创建一个文件，写入这些内容，然后使用include的方式包含到配置文件中。

```
  option space ipxe;
  option ipxe-encap-opts code 175 = encapsulate ipxe;
  option ipxe.priority code 1 = signed integer 8;
  option ipxe.keep-san code 8 = unsigned integer 8;
  option ipxe.skip-san-boot code 9 = unsigned integer 8;
  option ipxe.syslogs code 85 = string;
  option ipxe.cert code 91 = string;
  option ipxe.privkey code 92 = string;
  option ipxe.crosscert code 93 = string;
  option ipxe.no-pxedhcp code 176 = unsigned integer 8;
  option ipxe.bus-id code 177 = string;
  option ipxe.san-filename code 188 = string;
  option ipxe.bios-drive code 189 = unsigned integer 8;
  option ipxe.username code 190 = string;
  option ipxe.password code 191 = string;
  option ipxe.reverse-username code 192 = string;
  option ipxe.reverse-password code 193 = string;
  option ipxe.version code 235 = string;
  option iscsi-initiator-iqn code 203 = string;
  # Feature indicators
  option ipxe.pxeext code 16 = unsigned integer 8;
  option ipxe.iscsi code 17 = unsigned integer 8;
  option ipxe.aoe code 18 = unsigned integer 8;
  option ipxe.http code 19 = unsigned integer 8;
  option ipxe.https code 20 = unsigned integer 8;
  option ipxe.tftp code 21 = unsigned integer 8;
  option ipxe.ftp code 22 = unsigned integer 8;
  option ipxe.dns code 23 = unsigned integer 8;
  option ipxe.bzimage code 24 = unsigned integer 8;
  option ipxe.multiboot code 25 = unsigned integer 8;
  option ipxe.slam code 26 = unsigned integer 8;
  option ipxe.srp code 27 = unsigned integer 8;
  option ipxe.nbi code 32 = unsigned integer 8;
  option ipxe.pxe code 33 = unsigned integer 8;
  option ipxe.elf code 34 = unsigned integer 8;
  option ipxe.comboot code 35 = unsigned integer 8;
  option ipxe.efi code 36 = unsigned integer 8;
  option ipxe.fcoe code 37 = unsigned integer 8;
  option ipxe.vlan code 38 = unsigned integer 8;
  option ipxe.menu code 39 = unsigned integer 8;
  option ipxe.sdi code 40 = unsigned integer 8;
  option ipxe.nfs code 41 = unsigned integer 8;

```

如果你的dhcp服务没有代理，那么需要加这个选项，可以使dhcp获取ip的速度加快。如果没有dhcp代理，就别加了。
`option ipxe.no-pxedhcp 1;`
如果需要判断UEFI的网络启动，还需要加入这个参数。（默认就给加上吧）
`option client-arch code 93 = unsigned integer 16;`

在配置传统的pxe服务时，需要在/etc/dhcpd.conf写入filename和nextserver，ipxe也是一样的，不过我们加一些判断，代码如下：

```
  if exists user-class and option user-class = "iPXE" {
      filename "http://my.web.server/real_boot_script.php";
  } 
  else if option client-arch != 00:00 {
     filename "ipxe.efi";
  }
  else {
      filename "undionly.kpxe";
  }

```

我们来分析一下这些配置的意思：
首先机器通过网络启动，会到一个dhcp的界面，发送dhcp请求，给我们的dhcp服务器。
然后dhcp服务根据请求的信息，进行上面的逻辑判断。

第一个判断，该网卡是否支持ipxe，如果支持，那么直接到启动的menu界面，real_boot_script.php可以理解为传统的default文件。

第二个判断，该网卡是否是UEFI启动，如果是，那么加载ipxe.efi文件（<http://boot.ipxe.org/ipxe.efi>），加载完这个文件之后，可以使网卡支持ipxe启动，此时的网卡已经不是之前的网卡了。然后网卡会再次dhcp请求地址，这次的请求支持ipxe了。所以dhcp服务器会再次走一下这个判断逻辑，然后发送real_boot_script.php文件，进入启动的menu界面。

第三个判断，如果这个网卡，既不支持ipxe，又不是UEFI启动，那么加载undionly.kpxe文件（<http://boot.ipxe.org/undionly.kpxe>），这个文件和之前的ipxe.efi文件类似，可以使网卡支持ixpe。然后网卡会再次dhcp请求地址，这次的请求支持ipxe了。所以dhcp服务器会再次走一下这个判断逻辑，然后发送real_boot_script.php文件，进入启动的menu界面。

说的有点罗嗦，反正ipxe.efi和undionly.kpxe的作用就是使网卡下次dhcp请求的时候支持ipxe。

## Web端配置

这里其实就是那个real_boot_script.php文件，最基本的配置如下：

```
  #!ipxe
  kernel http://my.web.server/boot/vmlinuz initrd=initrd.img
  initrd http://my.web.server/boot/initrd.img
  boot

```

如果需要加入一些菜单的功能，可以参考这个：<http://ipxe.org/cmd/menu>
并且这里也有一个非常完善的例子，可以自行改改，直接拿来用。地址是：<https://gist.github.com/robinsmidsrod/2234639>

## 补充

还有一些命令需要了解一下，就是网卡启动的时候Ctrl-B出来的界面。

1. 查看网卡设备：

```bash
  iPXE> ifstat
  net0: 52:54:00:12:34:56 using rtl8139 on PCI00:03.0 (closed)
    [Link:up, TX:0 TXE:0 RX:0 RXE:0]

```

1. dhcp获取ip：

```
  iPXE> dhcp
  DHCP (net0 52:54:00:12:34:56).... ok

```

1. 查看目前获取到的IP和DNS：

```
  iPXE> route
  net0: 10.0.0.155/255.255.255.0 gw 10.0.0.1
  iPXE> show dns
  net0.dhcp/dns:ipv4 = 10.0.0.6

```

1. 直接链到“default”文件：

```
 iPXE> chain http://boot.ipxe.org/demo/boot.php
```

