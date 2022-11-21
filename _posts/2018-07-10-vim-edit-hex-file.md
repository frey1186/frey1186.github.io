---
layout: post
title: 使用VIM编辑16进制
date: 2018-07-10 12:00
author: felo
tags: vim
categories: public
typora-root-url: ..
---


首先以二进制方式编辑这个文件:

```bash
 vim -b datafile
```

用 xxd 把这个文件转换成十六进制:

```bash
 :%!xxd
```

文本看起来像这样:

```bash
0000000: 1f8b 0808 39d7 173b 0203 7474 002b 4e49  ....9..;..tt.+NI 
0000010: 4b2c 8660 eb9c ecac c462 eb94 345e 2e30  K,.`.....b..4^.0 
0000020: 373b 2731 0b22 0ca6 c1a2 d669 1035 39d9  7;'1.".....i.59. 
```

编辑完成之后，可以转换回来:

```bash
:%!xxd -r
```

> 注意：只有十六进制部分的修改才会被采用。右边可显示文本部分的修改忽略不计。

