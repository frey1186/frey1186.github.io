---

layout: post
title: python数据分析-Pandas入门学习笔记
date: 2017-02-04 21:33
author: felo
tags: pandas
---


摘要：
Pandas基础学习笔记，记录了《利用python进行数据分析》学习过程和笔记。




pandas是基于numpy创建，提供更高级的数据结构和操作工具，是一个不可获取的工具。

为了更好的阐述，约定如下：


```python
import pandas as pd
from pandas import Series,DataFrame
```

# 1 pandas数据结构
两个最重要的数据结构：Series和DataFrame，基本可以解决绝大部分问题。

## 1.1 Series
类似于一维数组的对象，由一组数据和一组索引组成。Series的表现形式一般为左边索引，
右边值。

```python
In [50]: obj = Series([4,7,-5,3])

In [51]: obj
Out[51]:
0    4
1    7
2   -5
3    3
dtype: int64

In [52]: obj.values
Out[52]: array([ 4,  7, -5,  3], dtype=int64)

In [53]: obj.index
Out[53]: RangeIndex(start=0, stop=4, step=1)
```
可以自定义索引：

```python
In [54]: obj2 = Series([4,7,-5,3],index=['d','b','a','c'])

In [55]: obj2
Out[55]:
d    4
b    7
a   -5
c    3
dtype: int64

In [56]: obj2.index
Out[56]: Index(['d', 'b', 'a', 'c'], dtype='object')
```
Series类似一个有序字典，可以进行查询和赋值等。

```python
In [5]: obj2['d']
Out[5]: 4

In [6]: obj2['d'] = 100

In [7]: obj2
Out[7]:
d    100
b      7
a     -5
c      3
dtype: int64

In [8]: obj2[['d','a']]
Out[8]:
d    100
a     -5
dtype: int64
```
同样可以对Series的值进行运算。

```python
In [9]: obj2 * 2
Out[9]:
d    200
b     14
a    -10
c      6
dtype: int64

In [10]: import numpy as np

In [11]: np.exp(obj2)
Out[11]:
d    2.688117e+43
b    1.096633e+03
a    6.737947e-03
c    2.008554e+01
dtype: float64
```
和字典一样的特性

```python
In [12]: 'a' in obj2
Out[12]: True

In [13]: 6 in obj2
Out[13]: False
```
可以通过字典直接来创建Series,字典的键就是Series的索引。

```python
In [14]: sdata = {'ohio':35000, 'Text':72134,'Uthch':5000}

In [15]: obj3 = Series(sdata)

In [16]: obj3
Out[16]:
Text     72134
Uthch     5000
ohio     35000
dtype: int64

# 在sdata中找不到的键值对，将使用NaN（Not a Number）来代替。
In [17]: obj4 = Series(sdata,index=['ohio','new_index'])

In [18]: obj4
Out[18]:
ohio         35000.0
new_index        NaN
dtype: float64

```
**pandas可以使用isnull和notnull检测是否缺失数据。**

```python
In [19]: obj3.isnull()
Out[19]:
Text     False
Uthch    False
ohio     False
dtype: bool

In [20]: obj4.notnull
Out[20]:
<bound method NDFrame.notnull of ohio         35000.0
new_index        NaN
dtype: float64>

In [21]: obj4.notnull()
Out[21]:
ohio          True
new_index    False
dtype: bool
In [22]: pd.isnull(obj4)
Out[22]:
ohio         False
new_index     True
dtype: bool
```
Series在算术运算中会自动对齐索引，并进行计算。

```python
In [24]: obj3 + obj4
Out[24]:
Text             NaN  #obj3
Uthch            NaN  #obj3
new_index        NaN  #obj4
ohio         70000.0
dtype: float64

```
Series还有一个name的属性，类似数据库表名。index也有一个name的属性，类似索引名字。

```python
In [27]: obj4.name

In [28]: obj4.name = "obj444"

In [29]: obj4
Out[29]:
ohio         35000.0
new_index        NaN
Name: obj444, dtype: float64

In [30]: obj4.index.name = 'state'

In [31]: obj4
Out[31]:
state
ohio         35000.0
new_index        NaN
Name: obj444, dtype: float64
```
可以通过赋值，就地就该index：

```python
In [39]: obj1 = Series([4,7,-5,3])

In [40]: obj1.index = ['Bob',"Steve","Jeff",'Ryan']

In [41]: obj1
Out[41]:
Bob      4
Steve    7
Jeff    -5
Ryan     3
dtype: int64
```
## 1.2 DataFrame

一个表格型数据结构，包含一组有序的列。典型的创建DataFrame如下：

```python
In [42]: data = {'state':['Ohio',"Ohio",'Ohio',"Nevada",'Nevada'],}

In [43]: data = {'state':['Ohio',"Ohio",'Ohio',"Nevada",'Nevada'],
    ...:          'year':[2000,2001,2002,2001,2002],
    ...:          'pop':[1.5,1.7,3.6,2.4,2.9]}

In [44]: frame = DataFrame(data)

In [45]: frame  #自动增加索引,列顺序是随机的。
Out[45]:
   pop   state  year
0  1.5    Ohio  2000
1  1.7    Ohio  2001
2  3.6    Ohio  2002
3  2.4  Nevada  2001
4  2.9  Nevada  2002
```
可以指定列进行创建：

```python
In [46]: DataFrame(data, columns=['year','state','pop'])
Out[46]:
   year   state  pop
0  2000    Ohio  1.5
1  2001    Ohio  1.7
2  2002    Ohio  3.6
3  2001  Nevada  2.4
4  2002  Nevada  2.9
In [47]: frame2 = DataFrame(data,columns=['year','state','pop','debt'],
    ...: index=['one','two','three','four','five'])

In [48]: frame2
Out[48]:
       year   state  pop debt
one    2000    Ohio  1.5  NaN
two    2001    Ohio  1.7  NaN
three  2002    Ohio  3.6  NaN
four   2001  Nevada  2.4  NaN
five   2002  Nevada  2.9  NaN
In [49]: frame2.columns
Out[49]: Index(['year', 'state', 'pop', 'debt'], dtype='object')
# 可以通过类似字典方式获取列数据，获取一列即为一个Series.
# 注意返回的是一个name被自动设置为state，索引与DataFrame相同。
In [50]: frame2['state']
Out[50]:
one        Ohio
two        Ohio
three      Ohio
four     Nevada
five     Nevada
Name: state, dtype: object

# 也可以获取行数据，通过ix
# 获取的内容与列类似
In [52]: frame2.ix['two']
Out[52]:
year     2001
state    Ohio
pop       1.7
debt      NaN
Name: two, dtype: object

# 可以给debt列赋值
In [53]: frame2['debt'] = 16.5  #可以是标量，自动全部填充

In [54]: frame2
Out[54]:
       year   state  pop  debt
one    2000    Ohio  1.5  16.5
two    2001    Ohio  1.7  16.5
three  2002    Ohio  3.6  16.5
four   2001  Nevada  2.4  16.5
five   2002  Nevada  2.9  16.5

In [55]: frame2['debt'] = np.arange(5.)  # 赋值长度必须与debt长度一直

In [56]: frame2
Out[56]:
       year   state  pop  debt
one    2000    Ohio  1.5   0.0
two    2001    Ohio  1.7   1.0
three  2002    Ohio  3.6   2.0
four   2001  Nevada  2.4   3.0
five   2002  Nevada  2.9   4.0

## 也可以用一个Series来赋值，缺失值NaN
In [59]: frame2['debt'] = Series([-1,-2,-4],index=['one','three','five'])

In [60]: frame2
Out[60]:
       year   state  pop  debt
one    2000    Ohio  1.5  -1.0
two    2001    Ohio  1.7   NaN
three  2002    Ohio  3.6  -2.0
four   2001  Nevada  2.4   NaN
five   2002  Nevada  2.9  -4.0

# 不存在列的赋值，会创建新列
In [61]: frame2['eastern'] = frame2.state == 'Ohio'

In [62]: frame2
Out[62]:
       year   state  pop  debt eastern
one    2000    Ohio  1.5  -1.0    True
two    2001    Ohio  1.7   NaN    True
three  2002    Ohio  3.6  -2.0    True
four   2001  Nevada  2.4   NaN   False
five   2002  Nevada  2.9  -4.0   False

# del 会删除列

In [63]: del frame2['eastern']

In [64]: frame2.columns
Out[64]: Index(['year', 'state', 'pop', 'debt'], dtype='object')

```
**注意：通过索引获取的数据，均为原始数据的视图，所有修改都会反应到源DataFrame上。
需要复制使用Series的copy方法。**

