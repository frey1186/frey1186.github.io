---
layout: post
title: MySQL8-InnoDB的BufferPool
date: 2022-04-08 15:41
tags: mysql innodb
categories: public
---

本文记录一些MySQL8 学习的一些笔记，主要来自MySQL 8.0 Reference Manual，以及一些其他文章和自己的思考，可能不对，有错的地方回头在改吧。

Buffer Pool 是 InnoDB 内存数据结构中最重要的一块，它的作用是缓存数据库和索引的数据。我们知道InnoDB 中操作的最小单元是页，数据库的页与操作系统页的大小是不同的，InnoDB 中默认是16k，操作系统一般是4k，这些都是可以调整的，但是一般不会去调整它。

那么 Buffer Pool 就是由N多数据库的页来组成的。比如默认启动参数启动后，BufferPool的大小是128MB，默认16K的页，那么它就存在了128M/16K=8192个页，用这些页来缓存表和索引。需要调整的时候配置innodb_buffer_pool_size参数即可。

知道了BufferPool的作用，再来考虑几个问题：

## 1. 页在 BufferPool 中是怎么组织的，或者说数据库的进程怎么去操作这些页来缓存表和索引的？

文档上说是用链表来实现的，就是把这些页穿成一串，每次数据库需要访问某页的时候，就从头开始搜索，如果找到该页，就读取；最终还是找不到，就去存储上取，大概思路就是这样。

这些页应该有一定的顺序，就是采用内存数据结构里最常见的 LRU （least recently used），感觉挺拗口的，实际上就是把刚访问过的数据放到最前面，其他的页依次向后排，最后一名直接淘汰。

但是 InnoDB 这么高级的数据库怎么能直接使用这种最常见的算法呢，必须要变化一下：

-   把这个 LRU 链表分成2段，分别命名为 新子列（前5/8） 和 旧子列（后3/8），每次搜索数据还是从前往后；
-   找到某页后，把该页放到最前面；
-   如果没找到，从磁盘取，取来之后不直接放到最前面，而是放在旧子列的最前面（默认后3/8的地方），每次从磁盘取得时候不是只取1页，可能取好多页。如果某页被读取，那么再放到最前面去。
-   链表中的其他页，依次往后排，最后一名出局。

