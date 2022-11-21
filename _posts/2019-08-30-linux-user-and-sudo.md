---
layout: post
title:  用户管理和sudo
date: 2019-08-30 12:00
tags: linux
categories: linux-basics 
---



# 0. 概述

用户和权限相关的内容而已。


# 1. 用户

在Linux中可以随意切换用户，而且十分方便。管理用户必须使用root。

## 1.1 创建和修改用户

创建用户：

```bash
# 直接创建一个用户，默认会增加一个同名的组
[root@vm-centos7 home]# useradd test1
[root@vm-centos7 home]# id test1
uid=1002(test1) gid=1002(test1) groups=1002(test1)
# 创建用户的时候指定一些参数
[root@vm-centos7 home]# useradd -u 1100 -g test1 -m -s /bin/bash test2
#  -u 指定用户id，一般1000以后，1000以前系统用；
#  -g 指定gid，-G指定groups GID
#  -m 创建home目录
#  -s 指定shell
```
修改用户：

```bash
# 修改用户的组
[root@vm-centos7 home]# usermod -G root,test1 test2
[root@vm-centos7 home]# id test2
uid=1100(test2) gid=1002(test1) groups=1002(test1),0(root)
```

## 1.2 删除用户

```bash
# 删除用户，保留home目录

# 删除用户并所有数据

```

## 1.3 其他特别的地方

- useradd和usermod差别很小，几乎命令都差不多；
- adduser也是增加用户的命令；
- -k命令

```bash
 -k, --skel SKEL_DIR           use this alternative skeleton directory
```

- 创建用户的同时可以修改密码策略

```bash
  -e, --expiredate EXPIRE_DATE  expiration date of the new account
  -f, --inactive INACTIVE       password inactivity period of the new account
```

# 2. 权限

## 2.1 文件和目录的权限

每个文件或者目录的权限分成三段，分别是：

- u  表示该文件所有者
- g  表示该文件所有者所在组
- o  表示其他人

每段三个权限：

- r  表示可读
- w  表示可写
- x  表示可执行

比如：

```bash

rwxr-x---   

---> 表示u具有rwx的权限
     g具有rx的权限
     o不具备任何权限

---> 也可以使用二进制的方式来表示
     上述权限就是： 111 101 000
     再转换为10进制就是：750
```

还有一点特殊权限，下一节说。
- 4 为 SUID ＝ u+s
- 2 为 SGID ＝ g+s
- 1 为 SBIT ＝ o+t


## 2.2 特殊权限

- SUID:(set UID)
	
    - 只是对二进制可执行文件有效；
    - 让g或者o的用户执行该文件的时候暂时具备这个文件owner的权限；
    - 只在执行过程中有效；
    - ** 对脚本是无效的**；

```bash
# /bin/passwd 可以为用户修改密码
# root用户可以为所有用户修改密码
# 其他用户只能为自己修改密码
# 可以看到这个文件有一个s的特殊权限，就是SUID权限。
[root@vm-centos7 ~]# ls -l /bin/passwd
-rwsr-xr-x. 1 root root 27832 Jun 10  2014 /bin/passwd

# passwd命令会修改该文件，但是只有root可以修改
[root@vm-centos7 ~]# ls -l /etc/shadow
---------- 1 root root 1061 Aug 31 23:51 /etc/shadow
```

- SGID:(set GID)

    - 跟SUID类似，只是s作用在g的x位置上；
    - 作用是让o的用户暂时具备g用户的权限
    - 对二进制有用，但是一般用于目录；


```bash
# 在一个具有SGID的目录中创建一个文件
# 这个文件的g权限将会是具有SGID的用户组

# 在g的x位置上改成了s
[root@vm-centos7 tmp]# mkdir d1;chmod -R 2777 d1
[root@vm-centos7 tmp]# ls -l |grep d1
drwxrwsrwx 2 root root  6 Sep  2 13:34 d1
[root@vm-centos7 tmp]# su test
[test@vm-centos7 tmp]$ touch d1/t1
# 创建的这个t1文件组权限是root
[test@vm-centos7 tmp]$ ls -l d1/t1
-rw-rw-r-- 1 test root 0 Sep  2 13:35 d1/t1
# 然而test用户居然不属于root组
[test@vm-centos7 tmp]$ id test
uid=1001(test) gid=1001(test) groups=1001(test)
```

- SBIT:(Sticky Bit)

    - 针对other权限的，只对目录有效
    - **不能对二进制文件作用**
    - o权限位置会变成t

```bash
# 最常见的就是tmp目录，所有人都可以在tmp下创建目录
# 但是只有root和自己才能删除该目录
[root@vm-centos7 ~]# ls -l / |grep tmp
drwxrwxrwt.  15 root root 4096 Sep  2 13:34 tmp
```