可以使用嵌套字典创建DataFrame。

```python
In [68]: pop = {'Nevada':{2001:2.4,2002:2.9},
    ...: 'Ohio':{2000:1.5,2001:1.7,2002:3.6}}

In [69]: frame3 = DataFrame(pop)

In [70]: frame3
Out[70]:
      Nevada  Ohio
2000     NaN   1.5
2001     2.4   1.7
2002     2.9   3.6

# 还可以转置
In [72]: frame3.T
Out[72]:
        2000  2001  2002
Nevada   NaN   2.4   2.9
Ohio     1.5   1.7   3.6

# 排序合并索引
In [73]: DataFrame(pop,index=[2001,2002,2003])
Out[73]:
      Nevada  Ohio
2001     2.4   1.7
2002     2.9   3.6
2003     NaN   NaN

In [75]: pdata = {'Ohio':frame3['Ohio'][:-1],'Nevada':frame3['Nevada'][:2]}

In [76]: DataFrame(pdata)
Out[76]:
      Nevada  Ohio
2000     NaN   1.5
2001     2.4   1.7

```
下面是所有DataFrame能接受的数据类型：

![](/images/2017-02-04-python数据分析-pandas入门/data_to_dataframe.PNG)



```python
In [78]: DataFrame(np.arange(10).reshape(2,5))
Out[78]:
   0  1  2  3  4
0  0  1  2  3  4
1  5  6  7  8  9
In [80]: frame3
Out[80]:
      Nevada  Ohio
2000     NaN   1.5
2001     2.4   1.7
2002     2.9   3.6

In [81]: frame3.name = 'states';frame3.index.name = 'year'

In [82]: frame3
Out[82]:
      Nevada  Ohio
year
2000     NaN   1.5
2001     2.4   1.7
2002     2.9   3.6

In [83]: frame3.columns.name = 'state'

In [84]: frame3
Out[84]:
state  Nevada  Ohio
year
2000      NaN   1.5
2001      2.4   1.7
2002      2.9   3.6

In [86]: frame3.values
Out[86]:
array([[ nan,  1.5],
       [ 2.4,  1.7],
       [ 2.9,  3.6]])

In [87]: frame2.values
Out[87]:
array([[2000, 'Ohio', 1.5, -1.0],
       [2001, 'Ohio', 1.7, nan],
       [2002, 'Ohio', 3.6, -2.0],
       [2001, 'Nevada', 2.4, nan],
       [2002, 'Nevada', 2.9, -4.0]], dtype=object)

```

## 1.3 索引

索引对象负责管理轴标签和其他元数据，没有指定的话会自动生成。一旦生成，索引对象不能修改。

```python
In [88]: obj = Series(range(3),index=['a','b','c'])

In [89]: obj.index
Out[89]: Index(['a', 'b', 'c'], dtype='object')

In [90]: index = obj.index

In [91]: index[1:]
Out[91]: Index(['b', 'c'], dtype='object')

In [92]: index[1] = 'd'
---------------------------------------------------------------------------
TypeError                                 Traceback (most recent call last)
<ipython-input-92-676fdeb26a68> in <module>()
----> 1 index[1] = 'd'

C:\Users\yangfl\Anaconda3\lib\site-packages\pandas\indexes\base.py
in __setitem__(self, key, value)
   1243
   1244     def __setitem__(self, key, value):
-> 1245         raise TypeError("Index does not support mutable operations")
   1246
   1247     def __getitem__(self, key):

TypeError: Index does not support mutable operations

```
因为不可修改，因此可以在多个数据结构中间传递index对象。


```python
In [94]: index = pd.Index(np.arange(3))

In [95]: obj2 = Series([-0.2,-1,2],index=index)

In [96]: obj2.index == index
Out[96]: array([ True,  True,  True], dtype=bool)
```

pandas中主要的index对象：


![](/images/2017-02-04-python数据分析-pandas入门/pandas_index.PNG)



index对象很像数组，也是一个固定的集合。

```python

In [97]: frame3
Out[97]:
state  Nevada  Ohio
year
2000      NaN   1.5
2001      2.4   1.7
2002      2.9   3.6

In [98]: 2001 in frame3.index
Out[98]: True

In [99]: 2003 in frame3.index
Out[99]: False

```
因此，索引也有自己的方法和属性：

![](/images/2017-02-04-python数据分析-pandas入门/pandas_index_method.PNG)


















# 2 基本功能

只是一些基本功能，更深奥的内容用到再摸索。

## 2.1 重新索引

reindex是pandas的重要方法，举个例子：

```python
In [101]: obj = Series([4,7,-5,3.4],index=['c','a','b','d'])

In [102]: obj
Out[102]:
c    4.0
a    7.0
b   -5.0
d    3.4
dtype: float64

In [103]: obj2 = obj.reindex(['a','b','c','d','e'])

In [104]: obj2
Out[104]:
a    7.0
b   -5.0
c    4.0
d    3.4
e    NaN
dtype: float64

# 缺失值可以自定义

In [105]: obj.reindex(['a','b','c','d','e'],fill_value=0)
Out[105]:
a    7.0
b   -5.0
c    4.0
d    3.4
e    0.0  #缺失值填充
dtype: float64


```
reindex的插值method选项：


参数|说明
-|-
ffill或pad | 前向填充值
bfill或backfill | 后向填充值




```python
In [106]: obj3 = Series(['blue','purple','yellow'],index=[0,2,4])

# 前向填充
In [107]: obj3.reindex(range(6),method='ffill')
Out[107]:
0      blue
1      blue
2    purple
3    purple
4    yellow
5    yellow
dtype: object

# 后向填充
In [109]: obj3.reindex(range(6),method='bfill')
Out[109]:
0      blue
1    purple
2    purple
3    yellow
4    yellow
5       NaN
dtype: object
```
针对DataFrame，可以修改行、列或两个都进行重新索引。

```python
In [111]: frame = DataFrame(np.arange(9).reshape(3,3), index=['a','b','c'],colmns=['Ohio','Texas','California'])

In [112]: frame
Out[112]:
   Ohio  Texas  California
a     0      1           2
b     3      4           5
c     6      7           8

In [113]: frame2 = frame.reindex(['a','b','c','d'])  # 默认行索引

In [115]: frame2
Out[115]:
   Ohio  Texas  California
a   0.0    1.0         2.0
b   3.0    4.0         5.0
c   6.0    7.0         8.0
d   NaN    NaN         NaN

In [116]: states = ['Texas','Utah','California']

In [117]: frame.reindex(columns=states)  #指定列索引
Out[117]:
   Texas  Utah  California
a      1   NaN           2
b      4   NaN           5
c      7   NaN           8

# 对行、列都进行重新索引，
# 并且进行插值，但是只能在0轴进行，即按行应用。
In [118]: frame.reindex(index=['a','b','c','d'],method='ffill',columns=states)
Out[118]:
   Texas  Utah  California
a      1   NaN           2
b      4   NaN           5
c      7   NaN           8
d      7   NaN           8

# 用ix更简洁。
In [119]: frame.ix[['a','b','c','d'],states]
Out[119]:
   Texas  Utah  California
a    1.0   NaN         2.0
b    4.0   NaN         5.0
c    7.0   NaN         8.0
d    NaN   NaN         NaN
```

