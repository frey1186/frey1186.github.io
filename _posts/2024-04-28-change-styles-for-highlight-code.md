---
layout: post
title: 修改博客中代码高亮的风格
date: 2024-04-28 00:00
tags: pygments
categories: public
---

## 创建虚拟环境

```bash
(py01) frey:~$ python -m venv py02
(py01) frey:~$ source py02/bin/activate
(py02) frey:~$
```

## 安装 pygments

```bash
(py02) frey:~$ pip install pygments
```

## 查看风格

```python
(py02) frey:statics$ python
Python 3.8.10 (default, Nov 22 2023, 10:22:35)
[GCC 9.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from pygments.styles import STYLE_MAP as styles
>>> list(styles.keys())    exptag1
['abap', 'algol', 'algol_nu', 'arduino', 'autumn', 'bw', 'borland', 'colorful', 'default', 'dracula', 'emacs', 'friendly_grayscale', 'friendly', 'fruity', 'github-dark', 'gruvbox-dark', 'gruvbox-light', 'igor', 'inkpot', 'lightbulb', 'lilypond', 'lovelace', 'manni', 'material', 'monokai', 'murphy', 'native', 'nord-darker', 'nord', 'one-dark', 'paraiso-dark', 'paraiso-light', 'pastie', 'perldoc', 'rainbow_dash', 'rrt', 'sas', 'solarized-dark', 'solarized-light', 'staroffice', 'stata-dark', 'stata-light', 'tango', 'trac', 'vim', 'vs', 'xcode', 'zenburn']

>>> s = iter(list(styles.keys()))
>>> a = next(s);print(a);os.system(f"pygmentize -S { a } -f html -a .highlighter-rouge > code.css")   exptag2
```

- exptag1 目前pygments支持的所有styles
- exptag2 将风格列表转化为python生成器，可以逐个查看，其中pygments的参数-a：指作用范围 -S：风格 -f：格式

## 选择喜欢的风格

```python
>>> os.system(f"pygmentize -S pastie -f html -a .highlighter-rouge > code.css")
```

## 把 code.css 安装到指定位置

```bash
$ vim ./_layouts/default.html
$ grep code.css _layouts/default.html
    <link href="/custom/code.css" rel="stylesheet">
$ cp /tmp/code.css ./custom/
```

## 链接

- https://pygments.org/
