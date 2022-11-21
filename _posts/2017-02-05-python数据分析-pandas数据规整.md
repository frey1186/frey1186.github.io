---

layout: post
title: python数据分析-Pandas数据规整学习笔记
date: 2017-02-05 14:00
author: felo
tags: pandas
---


摘要：
Pandas数据规整相关的学习笔记，记录了《利用python进行数据分析》学习过程和笔记。

**清理、转换、合并、重塑**

# 1 合并数据集

pandas有一些内置的合并数据集方法：
- pandas.merge：根据一个或多个键将多个DataFrame连接起来，类似数据库连接；
- pandas.concat：可以沿着一个轴将多个对象堆叠起来；
- 实例方法combine_first可以将重复数据编制在一起，用以填充另一个对象的缺失值。

## 1.1 数据库风格的DataFrame合并

数据库合并（merge）或连接（join）运行将一个或多个键将行链接起来。来个例子：

```python
In [1]: import pandas as pd

In [2]: from pandas import Series,DataFrame

In [3]: df1 = DataFrame({'key':list('bbacaab'),'data1':range(7)})

In [4]: df2 = DataFrame({'key':list('abd'),'data2':range(3)})

In [5]: df1
Out[5]:
   data1 key
0      0   b
1      1   b
2      2   a
3      3   c
4      4   a
5      5   a
6      6   b

In [6]: df2
Out[6]:
   data2 key
0      0   a
1      1   b
2      2   d

# merge 合并数据集，相同列的共同值。
In [7]: pd.merge(df1, df2)    #不指定列名，默认会选择列名相同的key列。
Out[7]:
   data1 key  data2
0      0   b      1
1      1   b      1
2      6   b      1
3      2   a      0
4      4   a      0
5      5   a      0

In [8]: pd.merge(df1, df2, on='key') # 指定列名
Out[8]:
   data1 key  data2
0      0   b      1
1      1   b      1
2      6   b      1
3      2   a      0
4      4   a      0
5      5   a      0

# 可以将不同列名进行链接。

In [9]: df3 = DataFrame({'lkey':list('bbacaab'),'data1':range(7)})

In [10]: df4 = DataFrame({'rkey':list('abd'),'data2':range(3)})

In [11]: pd.merge(df3,df4,left_on='lkey',right_on='rkey')
Out[11]:
   data1 lkey  data2 rkey
0      0    b      1    b
1      1    b      1    b
2      6    b      1    b
3      2    a      0    a
4      4    a      0    a
5      5    a      0    a

# 默认inner，通过how可以指定outer
In [12]: pd.merge(df1,df2,how='outer')
Out[12]:
   data1 key  data2
0    0.0   b    1.0
1    1.0   b    1.0
2    6.0   b    1.0
3    2.0   a    0.0
4    4.0   a    0.0
5    5.0   a    0.0
6    3.0   c    NaN
7    NaN   d    2.0

In [13]: pd.merge(df1,df2,how='left')
Out[13]:
   data1 key  data2
0      0   b    1.0
1      1   b    1.0
2      2   a    0.0
3      3   c    NaN
4      4   a    0.0
5      5   a    0.0
6      6   b    1.0

In [14]: pd.merge(df1,df2,how='right',on='key')
Out[14]:
   data1 key  data2
0    0.0   b      1
1    1.0   b      1
2    6.0   b      1
3    2.0   a      0
4    4.0   a      0
5    5.0   a      0
6    NaN   d      2

# 多个键 合并

In [15]: left = DataFrame({'key1':['foo','foo','bar'],'key2':['one','two','one']
    ...: ,'lval':[1,2,3]})

In [16]: right = DataFrame({'key1':['foo','foo','bar','bar'],'key2':['one','one'
    ...: ,'one','two'],'rval':[4,5,6,7]})

In [17]: pd.merge(left,right,on=['key1','key2'],how='outer')
Out[17]:
  key1 key2  lval  rval
0  foo  one   1.0   4.0
1  foo  one   1.0   5.0
2  foo  two   2.0   NaN
3  bar  one   3.0   6.0
4  bar  two   NaN   7.0

# 如果使用的on选项后，还有重复列名，怎么办？
# merge有一个suffixes选项，可以处理重复列名

In [18]: pd.merge(left,right,on='key1')
Out[18]:
  key1 key2_x  lval key2_y  rval
0  foo    one     1    one     4
1  foo    one     1    one     5
2  foo    two     2    one     4
3  foo    two     2    one     5
4  bar    one     3    one     6
5  bar    one     3    two     7

In [19]: pd.merge(left,right,on='key1',suffixes=('_left','_right'))
Out[19]:
  key1 key2_left  lval key2_right  rval
0  foo       one     1        one     4
1  foo       one     1        one     5
2  foo       two     2        one     4
3  foo       two     2        one     5
4  bar       one     3        one     6
5  bar       one     3        two     7

```

merge选项：

![](/images/python数据分析/pandas_merge_opt1.png)

![](/images/python数据分析/pandas_merge_opt2.png)


## 1.2 索引上的合并

传入left_index=True或者right_index=True，可以将索引作为链接键使用。

