---
layout: post
title: Django first steps Part2[译]
date: 2016-05-31 12：00
author: felo
tags: django
---




---
# 1 数据库设置
打开` mysite/settings.py`进行设置，这是一个普通的python模块作为设置文件。默认的数据库设置为SQLite，日常测试或开发可以使用它，但是要用于生产的话，你需要更加强劲的数据库。
如果要使用其他数据库，修改`DATABASES 'default'`下面的参数：

- ENGINE – Either 'django.db.backends.sqlite3',
 'django.db.backends.postgresql','django.db.backends.mysql', or
  'django.db.backends.oracle'. Other backends are also available.

- NAME – The name of your database. If you’re using SQLite, the database will be a file on your computer; in that case, NAME should be the full absolute path, including filename, of that file. The default value,os.path.join(BASE_DIR, 'db.sqlite3'), will store the file in your project directory.

如果不是使用SQLite还需要增加 USER, PASSWORD, and HOST这些参数，并且**需要创建好数据库实例**，但是我们这里就用sqlite，不需要对settings进行任何的修改就行使用。

另外，设置好set TIME_ZONE to your time zone.


By default, INSTALLED_APPS 包含下面几个APP，都是django自带的:
- django.contrib.admin – The admin site. You’ll use it shortly.
- django.contrib.auth – An authentication system.
- django.contrib.contenttypes – A framework for content types.
- django.contrib.sessions – A session framework.
- django.contrib.messages – A messaging framework.
- django.contrib.staticfiles – A framework for managing static files.

在使用这个默认的app之前，我们需要执行：

```
$ python manage.py migrate
```
migrate会根据app在数据库中创建相应的表结构，并且只对INSTALLED_APPS下面的app创建表结构。

---
# 2  创建models
本质上就是创建数据库的结构，model是一个单独的，权威的数据源，它包含你所存储数据必要的类型和动作，django遵循DRY Principle，目的是让所有数据都来自一个地方。
不同于Ruby On Rails ，django能够滚动更新数据库到最新的models。
在我们的polls例子中，创建两个models：Question and Choice.

```
localhost:polls$ more models.py
from __future__ import unicode_literals

from django.db import models

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")

class Choice(models.Model):
    question = models.ForeignKey(Question,on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
```

必选参数：max_length

可选参数：default=0，on_delete

> Django supports all the common database relationships: many-to-one, many-to-many, and one-to-one.

---
# 3 Activating models
简单的几行models代码做了很多事情：
- 创建了一个database schema (CREATE TABLE statements)
- Create a Python database-access API for accessing Question and Choice objects.

但是首先要将polls这个app installed：
编辑`mysite/settings.py`文件在`INSTALLED_APPS`下增加`polls.apps.PollsConfig`，如下所示：

```
INSTALLED_APPS = [
'polls.apps.PollsConfig',    #增加此行，直接增加"polls"亦可以
'django.contrib.admin',
'django.contrib.auth',
'django.contrib.contenttypes',
'django.contrib.sessions',
'django.contrib.messages',
'django.contrib.staticfiles',
]
```

然后运行：

```
$ python manage.py makemigrations polls
#$ python manage.py makemigrations 不加app名称将检查所有app的变化
```

可以看到类似下面的信息：

```
Migrations for 'polls':
0001_initial.py:
- Create model Choice
- Create model Question
- Add field question to choice
```
`makemigrations`告诉django在models中出现了哪些变化，这些变化将使用`migrate`保存到数据库中。
这些变化存放在`polls/migrations/0001_initial.py.`文件中。
在运行migrate之前，可以通过一个命令来查看将在数据库中执行哪些sql语句：

```
$ python manage.py sqlmigrate polls 0001
```

得到类似SQL语句：（这里是PostgreSQL的例子）

