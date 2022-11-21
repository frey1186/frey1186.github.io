







# 1. select基本用法

1. 显示表中有的列属性

```sql
HR@ test> desc EMPLOYEES                            
```

2. 基本select语句

```sql
HR@ test> select FIRST_NAME, SALARY from EMPLOYEES;
```

- select和from组成；
- 列之间用逗号分隔；

3. 查看四则运算后的列

```sql
HR@ test> select FIRST_NAME, SALARY, SALARY+100 from EMPLOYEES;
```

- 先乘除后加减

  ```sql
  HR@ test> select FIRST_NAME, SALARY, (SALARY+100)*12 from EMPLOYEES;   
  ```

4. null值：未定义的值，不是0，不是空格

```sql
HR@ test> select FIRST_NAME, SALARY, COMMISSION_PCT from EMPLOYEES;
```

- 必要的时候对空值进行转换；

5. 定义别名

```sql
#别名自动转化为大写
HR@ test> select FIRST_NAME as name, SALARY from EMPLOYEES;
#强制定义为小写
HR@ test> select FIRST_NAME as "name", SALARY from EMPLOYEES;
# as可以省略
HR@ test> select FIRST_NAME "name", SALARY from EMPLOYEES;
# 为长表达式定义别名
HR@ test> select FIRST_NAME, SALARY*12 as annual_sal from EMPLOYEES;
# 使用了如空格等特殊字符的别名，要用引号
HR@ test> select FIRST_NAME, SALARY*12 as "annual sal" from EMPLOYEES;
```

6. 连接列

```sql
HR@ test> select FIRST_NAME||EMAIL from employees;
# 将空格连接在两列之间
HR@ test> select FIRST_NAME||' '||EMAIL from employees;
# 或者
HR@ test> select FIRST_NAME||'@'||EMAIL from employees;
```

7. 去除重复列

```sql
HR@ test> select distinct EMPLOYEE_ID from employees;
```

# 2.select限制和排列数据

1. 简单过滤

```sql
HR@ test> select FIRST_NAME,SALARY from EMPLOYEES where SALARY>10000;
HR@ test> select FIRST_NAME,SALARY from EMPLOYEES where DEPARTMENT_ID=90;
# 字符串为条件的时候大小写敏感
HR@ test> select FIRST_NAME,SALARY from EMPLOYEES where LAST_NAME='Whalen';
# 日期做条件：格式敏感，要与系统日期格式一致
HR@ test> select FIRST_NAME,SALARY from EMPLOYEES where HIRE_DATE='14-JUN-05';
HR@ test> select FIRST_NAME,SALARY from EMPLOYEES where HIRE_DATE='14-jun-05';
# 查看系统日期格式
HR@ test> select sysdate from dual;
SYSDATE
---------
27-MAY-18
```

2. 复杂一点

```sql
HR@ test> select FIRST_NAME,SALARY from EMPLOYEES where SALARY>=4000 and SALARY<=5000;
```



# 3.sqlplus环境变量和命令

2018-7-30（任务8）

&的用法：替代变量，使用&或者&&

```sql
HR@ test> select &col1 from employees;
Enter value for col1: last_name
old   1: select &col1 from employees
new   1: select last_name from employees
```

```sql
HR@ test> select * from &tab;
Enter value for tab: departments
old   1: select * from &tab
new   1: select * from departments
```

```sql
HR@ test> select  last_name,salary from employees where last_name='&name';
Enter value for name: King
old   1: select  last_name,salary from employees where last_name='&name'
new   1: select  last_name,salary from employees where last_name='King'
```

```sql
HR@ test> select last_name,&col2 from employees order by &col2;
Enter value for col2: salary
Enter value for col2: salary
old   1: select last_name,&col2 from employees order by &col2
new   1: select last_name,salary from employees order by salary
```

```sql
双&&，直接将该变量定义环境变量
单&，每次需要输入
HR@ test> define col2=salary
HR@ test> undefine col2
```

verify变量

```sql
HR@ test> select last_name,&col2 from employees where rownum=1;
Enter value for col2: salary
old   1: select last_name,&col2 from employees where rownum=1  # 这两行是否显示
new   1: select last_name,salary from employees where rownum=1

LAST_NAME                     SALARY
------------------------- ----------
OConnell                        2600

Elapsed: 00:00:00.00
HR@ test>
HR@ test>
HR@ test> show verify
verify ON
HR@ test> set verify off
HR@ test> show verify
verify OFF
HR@ test> select last_name,&col2 from employees where rownum=1;
Enter value for col2: salary

LAST_NAME                     SALARY
------------------------- ----------
OConnell                        2600

Elapsed: 00:00:00.00

```

