---
layout: post
title: MySQL8-InnoDBinnodb_flush_log_at_trx_commit
date: 2022-05-16 15:44
tags: mysql innodb
categories: public
---



关于 global innodb_flush_log_at_trx_commit 参数：



### 准备表和存储过程



    create table test_load(

    a int,

    b char(80)

    );



    delimiter //

    create procedure p_load(count int  unsigned)

    begin

        declare s int unsigned default 1;

        declare c char(80) default repeat('a',80);

        while s <= count do

            insert into test_load select NULL,c;

            commit;

            set s = s+1;

        end while;

    end;

    //

    delimiter ;





### 修改 global innodb_flush_log_at_trx_commit 参数，看看情况如何



0 -- 不在commit的时候写入redo



1 -- commit的时候调用fsync写入文件 【默认参数】



2 -- commit的时候不用fsync，只写入缓存就不管了





    mysql> set global innodb_flush_log_at_trx_commit=0;

    Query OK, 0 rows affected (0.00 sec)



    mysql> call p_load(50000);

    Query OK, 0 rows affected (36.97 sec)



    mysql> set global innodb_flush_log_at_trx_commit=2;

    Query OK, 0 rows affected (0.00 sec)



    mysql> call p_load(50000);

    Query OK, 0 rows affected (39.05 sec)



    mysql> set global innodb_flush_log_at_trx_commit=1;

    Query OK, 0 rows affected (0.00 sec)



    mysql> call p_load(50000);

    Query OK, 0 rows affected (1 min 8.17 sec)











### 修改为全部插入后再commit，似乎也没有提升，不知道为啥？



    delimiter //

    create procedure p_load_2(count int  unsigned)

    begin

        declare s int unsigned default 1;

        declare c char(80) default repeat('a',80);

        while s <= count do

            insert into test_load select NULL,c;

            set s = s+1;

        end while;

        commit;

    end;

    //

    delimiter ;



    mysql> set global innodb_flush_log_at_trx_commit=1;

    Query OK, 0 rows affected (0.00 sec)



    mysql> call p_load_2(50000);

    Query OK, 0 rows affected (1 min 7.15 sec)



    mysql> call p_load_2(50000);

    Query OK, 0 rows affected (1 min 6.27 sec)



但是这么做的话，可以比较方便的回滚到最初状态
