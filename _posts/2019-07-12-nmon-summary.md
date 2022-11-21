---
layout: post
title:  使用 NMON 的一点总结
date: 2019-07-12 12:00
tags: nmon 
categories: public
typora-root-url: ..
---


为aix开发，也能用于linux。可以实时显示性能，也能采集性能数据，通过分析工具形成图表。

- nmon：http://nmon.sourceforge.net/pmwiki.php



# 1 下载和编译

二进制文件，下载后直接使用

```bash
wget http://sourceforge.net/projects/nmon/files/nmon16j.tar.gz
tar -zxf nmon16j.tar.gz
./nmon_x86_rhel75
```

也可以自己编译，编译一个和自己系统相近的版本即可，可以参看http://nmon.sourceforge.net/pmwiki.php?n=Site.CompilingNmon

```bash
wget http://sourceforge.net/projects/nmon/files/lmon16j.c 
wget http://sourceforge.net/projects/nmon/files/makefile
yum -y install gcc  ncurses-devel  make 
ln lmon16j.c lmon.c
make nmon_x86_rhel75   # 3秒钟即可
```

# 2. 使用方法

## 2.1 实时性能

使用几个快捷键可以打开或关闭功能：

![](/images/nmon/nmon-func.png)




## 2.2 采集性能

```bash
Hint for nmon_x86_rhel75 version 16j
        Full Help Info : nmon_x86_rhel75 -h

        On-screen Stats: nmon_x86_rhel75
        Data Collection: nmon_x86_rhel75 -f [-s <seconds>] [-c <count>] [-t|-T]
        Capacity Plan : nmon_x86_rhel75 -x
Interactive-Mode:
        Read the Welcome screen & at any time type: "h" for more help
        Type "q" to exit nmon

For Data-Collect-Mode
        -f Must be the first option on the line (switches off interactive mode)
                      Saves data to a CSV Spreadsheet format .nmon file in then local directory
                      Note: -f sets a defaults -s300 -c288 which you can then modify
        Further Data Collection Options:
        -s <seconds> time between data snapshots
        -c <count> of snapshots before exiting
        -t Includes Top Processes stats (-T also collects command arguments)
        -x Capacity Planning=15 min snapshots for 1 day. (nmon -ft -s 900 -c 96)
---- End of Hints
```

常见采集的方法如下：

```bash
# 手动采集 -f表示输出文件， -s表示采集时间间隔，-c表示采集数量
# nmon_x86_rhel75  -fs 10  -c 100
#  放在crontab中，每天采集并形成一个文件
# crontab -l 
0 0 * * *  /root/nmon_x86_rhel75 -x
```


## 2.3 分析性能

### 2.3.1  nmon analyser

这是一个excel工具，导入采集结果会获得一个新的excle表，里面含有大量的性能分析图表。但是针对大于10M的文件处理可能会出现问题。


- 网址：https://developer.ibm.com/articles/au-nmon_analyser/
- 下载地址：https://www.ibm.com/developerworks/community/wikis/form/anonymous/api/wiki/61ad9cf2-c6a3-4d2c-b779-61ff0266d32a/page/b7fc61a1-eef9-4756-8028-6e687997f176/attachment/ead4752f-8c08-4893-8946-d18911082f3d/media/nmon_analyser_v60.zip


### 2.3.2 NMONVisualizer

NMONVisualizer is a Java GUI tool for analyzing nmon system files from both AIX and Linux. It also parses IOStat files, IBM verbose GC logs, Windows Perfmon & ESXTop CSV data and JSON data.

不但可以作为nmon数据的GUI显示工具，还可以支持iostat等。


- GitHub：https://github.com/nmonvisualizer/nmonvisualizer
- 网址：http://nmonvisualizer.github.io/nmonvisualizer/index.html
- 下载地址：https://bintray.com/nmonvisualizer/NMONVisualizer/download_file?file_path=NMONVisualizer_2019-04-06.jar