其他几个变量

```sql
# 行显示字符数量
HR@ test> show linesize
linesize 120
HR@ test> set linesize 200

# 分页数量
HR@ test> show pagesize
pagesize 200
HR@ test> set pagesize 50

# select语句后跟查询的时间，off关闭
HR@ test> show timing
timing ON
HR@ test> set timing off
HR@ test> set timing on

# 提示符，类shell中的$PS1
HR@ test> show sqlp
sqlprompt "_user@ _connect_identifier> "

# 每次取15行数据进行打印，最大5000
HR@ test> show arraysize
arraysize 15

# 查询的多少行，统计总数
HR@ test> show feedback
FEEDBACK ON for 6 or more rows
HR@ test> set feedback off
HR@ test> set feedback on

# 是否显示列头
HR@ test> show heading
heading ON

# 显示超长的列
HR@ test> show long
long 50000
```

col用法：修改显示的样式

```sql
# 格式化显示列的长度：10位
HR@ test> col last_name for a10
HR@ test> select last_name,salary from employees where rownum=1;

LAST_NAME      SALARY
---------- ----------
OConnell         2600

1 row selected.

Elapsed: 00:00:00.00
# 显示5位，用5个9
HR@ test> col salary for 99999;
HR@ test> select last_name,salary from employees where rownum=1;

LAST_NAME  SALARY
---------- ------
OConnell     2600

1 row selected.

Elapsed: 00:00:00.02

# col来重命名列
HR@ test> col last_name heading 'employee|name'
HR@ test> select last_name,salary from employees where rownum=1;

employee
name       SALARY
---------- ------
OConnell     2600

1 row selected.

Elapsed: 00:00:00.00

# 清除定义
HR@ test> col last_name
COLUMN   last_name ON
HEADING  'employee|name' headsep '|'
FORMAT   a10
HR@ test> col last_name clear


HR@ test> col salary justify left for l999,999.99
HR@ test> select last_name,salary from employees where rownum=1;

LAST_NAME                 SALARY
------------------------- ---------------------
OConnell                              $2,600.00

1 row selected.

Elapsed: 00:00:00.00

# 如果没有值 显示 no manager
HR@ test> col manager_id for 9999 null 'NO MANAGER'
HR@ test> select last_name,manager_id from employees;

LAST_NAME                 MANAGER_ID
------------------------- ----------
OConnell                         124
Grant                            124
Whalen                           101
Hartstein                        100
Fay                              201
Mavris                           101
Baer                             101
Higgins                          101
Gietz                            205
King                      NO MANAGER
Kochhar                          100
...

```

break

```sql
# 不显示重复值
HR@ test> break on manager_id
HR@ test> clear break
breaks cleared
```

run，list

```sql
# 缓冲区里的最后一条sql语句
HR@ test> l
  1* select last_name,manager_id from employees
HR@ test> list
  1* select last_name,manager_id from employees

# 使用run，r，/都可以执行缓冲区里的最后一条语句

HR@ test> a  where rownum=1
  1* select last_name,manager_id from employees where rownum=1
HR@ test> /

LAST_NAME                 MANAGER_ID
------------------------- ----------
OConnell                         124

1 row selected.

Elapsed: 00:00:00.00
HR@ test> save 1.sql
Created file 1.sql
HR@ test> get 1.sql
  1* select last_name,manager_id from employees where rownum=1
HR@ test> @1.sql

LAST_NAME                 MANAGER_ID
------------------------- ----------
OConnell                         124

1 row selected.

Elapsed: 00:00:00.00

```

spool：将输出保存到一个文件中

```sql
HR@ test> spool 1.txt
HR@ test> @
SP2-1506: START, @ or @@ command has no arguments
HR@ test> list
  1* select last_name,manager_id from employees where rownum=1
HR@ test> /

LAST_NAME                 MANAGER_ID
------------------------- ----------
OConnell                         124

1 row selected.

Elapsed: 00:00:00.00
HR@ test> spool off

```

操作系统命令

```sql
# host，！，ho可以直接运行操作系统命令
```

编辑：将最后一行放进vi编辑器

```sql
HR@ test> ed
Wrote file afiedt.buf

  1* select last_name,manager_id from employees where rownum=1

```

tti，bti 可以设置select语句的页眉和页脚。

