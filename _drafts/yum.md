---
layout: post
title: YUM 简单用法
date: 2018-01-11 12:00
author: felo
tags: yum
---

```bash
yum 用法：

yum check-update 检查可更新的所有软件包
yum update 下载更新系统已安装的所有软件包
yum upgrade 大规模的版本升级,与yum update不同的是,连旧的淘汰的包也升级
yum install 安装新软件包
	yum install --downloadonly --downloaddir=$PATH_OF_FILE PKG 只下载不安装
yum update 更新指定的软件包
yum remove 卸载指定的软件包
yum groupinstall 安装指定软件组中的软件包
yum groupupdate 更新指定软件组中的软件
yum groupremove 卸载指定软件组中的软件包
yum grouplist 查看系统中已经安装的和可用的软件组
yum list 列出资源库中所有可以安装或更新以及已经安装的rpm包
yum list 列出资源库中与正则表达式匹配的可以安装或更新以及已经安装的rpm包
yum list available 列出资源库中所有可以安装的rpm包
yum list available 列出资源库中与正则表达式匹配的所有可以安装的rpm包
yum list updates 列出资源库中所有可以更新的rpm包
yum list updates 列出资源库中与正则表达式匹配的所有可以更新的rpm包
yum list installed 列出资源库中所有已经安装的rpm包
yum list installed 列出资源库中与正则表达式匹配的所有已经安装的rpm包
yum list extras 列出已经安装的但是不包含在资源库中的rpm包
yum list extras 列出与正则表达式匹配的已经安装的但是不包含在资源库中的rpm包
yum list recent 列出最近被添加到资源库中的软件包
yum search 检测所有可用的软件的名称、描述、概述和已列出的维护者，查找与正则表达式匹配的值
yum provides 检测软件包中包含的文件以及软件提供的功能，查找与正则表达式匹配的值
yum clean headers 清除缓存中的rpm头文件
yum clean packages 清除缓存中rpm包文件
yum clean all 清除缓存中的rpm头文件和包文件
yum makecache 创建缓存
	yum clean all && yum makecache 清空缓存并重新创建
yum deplist 显示软件包的依赖信息

```