```python
In [20]: left1 = DataFrame({'key':list('abaabc'),'value':range(6)})

In [21]: left2 = DataFrame({'group_val':[3.5,7]},index=['a','b'])

In [22]: left1
Out[22]:
  key  value
0   a      0
1   b      1
2   a      2
3   a      3
4   b      4
5   c      5

In [23]: left2
Out[23]:
   group_val
a        3.5
b        7.0

# 将右DataFrame的index作为链接键；
In [24]: pd.merge(left1, left2 ,left_on='key', right_index=True)
Out[24]:
  key  value  group_val
0   a      0        3.5
2   a      2        3.5
3   a      3        3.5
1   b      1        7.0
4   b      4        7.0

In [25]: pd.merge(left1, left2 ,left_on='key', right_index=True, how='outer')
Out[25]:
  key  value  group_val
0   a      0        3.5
2   a      2        3.5
3   a      3        3.5
1   b      1        7.0
4   b      4        7.0
5   c      5        NaN

# 对于层次化索引，比较复杂
In [28]: lefth = DataFrame({'key1':['Ohio','Ohio','Ohio','Nevada','Nevada'],'key
    ...: 2':[2000,2001,2002,2001,2002],'data':np.arange(5.)})

In [29]: righth = DataFrame(np.arange(12).reshape(6,2),index=[['Nevada','Nevada'
    ...: ,'Ohio','Ohio','Ohio','Ohio'],[2001,2000,2000,2000,2001,2002]],columns=
    ...: ['event1','event2'])

In [30]: lefth
Out[30]:
   data    key1  key2
0   0.0    Ohio  2000
1   1.0    Ohio  2001
2   2.0    Ohio  2002
3   3.0  Nevada  2001
4   4.0  Nevada  2002

In [31]: righth
Out[31]:
             event1  event2
Nevada 2001       0       1
       2000       2       3
Ohio   2000       4       5
       2000       6       7
       2001       8       9
       2002      10      11

# 使用列表的形式，指明多个列作为合并键
In [32]: pd.merge(lefth, righth, left_on=['key1','key2'],right_index=True)
Out[32]:
   data    key1  key2  event1  event2
0   0.0    Ohio  2000       4       5
0   0.0    Ohio  2000       6       7
1   1.0    Ohio  2001       8       9
2   2.0    Ohio  2002      10      11
3   3.0  Nevada  2001       0       1

In [33]: pd.merge(lefth, righth, left_on=['key1','key2'],right_index=True, how='
    ...: outer')
Out[33]:
   data    key1    key2  event1  event2
0   0.0    Ohio  2000.0     4.0     5.0
0   0.0    Ohio  2000.0     6.0     7.0
1   1.0    Ohio  2001.0     8.0     9.0
2   2.0    Ohio  2002.0    10.0    11.0
3   3.0  Nevada  2001.0     0.0     1.0
4   4.0  Nevada  2002.0     NaN     NaN
4   NaN  Nevada  2000.0     2.0     3.0

In [34]: left2 = DataFrame([[1,2],[3,4],[5,6]],index=['a','c','e'],columns=['Ohi
    ...: o','Nevada'])

In [35]: right2 = DataFrame([[7,8],[9,10],[11,12],[13,14]],index=list('bcde'),co
    ...: lumns=['Missouri','Alabama'])

In [36]: left2
Out[36]:
   Ohio  Nevada
a     1       2
c     3       4
e     5       6

In [37]: right2
Out[37]:
   Missouri  Alabama
b         7        8
c         9       10
d        11       12
e        13       14

# 同时根据两边索引合并
In [38]: pd.merge(left2, right2, how='outer', left_index=True, right_index=True)
    ...:
Out[38]:
   Ohio  Nevada  Missouri  Alabama
a   1.0     2.0       NaN      NaN
b   NaN     NaN       7.0      8.0
c   3.0     4.0       9.0     10.0
d   NaN     NaN      11.0     12.0
e   5.0     6.0      13.0     14.0
```

DataFrame还有join方法，更好的合并索引。

```python
In [39]: left2.join(right2, how='outer')
Out[39]:
   Ohio  Nevada  Missouri  Alabama
a   1.0     2.0       NaN      NaN
b   NaN     NaN       7.0      8.0
c   3.0     4.0       9.0     10.0
d   NaN     NaN      11.0     12.0
e   5.0     6.0      13.0     14.0
In [44]: right1
Out[44]:
   group_val
a        3.5
b        7.0

In [45]: left1
Out[45]:
  key  value
0   a      0
1   b      1
2   a      2
3   a      3
4   b      4
5   c      5

# left1 使用key来合并，right1使用索引。
In [46]: left1.join(right1, on='key')
Out[46]:
  key  value  group_val
0   a      0        3.5
1   b      1        7.0
2   a      2        3.5
3   a      3        3.5
4   b      4        7.0
5   c      5        NaN

# 对于简单的索引合并，可以在join传入一个DataFrame组。

In [47]: another = DataFrame([[7,8],[9,10],[11,12],[16,17]],index=list('acef'),c
    ...: olumns=['NewYork','Oregon'])

In [48]: left2.join([right2, another])  # 传入list
Out[48]:
   Ohio  Nevada  Missouri  Alabama  NewYork  Oregon
a     1       2       NaN      NaN        7       8
c     3       4       9.0     10.0        9      10
e     5       6      13.0     14.0       11      12
In [50]: left2.join([right2, another],how='outer')
Out[50]:
   Ohio  Nevada  Missouri  Alabama  NewYork  Oregon
a   1.0     2.0       NaN      NaN      7.0     8.0
b   NaN     NaN       7.0      8.0      NaN     NaN
c   3.0     4.0       9.0     10.0      9.0    10.0
d   NaN     NaN      11.0     12.0      NaN     NaN
e   5.0     6.0      13.0     14.0     11.0    12.0
f   NaN     NaN       NaN      NaN     16.0    17.0
```

concat函数也能实现类似功能，后面介绍。

## 1.3 轴向连接

这是另一种连接，也叫作：连接、绑定或堆叠。

```python
# numpy的函数：concatenation
In [51]: arr = np.arange(12).reshape(3,4)

In [52]: np.concatenate([arr,arr],axis=1)
Out[52]:
array([[ 0,  1,  2,  3,  0,  1,  2,  3],
       [ 4,  5,  6,  7,  4,  5,  6,  7],
       [ 8,  9, 10, 11,  8,  9, 10, 11]])

In [53]: np.concatenate([arr,arr],axis=0)
Out[53]:
array([[ 0,  1,  2,  3],
       [ 4,  5,  6,  7],
       [ 8,  9, 10, 11],
       [ 0,  1,  2,  3],
       [ 4,  5,  6,  7],
       [ 8,  9, 10, 11]])

```

对于pandas也能推广，