## 2.3 修改权限

- chmod  修改文件或目录的权限

```bash
[root@vm-centos7 tmp]# chmod 4755 file1
[root@vm-centos7 tmp]# ls -l file1
-rwsr-xr-x 1 root root 0 Sep  2 13:50 file1
[root@vm-centos7 tmp]# chmod 0755 file1
[root@vm-centos7 tmp]# ls -l file1
-rwxr-xr-x 1 root root 0 Sep  2 13:50 file1
[root@vm-centos7 tmp]# chmod -R 755 dir1
[root@vm-centos7 tmp]# ls -ld dir1
drwxr-xr-x 2 root root 6 Sep  2 13:50 dir1
```

- chown  修改文件或目录的属主

```bash
[root@vm-centos7 tmp]# chown test.test file1
[root@vm-centos7 tmp]# ls -l file1
-rwxr-xr-x 1 test test 0 Sep  2 13:50 file1
[root@vm-centos7 tmp]# chown -R test.test dir1
[root@vm-centos7 tmp]# ls -ld dir1
drwxr-xr-x 2 test test 6 Sep  2 13:50 dir1
```

# 3. 用户密码

## 3.1 `/etc/passwd`

```bash
[root@vm-centos7 tmp]# cat /etc/passwd
root:x:0:0:root:/root:/bin/bash
bin:x:1:1:bin:/bin:/sbin/nologin
daemon:x:2:2:daemon:/sbin:/sbin/nologin
...
# 登录名：口令：用户标识号：组标识号：用户名：用户主目录：shell

# 第一列：登录用的用户名，大小写敏感
# 第二列：用户口令，用x代替，保存口令已经使用/etc/shadow文件
# 第三列：用户UID，系统中的用户id标识，0-499系统用，500-普通用户，一般自动从1000开始
# 第四列：组ID，
# 第五列：用户名，用户说明，可以空，可以跟登录名一样
# 第六列：家目录，一般用户都在/home下
# 第七列：shell，如果不能登录就使用nologin

```

## 3.2 `/etc/shadow`

```bash
[root@vm-centos7 tmp]# cat /etc/shadow |head
root:$6$ZG/SVZBlg7fGdgjx$hcHX.aoHPxMGbu968ZezzwEYzd6lIieOaU8VBZnojQ0jQG/PNgBsVmbyoM/FaRMDB0T8rHOLHk3DscaXetgOA/::0:99999:7:::
bin:*:17834:0:99999:7:::
daemon:*:17834:0:99999:7:::
adm:*:17834:0:99999:7:::
lp:*:17834:0:99999:7:::
sync:*:17834:0:99999:7:::
shutdown:*:17834:0:99999:7:::
halt:*:17834:0:99999:7:::
mail:*:17834:0:99999:7:::
operator:*:17834:0:99999:7:::

1、账户名称 
2、加密后的密码，如果这一栏的第一个字符为!或者*的话，说明这是一个不能登录的账户，看来root用户可以登录；
3、最近改动密码的日期（这个是从1970年1月1日算起的总的天数）
4、密码不可被变更的天数：如果是0的话，则没有限制 
5、密码需要重新变更的天数：如果为99999则没有限制 
6、密码过期预警天数 
7、密码过期的宽恕时间：如果在5中设置的日期过后，用户仍然没有修改密码，则该用户还可以继续使用的天数 
8、账号失效日期，过了这个日期账号就无法使用 
9、保留的

```

## 3.3 密码策略

可以使用authconfig命令来配合很多密码策略，这是RHEL7/Centos7的一个工具。

```bash
authconfig, authconfig-tui - an interface for configuring system authentication resources

```
### 3.3.1 设置密码长度

```bash
# 密码长度最小为8
[root@vm-centos7 ~]# authconfig --passminlen=8 --update
[root@vm-centos7 ~]# cat /etc/security/pwquality.conf |grep ^minlen
minlen = 8
```
### 3.3.2 设置密码复杂度

```bash
# 至少包含一个大写字母
[root@vm-centos7 ~]# authconfig --enablerequpper --update
# 至少包含一个小写字母
[root@vm-centos7 ~]# authconfig --enablereqlower --update
# 至少包含一个数字
[root@vm-centos7 ~]# authconfig --enablereqdigit --update
# 至少包含一个特殊字符
[root@vm-centos7 ~]# authconfig --enablereqother --update

# 查看更改情况，默认1，修改为-1生效
[root@vm-centos7 ~]# cat /etc/security/pwquality.conf |grep credit
# credits are not disabled which is the default). (See pam_cracklib manual.)
# The maximum credit for having digits in the new password. If less than 0
# dcredit = 1
# The maximum credit for having uppercase characters in the new password.
# ucredit = 1
# The maximum credit for having lowercase characters in the new password.
# lcredit = 1
# The maximum credit for having other characters in the new password.
# ocredit = 1
lcredit     = -1
ucredit     = -1
dcredit     = -1
ocredit     = -1
```
### 3.3.3 设置密码有效期

