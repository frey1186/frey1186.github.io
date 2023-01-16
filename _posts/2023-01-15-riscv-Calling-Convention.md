---
layout: post
title: RISCV Calling Convention 调用规则
date: 2023-01-15 10:46
mdate: 2023-01-16 10:46
tags: xv6 os
categories: os
---

参考文档里介绍了32位和64位的规格，只关注64位。
操作系统部分涉及到的指令集其实不太多，比如浮点单元之类的就不需要。


## 数据类型

RV64 中 C 类型定义如下：

- int： 32bit，符号扩展
- long： 64 bit （== size of registers）
- void*： 64bit
- long long 64bit
- float: 32bit
- double: 64bit
- long double : 128bit
- char : 8bit unsigned int，0 扩展 （注意！）
- unsigned char : 8bit unsigned int，0 扩展
- unsigned short: 16bit unsigned int, 0 扩展
- signed char: 8bit int, 符号扩展
- short: 16bit, 符号扩展


## 参数：

RV64中约定，尽可能使用寄存器来传递参数，最多8个（a0-a7，浮点fa0-fa7），一般按顺序传递。

小于64位的参数，将在寄存器低位上存储，RV64是小端（little edtion）系统。

2\*64bit大小的参数，使用两个寄存器进行存储，并且对齐。

大于两倍的参数，使用引用传参

没有使用寄存器传参的使用stack，sp指向第一个；

## 返回值：

返回值保存在a0，如果不够a1，（同样的浮点寄存器就是fa0，fa1）。 只有很小的返回值才直接放入寄存器，大个的返回值都将保存在内存中。

caller（调用者）分配内存，callee（被调用者）将值写入到指定位置。


## 栈

标准RV调用中，栈向下增长，并16bit对齐。


## 其他寄存器

t0-t6，是在函数中临时使用的，由caller保存；
s0-s11，如果使用，由callee保存；

总结图如下：

![](/images/2023-01-15-riscv-Calling-Convention/caller-callee.png)



## xv6-riscv中的swtch函数

参考[https://github.com/mit-pdos/xv6-riscv/blob/riscv/kernel/swtch.S](https://github.com/mit-pdos/xv6-riscv/blob/riscv/kernel/swtch.S)

函数swtch，为了与C关键字switch区别，改为swtch，它的作用是xv6中切换内核线程, 不过使用汇编代码编写，如果用C定义如下：

```c 
void swtch(struct context *old, struct context *new);
```

内核线程之间切换，它们同属一个内核运行进程中，其实就是寄存器的切换。 根据上面说到的规则（gcc或其他编译器，会保证规则被正确使用），需要保存和恢复的寄存器是：

- ra： 函数返回值
- sp： 栈地址
- s0-s11：可能被callee使用的寄存器


# 参考

- [https://pdos.csail.mit.edu/6.828/2020/readings/riscv-calling.pdf](https://pdos.csail.mit.edu/6.828/2020/readings/riscv-calling.pdf)
- [https://github.com/mit-pdos/xv6-riscv/blob/riscv/kernel/swtch.S](https://github.com/mit-pdos/xv6-riscv/blob/riscv/kernel/swtch.S)
