---
layout: post
title: RHEL Filesystem Backup & Restore
date: 2019-12-23 12:00
tags: linux 
categories: linux-basics
typora-root-url: ..
---

# 1. 关于XFS的备份与恢复

xfs提供了xfsdump和xfsrestore工具，协助备份xfs文件系统中的数据。

xfsdump工具的特点：

- 在线备份
- 0表示全备，1-9表示增量备份；
- 支持备份到磁带设备


# 2. examples


```bash
# 备份级别0，备份目标/mnt/boot.bak
xfsdump -l 0 -L boot_bak -f /mnt/boot.bak /boot
xfsdump -l 0 -L boot_bak -f /mnt/boot.bak /dev/sda1

# 恢复目标/mnt/
xfsrestore -f /mnt/boot.bak  /mnt/

# 恢复单个文件到/mnt目录下
xfsrestore -f /mnt/boot.bak -s grub2/grub.cfg /mnt/
```



# X. 参考资料

- [1] Red_Hat_Enterprise_Linux-7-Storage_Administration_Guide-en-US.pdf
- [2] [xfs文件系统的备份与恢复](https://www.cnblogs.com/diantong/p/10191864.html)
