---
layout: post
title:  APUE笔记-2-文件IO
date: 2021-03-19 12:00
tags: apue c
categories: apue
typora-root-url: ..
---

文件IO，fileIO 也可以说是系统调用IO，以文件描述符(file descriptor)为核心。

## 原子操作

- 追加文件

- 创建文件




## 重定向的实现 dup dup2

```
#include <unistd.h>

int dup(int oldfd);  //复制到一个可用的最小的文件描述符
int dup2(int oldfd, int newfd); // 指定一个文件描述符，先关闭再复制
```


## 同步：sync fsync fdatasync

![1617688620295](/linux-sys/1617688620295.png)

```bash
void sync（void）：  缓冲区写到队列，马上返回；30s来一次；针对所有文件；不能保证已经写完；
fsync（int fd）: 只对一个fd起作用，等待写入磁盘，才返回；适用于数据库；
fdatasync（int fd）: 只针对数据，不更新文件的属性；不如fsync来的全。
```



## fcntl()  

修改已经打开的文件描述符。

## iocntl()

IO操作的杂物箱，不同的IO操作可能有不同的参数可以选择，根据实际情况来选择。

## /dev/fd

在`/dev/fd`目录下，保存已经打开的文件描述符。

fd  = open("/dev/fd/0", mode)

等同于：

fd = dup(0)

但是无法直接修改文件描述符的可写权限，只能保持原先的读写权限；