```python
In [54]: s1 = Series([0,1],index=list('ab'))

In [55]: s2 = Series([2,3,4],index=list('cde'))

In [56]: s3 = Series([5,6],index=list('fg'))

In [57]: pd.concat([s1,s2,s3])
Out[57]:
a    0
b    1
c    2
d    3
e    4
f    5
g    6
dtype: int64

# 做一个DataFrame出来。
In [58]: pd.concat([s1,s2,s3],axis=1)
Out[58]:
     0    1    2
a  0.0  NaN  NaN
b  1.0  NaN  NaN
c  NaN  2.0  NaN
d  NaN  3.0  NaN
e  NaN  4.0  NaN
f  NaN  NaN  5.0
g  NaN  NaN  6.0


# 使用inner选项，求并集
In [59]: s4 = pd.concat([s1*5,s3])

In [60]: s4
Out[60]:
a    0
b    5
f    5
g    6
dtype: int64

In [61]: pd.concat([s1,s4],axis=1)
Out[61]:
     0  1
a  0.0  0
b  1.0  5
f  NaN  5
g  NaN  6

In [62]: pd.concat([s1,s4],axis=1,join='inner')
Out[62]:
   0  1
a  0  0
b  1  5


# 指定求那些索引的并集
In [63]: pd.concat([s1,s4],axis=1,join_axes=[list('acbe')])
Out[63]:
     0    1
a  0.0  0.0
c  NaN  NaN
b  1.0  5.0
e  NaN  NaN

In [64]: pd.concat([s1,s4],axis=1,join_axes=[list('acbef')])
Out[64]:
     0    1
a  0.0  0.0
c  NaN  NaN
b  1.0  5.0
e  NaN  NaN
f  NaN  5.0

# 用keys创建一个自己的层次化索引
In [65]: result = pd.concat([s1,s2,s3],keys=['one','two','three'])

In [66]: result
Out[66]:
one    a    0
       b    1
two    c    2
       d    3
       e    4
three  f    5
       g    6
dtype: int64

# 在axis=1轴上连接的话，keys就成了列
In [70]: result = pd.concat([s1,s2,s3],keys=['one','two','three'],axis=1)

In [71]: result
Out[71]:
   one  two  three
a  0.0  NaN    NaN
b  1.0  NaN    NaN
c  NaN  2.0    NaN
d  NaN  3.0    NaN
e  NaN  4.0    NaN
f  NaN  NaN    5.0
g  NaN  NaN    6.0
```

同样的逻辑，对DataFrame也是一样，

```python
In [72]: df1 = DataFrame(np.arange(6).reshape(3,2),index=list('abc'),columns=['o
    ...: ne','two'])

In [73]: df2 = DataFrame(np.arange(4).reshape(2,2),index=list('ac'),columns=['th
    ...: ree','four'])

In [74]: pd.concat([df1,df2],axis=1,keys=['level1','level2'])
Out[74]:
  level1     level2     
     one two  three four
a      0   1    0.0  1.0
b      2   3    NaN  NaN
c      4   5    2.0  3.0

In [75]: pd.concat([df1,df2],axis=1)
Out[75]:
   one  two  three  four
a    0    1    0.0   1.0
b    2    3    NaN   NaN
c    4    5    2.0   3.0

In [76]: pd.concat([df1,df2])
Out[76]:
   four  one  three  two
a   NaN  0.0    NaN  1.0
b   NaN  2.0    NaN  3.0
c   NaN  4.0    NaN  5.0
a   1.0  NaN    0.0  NaN
c   3.0  NaN    2.0  NaN


# 还可以传入字典
In [77]: pd.concat({'level1':df1,'level2':df2},axis=1)
Out[77]:
  level1     level2     
     one two  three four
a      0   1    0.0  1.0
b      2   3    NaN  NaN
c      4   5    2.0  3.0

# 没用的索引怎么处理？
In [78]: df3 = DataFrame(np.random.randn(3,4),columns=list('abcd'))

In [79]: df4 = DataFrame(np.random.randn(2,3),columns=list('bda'))

  ## 产生新的一列索引，顺序从0开始
In [80]: pd.concat([df3,df4],ignore_index=True)
Out[80]:
          a         b         c         d
0  0.322805 -1.495024  0.971860 -0.904791
1  0.332766 -2.320841 -0.903456  0.026713
2 -0.163670  0.387144 -0.746927 -0.360291
3 -0.074411 -0.557447       NaN  0.704929
4  2.673221 -1.143143       NaN  0.592930
```

![](/images/python数据分析/pandas_concat_opt.png)

## 1.4 合并重叠数据

合并重叠数据不能使用merge和concat来实现，使用np.where函数。

```python
In [81]: a = Series([np.nan,2.5,np.nan,3.5,4.5,np.nan],index=list('fedcba'))

In [85]: b = Series([0,1,2,3,4,np.nan],index=list('fedcba'))

In [86]: a
Out[86]:
f    NaN
e    2.5
d    NaN
c    3.5
b    4.5
a    NaN
dtype: float64

In [87]: b
Out[87]:
f    0.0
e    1.0
d    2.0
c    3.0
b    4.0
a    NaN
dtype: float64

# 实现如果a为空，就是用b
In [88]: np.where(pd.isnull(a), b, a)
Out[88]: array([ 0. ,  2.5,  2. ,  3.5,  4.5,  nan])

# 相同的目标
In [95]: a.combine_first(b)
Out[95]:
f    0.0
e    2.5
d    2.0
c    3.5
b    4.5
a    NaN
dtype: float64

```

针对DataFrame：

```python
In [96]: df1 = DataFrame({'a':[1,np.nan,5,np.nan],'b':[np.nan,2,np.nan,6],'c':ra
    ...: nge(2,18,4)})

In [97]: df2 = DataFrame({'a':[5,4,np.nan,3,7],'b':[np.nan,3,4,6,8]})

In [98]: df1.combine_first(df2)
Out[98]:
     a    b     c
0  1.0  NaN   2.0
1  4.0  2.0   6.0
2  5.0  4.0  10.0
3  3.0  6.0  14.0
4  7.0  8.0   NaN
```