reindex函数的参数

![](/images/2017-02-04-python数据分析-pandas入门/reindex_func.PNG)


## 2.2 丢弃指定轴上的项

丢弃项，只要一个索引或列表即可。drop方法会返回一个删除了指定值的新对象。

```python
In [120]: obj = Series(np.arange(5.),index=['a','b','c','d','e'])

In [121]: new_obj = obj.drop('c')

In [122]: new_obj
Out[122]:
a    0.0
b    1.0
d    3.0
e    4.0
dtype: float64

In [124]: obj.drop(['d','c'])
Out[124]:
a    0.0
b    1.0
e    4.0
dtype: float64

```
针对DataFrame,可以删除任意轴上的索引值。

```python
In [125]: data = DataFrame(np.arange(16).reshape(4,4),index=['Ohio','Colorado',
     ...: 'Utah','New York'],columns=['one','two','three','four'])

In [126]: data
Out[126]:
          one  two  three  four
Ohio        0    1      2     3
Colorado    4    5      6     7
Utah        8    9     10    11
New York   12   13     14    15

In [127]: data.drop(['Colorado','Ohio'])
Out[127]:
          one  two  three  four
Utah        8    9     10    11
New York   12   13     14    15

In [128]: data.drop(['two',],axis=1)
Out[128]:
          one  three  four
Ohio        0      2     3
Colorado    4      6     7
Utah        8     10    11
New York   12     14    15
```

## 2.3 索引、选取和过滤



```python
In [129]: obj = Series(np.arange(4.),index=['a','b','c','d'])

In [130]: obj['a']  #使用index索引
Out[130]: 0.0

In [131]: obj[0]    #使用序号来索引
Out[131]: 0.0

In [132]: obj[1]
Out[132]: 1.0

In [133]: obj
Out[133]:
a    0.0
b    1.0
c    2.0
d    3.0
dtype: float64

In [134]: obj[1:2]  # 使用序号切片
Out[134]:
b    1.0
dtype: float64

In [135]: obj[1:3]
Out[135]:
b    1.0
c    2.0
dtype: float64

In [136]: obj[obj<2]  # 使用值判断
Out[136]:
a    0.0
b    1.0
dtype: float64

In [137]: obj['b':'c']  # 使用索引切片，注意是两端包含的。
Out[137]:
b    1.0
c    2.0
dtype: float64

In [138]: obj['b':'c'] = 100  # 赋值

In [139]: obj
Out[139]:
a      0.0
b    100.0
c    100.0
d      3.0
dtype: float64

```
针对DataFrame,索引就是获取一个或多个列。
**使用列名：获取列
使用序号或bool值：获取行**

```python
In [140]: data
Out[140]:
          one  two  three  four
Ohio        0    1      2     3
Colorado    4    5      6     7
Utah        8    9     10    11
New York   12   13     14    15

In [141]:

In [141]: data['two']  # 获取第2列
Out[141]:
Ohio         1
Colorado     5
Utah         9
New York    13
Name: two, dtype: int32

In [142]: data[['two','one']]  # 按要求获取列
Out[142]:
          two  one
Ohio        1    0
Colorado    5    4
Utah        9    8
New York   13   12

In [143]: data[:2]  # 获取前面两行，使用数字序号获取的是行
Out[143]:
          one  two  three  four
Ohio        0    1      2     3
Colorado    4    5      6     7

In [144]: data[data['three']>5]  # 获取第三列大于5的行
Out[144]:
          one  two  three  four
Colorado    4    5      6     7
Utah        8    9     10    11
New York   12   13     14    15
```
DataFrame在语法上与ndarray是比较相似的。

```python
In [146]: data < 5
Out[146]:
            one    two  three   four
Ohio       True   True   True   True
Colorado   True  False  False  False
Utah      False  False  False  False
New York  False  False  False  False

In [147]: data[data<5] = 0

In [148]: data
Out[148]:
          one  two  three  four
Ohio        0    0      0     0
Colorado    0    5      6     7
Utah        8    9     10    11
New York   12   13     14    15

```
**索引字段ix：
可以通过Numpy的标记法以及轴标签从DataFrame中选取行和列的子集。
此外，ix得表述方式很简单**


```python
In [150]: data.ix['Colorado',['two','three']]
Out[150]:
two      5
three    6
Name: Colorado, dtype: int32

In [151]: data.ix[['Colorado','Utah'],[3,0,1]]
Out[151]:
          four  one  two
Colorado     7    0    5
Utah        11    8    9

In [152]: data.ix[2]
Out[152]:
one       8
two       9
three    10
four     11
Name: Utah, dtype: int32

In [153]: data.ix[:'Utah','two']
Out[153]:
Ohio        0
Colorado    5
Utah        9
Name: two, dtype: int32
```
DataFrame的索引选项

![](/images/2017-02-04-python数据分析-pandas入门/dataframe_index_opt.PNG)


![](/images/2017-02-04-python数据分析-pandas入门/dataframe_index_opt2.PNG)


## 2.4 算术运算和数据对齐

算术运算结果就是不同索引之间的并集，不存在的值之间运算结果用NaN表示。

```python
In [4]: s1 = Series([-2,-3,5,-1],index=list('abcd'))

In [5]: s2 = Series([9,2,5,1,5],index=list('badef'))

In [6]: s1 + s2
Out[6]:
a    0.0
b    6.0
c    NaN
d    4.0
e    NaN
f    NaN
dtype: float64

```
DataFrame也是一样，会同时发生在行和列上。


### 在算术方法中填充值


```python
In [7]: df1 = DataFrame(np.arange(12.).reshape(3,4),columns=list('abcd'))

In [8]: df2 = DataFrame(np.arange(20.).reshape(4,5),columns=list('abcde'))

In [9]: df1
Out[9]:
     a    b     c     d
0  0.0  1.0   2.0   3.0
1  4.0  5.0   6.0   7.0
2  8.0  9.0  10.0  11.0

In [10]: df2
Out[10]:
      a     b     c     d     e
0   0.0   1.0   2.0   3.0   4.0
1   5.0   6.0   7.0   8.0   9.0
2  10.0  11.0  12.0  13.0  14.0
3  15.0  16.0  17.0  18.0  19.0

In [11]: df1 + df2  # 不填充值
Out[11]:
      a     b     c     d   e
0   0.0   2.0   4.0   6.0 NaN
1   9.0  11.0  13.0  15.0 NaN
2  18.0  20.0  22.0  24.0 NaN
3   NaN   NaN   NaN   NaN NaN

In [12]: df1.add(df2, fill_value=0)  # 填充0
Out[12]:
      a     b     c     d     e
0   0.0   2.0   4.0   6.0   4.0
1   9.0  11.0  13.0  15.0   9.0
2  18.0  20.0  22.0  24.0  14.0
3  15.0  16.0  17.0  18.0  19.0

In [13]: df1.reindex(columns=df2.columns, method='ffill')
Out[13]:
     a    b     c     d   e
0  0.0  1.0   2.0   3.0 NaN
1  4.0  5.0   6.0   7.0 NaN
2  8.0  9.0  10.0  11.0 NaN

In [14]: df1.reindex(columns=df2.columns, fill_value=0)  # 重新索引的时候也可以填充。
Out[14]:
     a    b     c     d  e
0  0.0  1.0   2.0   3.0  0
1  4.0  5.0   6.0   7.0  0
2  8.0  9.0  10.0  11.0  0

```

