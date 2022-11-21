---
layout: post
title: 为Win7镜像添加USB3.0驱动
date: 2018-09-16 12:00
author: felo
tags: win7
categories: public
typora-root-url: ..
---

在安装`win7`的时候，由于`win7`镜像中没有`USB3.0`的驱动，但是因为没有`USB3.0`驱动，又不能通过U盘或者移动硬盘加载驱动。所以，如果在使用`USB`启动的安装镜像时，可以添加离线驱动。
`win7`安装的时候，简单分成下面三步：

- 首先加载`source/boot.wim`启动一个PE的环境；
- 完成硬盘分区等基本配置；
- 安装`source/install.wim`到硬盘中。

出现没有办法安装，就是因为这个`PE`环境缺少`USB3.0`的驱动，因此，修改`boot.wim`这个镜像文件即可。`install.wim`里面加不加都行，可以安装系统后再补充驱动。

1. 制作`USB`启动盘

工具很多，比如使用`UltraISO`工具：
- “打开”，浏览到`win.iso`
- "启动"，选择“写入硬盘映像”，选择指定的U盘
- 等待完成即可。


2. 添加驱动

使用`dism`工具即可，将U盘中source文件夹下面的`boot.wim`拷贝到一个临时目录中，如`d:\mount`，通过`dism`将`boot.wim`临时挂载到`d:\mount\boot`下。

```bash
d:
cd mount
mkdir boot
dism /mount-wim /wimfile:boot.wim /index:2 /mountdir:boot
```

准备`USB3.0`驱动文件，需要使用`inf`文件，不能使用`exe`包，一般先运行`exe`包，解压到一个文件，但不安装，如解压到`d:\mount\mydrives`，使用`dism`将驱动添加进去即可。

```bash
dism /image:boot /add-driver:mydrivers /recurse
```

- `/recurse`遍历目录下面的文件和子文件夹

退出

```bash
dism /unmount-wim /mountdir:boot /commit
```

将这个`boot.wim`覆盖到U盘中即可。




### 参考
- https://wenku.baidu.com/view/8ca7561a590216fc700abb68a98271fe910eaf16.html
- https://blog.csdn.net/g_newbie/article/details/60578199