# 2 重塑和轴向旋转

# 2.1 重塑层次化索引

针对DataFrame，有stack和unstack。stack将数据的列“旋转”为行，unstack反之。

```python
In [6]: data = DataFrame(np.arange(6).reshape(2,3),index=pd.Index(['Ohio','Color
   ...: ado'], name='state'),columns=pd.Index(['one','two','three'],name='number
   ...: '))

In [7]: data
Out[7]:
number    one  two  three
state                    
Ohio        0    1      2
Colorado    3    4      5

In [8]: data.stack()  # 把列转化为行，即形成一个层次化索引的Series
Out[8]:
state     number
Ohio      one       0
          two       1
          three     2
Colorado  one       3
          two       4
          three     5
dtype: int64

In [9]: data.stack().unstack()  # 把层次化索引的Series转化为一个普通的DataFrame
Out[9]:
number    one  two  three
state                    
Ohio        0    1      2
Colorado    3    4      5
In [10]: data.stack().unstack('number')
Out[10]:
number    one  two  three
state                    
Ohio        0    1      2
Colorado    3    4      5

In [11]: data.stack().unstack(1)
Out[11]:
number    one  two  three
state                    
Ohio        0    1      2
Colorado    3    4      5

In [12]: data.stack().unstack(0)
Out[12]:
state   Ohio  Colorado
number                
one        0         3
two        1         4
three      2         5

In [13]: data.stack().unstack('state')  # 选择指定的列，进行旋转
Out[13]:
state   Ohio  Colorado
number                
one        0         3
two        1         4
three      2         5

```

对于Series也是一样，

```python
In [14]: s1 = Series([0,1,2,3],index=list('abcd'))

In [15]: s2 = Series([4,5,6],index=list('cde'))

In [16]: data2 = pd.concat([s1,s2],keys=['one','two'])

In [17]: data2
Out[17]:
one  a    0
     b    1
     c    2
     d    3
two  c    4
     d    5
     e    6
dtype: int64

In [18]: data2.unstack()
Out[18]:
       a    b    c    d    e
one  0.0  1.0  2.0  3.0  NaN
two  NaN  NaN  4.0  5.0  6.0

In [19]: data2.unstack().stack()  # 默认丢弃nan值
Out[19]:
one  a    0.0
     b    1.0
     c    2.0
     d    3.0
two  c    4.0
     d    5.0
     e    6.0
dtype: float64

In [20]: data2.unstack().stack(dropna=False) # 不丢弃nan值
Out[20]:
one  a    0.0
     b    1.0
     c    2.0
     d    3.0
     e    NaN
two  a    NaN
     b    NaN
     c    4.0
     d    5.0
     e    6.0
dtype: float64
```



## 2.2 将“长格式”转化为“宽格式”

时间序列的通常以“长格式”或“堆栈”格式存放在数据库或者CSV中。

```python
In [28]: df = pd.DataFrame({'A' : ['one', 'one', 'two', 'three'] * 3,
    ...: 'B' : ['A', 'B', 'C'] * 4,'C' : ['foo', 'foo', 'foo', 'bar', 'bar', 'ba
    ...: r'] * 2,
    ...: 'D' : np.random.randn(12),'E' : np.random.randn(12)})

In [29]: df
Out[29]:
        A  B    C         D         E
0     one  A  foo -1.130142 -0.800142
1     one  B  foo  1.453914 -1.344615
2     two  C  foo  0.452666  0.103939
3   three  A  bar  0.053393  0.284834
4     one  B  bar -0.435699  0.885828
5     one  C  bar  0.492411 -1.280743
6     two  A  foo -1.819792 -1.654636
7   three  B  foo  0.364982  1.654728
8     one  C  foo -1.205436  0.712150
9     one  A  bar  2.696329  1.357930
10    two  B  bar -0.561867  1.326672
11  three  C  bar  0.782410 -0.600689

# 这样就是df表中以D作为数值域，A,B为行，C为列的数据视图。

In [30]: pd.pivot_table(df, values='D', index=['A', 'B'], columns=['C'])
Out[30]:
C             bar       foo
A     B                    
one   A  2.696329 -1.130142
      B -0.435699  1.453914
      C  0.492411 -1.205436
three A  0.053393       NaN
      B       NaN  0.364982
      C  0.782410       NaN
two   A       NaN -1.819792
      B -0.561867       NaN
      C       NaN  0.452666
```


# 3 数据转换

前面两部分说的都是数据的重排，还有一类操作就是过滤、清理和转换。

## 3.1 移除重复数据


duplicated方法返回一个bool型Series，判断行是否为重复行。
drop_duplicates方法：返回一个删除了重复行的DataFrame

```python
In [31]: data = DataFrame({'k1':['one']*3+['two']*4,'k2':[1,1,2,3,3,4,4]})

In [32]: data
Out[32]:
    k1  k2
0  one   1
1  one   1
2  one   2
3  two   3
4  two   3
5  two   4
6  two   4

In [33]: data.duplicated()
Out[33]:
0    False
1     True
2    False
3    False
4     True
5    False
6     True
dtype: bool

In [34]: data.duplicated('k2')  # 按照列进行判断
Out[34]:
0    False
1     True
2    False
3    False
4     True
5    False
6     True
dtype: bool

In [35]: data.drop_duplicates
Out[35]:
<bound method DataFrame.drop_duplicates of     k1  k2
0  one   1
1  one   1
2  one   2
3  two   3
4  two   3
5  two   4
6  two   4>

In [36]: data.drop_duplicates()  # 返回一个新的去重后的对象
Out[36]:
    k1  k2
0  one   1
2  one   2
3  two   3
5  two   4

In [37]: data  # 原对象不变
Out[37]:
    k1  k2
0  one   1
1  one   1
2  one   2
3  two   3
4  two   3
5  two   4
6  two   4

# 默认保留的是第一个重复值
In [41]: data.drop_duplicates(['k1','k2'])  #
Out[41]:
    k1  k2  v1
0  one   1   0
2  one   2   2
3  two   3   3
5  two   4   5

In [42]: data.drop_duplicates(['k1','k2'],take_last=True)
/Users/yangfeilong/anaconda/bin/ipython:1: FutureWarning: the take_last=True keyword is deprecated, use keep='last' instead
  #!/bin/bash /Users/yangfeilong/anaconda/bin/python.app
Out[42]:
    k1  k2  v1
1  one   1   1
2  one   2   2
4  two   3   4
6  two   4   6

# 也可以指定保留最后一个值
In [43]: data.drop_duplicates(['k1','k2'],keep='last')
Out[43]:
    k1  k2  v1
1  one   1   1
2  one   2   2
4  two   3   4
6  two   4   6

In [44]: data.drop_duplicates(['k1','k2'],keep='first')
Out[44]:
    k1  k2  v1
0  one   1   0
2  one   2   2
3  two   3   3
5  two   4   5
```