可用的算术算法有：
- add：加法，
- sub：减法，
- div：除法
- mul：乘法

### DataFrame和Series之间的运算

采用广播的方式，就是会按照一定的规律作用到整个DataFrame之中。

```python
In [15]: frame = DataFrame(np.arange(12.).reshape(4,3),columns=list('bde'),index
    ...: =['Utah','Ohio','Texas','Oregon'])

In [16]: series = frame.ix[0]  # 获取第一行

In [17]: frame
Out[17]:
          b     d     e
Utah    0.0   1.0   2.0
Ohio    3.0   4.0   5.0
Texas   6.0   7.0   8.0
Oregon  9.0  10.0  11.0

In [18]: series
Out[18]:
b    0.0
d    1.0
e    2.0
Name: Utah, dtype: float64

In [19]: frame - series   # 自动广播到其他行
Out[19]:
          b    d    e
Utah    0.0  0.0  0.0
Ohio    3.0  3.0  3.0
Texas   6.0  6.0  6.0
Oregon  9.0  9.0  9.0

In [20]: series2 = Series(np.arange(3),index=list('bef'))

In [21]: series2
Out[21]:
b    0
e    1
f    2
dtype: int64

In [22]: frame + series2  # 没有的列使用NaN
Out[22]:
          b   d     e   f
Utah    0.0 NaN   3.0 NaN
Ohio    3.0 NaN   6.0 NaN
Texas   6.0 NaN   9.0 NaN
Oregon  9.0 NaN  12.0 NaN

In [23]: series3 = frame['d']   # 获取列

In [24]: frame.sub(series3, axis=0) #列相减，指定axis
Out[24]:
          b    d    e
Utah   -1.0  0.0  1.0
Ohio   -1.0  0.0  1.0
Texas  -1.0  0.0  1.0
Oregon -1.0  0.0  1.0

```

## 2.5 函数应用和映射

Numpy中的通用函数（ufunc）也可以作用于pandas的Series和DataFrame对象。

```python
In [31]: np.abs(frame)
Out[31]:
          b     d     e
Utah    0.0   1.0   2.0
Ohio    3.0   4.0   5.0
Texas   6.0   7.0   8.0
Oregon  9.0  10.0  11.0

In [32]: np.max(frame)
Out[32]:
b     9.0
d    10.0
e    11.0
dtype: float64

```
DataFrame有一个apply方法，可以接受自定义函数。

```python
In [33]: f = lambda x: np.max(x) - np.min(x)

In [34]: frame.apply(f)
Out[34]:
b    9.0
d    9.0
e    9.0
dtype: float64

In [35]: frame
Out[35]:
          b     d     e
Utah    0.0   1.0   2.0
Ohio    3.0   4.0   5.0
Texas   6.0   7.0   8.0
Oregon  9.0  10.0  11.0

In [36]: f = lambda x : np.exp2(x)

In [37]: frame.apply(f)
Out[37]:
            b       d       e
Utah      1.0     2.0     4.0
Ohio      8.0    16.0    32.0
Texas    64.0   128.0   256.0
Oregon  512.0  1024.0  2048.0

```
许多常用的方法，DataFrame已经实现，不需要使用apply方法自定义。

```python
In [38]: f = lambda x: Series([np.max(x),np.min(x)],index=['max','min'])

In [39]: frame.apply(f)
Out[39]:
       b     d     e
max  9.0  10.0  11.0
min  0.0   1.0   2.0

# 如果f函数是一个元素级别的函数，就使用applymap
In [40]: f = lambda x : '%.2f' % x

In [41]: frame.applymap(f)
Out[41]:
           b      d      e
Utah    0.00   1.00   2.00
Ohio    3.00   4.00   5.00
Texas   6.00   7.00   8.00
Oregon  9.00  10.00  11.00

# 同样对于Series就使用map，与DataFrame的applymap是对应的。
In [43]: series
Out[43]:
b    0.0
d    1.0
e    2.0
Name: Utah, dtype: float64

In [44]: series.map(f)
Out[44]:
b    0.00
d    1.00
e    2.00
Name: Utah, dtype: object


```

## 2.6 排序与排名

### 排序

排序可以使用：
- sort_index方法：按索引排序，
- sort_value方法（order方法）：按值排序，使用by参数


```python
In [45]: obj = Series(range(4),index=list('dbca'))

In [46]: obj
Out[46]:
d    0
b    1
c    2
a    3
dtype: int64

In [47]: obj.sort_index()
Out[47]:
a    3
b    1
c    2
d    0
dtype: int64

In [50]: frame
Out[50]:
          b     d     e
Utah    0.0   1.0   2.0
Ohio    3.0   4.0   5.0
Texas   6.0   7.0   8.0
Oregon  9.0  10.0  11.0

In [51]: frame.sort_index()
Out[51]:
          b     d     e
Ohio    3.0   4.0   5.0
Oregon  9.0  10.0  11.0
Texas   6.0   7.0   8.0
Utah    0.0   1.0   2.0

In [52]: frame.sort_index(axis=0)
Out[52]:
          b     d     e
Ohio    3.0   4.0   5.0
Oregon  9.0  10.0  11.0
Texas   6.0   7.0   8.0
Utah    0.0   1.0   2.0

In [53]: frame.sort_index(axis=1)
Out[53]:
          b     d     e
Utah    0.0   1.0   2.0
Ohio    3.0   4.0   5.0
Texas   6.0   7.0   8.0
Oregon  9.0  10.0  11.0

In [54]: frame.sort_index(axis=1, ascending=False) # 倒序
Out[54]:
           e     d    b
Utah     2.0   1.0  0.0
Ohio     5.0   4.0  3.0
Texas    8.0   7.0  6.0
Oregon  11.0  10.0  9.0

```
按值排序：

```python
In [55]: s1 = Series([3,-2,-7,4])

In [56]: s1.order()
/Users/yangfeilong/anaconda/bin/ipython:1: FutureWarning: order is deprecated, use sort_values(...)
  #!/bin/bash /Users/yangfeilong/anaconda/bin/python.app
Out[56]:
2   -7
1   -2
0    3
3    4
dtype: int64


In [58]: frame.sort_index(by='b')
/Users/yangfeilong/anaconda/bin/ipython:1: FutureWarning:
by argument to sort_index is deprecated, pls use .sort_values(by=...)
  #!/bin/bash /Users/yangfeilong/anaconda/bin/python.app
Out[58]:
          b     d     e
Utah    0.0   1.0   2.0
Ohio    3.0   4.0   5.0
Texas   6.0   7.0   8.0
Oregon  9.0  10.0  11.0

In [59]: frame.sort_values(by='b')
Out[59]:
          b     d     e
Utah    0.0   1.0   2.0
Ohio    3.0   4.0   5.0
Texas   6.0   7.0   8.0
Oregon  9.0  10.0  11.0


```

### 排名

rank方法，默认情况下为“相同的值分配一个平均排名”：

```python
In [60]: s1 = Series([7,-5,7,4,2,0,4])

In [61]: s1.rank()  # 可见0和2索引对应的值都是7，排名分别为6，7；因此取平均值6.5
Out[61]:
0    6.5
1    1.0
2    6.5
3    4.5
4    3.0
5    2.0
6    4.5
dtype: float64

```
当然，有很多方法可以“打破”这种平级关系。


![](/images/2017-02-04-python数据分析-pandas入门/data_rank1.png)



```python
In [62]: s1.rank(method='first')  # 按原始数据出现顺序排序
Out[62]:
0    6.0
1    1.0
2    7.0
3    4.0
4    3.0
5    2.0
6    5.0
dtype: float64

In [63]: s1.rank(ascending=False, method='max')  # 倒序，平级处理使用最大排名
Out[63]:
0    2.0
1    7.0
2    2.0
3    4.0
4    5.0
5    6.0
6    4.0
dtype: float64

```
DataFrame排名可以使用axis按行或按列进行排名。


