---
layout: post
title: MySQL8-InnoDB-内存结构-ChangeBuffer
date: 2022-04-15 09:39
tags: mysql8 innodb
categories: public
---



有了 Buffer Pool来缓存了页，数据库要读一个页，先到 Buffer Pool 找，要是没找到就到磁盘上去取，读操作不更新实际的页，所以只能老老实实到磁盘上去找了。那么对于 insert、update 或者 delete 操作，同样先到 buffer pool 里查看一番，没有就到磁盘里找，这里有没有能够优化的地方？



有，一般表更新完成之后，需要同时进行表上索引的更新，这两个操作类似于事务，必须都完成才行。 表上的更新用的 buffer pool缓存，如果没有就到磁盘上的 B+tree上更新。对于索引，就没有表更新那么幸运，随机IO会更多，特别针对insert操作来说。所以InnoDB 就搞了一块缓存空间来优化这部分操作，那就是 change buffer了。



其实最早的时候只有 insert buffer，只对插入操作进行缓存，我觉得很可能是因为 update 操作需要先删除再插入，delete操作也不是那么普遍，所以总体来说大部分还是在做 insert的操作，优化insert操作就差不多啦。那么，change buffer 可以缓存哪些操作，通过 innodb_change_buffering的取值就知道啦：



- all :  默认值，包含 **buffer inserts, delete-marking 和 purges**

- none： 不缓存，也就是不使用 changebuffer

- inserts： 缓存插入操作

- deletes：缓存删除操作，这个删除操作指的是 为数据添加删除标记的操作，不是真正的删除操作

- changes：就是常规说的 update 操作，先delete后再insert

- purges：真正的物理删除操作



有以下几个注意点：



- change buffer 缓存的是上面说到的几个操作，应该不是页。

- **change buffer 针对的是 secondary indexes** 的更新，而不是表的更新；优化的是索引更新的性能，不会提升其他性能。

- 这个非聚簇索引（ secondary indexes ）必须是非唯一值的（如果该列要求是唯一的，那么每次插入的时候就需要验证唯一性，势必要把磁盘里的该列数据全部比对一遍，那缓存这个操作就没有任何意义了）。



使用了 change buffer 后 插入操作的过程：



- 在 buffer pool 中查找插入数据所要写入的页，如果找到就更新该页，找不到就到磁盘上找（好像会涉及到redo log的操作，将来再说）；

- 在 buffer pool 中查找写 secondary indexes 所在页，找到就更新该页；

- 如果没有，就把这个操作记录在 changebuffer 中，等待时机如果该页被缓存进了 buffer pool，那就把 change buffer 里缓存的操作与该页进行合并；

- change buffer 和 buffer pool 的数据会有相应的刷新机制刷新到磁盘；



涉及的参数就两个：



- **innodb_change_buffering**：默认all；

- **innodb_change_buffer_max_size**：控制 change buffer 在 buffer pool 中的比例，默认25%，最大50%，5.6版本引入该参数。



change buffer 不适用的场景：



- 没有secondary indexes的场景；

- secondary indexes 列的值是唯一的；

- 插入后立即读的场景（插入之后马上就读，缓存插入操作还有啥意义，还是操作了磁盘）；

- 使用了SSD硬盘（SSD硬盘的随机读和顺序读性能差距不大，使用 change buffer 可能没有什么提升）；

- 数据集足够小，可以直接缓存到 buffer pool 中（就没必要在用 change buffer了）；



参考链接：



- https://www.shuzhiduo.com/A/gGdXjK3ZJ4/

- https://www.shuzhiduo.com/A/A7zgyrQn54/

- https://dev.mysql.com/doc/refman/8.0/en/innodb-change-buffer.html#innodb-change-buffer-configuration

- https://dev.mysql.com/doc/refman/8.0/en/faqs-innodb-change-buffer.html

- https://dev.mysql.com/doc/refman/8.0/en/innodb-parameters.html#sysvar_innodb_change_buffer_max_size

- https://dev.mysql.com/doc/refman/8.0/en/innodb-parameters.html#sysvar_innodb_change_buffering