## 3.2 利用函数或映射进行数据转换

映射可以是一个字典，key为源，value为目标。
如何转换呢？DataFrame通过apply或者applymap，Series通过map函数进行。

```python
In [45]: data = DataFrame({'food':['bacon','pulled pork','bacon','Pastrami','cor
    ...: ned beef','Bacon','pastrami','honey ham','nova lox'],'ounces':[4,3,12,6
    ...: ,7.5,8,3,5,6]})

In [46]: data
Out[46]:
          food  ounces
0        bacon     4.0
1  pulled pork     3.0
2        bacon    12.0
3     Pastrami     6.0
4  corned beef     7.5
5        Bacon     8.0
6     pastrami     3.0
7    honey ham     5.0
8     nova lox     6.0

In [47]: meat_to_animal = {'bacon':'pig','pulled pork':'pig','pastrami':'cow','c
    ...: orned beef':'cow','honey ham':'pig','nova lox':'salmon'}

In [49]: data['food']
Out[49]:
0          bacon
1    pulled pork
2          bacon
3       Pastrami
4    corned beef
5          Bacon
6       pastrami
7      honey ham
8       nova lox
Name: food, dtype: object

# 在data中food列，有些存在大写，所以需要处理一下。
In [50]: data['food'].map(str.lower).map(meat_to_animal)
Out[50]:
0       pig
1       pig
2       pig
3       cow
4       cow
5       pig
6       cow
7       pig
8    salmon
Name: food, dtype: object


# 通过字典进行映射
In [51]: data['animal']=data['food'].map(str.lower).map(meat_to_animal)

In [52]: data
Out[52]:
          food  ounces  animal
0        bacon     4.0     pig
1  pulled pork     3.0     pig
2        bacon    12.0     pig
3     Pastrami     6.0     cow
4  corned beef     7.5     cow
5        Bacon     8.0     pig
6     pastrami     3.0     cow
7    honey ham     5.0     pig
8     nova lox     6.0  salmon


#通过函数进行映射
In [53]: data['animal']=data['food'].map(lambda x:meat_to_animal[(x.lower())])

In [54]: data
Out[54]:
          food  ounces  animal
0        bacon     4.0     pig
1  pulled pork     3.0     pig
2        bacon    12.0     pig
3     Pastrami     6.0     cow
4  corned beef     7.5     cow
5        Bacon     8.0     pig
6     pastrami     3.0     cow
7    honey ham     5.0     pig
8     nova lox     6.0  salmon
```

## 3.3 替换值

fillna是填充nan值，可以看成是替换值的一种特殊情况。
replace方法提供一个简单的替换值得方法。

```python
In [55]: data = Series([1,-999,2,-999,-1000,3])

In [56]: data
Out[56]:
0       1
1    -999
2       2
3    -999
4   -1000
5       3
dtype: int64

In [57]: data.replace(-999,np.nan)
Out[57]:
0       1.0
1       NaN
2       2.0
3       NaN
4   -1000.0
5       3.0
dtype: float64

In [58]: data.replace([-999,-1000],np.nan) # 列表 + 标量
Out[58]:
0    1.0
1    NaN
2    2.0
3    NaN
4    NaN
5    3.0
dtype: float64

In [59]: data.replace([-999,-1000],[np.nan,0])  # 两个列表
Out[59]:
0    1.0
1    NaN
2    2.0
3    NaN
4    0.0
5    3.0
dtype: float64

In [60]: data.replace({-999:np.nan,-1000:0})  # 字典形式
Out[60]:
0    1.0
1    NaN
2    2.0
3    NaN
4    0.0
5    3.0
dtype: float64

```

## 3.4 重命名轴索引

```python
# 修改源数据
In [62]: data
Out[62]:
0       1
1    -999
2       2
3    -999
4   -1000
5       3
dtype: int64

In [63]: data.index = range(2,8)

In [64]: data
Out[64]:
2       1
3    -999
4       2
5    -999
6   -1000
7       3
dtype: int64

In [65]: data.index.map(lambda x:x+100)
Out[65]: array([102, 103, 104, 105, 106, 107])

In [67]: data.index = data.index.map(lambda x:x+100)

In [68]: data
Out[68]:
102       1
103    -999
104       2
105    -999
106   -1000
107       3
dtype: int64

# 创建一个新数据，使用rename
In [73]: data2 = DataFrame(np.arange(12).reshape(3,4),columns=list('abcd'),index
    ...: =range(3))

In [74]: data2
Out[74]:
   a  b   c   d
0  0  1   2   3
1  4  5   6   7
2  8  9  10  11
In [77]: data2.rename(index={0:100})
Out[77]:
     a  b   c   d
100  0  1   2   3
1    4  5   6   7
2    8  9  10  11

In [78]: data2.rename(index={0:100},columns={'a':'ff'})
Out[78]:
     ff  b   c   d
100   0  1   2   3
1     4  5   6   7
2     8  9  10  11
```


## 3.5 离散化和面元划分

连续数据常常需要被拆分为离散数据。这就需要用cut函数。