## 2.7 带有重复值的轴索引

目前所有的例子中索引都是唯一的，而且如pandas中的许多函数（reindex）就要求索引唯一。
但是也不是强制的。

```python
In [64]: obj  = Series(range(5),index=list('aabbc'))

In [65]: obj
Out[65]:
a    0
a    1
b    2
b    3
c    4
dtype: int64

In [67]: obj.index.is_unique
Out[67]: False

In [68]: obj['a']
Out[68]:
a    0
a    1
dtype: int64

In [69]: obj['c']
Out[69]: 4
```
对于DataFrame，也是如此。

```python
In [70]: df =DataFrame(np.random.randn(4,3),index=list('aabb'))

In [79]: df.ix['a']
Out[79]:
          0         1         2
a  1.099692 -0.491098  0.625690
a -0.816857  1.025018  0.558494

In [80]: df.reindex(['b','a'])  # 不能重新索引有重复索引的DataFrame
...
ValueError: cannot reindex from a duplicate axis
```


# 3 汇总和计算描述统计

pandas有一组用于常用的数学和统计方法。他们一般都是基于没有缺失数据而构建的。
下面是一些简约方法的选项：

![](/images/2017-02-04-python数据分析-pandas入门/pandas_sample_func_opt.png)



```python
In [81]: df = DataFrame([[1.4,np.nan],[7.1,-4.5],[np.nan,np.nan],[0.73,-1.3]],
index=list('abcd'),columns=['one','two'])

In [82]: df
Out[82]:
    one  two
a  1.40  NaN
b  7.10 -4.5
c   NaN  NaN
d  0.73 -1.3

In [83]: df.sum()
Out[83]:
one    9.23
two   -5.80
dtype: float64

In [84]: df.mean()
Out[84]:
one    3.076667
two   -2.900000
dtype: float64

In [85]: df.mean(axis=1)  # 指定方向
Out[85]:
a    1.400
b    1.300
c      NaN
d   -0.285
dtype: float64

In [86]: df.mean(axis=1, skipna=False) # 排除nan
Out[86]:
a      NaN
b    1.300
c      NaN
d   -0.285
dtype: float64
```
下面是描述和汇总统计相关的方法：


![](/images/2017-02-04-python数据分析-pandas入门/描述和汇总统计1.png)

![](/images/2017-02-04-python数据分析-pandas入门/描述和汇总统计2.png)


```python
In [88]: df.describe()
/Users/yangfeilong/anaconda/lib/python2.7/site-packages/numpy/lib/
function_base.py:3834: RuntimeWarning: Invalid value encountered in percentile
  RuntimeWarning)
Out[88]:
            one       two
count  3.000000  2.000000
mean   3.076667 -2.900000
std    3.500376  2.262742
min    0.730000 -4.500000
25%         NaN       NaN
50%         NaN       NaN
75%         NaN       NaN
max    7.100000 -1.300000

In [89]: df.max()
Out[89]:
one    7.1
two   -1.3
dtype: float64

In [90]: df.min(axis=1)
Out[90]:
a    1.4
b   -4.5
c    NaN
d   -1.3
dtype: float64

In [91]: df.quantile()
Out[91]:
one   NaN
two   NaN
dtype: float64

In [92]: s1 = Series(np.arange(100))

In [93]: s1.quantile()
Out[93]: 49.5

In [94]:

In [95]: s1.quantile(0.2)
Out[95]: 19.800000000000001

In [96]: s1.quantile(0.24)
Out[96]: 23.759999999999998

In [97]: s1.quantile(0.25)
Out[97]: 24.75

In [98]: s1.quantile(0.5)
Out[98]: 49.5

In [99]: s1.quantile()
Out[99]: 49.5

In [100]: s1.median()
Out[100]: 49.5

In [101]: s1.mad()
Out[101]: 25.0

In [102]: df = DataFrame(np.arange(100).reshape(10,10),
columns=list('abcdefghij'))

In [103]: df
Out[103]:
    a   b   c   d   e   f   g   h   i   j
0   0   1   2   3   4   5   6   7   8   9
1  10  11  12  13  14  15  16  17  18  19
2  20  21  22  23  24  25  26  27  28  29
3  30  31  32  33  34  35  36  37  38  39
4  40  41  42  43  44  45  46  47  48  49
5  50  51  52  53  54  55  56  57  58  59
6  60  61  62  63  64  65  66  67  68  69
7  70  71  72  73  74  75  76  77  78  79
8  80  81  82  83  84  85  86  87  88  89
9  90  91  92  93  94  95  96  97  98  99

In [104]: df.mad()
Out[104]:
a    25.0
b    25.0
c    25.0
d    25.0
e    25.0
f    25.0
g    25.0
h    25.0
i    25.0
j    25.0
dtype: float64

In [105]: df.mad(axis=1)
Out[105]:
0    2.5
1    2.5
2    2.5
3    2.5
4    2.5
5    2.5
6    2.5
7    2.5
8    2.5
9    2.5
dtype: float64

In [106]: df.var(axis=1)
Out[106]:
0    9.166667
1    9.166667
2    9.166667
3    9.166667
4    9.166667
5    9.166667
6    9.166667
7    9.166667
8    9.166667
9    9.166667
dtype: float64

In [107]: df.var(axis=0)
Out[107]:
a    916.666667
b    916.666667
c    916.666667
d    916.666667
e    916.666667
f    916.666667
g    916.666667
h    916.666667
i    916.666667
j    916.666667
dtype: float64

In [108]: df.cummax()
Out[108]:
    a   b   c   d   e   f   g   h   i   j
0   0   1   2   3   4   5   6   7   8   9
1  10  11  12  13  14  15  16  17  18  19
2  20  21  22  23  24  25  26  27  28  29
3  30  31  32  33  34  35  36  37  38  39
4  40  41  42  43  44  45  46  47  48  49
5  50  51  52  53  54  55  56  57  58  59
6  60  61  62  63  64  65  66  67  68  69
7  70  71  72  73  74  75  76  77  78  79
8  80  81  82  83  84  85  86  87  88  89
9  90  91  92  93  94  95  96  97  98  99

In [109]: df
Out[109]:
    a   b   c   d   e   f   g   h   i   j
0   0   1   2   3   4   5   6   7   8   9
1  10  11  12  13  14  15  16  17  18  19
2  20  21  22  23  24  25  26  27  28  29
3  30  31  32  33  34  35  36  37  38  39
4  40  41  42  43  44  45  46  47  48  49
5  50  51  52  53  54  55  56  57  58  59
6  60  61  62  63  64  65  66  67  68  69
7  70  71  72  73  74  75  76  77  78  79
8  80  81  82  83  84  85  86  87  88  89
9  90  91  92  93  94  95  96  97  98  99

In [112]: df.diff()
Out[112]:
      a     b     c     d     e     f     g     h     i     j
0   NaN   NaN   NaN   NaN   NaN   NaN   NaN   NaN   NaN   NaN
1  10.0  10.0  10.0  10.0  10.0  10.0  10.0  10.0  10.0  10.0
2  10.0  10.0  10.0  10.0  10.0  10.0  10.0  10.0  10.0  10.0
3  10.0  10.0  10.0  10.0  10.0  10.0  10.0  10.0  10.0  10.0
4  10.0  10.0  10.0  10.0  10.0  10.0  10.0  10.0  10.0  10.0
5  10.0  10.0  10.0  10.0  10.0  10.0  10.0  10.0  10.0  10.0
6  10.0  10.0  10.0  10.0  10.0  10.0  10.0  10.0  10.0  10.0
7  10.0  10.0  10.0  10.0  10.0  10.0  10.0  10.0  10.0  10.0
8  10.0  10.0  10.0  10.0  10.0  10.0  10.0  10.0  10.0  10.0
9  10.0  10.0  10.0  10.0  10.0  10.0  10.0  10.0  10.0  10.0

```

