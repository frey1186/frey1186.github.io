---
layout: post
title: 04 xv6-riscv 中使用的寄存器
date: 2022-11-16 16:43
tags: xv6 os
categories: os
---

记录一些xv6-riscv中使用到的寄存器，特别是`CSR`寄存器相关的内容，
主要记录一些不太好理解的。riscv中详细的寄存器说明和用法参见ISA
文档。


# 1. `medeleg` 和 `mideleg` 寄存器

默认情况下，所有异常和中断都发给M-mode来处理，但是xv6的实现主要都在
S-mode下，这两个寄存器是将异常和中断委托给S-mode的关键所在。寄存器的
名字也很好理解medeleg（M-mode expection delegation register）和mideleg
（M-mode interrupt delegation register），在xv6中只是在初始化操作中
对这两个寄存器进行写操作（kernel/start.c）:

```c
// delegate all interrupts and exceptions to supervisor mode.
w_medeleg(0xffff);
w_mideleg(0xffff);
```

在xv6中的操作十分简单，但是需要理解这两个寄存器的作用。

- `medeleg`：64位寄存器，每个bit与mcause相对应，表示异常的代码（expection code），在FU540文档
中详细说明了异常代码的对应关系。需要将对应的位置1，就可以实现委托异常的目的。
xv6的处理简单直接，将0-15位全部置1。

![](/images/2022-11-16-04-xv6-riscv-some-registers/medeleg.png)


- `mideleg`：64位寄存器，每个bit与mie相对应，如下图所示。
xv6的处理同样直接，将0-15位全部置1。

![](/images/2022-11-16-04-xv6-riscv-some-registers/mideleg.png)



**注意**的一点是，来自高级别的trap是不会被委托给低级别来处理。如果M-mode将trap
委托给了S-mode，那么来自M-mode的软件中断只能给M-mode下处理，不会被委托到S-mode
来处理。而来自S-mode的软件中断则会被M-mode委托给S-mode来处理。



# 2. `PMP`寄存器

PMP是Physical Memory Protection的意思，需要在M-mode下设置指定的寄存器来
限制内存区域的权限，需要在所有hart上执行。

这部分内容，在FU540似乎并没有实现的很完善，但是在ISA中有明确的说明，我感觉
并没有理解。在xv6中kernel/start.c中，如果将这两个初始化的内容注释掉，似乎也能
正常运行。

```c
// configure Physical Memory Protection to give supervisor mode
// access to all of physical memory.
w_pmpaddr0(0x3fffffffffffffull);
w_pmpcfg0(0xf);
```

> 2023-06-22 增加
这两行代码注释调的话，使用新的qemu-system-riscv64 7.2.0 模拟器运行时候，会在start.c最后的mret指令时候无法正确的切换到
S-mode。使用qemu-system-riscv64 4.2 下能正常运行，可能旧版本实现相对粗犷吧。
![](/images/2022-11-16-04-xv6-riscv-some-registers/mret.png)


# 3. `*ip` 和 `*ie`

xv6中主要用到了 sip 和 sie 寄存器， sip = "S-mode interrupt pending"寄存器，保存了发生但是为处理的中断或者异常。 sie寄存器="S-mode interrupt enable", 根据bit位置保存相应的中断或异常是否开启。

下图是FU540中sip各bit位的作用，比 ISA 文档更加直观。

![](/images/2022-11-16-04-xv6-riscv-some-registers/sip.png)

# 4. sstatus 寄存器

sstatus寄存器与mstatus寄存器一样，表示当前cpu状态是否能够接受中断（sstatus.SIE）、 上一次中断是否打开(sstatus.SPIE)、 上一次运行模式(sstatus.SPP)，如果执行 sret 指令，切换中断打开情况和运行模式。

![](/images/2022-11-16-04-xv6-riscv-some-registers/sstatus.png)