```python
In [79]: ages = range(100)

In [80]: bins = [18,25,35,60,100]

In [81]: pd.cut(ages,bins)
Out[81]:
[NaN, NaN, NaN, NaN, NaN, ..., (60, 100], (60, 100], (60, 100], (60, 100], (60, 100]]
Length: 100
Categories (4, object): [(18, 25] < (25, 35] < (35, 60] < (60, 100]]

In [82]: cuts = pd.cut(ages,bins)

In [83]: cuts[45]
Out[83]: '(35, 60]'

In [85]: cuts.dtype
Out[85]: category
```

这时，cut返回的是一个category对象，

```python
In [86]: cuts.labels
/Users/yangfeilong/anaconda/bin/ipython:1: FutureWarning: 'labels' is deprecated. Use 'codes' instead
  #!/bin/bash /Users/yangfeilong/anaconda/bin/python.app
Out[86]:
array([-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
       -1, -1,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1,  1,  1,  1,  1,
        1,  1,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,
        2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  3,  3,  3,  3,  3,  3,  3,
        3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,
        3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3], dtype=int8)

In [87]: cuts.levels
/Users/yangfeilong/anaconda/bin/ipython:1: FutureWarning: Accessing 'levels' is deprecated, use 'categories'
  #!/bin/bash /Users/yangfeilong/anaconda/bin/python.app
Out[87]: Index([u'(18, 25]', u'(25, 35]', u'(35, 60]', u'(60, 100]'], dtype='object')

In [88]: pd.value_counts(cuts) #查看每个种类的数量
Out[88]:
(60, 100]    39
(35, 60]     25
(25, 35]     10
(18, 25]      7
dtype: int64

# 使用right=False可以修改开端和闭端

In [89]: cuts = pd.cut(ages,bins,right=False)

In [90]: cuts
Out[90]:
[NaN, NaN, NaN, NaN, NaN, ..., [60, 100), [60, 100), [60, 100), [60, 100), [60, 100)]
Length: 100
Categories (4, object): [[18, 25) < [25, 35) < [35, 60) < [60, 100)]

In [91]: cuts = pd.cut(ages,bins,right=False,labels=list('abcd'))

In [92]: cuts
Out[92]:
[NaN, NaN, NaN, NaN, NaN, ..., d, d, d, d, d]
Length: 100
Categories (4, object): [a < b < c < d]

# 如果cut传入的是数字n，那么就会均分成n份。
In [94]: pd.cut(ages,5)
Out[94]:
[(-0.099, 19.8], (-0.099, 19.8], (-0.099, 19.8], (-0.099, 19.8], (-0.099, 19.8], ..., (79.2, 99], (79.2, 99], (79.2, 99], (79.2, 99], (79.2, 99]]
Length: 100
Categories (5, object): [(-0.099, 19.8] < (19.8, 39.6] < (39.6, 59.4] < (59.4, 79.2] < (79.2, 99]]

# qcut使用样本分位数进行划分，比cut更平均，获得大小基本相同的面元
In [95]: pd.qcut(ages,5)
Out[95]:
[[0, 19.8], [0, 19.8], [0, 19.8], [0, 19.8], [0, 19.8], ..., (79.2, 99], (79.2, 99], (79.2, 99], (79.2, 99], (79.2, 99]]
Length: 100
Categories (5, object): [[0, 19.8] < (19.8, 39.6] < (39.6, 59.4] < (59.4, 79.2] < (79.2, 99]]
In [96]: pd.value_counts(pd.qcut(ages,5))
Out[96]:
(79.2, 99]      20
(59.4, 79.2]    20
(39.6, 59.4]    20
(19.8, 39.6]    20
[0, 19.8]       20
dtype: int64

In [98]: ages = np.random.randn(1000)

In [99]: pd.value_counts(pd.qcut(ages,5))
Out[99]:
(0.883, 3.534]      200
(0.25, 0.883]       200
(-0.266, 0.25]      200
(-0.806, -0.266]    200
[-3.172, -0.806]    200
dtype: int64

In [100]: pd.value_counts(pd.cut(ages,5))
Out[100]:
(-0.489, 0.852]     481
(-1.831, -0.489]    283
(0.852, 2.193]      198
(-3.179, -1.831]     23
(2.193, 3.534]       15
dtype: int64


```

## 3.6 检测和过滤异常值

只看个例子：把绝对值大于3的值都替换为`3`或`-3`。


```python
In [101]: data = DataFrame(np.random.randn(1000,4))

In [102]: data
Out[102]:
            0         1         2         3
0    0.746898 -0.657217  0.358517  1.075503
1   -0.821582  1.408816  0.937318 -0.548889
2   -0.527847  0.749256 -0.524283 -0.977338
3    0.800118 -0.544609  0.481839  0.555546
...
996 -0.081920  0.100507 -0.431551 -1.832261
997 -1.069475  0.205978  0.918592  0.881498
998  1.749007  2.658384 -1.079657 -0.023890
999  1.488167 -0.061146  0.006189  0.070564

[1000 rows x 4 columns]

In [103]: data.describe()
Out[103]:
                 0            1            2            3
count  1000.000000  1000.000000  1000.000000  1000.000000
mean     -0.018474     0.030781     0.025966     0.041950
std       1.020634     0.982547     1.010164     0.948116
min      -3.150278    -3.422772    -3.406069    -2.575391
25%      -0.719646    -0.621461    -0.644949    -0.572558
50%      -0.021287     0.043128     0.027890     0.050492
75%       0.701195     0.711455     0.678644     0.665413
max       3.270054     2.983500     3.323021     2.925822


In [105]: data[(np.abs(data) > 3).any(1)]
Out[105]:
            0         1         2         3
16   1.450842  2.222636 -3.289273  1.265199
353 -3.067571  0.490152  0.536051  1.252143
531  1.518928  0.289636  3.323021 -0.695272
688  1.776682 -0.799736 -3.406069  0.632751
702  0.807953 -0.674675 -3.045511 -0.267613
704 -0.469205 -3.422772 -2.669146 -0.712407
772 -0.861015 -0.573432  3.012727  0.325476
808  3.270054 -0.035521  0.061092  1.263363
812 -3.150278 -0.734308  1.376565  0.671424

In [108]: data[np.abs(data) > 3] = 100

In [110]: data.describe()
Out[110]:
                 0            1            2            3
count  1000.000000  1000.000000  1000.000000  1000.000000
mean      0.284474     0.134204     0.529371     0.041950
std       5.564261     3.308565     7.123116     0.948116
min      -2.746446    -2.983108    -2.710984    -2.575391
25%      -0.714890    -0.619551    -0.635457    -0.572558
50%      -0.018859     0.048775     0.036321     0.050492
75%       0.710050     0.712375     0.686314     0.665413
max     100.000000   100.000000   100.000000     2.925822

In [111]: data[np.abs(data) > 3] = np.sign(data) * 3

In [113]: data.describe()
Out[113]:
                 0            1            2            3
count  1000.000000  1000.000000  1000.000000  1000.000000
mean     -0.006526     0.037204     0.044371     0.041950
std       1.019295     0.980940     1.006138     0.948116
min      -2.746446    -2.983108    -2.710984    -2.575391
25%      -0.714890    -0.619551    -0.635457    -0.572558
50%      -0.018859     0.048775     0.036321     0.050492
75%       0.710050     0.712375     0.686314     0.665413
max       3.000000     3.000000     3.000000     2.925822

```