## 3.1 相关系数和协方差

相关概念：
- 相关系数：反映两变量间线性相关关系的统计指标称为相关系数
- 协方差：在概率论和统计学中，协方差用于衡量两个变量的总体误差。
而方差是协方差的一种特殊情况，即当两个变量是相同的情况。


```python
In [92]: s1 = Series(np.arange(100))

In [117]: s1.corr(s2)
Out[117]: 0.99999999999999989

In [118]: s2 = Series(np.arange(2,202,2))

In [119]: s1.corr(s2)
Out[119]: 0.99999999999999989

In [120]: s1.cov(s2)
Out[120]: 1683.3333333333335

In [102]: df = DataFrame(np.arange(100).reshape(10,10),columns=list('abcdefghij'))

In [122]: df.corr()
Out[122]:
     a    b    c    d    e    f    g    h    i    j
a  1.0  1.0  1.0  1.0  1.0  1.0  1.0  1.0  1.0  1.0
b  1.0  1.0  1.0  1.0  1.0  1.0  1.0  1.0  1.0  1.0
c  1.0  1.0  1.0  1.0  1.0  1.0  1.0  1.0  1.0  1.0
d  1.0  1.0  1.0  1.0  1.0  1.0  1.0  1.0  1.0  1.0
e  1.0  1.0  1.0  1.0  1.0  1.0  1.0  1.0  1.0  1.0
f  1.0  1.0  1.0  1.0  1.0  1.0  1.0  1.0  1.0  1.0
g  1.0  1.0  1.0  1.0  1.0  1.0  1.0  1.0  1.0  1.0
h  1.0  1.0  1.0  1.0  1.0  1.0  1.0  1.0  1.0  1.0
i  1.0  1.0  1.0  1.0  1.0  1.0  1.0  1.0  1.0  1.0
j  1.0  1.0  1.0  1.0  1.0  1.0  1.0  1.0  1.0  1.0

```

## 3.2 唯一值、值计数以及成员资格

unique:去重

```python
In [124]: s1 = Series(list('ccbbabcddacbd'))

In [125]: s1.unique()
Out[125]: array(['c', 'b', 'a', 'd'], dtype=object)
```
value_counts:值计数

```python
In [129]: s1.value_counts()  # 默认降序排列
Out[129]:
b    4
c    4
d    3
a    2
dtype: int64

In [130]: pd.value_counts(s1,sort=False)  # pd也可以直接调用
Out[130]:
a    2
c    4
b    4
d    3
dtype: int64

```
isin:判断矢量化的集合成员


```python
In [134]: obj = Series(list('abcbcdcddcba'))

In [135]: mask = obj.isin(['b','c'])

In [136]: mask
Out[136]:
0     False
1      True
2      True
3      True
4      True
5     False
6      True
7     False
8     False
9      True
10     True
11    False
dtype: bool

In [137]: obj[mask]
Out[137]:
1     b
2     c
3     b
4     c
6     c
9     c
10    b
dtype: object

```

如下表：

![](/images/2017-02-04-python数据分析-pandas入门/pandas_unique_valuecounts_isin.png)


形成一个相关列的柱状图

```python
In [138]: data = DataFrame({'Qu1':[1,3,4,3,4],'Qu2':[2,3,1,2,3],'Qu3':[1,5,2,4,4]})

In [139]: data
Out[139]:
   Qu1  Qu2  Qu3
0    1    2    1
1    3    3    5
2    4    1    2
3    3    2    4
4    4    3    4

In [143]: data.apply(pd.value_counts).fillna(0)
Out[143]:
   Qu1  Qu2  Qu3
1  1.0  1.0  1.0
2  0.0  2.0  1.0
3  2.0  2.0  0.0
4  2.0  0.0  2.0
5  0.0  0.0  1.0
```


# 4 处理缺失数据
pandas使用非浮点数（NaN）来表示缺失数据，它只是表示缺少数据的一种标识。

```python
In [144]: string_data = Series(['hello',np.nan,'world'])

In [145]: string_data
Out[145]:
0    hello
1      NaN
2    world
dtype: object

In [146]: string_data.isnull()
Out[146]:
0    False
1     True
2    False
dtype: bool

```
**注意**：python中的None值也会被当成Nan处理。

![](/images/2017-02-04-python数据分析-pandas入门/NA_process.png)


## 4.1 滤除缺失数据

纯手工处理永远是最好的，但是很麻烦，使用dropna来处理简单一些。

```python
In [146]: string_data.isnull()
Out[146]:
0    False
1     True
2    False
dtype: bool

In [147]: data = Series([1,np.nan,3,np.nan])

In [148]: data
Out[148]:
0    1.0
1    NaN
2    3.0
3    NaN
dtype: float64

In [149]: data.dropna()
Out[149]:
0    1.0
2    3.0
dtype: float64

```
当然也可以使用bool索引来处理。

```python

In [150]: data[data.notnull()]
Out[150]:
0    1.0
2    3.0
dtype: float64

```
DataFrame而言比较麻烦。

```python
In [152]: df = DataFrame([[1,2,3],[np.nan,np.nan,np.nan],[3,4,np.nan],[2,3,4]])

In [153]: df
Out[153]:
     0    1    2
0  1.0  2.0  3.0
1  NaN  NaN  NaN
2  3.0  4.0  NaN
3  2.0  3.0  4.0

In [154]: df.dropna()
Out[154]:
     0    1    2
0  1.0  2.0  3.0
3  2.0  3.0  4.0

In [155]: df.dropna(how='all')  # 只丢弃全部都是nan的行。
Out[155]:
     0    1    2
0  1.0  2.0  3.0
2  3.0  4.0  NaN
3  2.0  3.0  4.0

In [164]: df[4] = np.nan

In [165]: df
Out[165]:
     0    1    2   4
0  1.0  2.0  3.0 NaN
1  NaN  NaN  NaN NaN
2  3.0  4.0  NaN NaN
3  2.0  3.0  4.0 NaN

In [166]: df.dropna(axis=1,how='all')
Out[166]:
     0    1    2
0  1.0  2.0  3.0
1  NaN  NaN  NaN
2  3.0  4.0  NaN
3  2.0  3.0  4.0


```
## 4.2 填充缺失数据
生成数据：

```python
In [167]: df = DataFrame(np.random.randn(4,4),columns=list('abcd'))

In [168]: df
Out[168]:
          a         b         c         d
0 -0.010218 -0.256541 -0.507837  0.470124
1  0.293587  0.517149 -1.813092 -0.791727
2  0.434398  1.352332  0.012355 -1.687852
3  0.573836 -0.701182 -0.548737  0.022037

In [169]: df.ix[:2,2]
Out[169]:
0   -0.507837
1   -1.813092
2    0.012355
Name: c, dtype: float64

In [170]: df.ix[:2,2]= np.nan

In [171]: df.ix[:1,3]= np.nan

In [172]: df
Out[172]:
          a         b         c         d
0 -0.010218 -0.256541       NaN       NaN
1  0.293587  0.517149       NaN       NaN
2  0.434398  1.352332       NaN -1.687852
3  0.573836 -0.701182 -0.548737  0.022037
```


