---
layout: post
title: Django Middleware 介绍[译]
date: 2016-06-20 12：00
author: felo
tags: django
---

# Middleware
Middleware是一个镶嵌到django的request/response处理机制中的一个hooks框架。它是一个修改django全局输入输出的一个底层插件系统。

每个中间件组件负责一些特定的功能，比如说 Django包含一个 AuthenticationMiddleware的中间间，使用sessions将用户和请求联系在一起（ that associates users with requests using sessions.）。

这篇文章解释了中间件如何工作，如果激活中间件，如何编写自己的中间件。django有很多内建的中间件，详细内容查看内建中间件附录。



## 激活中间件

要想激活中间件，需要在settings文件中的 MIDDLEWARE_CLASSES下增加。在 MIDDLEWARE_CLASSES中，每个中间件以一个字符串的形势保存。比如，下面是默认创建工程的中间件 MIDDLEWARE_CLASSES内容：

```python
MIDDLEWARE_CLASSES = ['django.middleware.security.SecurityMiddleware',
'django.contrib.sessions.middleware.SessionMiddleware',
'django.middleware.common.CommonMiddleware',
'django.middleware.csrf.CsrfViewMiddleware',
'django.contrib.auth.middleware.AuthenticationMiddleware',
'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
'django.contrib.messages.middleware.MessageMiddleware',
'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

一个django工程的创建不需要任何一个中间件，即如果你喜欢的话，MIDDLEWARE_CLASSES可以为空，但是强烈建议至少包含 CommonMiddleware这个中间件。
中间件在MIDDLEWARE_CLASSES中是有顺序的，因为中间件之间有相互依赖关系。比如说AuthenticationMiddleware 在session中保存认证的用户信息，因此，它必须在 SessionMiddleware之后，详细的内容可以参考[Middleware ordering](https://docs.djangoproject.com/en/1.9/ref/middleware/#middleware-ordering)。


## Hooks和application的顺序
在请求阶段，调用views之前，django按照MIDDLEWARE_CLASSES中定义的顺序从上到下调用中间件。有两个hooks：
- process_request()
- process_view()


在响应阶段，调用views之后，中间件被从下到上反向调用，有三个hooks：
- process_exception() (只有当view中raise一个例外时)
- process_template_response() (只有view中返回template时）
- process_response()

![](http://images2015.cnblogs.com/blog/866969/201606/866969-20160620145833709-416633611.png)



如果你喜欢，可以把它比作洋葱，每个中间件就是洋葱的一层皮。
每个hooks在下面描述：

## 编写你自己的中间件
写一个自己的中间件很简单，每个中间件就是一个普通的python类，包含下面的一个或多个方法：

### 1） process_request()

 process_request(request)
其中request是HttpRequest对象，process_request() 将会在每个request被决定使用哪个view之前调用，它会返回None或者一个HttpResponse对象。
- 如果返回None，django会继续执行其他中间件的process_request()， 然后是process_view() ，然后是恰当的view函数。
- 如果返回HttpResponse对象，它就直接返回了，不再执行其他中间件，view等。


### 2） process_view()

 process_view(request, view_func, view_args, view_kwargs)
其中request是HttpRequest 对象， view_func是django要使用的view函数 (它是实际的函数对象，而不是函数名字的字符串) view_args是view函数的列表参数, view_kwargs是view函数的字典参数。  view_args和 view_kwargs都不需要包含request这个参数。
process_view()就在django调用view函数之前被调用。
与process_request()相同，process_request()会返回None或者一个HttpResponse对象。
- 如果返回None，django会继续执行其他中间件的process_view()，然后是恰当的view函数。
- 如果返回HttpResponse对象，它就直接返回了，不再执行其他中间件，view等。


>Note
尽量避免使用process_request 或者process_view 来访问request.POST。但是 CsrfViewMiddleware中间件是一个例外，它提供 csrf_exempt() 和 csrf_protect() 两个装饰器来解决此问题。
Accessing request.POST inside middleware from process_request orprocess_view will prevent any view running after the middleware from being able to modify the upload handlers for the request, and should normally be avoided.
The CsrfViewMiddleware class can be considered an exception, as it provides the csrf_exempt() and csrf_protect() decorators which allow views to explicitly control at what point the CSRF validation should occur.

### 3） process_template_response()

process_template_response(request, response)
其中request 是 HttpRequest 对象， response 是一个由django view或者中间件返回的TemplateResponse  对象。
process_template_response()在view使用render渲染一个模版对象完成之后被调用，它必须返回一个render 方法执行后的response对象，它可以修改view中返回的 response.template_name 和 response.context_data，或者为view返回的模板增加一个商标等等。
你不需要明确的渲染响应，当所有的template响应中间件处理完成后会被自动渲染。
带有process_template_response()的中间件将会被自下而上反向执行。

### 4） process_response()

process_response(request, response)
其中request是 HttpRequest 对象， response 是一个django view或者中间件返回的 HttpResponse 或者StreamingHttpResponse对象。
process_response()在所有的响应被返回到浏览器之前执行。
它**必须**返回一个 HttpResponse 或者StreamingHttpResponse 对象，它可以修改response, 或者为 HttpResponse 或StreamingHttpResponse增加一个商标等。
它不像 process_request() 和process_view() 方法可能会被跳过（在他之前有人返回了HttpResponse对象）， process_response()方法一定会被执行。因此，你的process_response() 方法不能依赖于你的process_request()方法。
最后，记住在响应阶段，中间件会被反向执行，你最后在 MIDDLEWARE_CLASSES定义的中间件将会被最先执行。

#### 处理流式响应

不同于HttpResponse，StreamingHttpResponse沒有content属性，因此中间件不能认为所有的响应都有content 属性，如果想要访问content，需要测试流式响应：

```
if response.streaming:
    response.streaming_content = wrap_streaming_content(response.streaming_content)
else:
    response.content = alter_content(response.content)
```

>Note
streaming_content 被假定为太大而不能存放在内存中， 响应中间件可以将它包裹在一个生成器中，但是必须不能消费它，通常如下所示：

```python
def wrap_streaming_content(content):
    for chunk in content:
        yield alter_content(chunk)
```

### 5) process_exception()
process_exception(request, exception)
其中request 是 HttpRequest 对象. exception是view函数中raise的Exception对象。
Django当view函数raise一个例外时调用process_exception() 。process_exception()返回None 或者HttpResponse 对象
- 如果返回 HttpResponse 对象,template response 和response中间件会被应用, 然后在浏览器中返回结果，否则，默认的例外处理将会被使用。
再说一遍，包含process_exception的中间件将会被反向执行，如果下面的中间件返回一个response，上面的中间间将不会被执行。

### 6） __init__()
大多数处理 process_* 方法的中间件都不需要自定义构造函数，如果你确实需要有一些全局的内容需要定义也可以使用，但是注意下面两点：
- Django初始化中间件不会包含任何参数,所以不能在__init__ 要求任何参数；
- 不像process_* 方法在每次请求时调用，__init__方法只会在web server首次处理请求的时候调用。

#### 标记中间件为不可用
有时候在运行的时候决定哪个中间件是否可用是十分必要的，这种情况下你的自定义中间件__init__方法可以 raise django.core.exceptions.MiddlewareNotUsed，django将会移除中间件，并且报一个日志，如果DEBUG打开的话，可以在django.request logger里看到。（1.8之前的版本，MiddlewareNotUsed不会在日志中体现）

### 7）指导意见
- 中间件不继承；
- 中间件写在哪里都行，只需要加到MIDDLEWARE_CLASSES settings中。

---
来源： https://docs.djangoproject.com/en/1.9/topics/http/middleware/
