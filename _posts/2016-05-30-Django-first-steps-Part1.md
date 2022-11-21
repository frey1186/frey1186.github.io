---
layout: post
title: Django first steps Part1[译]
date: 2016-05-30 12：00
author: felo
tags: django
---





---

> 实验环境：
   os:mac os
   python:2.7.10



确认django是否安装在本机上：

```python
$python -c "import django; print(django.get_version())"
1.9.6
```

---

# 1 Creating a project 创建一个工程



```python
localhost:PycharmProjects$ django-admin startproject mysite
```

startproject将会创建以下文件：

```python
mysite/  #django工程的根目录
    manage.py  #django工程的一个命令行工具
    mysite/    #这是一个python包，后面我们会用来导入使用，
        __init__.py  #不能缺少
        settings.py  #django工程配置文件
        urls.py    #django工程的url表
        wsgi.py    #一个wsgi web server的入口
```



---

# 2 The development server 开发服务器

来确认下project是否工作？

```
localhost:PycharmProjects$ cd mysite/

localhost:mysite$ ls

manage.py	mysite

localhost:mysite$

localhost:mysite$ python manage.py runserver

Performing system checks...



System check identified no issues (0 silenced).



You have unapplied migrations; your app may not work properly until they are applied.

Run 'python manage.py migrate' to apply them.



May 30, 2016 - 14:34:42

Django version 1.9.6, using settings 'mysite.settings'

Starting development server at http://127.0.0.1:8000/

Quit the server with CONTROL-C.
```

使用chrome浏览器，http://127.0.0.1:8000/ ,查看效果,it worked!


如果想要指定端口：

```python
$ python manage.py runserver 8080
```

如果想要指定ip地址：

```python
$ python manage.py runserver 0.0.0.0:8000
# 0.0.0.0 表示这个设备上的所有IP地址
```



自动重载runserver

 - 需要的情况下，The development server 会自动重载，你不需要经常去重启。 但是，像增加文件等操作是不会触发自动重载的，需要手动重载。



---

# 3 创建Polls app

>**project和app**
An app is a Web application that does something
A project is a collection of configuration and apps for a particular website.
一个project能够拥有多个app，一个app也能属于多个project





创建app，可以在任何python能够识别的路径下

```python
$ python manage.py startapp polls
```

查看下pools的目录结构：

```python
polls/
    __init__.py
    admin.py
    apps.py
    migrations/
        __init__.py
    models.py
    tests.py
    views.py
```



---

# 4 写第一个view

在polls/views下写一个最简单的view：

```python
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")
```

想要访问这个view，就需要配置URLconf，在polls下创建一个urls.py文件

```python
polls/
    __init__.py
    admin.py
    apps.py
    migrations/
        __init__.py
    models.py
    tests.py
    urls.py  #新增URLconf
    views.py
```

在polls/urls.py中增加：

```python
localhost:polls$ more urls.py

from django.conf.urls import url

from . import views



urlpatterns = [

    url(r'^$',views.index,name="index"),

]

```

然后需要将这个URLconf添加到mysite的url中。

```python
localhost:mysite$ more mysite/urls.py

from django.conf.urls import url,include
from django.contrib import admin

urlpatterns = [
    url(r'^polls/', include("polls.urls")),
    url(r'^admin/', admin.site.urls),
]
```

include函数允许访问其他URLconf，注意include函数对应的前面正则表达式中包含“^”，但是不含“$”,使用include能够简化urls，将polls使用的url都规划到polls下面。



运行runserver，查看以下地址：http://127.0.0.1:8000/polls/ 显示views中index函数返回信息




## url() argument: 正则表达式regex

正则表达式不包含get和post的参数，如

```python
https://www.example.com/myapp/, the URLconf will look for myapp/.
https://www.example.com/myapp/?page=3, the URLconf will also look for myapp/.
```



## url() argument: 视图view



在url正则表达式匹配到之后，即调用view函数



## url() argument: kwargs

字典，可以传入额外的参数；

Arbitrary keyword arguments can be passed in a dictionary to the target view. We aren’t going to use this feature of Django in the tutorial.

## url() argument: name

为这个url定义一个名字，可以在模板中访问，

Naming your URL lets you refer to it unambiguously from elsewhere in Django especially templates. This powerful feature allows you to make global changes to the url patterns of your project while only touching a single file.



---

未完待续，Part2