```python
In [173]: df.fillna(0)  #全部填充0
Out[173]:
          a         b         c         d
0 -0.010218 -0.256541  0.000000  0.000000
1  0.293587  0.517149  0.000000  0.000000
2  0.434398  1.352332  0.000000 -1.687852
3  0.573836 -0.701182 -0.548737  0.022037


In [176]: df.fillna({'c':0,'d':0.5}) #不同列填充不同的值
Out[176]:
          a         b         c         d
0 -0.010218 -0.256541  0.000000  0.500000
1  0.293587  0.517149  0.000000  0.500000
2  0.434398  1.352332  0.000000 -1.687852
3  0.573836 -0.701182 -0.548737  0.022037

#默认总是会返回新的对象，也可以在源对象上修改；
In [177]: _ = df.fillna({'c':0,'d':0.5},inplace=True)

In [178]: df
Out[178]:
          a         b         c         d
0 -0.010218 -0.256541  0.000000  0.500000
1  0.293587  0.517149  0.000000  0.500000
2  0.434398  1.352332  0.000000 -1.687852
3  0.573836 -0.701182 -0.548737  0.022037

```
同样，也可以使用其他选项


![](/images/2017-02-04-python数据分析-pandas入门/fillna_opt1.png)


![](/images/2017-02-04-python数据分析-pandas入门/fillna_opt2.png)




```python
In [181]: df
Out[181]:
          a         b         c         d
0 -0.010218 -0.256541       NaN       NaN
1  0.293587  0.517149       NaN       NaN
2  0.434398  1.352332       NaN -1.687852
3  0.573836 -0.701182 -0.548737  0.022037

In [184]: df.fillna(method='bfill',limit=2)
Out[184]:
          a         b         c         d
0 -0.010218 -0.256541       NaN -1.687852
1  0.293587  0.517149 -0.548737 -1.687852
2  0.434398  1.352332 -0.548737 -1.687852
3  0.573836 -0.701182 -0.548737  0.022037
```


# 5 层次化索引

层次化索引是pandas的重要功能。以低维度的形式处理高维度数据。

```python
In [185]: data = Series(np.random.randn(10),index=[list('aaabbbccdd'),[1,2,3,1,2,3,2,3,2,3]])

In [186]: data
Out[186]:
a  1    0.458553
   2    0.077532
   3   -1.561180
b  1    2.498391
   2    0.243617
   3   -0.818542
c  2   -1.222213
   3   -0.797079
d  2    1.131352
   3   -1.292136
dtype: float64
```
获取索引。

```python
In [187]: data.index
Out[187]:
MultiIndex(levels=[[u'a', u'b', u'c', u'd'], [1, 2, 3]],
           labels=[[0, 0, 0, 1, 1, 1, 2, 2, 3, 3], [0, 1, 2, 0, 1, 2, 1, 2, 1, 2]])

In [188]: data['b']
Out[188]:
1    2.498391
2    0.243617
3   -0.818542
dtype: float64

In [189]: data['b':'c']
Out[189]:
b  1    2.498391
   2    0.243617
   3   -0.818542
c  2   -1.222213
   3   -0.797079
dtype: float64

In [190]: data[:,2]  # 获取内层索引
Out[190]:
a    0.077532
b    0.243617
c   -1.222213
d    1.131352
dtype: float64


In [191]: data.unstack()  # unstack来重新安排到dataframe中。
Out[191]:
          1         2         3
a  0.458553  0.077532 -1.561180
b  2.498391  0.243617 -0.818542
c       NaN -1.222213 -0.797079
d       NaN  1.131352 -1.292136

In [192]: data.unstack().stack()  # 逆运算--stack
Out[192]:
a  1    0.458553
   2    0.077532
   3   -1.561180
b  1    2.498391
   2    0.243617
   3   -0.818542
c  2   -1.222213
   3   -0.797079
d  2    1.131352
   3   -1.292136
dtype: float64

```
DataFrame每条轴都可以分层索引。

## 5.1 重排分级顺序

可以重排调整某条轴上的索引顺序，swaplevel可以互换两个索引值，并范围一个新的对象。

```python
In [193]: frame = DataFrame(np.random.randn(4,3),index=[list('aabb'),[1,2,1,2]],
columns=[['Ohio','Ohio','Colorado'],['Green','Red','Green']])
     ...:

In [194]: frame
Out[194]:
         Ohio            Colorado
        Green       Red     Green
a 1  0.368997  0.670430  1.056365
  2 -0.352259 -0.656101  0.018544
b 1 -0.574535 -0.531988  0.295466
  2 -0.973587  0.225511 -0.250887

In [198]: frame.index.names = ['key1','key2']

In [199]: frame.columns.names = ['state','color']

In [200]: frame
Out[200]:
state          Ohio            Colorado
color         Green       Red     Green
key1 key2                              
a    1     0.368997  0.670430  1.056365
     2    -0.352259 -0.656101  0.018544
b    1    -0.574535 -0.531988  0.295466
     2    -0.973587  0.225511 -0.250887

In [201]: frame.swaplevel('key1','key2')
Out[201]:
state          Ohio            Colorado
color         Green       Red     Green
key2 key1                              
1    a     0.368997  0.670430  1.056365
2    a    -0.352259 -0.656101  0.018544
1    b    -0.574535 -0.531988  0.295466
2    b    -0.973587  0.225511 -0.250887

In [202]: frame.sortlevel(1)
Out[202]:
state          Ohio            Colorado
color         Green       Red     Green
key1 key2                              
a    1     0.368997  0.670430  1.056365
b    1    -0.574535 -0.531988  0.295466
a    2    -0.352259 -0.656101  0.018544
b    2    -0.973587  0.225511 -0.250887

In [203]: frame.swaplevel(0,1)
Out[203]:
state          Ohio            Colorado
color         Green       Red     Green
key2 key1                              
1    a     0.368997  0.670430  1.056365
2    a    -0.352259 -0.656101  0.018544
1    b    -0.574535 -0.531988  0.295466
2    b    -0.973587  0.225511 -0.250887

In [204]: frame.swaplevel(0,1).sortlevel(0)
Out[204]:
state          Ohio            Colorado
color         Green       Red     Green
key2 key1                              
1    a     0.368997  0.670430  1.056365
     b    -0.574535 -0.531988  0.295466
2    a    -0.352259 -0.656101  0.018544
     b    -0.973587  0.225511 -0.250887
```

## 5.2 根据级别汇总统计

许多DataFrame和Series汇总和统计方法都有level选项，指定在某个轴。

```python

In [205]: frame
Out[205]:
state          Ohio            Colorado
color         Green       Red     Green
key1 key2                              
a    1     0.368997  0.670430  1.056365
     2    -0.352259 -0.656101  0.018544
b    1    -0.574535 -0.531988  0.295466
     2    -0.973587  0.225511 -0.250887


In [207]: frame.sum(level='key2')
Out[207]:
state      Ohio            Colorado
color     Green       Red     Green
key2                               
1     -0.205538  0.138443  1.351831
2     -1.325846 -0.430590 -0.232343

In [209]: frame.sum(level='color',axis=1)
Out[209]:
color         Green       Red
key1 key2                    
a    1     1.425362  0.670430
     2    -0.333715 -0.656101
b    1    -0.279069 -0.531988
     2    -1.224474  0.225511
```

## 5.3 使用DataFrame的列

经常需要用DataFrame的列作为索引，或者希望将索引变成DataFrame的列。

```python
In [210]: df = DataFrame({'a':range(7),'b':range(7,0,-1),'c':['one']*7,'d':[0,1,2,0,1,2,3]})

In [211]: df
Out[211]:
   a  b    c  d
0  0  7  one  0
1  1  6  one  1
2  2  5  one  2
3  3  4  one  0
4  4  3  one  1
5  5  2  one  2
6  6  1  one  3

In [212]: df2 = df.set_index(['c','d']) #默认情况下，会将转换的这两列删除掉；

In [213]: df2
Out[213]:
       a  b
c   d      
one 0  0  7
    1  1  6
    2  2  5
    0  3  4
    1  4  3
    2  5  2
    3  6  1

    In [215]: df2 = df.set_index(['c','d'],drop=False) # 仍然保留这两列

    In [216]: df2
    Out[216]:
           a  b    c  d
    c   d              
    one 0  0  7  one  0
        1  1  6  one  1
        2  2  5  one  2
        0  3  4  one  0
        1  4  3  one  1
        2  5  2  one  2
        3  6  1  one  3

```
用reset_index可以将索引合并到DataFrame中。