```
BEGIN;
--
-- Create model Choice
--
CREATE TABLE "polls_choice" (
"id" serial NOT NULL PRIMARY KEY,
"choice_text" varchar(200) NOT NULL,
"votes" integer NOT NULL
);
--
-- Create model Question
--
CREATE TABLE "polls_question" (
"id" serial NOT NULL PRIMARY KEY,
"question_text" varchar(200) NOT NULL,
"pub_date" timestamp with time zone NOT NULL
);
--
-- Add field question to choice
--
ALTER TABLE "polls_choice" ADD COLUMN "question_id" integer NOT NULL;
ALTER TABLE "polls_choice" ALTER COLUMN "question_id" DROP DEFAULT;
CREATE INDEX "polls_choice_7aa0f6ee" ON "polls_choice" ("question_id");
ALTER TABLE "polls_choice"
ADD CONSTRAINT "polls_choice_question_id_246c99a640fbbd72_fk_polls_question_id"
FOREIGN KEY ("question_id")
REFERENCES "polls_question" ("id")
DEFERRABLE INITIALLY DEFERRED;
COMMIT;
```

如果你有兴趣，可以运行python manage.py check; this checks for any problems in your project
without making migrations or touching the database.

好，下面开始运行migrate了：

```
$ python manage.py migrate
Operations to perform:
Apply all migrations: admin, contenttypes, polls, auth, sessions
Running migrations:
Rendering model states... DONE
Applying polls.0001_initial... OK
```

django的migration十分的强大，不需要删除database或tables，就能直接修改至models所需要的，使用django的migration，只需要三步：
- 修改 models (in models.py).
- 运行`python manage.py makemigrations`创建变化
- 运行`python manage.py migrate` 应用变化到数据库

分开创建和接受migrations的原因是便于版本控制系统，也方便其他开发者阅读。

# 4 Playing with the API

django有一个单独的shell，直接用python的话存在一些问题， manage.py文件设置了从 mysite/settings.py中导入的DJANGO_SETTINGS_MODULE的环境变量。

```
$ python manage.py shell
```

那么有没有办法绕过manage.py呢，有。

```
>>> import django
>>> django.setup()
```
但是试了下，貌似不行，还是用第一个办法吧。

```
>>> from polls.models import Question, Choice #导入我们刚写的models类
>>> Question.objects.all()  #列举所有对象，现在沒有对象
[]
# Create a new Question.
#注意首先设置一下settings中的timezone
>>> from django.utils import timezone
>>> q = Question(question_text="What's new?", pub_date=timezone.now())  #创建一个对象
>>> q.save()  #保存
>>> q.id  #自动产生一个id 的列，自增
1
>>> q.question_text  #查看question_text列
"What's new?"
>>> q.pub_date
datetime.datetime(2012, 2, 26, 13, 0, 0, 775217, tzinfo=<UTC>)
# Change values by changing the attributes, then calling save().
>>> q.question_text = "What's up?"  #修改列
>>> q.save()  #注意要保存
>>> Question.objects.all()
[<Question: Question object>]

```

等等，`[<Question: Question object>]`根本就不是人能看明白的啊，让我们在`polls/models.py`文件中增加一个__str__()的方法，django默认会将对象显示为__str__()方法所返回的内容。

```
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

@python_2_unicode_compatible # 兼容python2
class Question(models.Model):
# ...
def __str__(self):
    return self.question_text

@python_2_unicode_compatible #兼容python2
class Choice(models.Model):
# ...
def __str__(self):
    return self.choice_text
```
咱也可以自定义一个方法：

```
import datetime
from django.db import models
from django.utils import timezone
class Question(models.Model):
# ...
def was_published_recently(self):  #
    return self.pub_date >= timezone.now() - datetime.timedelta(days=1) #如果pub_date在一天内就返回True
```

保存这些变化，开启一个manage.py shell，

