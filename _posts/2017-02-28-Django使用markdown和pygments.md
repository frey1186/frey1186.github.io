---
layout: post
title: Django中解析markdown文本
date: 2017-02-28 12:00
author: felo
tags: django markdown
---





获取python和django版本：

```python
localhost:css$ python3
Python 3.5.1 (v3.5.1:37a07cee5969, Dec  5 2015, 21:12:44)
[GCC 4.2.1 (Apple Inc. build 5666) (dot 3)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import django
>>> django.VERSION
(1, 9, 5, 'final', 0)
```

# 1. 安装插件

这里需要用到的有两个插件

- markdown: 用于解析markdown文本
- pygments: 代码高亮显示

```python
localhost:css$ pip install markdown pygments
# or
localhost:css$ easy_install install markdown pygments
```

# 2. markdown

具体内容参考python-markdown[官网地址](https://pythonhosted.org/Markdown)。

最简单的应用就是：

```python
import markdown
html = markdown.markdown(your_text_string)  # so easy
```

但是需要在django中使用下面的方法实现：

## 2.1 使用templatetags

在app目录下增加一个templatetags文件夹，并增加两个文件

```python
localhost:blog$ mkdir templatetags
localhost:blog$ cd templatetags
localhost:templatetags$ touch __init__.py
localhost:templatetags$ touch custom_markdown.py  # 随意，其他名字也可以
```

修改custom_markdown.py这个文件

```python
import markdown
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()  # 自定义filter时必须加上
@register.filter(is_safe=True)  # 注册template filter
@stringfilter  # 希望字符串作为参数
def custom_markdown(value):
    return mark_safe(markdown.markdown(
           value,
           extensions=['markdown.extensions.fenced_code',
            'markdown.extensions.codehilite'], # codehilite即为代码高亮准备
           safe_mode=True,
           enable_attributes=False))
```

## 2.2 在template中使用

在模板文件中增加：

```python
...
load custom_markdown  # 加载tag文件
...
{{ articles.content | custom_markdown  }}  # 使用函数

```

content中一部分markdown文本作为例子，如下所示：

```python

    # 4 写第一个view
    在polls/views下写一个最简单的view：

    ```python
    from django.http import HttpResponse
    def index(request):
        return HttpResponse("Hello, world. You're at the polls index.")

```


查看markdown编写的内容已经被解析了。但是代码没有高亮。

![](/images/2017-02-28-Django使用markdown和pygments/markdown_code.png)


# 3. pygments

使用pyments创建一个css文件，放到django的static文件目录中，让它能够给页面中的代码进行渲染即可。
具体内容参见[Pygments](http://pygments.org/).

## 3.1 创建css

一步：

```python
localhost:css$ pygmentize -S xcode -f html -a .codehilite > code.css
```

当然，可以选择其他的style，替换`xcode`即可。风格有下面这些。

```python
>>> from pygments.styles import STYLE_MAP
>>> STYLE_MAP.keys()
dict_keys(['perldoc', 'vs', 'fruity', 'borland', 'monokai', 'xcode', 'autumn',
 'algol_nu', 'abap', 'paraiso-dark', 'rainbow_dash', 'murphy', 'emacs', 'manni',
  'pastie', 'bw', 'arduino', 'lovelace', 'native', 'algol', 'trac', 'friendly',
   'paraiso-light', 'vim', 'colorful', 'tango', 'igor', 'rrt', 'default'])
```

## 3.2 使用

在模板头部增加：

```python
# 确保路径正确
<link type="text/css" rel="stylesheet" href="<css_file_path>/code.css"/>
```

可以了。

![](/images/2017-02-28-Django使用markdown和pygments/markdown_codehilite.png)