## 3.7 排列和随机采样

```python
# 随机重排序
In [114]: df = DataFrame(np.arange(20).reshape(5,4))

In [115]: df.ix[np.random.permutation(5)]
Out[115]:
    0   1   2   3
0   0   1   2   3
4  16  17  18  19
1   4   5   6   7
2   8   9  10  11
3  12  13  14  15

# 获取随机前三行
In [116]: df.ix[np.random.permutation(len(df))[:3]]
Out[116]:
    0   1   2   3
0   0   1   2   3
2   8   9  10  11
4  16  17  18  19

# 随机获取10，每个值随机取自bag
In [118]: bag = np.array([5,7,-1,4,6])

In [119]: bag.take(np.random.randint(0,len(bag),size=10))
Out[119]: array([ 7,  7,  7,  5,  7,  6,  4, -1,  6,  4])
```

## 3.8 计算标量/哑变量

还有一种常用的转换方式是：将分类变量转换为哑变量矩阵或指标矩阵。

```python
# 比较复杂，其实就是用1和0填充一个矩阵，说明元素在一个Series中的位置。
In [120]: s1 = Series(list('bbacab'))

In [121]: pd.get_dummies(s1)
Out[121]:
     a    b    c
0  0.0  1.0  0.0
1  0.0  1.0  0.0
2  1.0  0.0  0.0
3  0.0  0.0  1.0
4  1.0  0.0  0.0
5  0.0  1.0  0.0

```

结合cut和get_dummies函数可以来做一些统计有用的事情：

```python
In [122]: values = np.random.rand(10)

In [123]: values
Out[123]:
array([ 0.96294606,  0.15142481,  0.38260636,  0.01174038,  0.44699216,
        0.3726047 ,  0.50965999,  0.61532174,  0.27740518,  0.28994142])

In [126]: bins = [0,0.2,0.4,0.6,0.8,1.]

In [127]: pd.cut(values,bins)
Out[127]:
[(0.8, 1], (0, 0.2], (0.2, 0.4], (0, 0.2], (0.4, 0.6], (0.2, 0.4], (0.4, 0.6], (0.6, 0.8], (0.2, 0.4], (0.2, 0.4]]
Categories (5, object): [(0, 0.2] < (0.2, 0.4] < (0.4, 0.6] < (0.6, 0.8] < (0.8, 1]]

In [128]: pd.get_dummies(pd.cut(values, bins)) # 查看每个类型的指标矩阵
Out[128]:
   (0, 0.2]  (0.2, 0.4]  (0.4, 0.6]  (0.6, 0.8]  (0.8, 1]
0       0.0         0.0         0.0         0.0       1.0
1       1.0         0.0         0.0         0.0       0.0
2       0.0         1.0         0.0         0.0       0.0
3       1.0         0.0         0.0         0.0       0.0
4       0.0         0.0         1.0         0.0       0.0
5       0.0         1.0         0.0         0.0       0.0
6       0.0         0.0         1.0         0.0       0.0
7       0.0         0.0         0.0         1.0       0.0
8       0.0         1.0         0.0         0.0       0.0
9       0.0         1.0         0.0         0.0       0.0

In [129]: a =pd.get_dummies(pd.cut(values, bins))

In [131]: a.sum(axis=0)  # 统计一下每个类型的数量
Out[131]:
(0, 0.2]      2.0
(0.2, 0.4]    4.0
(0.4, 0.6]    2.0
(0.6, 0.8]    1.0
(0.8, 1]      1.0
dtype: float64
```



# 4 字符串操作

## 4.1 字符串对象方法

大部分的字符处理，内置方法已经够用了。结合“split”和“strip”、‘+’、“join”等方法。

```python
In [1]: a = 'a,b, guide'

In [2]: a.split(',')
Out[2]: ['a', 'b', ' guide']

In [4]: [x.strip() for x in a.split(',')]
Out[4]: ['a', 'b', 'guide']

In [5]: first,second,third = [x.strip() for x in a.split(',')]

In [6]: first
Out[6]: 'a'

In [7]: second
Out[7]: 'b'

In [8]: third
Out[8]: 'guide'

In [9]: first + third
Out[9]: 'aguide'

In [10]: first.join(third)
Out[10]: 'gauaiadae'

In [12]: ''.join([third,first])
Out[12]: 'guidea'

In [13]: 'a' in a
Out[13]: True

In [14]: a.find(':')
Out[14]: -1

In [15]: a.index(':')
---------------------------------------------------------------------------
ValueError                                Traceback (most recent call last)
<ipython-input-15-e54927e30300> in <module>()
----> 1 a.index(':')

ValueError: substring not found

In [16]: a.count(',')
Out[16]: 2
```