```bash
# 修改新建用户的默认策略
[root@vm-centos7 ~]# cat /etc/login.defs
...
# Password aging controls:
#
#       PASS_MAX_DAYS   Maximum number of days a password may be used.
#       PASS_MIN_DAYS   Minimum number of days allowed between password changes.
#       PASS_MIN_LEN    Minimum acceptable password length.
#       PASS_WARN_AGE   Number of days warning given before a password expires.
#
PASS_MAX_DAYS   99999
PASS_MIN_DAYS   0
PASS_MIN_LEN    5
PASS_WARN_AGE   7
...
```

```bash
# 修改已经创建的用户
# 使用chage命令修改
[root@vm-centos7 ~]# chage -l test
Last password change                                    : Aug 31, 2019
Password expires                                        : never
Password inactive                                       : never
Account expires                                         : never
Minimum number of days between password change          : 0
Maximum number of days between password change          : 99999
Number of days of warning before password expires       : 7
[root@vm-centos7 ~]#
[root@vm-centos7 ~]#
[root@vm-centos7 ~]#
[root@vm-centos7 ~]# chage --help
Usage: chage [options] LOGIN

Options:
  -d, --lastday LAST_DAY        set date of last password change to LAST_DAY
  -E, --expiredate EXPIRE_DATE  set account expiration date to EXPIRE_DATE
  -h, --help                    display this help message and exit
  -I, --inactive INACTIVE       set password inactive after expiration
                                to INACTIVE
  -l, --list                    show account aging information
  -m, --mindays MIN_DAYS        set minimum number of days before password
                                change to MIN_DAYS
  -M, --maxdays MAX_DAYS        set maximim number of days before password
                                change to MAX_DAYS
  -R, --root CHROOT_DIR         directory to chroot into
  -W, --warndays WARN_DAYS      set expiration warning days to WARN_DAYS
```
### 3.3.4 手动生成shadow中的密码

shadow文件中第二个字段是加密后的密码，如果格式为"$id$salt$hashed"，则表示该用户密码正常。其中$id$的id表示密码的加密算法，$1$表示使用MD5算法，$2a$表示使用Blowfish算法，"$2y$"是另一算法长度的Blowfish,"$5$"表示SHA-256算法，而"$6$"表示SHA-512算法，

```bash
# 生成一个加密的密码，这个办法也可以用于kickstart脚本
[root@vm-centos7 tmp]# openssl passwd -1 123456
$1$4VQqQlQp$ZFucFpLz9N8ym8gvCVlNT/

# 直接替换到/etc/shadow第二个字段中即可
[root@vm-centos7 tmp]# vim /etc/shadow
[root@vm-centos7 tmp]# cat /etc/shadow|grep test:
test:$1$4VQqQlQp$ZFucFpLz9N8ym8gvCVlNT/:18139:0:99999:7:::
```
# 4. `sudo`

Linux sudo命令以系统管理者的身份执行指令，也就是说，经由 sudo 所执行的指令就好像是 root 亲自执行。

直接上例子吧。

## 4.1 增加用户或组

`vi /etc/sudoers` 或者`visudo`修改98行。

```bash
Syntax:    user    MACHINE=COMMANDS      # sudo 语法
root    ALL=(ALL)       ALL              #  (All)表示允许用户以哪个用户的权限做事情
omd     ALL=(ALL)       ALL              #  omd用户在任何机器上，可以只需任何用户的任何命令 == root用户
omd     ALL=(ALL)     NOPASSWD: ALL      #  免密而且omd用户在任何机器上，可以只需任何用户的任何命令
ftl     ALL=(ALL)   /bin/cp,/bin/touch   # 只允许ftl用户只需root用户的cp,touch命令
```

# x. 参考

- [手动生成/etc/shadow文件中的密码](https://www.cnblogs.com/f-ck-need-u/p/7545187.html)
- [使用 PAM 集成 OpenLDAP 实现 Linux 统一管理系统用户](https://www.ibm.com/developerworks/cn/linux/1406_liulz_pamopenldap/#1.Linux-PAM%20%E5%92%8C%20OpenLDAP%20%E7%AE%80%E4%BB%8B%20%7Coutline)
- [如何设置 Linux 系统的密码策略](https://linux.cn/article-10698-1.html?pr)
- [Linux sudo详解](https://www.cnblogs.com/ftl1012/p/sudo.html)

