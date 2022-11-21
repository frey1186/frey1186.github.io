---
layout: post
title: Linux Login Profile 配置方法
date: 2018-3-2 12:00
author: felo
tags: linux
categories: public
typora-root-url: ..
---


## 1. 配置文件

全局配置文件：

- `/etc/profile`：环境变量
- `/etc/profile.d/`：自定义配置存放位置
- `/etc/bashrc`或者`/etc/bash.bashrc`：系统全局函数和别名

用户配置文件：

- `~/.bash_profile`
- `~./bash_login`
- `~/.profile`
- `~/.bashrc`

## 2. 测试环境-CentOS7

```bash
[root@mycentos7 ~]# cat /etc/redhat-release 
CentOS Linux release 7.4.1708 (Core) 
[root@mycentos7 ~]# uname -a
Linux mycentos7 3.10.0-693.el7.x86_64 #1 SMP Tue Aug 22 21:09:27 UTC 2017 x86_64 x86_64 x86_64 GNU/Linux

# 默认home下有.bash_profile和.bashrc
[user01@mycentos7 ~]$ ls -la
-rw-r--r--  1 user01 user01  18 Aug  3  2017 .bash_logout
-rw-r--r--  1 user01 user01 193 Aug  3  2017 .bash_profile
-rw-r--r--  1 user01 user01 231 Aug  3  2017 .bashrc

# 默认全局文件
[root@mycentos7 etc]# pwd
/etc
[root@mycentos7 etc]# ls -l |grep profile
-rw-r--r--.  1 root root     1795 Nov  6  2016 profile
drwxr-xr-x.  2 root root     4096 Feb 19 21:41 profile.d
[root@mycentos7 etc]# ls -l |grep bash
-rw-r--r--   1 root root      139 Feb 19 15:59 bash.bashrc
drwxr-xr-x.  2 root root     4096 Feb 19 21:41 bash_completion.d
-rw-r--r--.  1 root root     2853 Nov  6  2016 bashrc
```

### 2.1 全局环境变量

```bash
[root@mycentos7 etc]# head -n 10 profile
# /etc/profile

# System wide environment and startup programs, for login setup
# Functions and aliases go in /etc/bashrc

# It's NOT a good idea to change this file unless you know what you
# are doing. It's much better to create a custom.sh shell script in
# /etc/profile.d/ to make custom changes to your environment, as this
# will prevent the need for merging in future updates.

[root@mycentos7 etc]# head -n 10 bashrc
# /etc/bashrc

# System wide functions and aliases
# Environment stuff goes in /etc/profile

# It's NOT a good idea to change this file unless you know what you
# are doing. It's much better to create a custom.sh shell script in
# /etc/profile.d/ to make custom changes to your environment, as this
# will prevent the need for merging in future updates.
```

这两个全局环境变量的文件都说明了，**不要**修改当前文件，如果需要自定义的话，可以在`/etc/profile.d/`下编写相应的脚本。

下面是`/etc/profile`中的一段调用`profile.d`目录下脚本的代码：

```bash
for i in /etc/profile.d/*.sh; do
        if [ -r "$i" ]; then
            if [ "$PS1" ]; then
                . "$i"
            else
                . "$i" >/dev/null
            fi
        fi
```

如果需要一个全局变量，在`profile.d`下面编写一个测试脚本：

```bash
[root@mycentos7 ~]# cd /etc/profile.d/
# 注意文件名需要写成：*.sh
[root@mycentos7 profile.d]# echo "echo test-own-profile"  >> test.sh
# 登陆用户
[root@mycentos7 profile.d]# su - user01
Last login: Fri Mar  2 11:35:15 CST 2018 on pts/0
test-own-profile  # 执行了test.sh
```



### 2.2 用户配置文件

用户`home`中的`.bash_profile`是自动加载的配置文件：

```bash
[user01@mycentos7 ~]$ ls -la
-rw-r--r--  1 user01 user01 193 Aug  3  2017 .bash_profile
-rw-r--r--  1 user01 user01 231 Aug  3  2017 .bashrc
[user01@mycentos7 ~]$ cat .bash_profile 
# .bash_profile

# Get the aliases and functions
if [ -f ~/.bashrc ]; then
        . ~/.bashrc
fi

# User specific environment and startup programs

PATH=$PATH:$HOME/.local/bin:$HOME/bin

export PATH
[user01@mycentos7 ~]$ 
```

