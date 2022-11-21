---
layout: post
title: logstash简单配置
date: 2018-06-21 12:00
author: felo
tags: logstash
categories: public
typora-root-url: ..
---

![](/images/logstash/arch.jpeg)



Logstash 是开源的服务器端数据处理管道，能够同时从多个来源采集数据，转换数据，然后将数据发送到您最喜欢的 “存储库” 中。（我们的存储库当然是 Elasticsearch。）

# 基本结构

![](https://www.elastic.co/guide/en/logstash/current/static/images/basic_logstash_pipeline.png)

- data source可以使文件、syslog等等
- logstash只是接受过滤和输出
- 输出可以是es、文件、redis等等



#  logstash 简单配置

服务器环境

```bash
[root@localhost ~]# cat /etc/redhat-release 
CentOS Linux release 7.4.1708 (Core) 
[root@localhost ~]# uname -a 
Linux localhost 3.10.0-693.el7.x86_64 #1 SMP Tue Aug 22 21:09:27 UTC 2017 x86_64 x86_64 x86_64 GNU/Linux
[root@localhost ~]# 
```

安装一个java,1.8以上

```bash
[root@localhost ~]# yum install java
[root@localhost logstash-6.3.0]# rpm -qa |grep java
javapackages-tools-3.4.1-11.el7.noarch
python-javapackages-3.4.1-11.el7.noarch
tzdata-java-2018e-3.el7.noarch
java-1.8.0-openjdk-headless-1.8.0.171-8.b10.el7_5.x86_64
java-1.8.0-openjdk-1.8.0.171-8.b10.el7_5.x86_64
```

下载logstash

```bash
[root@localhost ~]# wget https://artifacts.elastic.co/downloads/logstash/logstash-6.3.0.tar.gz
[root@localhost ~]# tar -xzvf logstash-6.3.0.tar.gz
# 执行文件
[root@localhost ~]# cd logstash-6.3.0
[root@localhost logstash-6.3.0]# bin/logstash
```

写一个配置文件

```bash
[root@localhost logstash-6.3.0]# cat my.conf 
input {
	# 从文件输入
	file {
		path => "/var/log/messages"
		type => "system"
		start_position => "beginning"
	}
	
	# 从syslog输入
	syslog {
		type => "localhost-syslog"
		port => 514
	}
}

# filter {
#	
# }

output {
    # 标准输出
	stdout { codec => rubydebug }
	# 输出到文件
	file {
 	  path => "/tmp/my2.log"
 	  # 自己修改格式
 	  #codec => line { format => "custom format: %{message}"}
 	}
}
[root@localhost logstash-6.3.0]# 

```

执行下面命令开始收集

```bash
[root@localhost logstash-6.3.0]# ./bin/logstash -f my.conf  
```

在syslog源端指定syslog发送目标

```bash
[root@localhost ~]# cat /etc/rsyslog.conf |grep 192.168.56
*.* @@192.168.56.154:514
[root@localhost ~]# systemctl restart rsyslog
# 或者
[root@localhost ~]# service rsyslog restart
```

# 参考

- [logstash输入插件](https://www.elastic.co/guide/en/logstash/current/input-plugins.html)

- [logstash实战input插件syslog](https://www.cnblogs.com/minseo/p/7062361.html)