这就是 BufferPool 里的 LRU 算法(https://dev.mysql.com/doc/refman/8.0/en/innodb-buffer-pool.html)。 这样做的好处，我觉得1是可以预读一些页，没用的页会很快的被排除出去，2是真正常用的页会被放在前面的子列表中。

![](/images/2022-04-08-MySQL8-InnoDB的BufferPool/innodb-buffer-pool-list.png)


## 2. 现在的服务器内存越来越大， BufferPool 越大越好吗？

理论上来说是的，能缓存的东西越多，肯定比从磁盘或者存储上取数据要快的多。 但是也有个问题，我们这个 LRU 链表一直被访问和修改啥的，要是并发高的情况下，肯定是有点问题的。 如果把 BufferPool 分成好几个相对独立的空间，每个空间都有一条 LRU 链表，是不是可以增加并发，提高性能。InnoDB 提供了一个参数叫 innodb_buffer_pool_instances 可以将 BufferPool 分成多个实例，要求每个instances大于1G。 另外，BufferPool 必须是 innodb_buffer_pool_chunk_size * innodb_buffer_pool_instances的整数倍，如果不是系统直接调整为整数倍。

- [innodb_buffer_pool_instances](https://dev.mysql.com/doc/refman/8.0/en/innodb-parameters.html#sysvar_innodb_buffer_pool_instances)

## 3. 为啥是3/8的地方分开两个子列表？

估计是拍脑袋的一个值，作为业界这么牛逼数据库肯定是可以调整的，看这参数innodb_old_blocks_pct。

想一下，如果执行了一个 select * from t 类的语句，是不是需要把该表所有所在的页都从磁盘中读到BufferPool中来，而且每个页会被移动到 LRU最前端一次，但是以后这些数据可能再也不用了，那是不是很扯淡。 

如果我们加一个参数，让新页在加入到LRU链表的时候，被访问的时候先别着急移动到最前面，一定时间段后，如果还被访问再移动。是不是就能解决这种全表扫描一次以后再不访问的场景了。可以看看innodb_old_blocks_time参数。


- [innodb_old_blocks_pct](https://dev.mysql.com/doc/refman/8.0/en/innodb-parameters.html#sysvar_innodb_old_blocks_pct)
- [innodb_old_blocks_time](https://dev.mysql.com/doc/refman/8.0/en/innodb-parameters.html#sysvar_innodb_old_blocks_time)


## 4. 预读可以提高性能，BufferPool的预读机制

预读提高性能，大家都这么说。 BufferPool 有两种预读机制：

（1）发现访问的一段连续的页，都同属于一个extent，那么我为啥不直接把下一个extent也一下子读进来；对应参数innodb_read_ahead_threshold参数，默认56，取值0~64；

（2）发现一个extent里面的N个页已经被访问了，那我也把下一个extent读进来吧。 对应参数 innodb_random_read_ahead = ON；
 
- [innodb_read_ahead_threshold](https://dev.mysql.com/doc/refman/8.0/en/innodb-parameters.html#sysvar_innodb_read_ahead_threshold)
- [ innodb_random_read_ahead](https://dev.mysql.com/doc/refman/8.0/en/innodb-parameters.html#sysvar_innodb_random_read_ahead)



## 5. 还有个重要的问题，如果 BufferPool 里的页被修改了，那如何刷新到磁盘上？

MySQL 采用的是多线程机制，牛逼的数据库肯定是有专用的线程来做这个事情的，它就是页面清理线程，用innodb_page_cleaners参数可以调整清理线程的数量(默认4）。

[达到什么条件开始清理？](https://dev.mysql.com/doc/refman/8.0/en/innodb-buffer-pool-flushing.html)（1）如果被修改的页（脏页）数量达到的一定的程度，肯定需要清理一下；（2）每间隔一定的时间应该清理一次；等等

那清理的时候有没有必要将同一个extent的其他页也刷新了？innodb_flush_neighbors

每次刷脏页的时候是整个LRU都刷还是只刷一部分？innodb_lru_scan_depth

这些参数真是好麻烦，其实InnoDB提供了自适应的刷新算法。


[innodb_page_cleaners](https://dev.mysql.com/doc/refman/8.0/en/innodb-parameters.html#sysvar_innodb_page_cleaners)


## 6. 如果重启，BufferPool里的数据会被清除吗？

肯定会的。但是BufferPool里的LRU是有用的，不然数据库启动之后还需要预热很长时间才能恢复之前的状态。InnoDB 可以保存 BufferPool 里的一部分页到一个特定文件上，重启之后直接加载进来。 当然直接保存页数据太占用空间，InnoDB会保存该页所在表空间ID和页ID，这样就不会占用太多的空间。
保存和恢复 BufferPool的操作比较多，参考下面的连接：
https://dev.mysql.com/doc/refman/8.0/en/innodb-preload-buffer-pool.html


- [innodb_buffer_pool_dump_pct](https://dev.mysql.com/doc/refman/8.0/en/innodb-parameters.html#sysvar_innodb_buffer_pool_dump_pct)
- [innodb_buffer_pool_filename](https://dev.mysql.com/doc/refman/8.0/en/innodb-parameters.html#sysvar_innodb_buffer_pool_filename)

## 7. 如果数据库宕了，会生成core文件

core文件会记录mysql进程状态和内存映像，要是把 BufferPool 也放进去，可能是个很大的文件。 调整innodb_buffer_pool_in_core_file参数，不再将 BufferPool 的内容放到core文件中。


## 其他

- [InnoDB Startup Options and System Variables](https://dev.mysql.com/doc/refman/8.0/en/innodb-parameters.html#sysvar_innodb_buffer_pool_size)