其中`.bash_profile`中调用了`.bashrc`这个文件，因此，如果需要自定义用户的配置文件的话，在`.bashrc`中添加是比较合适的，可以用于定义别名或者函数。

下面写一个简单的例子：

```bash
[user01@mycentos7 ~]$ echo "echo test-bashrc" >>.bashrc 
[user01@mycentos7 ~]$ exit
logout
# 登陆用户
[root@mycentos7 ~]# su - user01
Last login: Fri Mar  2 12:36:04 CST 2018 on pts/2
test-bashrc   # 执行了.bashrc
```

## 3. 测试环境-ubuntu16.04

```bash
[root@host1 /]# cat /etc/os-release
NAME="Ubuntu"
VERSION="16.04.2 LTS (Xenial Xerus)"
ID=ubuntu
ID_LIKE=debian
PRETTY_NAME="Ubuntu 16.04.2 LTS"
VERSION_ID="16.04"
HOME_URL="http://www.ubuntu.com/"
SUPPORT_URL="http://help.ubuntu.com/"
BUG_REPORT_URL="http://bugs.launchpad.net/ubuntu/"
VERSION_CODENAME=xenial
UBUNTU_CODENAME=xenial
```

### 3.1 全局

```bash
[root@host1 /]# ls -l /etc/ |grep profile
-rw-r--r-- 1 root root     575 Oct 23  2015 profile
drwxr-xr-x 2 root root    4096 Dec 26 21:17 profile.d
[root@host1 /]# ls -l /etc/ |grep bash
-rw-r--r-- 1 root root    2188 Sep  1  2015 bash.bashrc
-rw-r--r-- 1 root root      45 Aug 13  2015 bash_completion
drwxr-xr-x 2 root root    4096 Dec 27 08:37 bash_completion.d
```

有两个地方：

- `profile.d`：自定义全局配置文件，编写`.sh`文件放在这个目录下面即可；

  ```bash
  [root@host1 ~]# ls -l /etc/profile.d/
  total 16
  -rw-r--r-- 1 root root  101 Jan 14  2017 apps-bin-path.sh
  -rw-r--r-- 1 root root  663 May 18  2016 bash_completion.sh
  -rw-r--r-- 1 root root 1003 Dec 29  2015 cedilla-portuguese.sh
  -rw-r--r-- 1 root root 1557 Apr 15  2016 Z97-byobu.sh
  ```

- `bash_completion.d`：自定义补全脚本

  ```bash
  [root@host1 ~]# ls -l /etc/bash_completion.d/
  total 52
  -rw-r--r-- 1 root root  6636 Mar 31  2016 apport_completion
  -rw-r--r-- 1 root root   408 Aug 21  2015 cryptdisks
  -rw-r--r-- 1 root root 12179 Dec 27 08:36 docker-machine.bash
  -rw-r--r-- 1 root root  1469 Dec 27 08:36 docker-machine-prompt.bash
  -rw-r--r-- 1 root root  1525 Dec 27 08:37 docker-machine-wrapper.bash
  -rw-r--r-- 1 root root   439 Mar 23  2016 git-prompt
  -rw-r--r-- 1 root root 11144 Oct 13 04:48 grub
  -rw-r--r-- 1 root root   736 May  7  2013 insserv
  ```

### 3.2 用户配置文件

默认有两个配置文件，`.bashrc`和`.profile`：

```bash
user01@host1:~$ ls -al
-rw-r--r-- 1 felo felo 3771 Dec 26 21:20 .bashrc
-rw-r--r-- 1 felo felo  655 Dec 26 21:20 .profile
```

从`.profile`可以看到

```bash
user01@host1:~$ head -n 5 .profile
# ~/.profile: executed by the command interpreter for login shells.
# This file is not read by bash(1), if ~/.bash_profile or ~/.bash_login
# exists.
# see /usr/share/doc/bash/examples/startup-files for examples.
# the files are located in the bash-doc package.
```

如果`~/.bash_profile`和`~/.bash_login`不存在的情况下，会读取`.profile`这个文件。`.profile`再调用`.bashrc`：

```bash
# if running bash
if [ -n "$BASH_VERSION" ]; then
    # include .bashrc if it exists
    if [ -f "$HOME/.bashrc" ]; then
        . "$HOME/.bashrc"
    fi
fi
```

所以，同样的，还是定义`.bashrc`是最合适的。

## 4. 总结

- 如果添加系统全局配置的话，在`/etc/profile.d/`下自定义一个`.sh`的脚本；
- 如果添加用户配置的话，直接修改`~/.bashrc`即可。