```python
In [217]: df2 = df.set_index(['c','d'])

In [218]: df2
Out[218]:
       a  b
c   d      
one 0  0  7
    1  1  6
    2  2  5
    0  3  4
    1  4  3
    2  5  2
    3  6  1

In [219]: df2.reset_index()
Out[219]:
     c  d  a  b
0  one  0  0  7
1  one  1  1  6
2  one  2  2  5
3  one  0  3  4
4  one  1  4  3
5  one  2  5  2
6  one  3  6  1

```

# 6 其他

## 6.1 整数索引

先看一个例子：我们很难判断是要通过位置还是通过标签的索引来获取数据。

```python
In [220]: ser = Series(np.arange(3))

In [221]: ser
Out[221]:
0    0
1    1
2    2
dtype: int64

In [222]: ser[-1]
---------------------------------------------------------------------------
KeyError                                  Traceback (most recent call last)
...
```
这样对于使用字母索引的Series就不存在这个问题。

如果需要可靠的、不考虑索引类型的、基于位置的索引，可以使用：
- Series：iget_value
- DataFrame：irow和icol

新的版本有些变化：都是用iloc来通过位置准确获取。


```python
In [231]: ser3 = Series(np.arange(3),index=[-5,1,3])

In [232]: ser3.iget_value(2)
/Users/yangfeilong/anaconda/bin/ipython:1: FutureWarning:
iget_value(i) is deprecated. Please use .iloc[i] or .iat[i]
  #!/bin/bash /Users/yangfeilong/anaconda/bin/python.app
Out[232]: 2

In [236]: ser3.iloc[2]
Out[236]: 2

In [237]: ser3.iat[2]
Out[237]: 2

In [239]: frame = DataFrame(np.arange(6).reshape(3,2),index=[2,0,1])

In [241]: frame
Out[241]:
   0  1
2  0  1
0  2  3
1  4  5

In [242]: frame.irow(1)
/Users/yangfeilong/anaconda/bin/ipython:1: FutureWarning: irow(i) is deprecated. Please use .iloc[i]
  #!/bin/bash /Users/yangfeilong/anaconda/bin/python.app
Out[242]:
0    2
1    3
Name: 0, dtype: int64

In [243]: frame.icol(1)
/Users/yangfeilong/anaconda/bin/ipython:1: FutureWarning: icol(i) is deprecated. Please use .iloc[:,i]
  #!/bin/bash /Users/yangfeilong/anaconda/bin/python.app
Out[243]:
2    1
0    3
1    5
Name: 1, dtype: int64

In [245]: frame.iloc[1]  # 按行位置获取
Out[245]:
0    2
1    3
Name: 0, dtype: int64

In [246]: frame.iloc[:,1]  #按列位置获取
Out[246]:
2    1
0    3
1    5
Name: 1, dtype: int64

```




## 6.2 面板数据
Panel数据结构，可以看成是一个三维的DataFrame数据结构。
Panel中的每一项都是一个DataFrame。
同样使用堆积式（层次化索引的）的DataFrame可以表示一个panel。

```python
In [247]: import pandas.io.data as web
/Users/yangfeilong/anaconda/lib/python2.7/site-packages/pandas/io/data.py:35:
 FutureWarning:
The pandas.io.data module is moved to a separate package (pandas-datareader)
 and will be removed from pandas in a future version.
After installing the pandas-datareader package
 (https://github.com/pydata/pandas-datareader),
 you can change the import ``from pandas.io import data, wb`` to ``from
  pandas_datareader import data, wb``.
  FutureWarning)

In [248]: web
Out[248]: <module 'pandas.io.data' from '/Users/yangfeilong/anaconda/
lib/python2.7/site-packages/pandas/io/data.py'>

In [249]: pdata = pd.Panel(dict((stk ,web.get_data_yahoo(stk,'1/1/2009',
'6/1/2012')) for stk in ['AAPL','GOOG','MSFT','DELL']))

In [250]: pdata
Out[250]:
<class 'pandas.core.panel.Panel'>
Dimensions: 4 (items) x 868 (major_axis) x 6 (minor_axis)
Items axis: AAPL to MSFT
Major_axis axis: 2009-01-02 00:00:00 to 2012-06-01 00:00:00
Minor_axis axis: Open to Adj Close

In [252]: pdata = pdata.swapaxes('items','minor')

In [253]: pdata['Adj Close']
Out[253]:
                 AAPL      DELL        GOOG       MSFT
Date                                                  
2009-01-02  11.808505  10.39902  160.499779  16.501303
...
2012-05-30  75.362333  12.14992  293.821674  25.878448
2012-05-31  75.174961  11.92743  290.140354  25.746145
2012-06-01  72.996726  11.67592  285.205295  25.093451

[868 rows x 4 columns]

In [256]: pdata.ix[:,'6/1/2012',:]  # ix扩展为三维
Out[256]:
            Open        High         Low       Close       Volume   Adj Close
AAPL  569.159996  572.650009  560.520012  560.989983  130246900.0   72.996726
DELL   12.150000   12.300000   12.045000   12.070000   19397600.0   11.675920
GOOG  571.790972  572.650996  568.350996  570.981000    6138700.0  285.205295
MSFT   28.760000   28.959999   28.440001   28.450001   56634300.0   25.093451

In [260]: pdata.ix[:,'5/30/2012':,:].to_frame()
Out[260]:
                        Open        High         Low       Close       Volume  \
Date       minor                                                                
2012-05-30 AAPL   569.199997  579.989990  566.559990  579.169998  132357400.0   
           DELL    12.590000   12.700000   12.460000   12.560000   19787800.0   
           GOOG   588.161028  591.901014  583.530999  588.230992    3827600.0   
           MSFT    29.350000   29.480000   29.120001   29.340000   41585500.0   
2012-05-31 AAPL   580.740021  581.499985  571.460022  577.730019  122918600.0   
           DELL    12.530000   12.540000   12.330000   12.330000   19955600.0   
           GOOG   588.720982  590.001032  579.001013  580.860990    5958800.0   
           MSFT    29.299999   29.420000   28.940001   29.190001   39134000.0   
2012-06-01 AAPL   569.159996  572.650009  560.520012  560.989983  130246900.0   
           DELL    12.150000   12.300000   12.045000   12.070000   19397600.0   
           GOOG   571.790972  572.650996  568.350996  570.981000    6138700.0   
           MSFT    28.760000   28.959999   28.440001   28.450001   56634300.0   

                   Adj Close  
Date       minor              
2012-05-30 AAPL    75.362333  
           DELL    12.149920  
           GOOG   293.821674  
           MSFT    25.878448  
2012-05-31 AAPL    75.174961  
           DELL    11.927430  
           GOOG   290.140354  
           MSFT    25.746145  
2012-06-01 AAPL    72.996726  
           DELL    11.675920  
           GOOG   285.205295  
           MSFT    25.093451  

# 可以转化为DataFrame
In [261]: stacked = pdata.ix[:,'5/30/2012':,:].to_frame()

In [262]: stacked.to_panel() # 转化为panel
Out[262]:
<class 'pandas.core.panel.Panel'>
Dimensions: 6 (items) x 3 (major_axis) x 4 (minor_axis)
Items axis: Open to Adj Close
Major_axis axis: 2012-05-30 00:00:00 to 2012-06-01 00:00:00
Minor_axis axis: AAPL to MSFT
```
