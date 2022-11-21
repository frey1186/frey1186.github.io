---
layout: post
title:  tar 和 find 工具的使用
date: 2019-08-13 12:00
tags: linux
categories: linux-basics 
typora-root-url: ..
---



# 1. tar  -- linux中最常用的归档/压缩工具

配合gzip, bzip2, 和xz 可以实现压缩的功能。
基本语法：

```bash
# tar [options] [pathname ...]
```

常用选项：

```bash
c        归档
x         解归档或解压缩
v         显示过程
f  file   归档的文件
X  --exclude-file   排除某个文件中列举的文件名
--exclude  排除某个目录或文件
-p, --preserve-permissions, --same-permissions   提取文件或目录的权限，使用root用户默认保持
-u, --update  更新归档文件中的某个文件
--delete  删除归档文件中的某个文件
-r, --append  为归档文件添加新文件
-t, --list  列举归档文件中的文件列表
-C, --directory=DIR  解压到目录

```

归档并压缩命令如下，其中`f`后跟的文件名称一般用`.tar.gz`等来结尾，但是不是强制的。

```bash
# 帮助如下
 –gzip or –gunzip	z    	Processes an archive through gzip
 –bzip2	j	                 Processes an archive through bzip2
 –xz	J	                 Processes an archive through xz
# 例子：
# tar czf myfiles.tar.gz file[0-9]
# tar cjf myfiles.tar.bz2 file[0-9]
# tar cJf myfile.tar.xz file[0-9]
```

常用的例子如下：

```bash
# 归档文件
tar cf myfiles.tar file[0-9]
# 归档并压缩文件
tar czf myfiles.tar.gz file[0-9]
# 查看归档的文件列表
tar tzf myfiles.tar.gz
# 只是解压文件
gzip -d myfiles.tar.gz	    [#1] 
bzip2 -d myfiles.tar.bz2	[#2] 
xz -d myfiles.tar.xz 		[#3] 
# 删除归档中的某个文件
tar --delete --file myfile.tar file4
# 更新归档中的某个文件
tar --update --file myfile.tar file5
#  增加文件到归档文件中
tar -rvf tecmint-14-09-12.tar xyz.txt
# 压缩归档文件
gzip myfiles.tar		[ if you choose #1 above ]
bzip2 myfiles.tar		[ if you choose #2 above ]
xz myfiles.tar           [ if you choose #3 above ]
# 备份文件
# Create the tarball and compress it. Exclude files with the MPEG string in its file type.
tar X <(for i in $DIR/*; do file $i | grep -i mpeg; if [ $? -eq 0 ]; then echo $i; fi;done) -cjf backupfile.tar.bz2 $DIR/*

# 其中 X表示排除后面输入的文件中的列表。
# 解压并保持权限
tar xjf backupfile.tar.bz2 --directory user_restore --same-permissions
# 解压归档中的某一个文件
tar -xvf cleanfiles.sh.tar cleanfiles.sh
或者 tar --extract --file=cleanfiles.sh.tar cleanfiles.sh

# 解压归档中的某几个文件
tar -xvf tecmint-14-09-12.tar "file 1" "file 2" 

# 解压归档中的一组文件
tar -xvf Phpfiles-org.tar --wildcards '*.php'
```

更多的例子查看[18个tar例子](https://www.tecmint.com/18-tar-command-examples-in-linux/)。


# 2.find  -- linux中常用的文件查找工具

常用命令选项

```bash
-name  精确匹配名字，也可以使用通配符
-type 类型，后面跟 d，f等
-iname  忽略大小写
-maxdepth  最大深度
-size  文件大小
-user  属主
-perm  权限
-mtime 修改时间，以天为单位，如果要以分钟为单位使用-mmin
-print  打印到标准输出
-exec 执行命令，常用的是后面跟 rm '{}' \   或者   -exec rm -f {} \
```

来看下几个不错的例子：
- [35个find的例子](https://www.tecmint.com/35-practical-examples-of-linux-find-command/)
- [骏马金龙-Linux find常用用法示例](https://www.cnblogs.com/f-ck-need-u/p/10704754.html)


摘几个常用的例子：

```bash
# 最常见的查看文件名和类型
find /tmp -type f -name "a*.sh"

# 根据文件大小
find /tmp -type f -size +100k -name '*.sh'
find / -size +50M -size -100M

# 空目录
find /tmp -type d -empty

# 根据权限来查询
find . -type f -perm 0777 -print

# 将查找到的777权限的文件修改为644
find / -type f -perm 0777 -print -exec chmod 644 {} \;
find / -type d -perm 777 -print -exec chmod 755 {} \;

# 查找并删除一个文件
find . -type f -name "tecmint.txt" -exec rm -f {} \;

# 查看owner是root的文件
find / -user root -name tecmint.txt

# 查找50天以内修改的文件
find / -mtime 50

# 查找50-100天修改的文件
find / -mtime +50 –mtime -100

# 一个小时内修改的文件
find / -mmin -60

```