字符串内置方法：

![](/images/python数据分析/python_inner_str_func1.png)

![](/images/python数据分析/python_inner_str_func2.png)


## 4.2 正则表达式

复习一下正则表达式

```python
In [17]: import re

In [18]: text = 'foo    bar\t baz  \tqux'

In [19]: re.split('\s+', text)  # \s+  表示一个或多个空格
Out[19]: ['foo', 'bar', 'baz', 'qux']

In [20]: regex = re.compile('\s+')  # 创建regex对象，多次复用，减少大量CPU时间

In [21]: regex.split(text)
Out[21]: ['foo', 'bar', 'baz', 'qux']

In [22]: regex.findall(text)  # 所有text中匹配到的对象
Out[22]: ['    ', '\t ', '  \t']

# match ：从头开始匹配
# search：第一个
# findall：找到所有

In [23]: text = '''
    ...: Dave dave@google.com
    ...: Steve steve@gmail.com
    ...: Rob rob@gmail.com
    ...: Ryan ryan@yahoo.com
    ...: '''

In [24]: pattern = r'[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}'
# flags=re.IGNORECASE 表示忽略大小写
In [25]: regex = re.compile(pattern, flags=re.IGNORECASE)

In [26]: regex.findall(text)
Out[26]: ['dave@google.com', 'steve@gmail.com', 'rob@gmail.com', 'ryan@yahoo.com']


In [27]: regex.search(text)
Out[27]: <_sre.SRE_Match at 0x104227b28>

In [29]: regex.search(text).group(0)
Out[29]: 'dave@google.com'

# sub 替换
In [30]: regex.sub('HAHAHA', text)
Out[30]: '\nDave HAHAHA\nSteve HAHAHA\nRob HAHAHA\nRyan HAHAHA\n'

In [31]: print(regex.sub("HAHAHAAHA", text))

Dave HAHAHAAHA
Steve HAHAHAAHA
Rob HAHAHAAHA
Ryan HAHAHAAHA

# 分组
In [33]: pattern = r'([A-Z0-9._%+-]+)@([A-Z0-9.-]+)\.([A-Z]{2,4})'

In [34]: regex = re.compile(pattern, flags=re.IGNORECASE)

In [35]: m=regex.match('wesm@bright.net')

In [36]: m.groups()
Out[36]: ('wesm', 'bright', 'net')

In [37]: m.group(0)
Out[37]: 'wesm@bright.net'

In [38]: m.group(1)
Out[38]: 'wesm'

In [39]: m.group(2)
Out[39]: 'bright'

In [40]: m.group(3)
Out[40]: 'net'

# 返回一个大的列表
In [41]: regex.findall(text)
Out[41]:
[('dave', 'google', 'com'),
 ('steve', 'gmail', 'com'),
 ('rob', 'gmail', 'com'),
 ('ryan', 'yahoo', 'com')]

# 指定替换
 In [48]: regex.sub(r'Username:\1,Domain:\2,Suffix:\3',text)
 Out[48]: '\nDave Username:dave,Domain:google,Suffix:com\nSteve Username:steve,Domain:gmail,Suffix:com\nRob Username:rob,Domain:gmail,Suffix:com\nRyan Username:ryan,Domain:yahoo,Suffix:com\n'

```

![](/images/python数据分析/python_re_func.png)


## 4.3 pandas矢量化的字符串函数

```python
In [61]: data = {
    ...: 'Dave':'dave@google.com',
    ...: 'Steve':'steve@gmail.com',
    ...: 'Rob':'rob@gmail.com',
    ...: 'Ryan':'ryan@yahoo.com',
    ...: 'Wes':np.nan}

In [62]: data = Series(data)

In [63]: data
Out[63]:
Dave     dave@google.com
Rob        rob@gmail.com
Ryan      ryan@yahoo.com
Steve    steve@gmail.com
Wes                  NaN
dtype: object

In [64]: data.isnull()
Out[64]:
Dave     False
Rob      False
Ryan     False
Steve    False
Wes       True
dtype: bool

# 查看是否包含，返回一个bool Series
In [65]: data.str.contains('gmail')
Out[65]:
Dave     False
Rob       True
Ryan     False
Steve     True
Wes        NaN
dtype: object


In [66]: pattern
Out[66]: '([A-Z0-9._%+-]+)@([A-Z0-9.-]+)\\.([A-Z]{2,4})'
# 返回一个匹配好的Series
In [67]: data.str.findall(pattern, flags=re.IGNORECASE)
Out[67]:
Dave     [(dave, google, com)]
Rob        [(rob, gmail, com)]
Ryan      [(ryan, yahoo, com)]
Steve    [(steve, gmail, com)]
Wes                        NaN
dtype: object


In [68]: matches = data.str.match(pattern, flags=re.IGNORECASE)
/Users/yangfeilong/anaconda/bin/ipython:1: FutureWarning: In future versions of pandas, match will change to always return a bool indexer.
  #!/bin/bash /Users/yangfeilong/anaconda/bin/python.app

In [69]: matches
Out[69]:
Dave     (dave, google, com)
Rob        (rob, gmail, com)
Ryan      (ryan, yahoo, com)
Steve    (steve, gmail, com)
Wes                      NaN
dtype: object

In [70]: matches.str.get(1)
Out[70]:
Dave     google
Rob       gmail
Ryan      yahoo
Steve     gmail
Wes         NaN
dtype: object

In [71]: matches.str.get(2)
Out[71]:
Dave     com
Rob      com
Ryan     com
Steve    com
Wes      NaN
dtype: object

In [72]: matches.str[0]
Out[72]:
Dave      dave
Rob        rob
Ryan      ryan
Steve    steve
Wes        NaN
dtype: object

In [73]: data.str[:5]
Out[73]:
Dave     dave@
Rob      rob@g
Ryan     ryan@
Steve    steve
Wes        NaN
dtype: object


```

![](/images/python数据分析/矢量化字符串方法.png)



# 5 示例：usda食品数据库


























本部分完。