```
>>> from polls.models import Question, Choice
# Make sure our __str__() addition worked.
>>> Question.objects.all()
[<Question: What's up?>]
# Django提供了丰富的database关键参数查询API
>>> Question.objects.filter(id=1)
[<Question: What's up?>]
>>> Question.objects.filter(question_text__startswith='What')  #__startswith开始于
[<Question: What's up?>]
# Get the question that was published this year.
>>> from django.utils import timezone
>>> current_year = timezone.now().year
>>> Question.objects.get(pub_date__year=current_year) # __year年
<Question: What's up?>
# Request an ID that doesn't exist, this will raise an exception.
>>> Question.objects.get(id=2)  #不存在记录
Traceback (most recent call last):
...
DoesNotExist: Question matching query does not exist.
# Lookup by a primary key is the most common case, so Django provides a
# shortcut for primary-key exact lookups.
# The following is identical to Question.objects.get(id=1).
>>> Question.objects.get(pk=1)  #通过逐渐查询
<Question: What's up?>
# Make sure our custom method worked.
>>> q = Question.objects.get(pk=1)
>>> q.was_published_recently()  #自定义参数
True
# Give the Question a couple of Choices. The create call constructs a new
# Choice object, does the INSERT statement, adds the choice to the set
# of available choices and returns the new Choice object. Django creates
# a set to hold the "other side" of a ForeignKey relation
# (e.g. a question's choice) which can be accessed via the API.
>>> q = Question.objects.get(pk=1)
# Display any choices from the related object set -- none so far.
>>> q.choice_set.all()  #choice是question的一个外键，通过choice_set能够关联查询
[]
# Create three choices.
>>> q.choice_set.create(choice_text='Not much', votes=0)  #创建
<Choice: Not much>
>>> q.choice_set.create(choice_text='The sky', votes=0)
<Choice: The sky>
>>> c = q.choice_set.create(choice_text='Just hacking again', votes=0)
# Choice objects have API access to their related Question objects.
>>> c.question
<Question: What's up?>
# And vice versa: Question objects get access to Choice objects.
>>> q.choice_set.all()
[<Choice: Not much>, <Choice: The sky>, <Choice: Just hacking again>]
>>> q.choice_set.count()
3
# The API automatically follows relationships as far as you need.
# Use double underscores to separate relationships.
# This works as many levels deep as you want; there's no limit.
# Find all Choices for any question whose pub_date is in this year
# (reusing the 'current_year' variable we created above).
>>> Choice.objects.filter(question__pub_date__year=current_year)
[<Choice: Not much>, <Choice: The sky>, <Choice: Just hacking again>]
# Let's delete one of the choices. Use delete() for that.
>>> c = q.choice_set.filter(choice_text__startswith='Just hacking')
>>> c.delete()
```

---

# 5 django admin简介

django admin的理念是用于后台管理员使用的，而非普通用户使用。django admin完全自动的为models生成管理接口。
django产生于新闻编辑室的环境下，非常清晰的分开内容发布和公开的位置，管理员们轻松的增加新闻，内容，故事等，然后这些内容在相应的地方公开显示，django解决了一个管理员们创建统一的编辑内容的接口。

## 创建一个admin user

```
localhost:mysite$ python manage.py createsuperuser
Username (leave blank to use 'admin'): admin
Email address: admin@example.com
Password:
Password (again):
Superuser created successfully.
```

## 启动开发服务器，查看登陆admin界面
![](http://images2015.cnblogs.com/blog/866969/201605/866969-20160531213116055-919544631.jpg)
admin显示语言可以在setting中设置。

## 进入管理界面
刚开始只能管理admin中默认的Groups和Users两个类，他们是由django.contrib.auth这个app提供的。
![](http://images2015.cnblogs.com/blog/866969/201605/866969-20160531213124961-1854698528.jpg)

## 使得polls在admin中可修改

我们要告诉admin，Question对象有admin接口，即在polls/admin.py 下增加几行：

```
from django.contrib import admin

# Register your models here.
from . import models

admin.site.register(models.Question)
```

## 探索admin的简单功能
![](http://images2015.cnblogs.com/blog/866969/201605/866969-20160531213138117-953752625.jpg)
可以对Questions进行增加记录，修改记录，删除记录，查询记录等操作，还可以查看历史。
