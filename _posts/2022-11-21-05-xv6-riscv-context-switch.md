---
layout: post
title: 05 xv6-riscv Context Switch 1
date: 2022-11-21 16:07
tags: xv6 os
categories: os
---

经常说到context switch，可能有好几种理解，比如说用户空间切换到内核空间，
比如用户内核线程之间发生切换，再比如用户进程切换到另一个进程，可能都会被认为
是context swtich，下面记录一下xv6中这几种切换的过程吧。

下面说到的一些过程，主要是我个人的学习中的一些理解，不一定完全准确，有问题
的以后再修正。

# 0x00 几个概念之间的区别和联系

- 内核空间和用户空间

我想直观的理解，用户空间就是运行在U-mode的过程，内核空间就是运行在M-mode和S-mode中。
xv6的时钟中断处理会有一小段在M-mode中，还有就是初始化start.c运行在M-mode中，其余内核
空间均在S-mode。

那么用户空间如何切换到内核空间呢，主要是通过trap（中断+异常+系统调用ecall指令），内核
空间切换到用户空间使用sret指令（M-mode就是mret）。

- 用户进程和线程、内核线程

xv6中用户进程中只有一个线程，也就是常规理解的用户空间是多进程运行。而在xv6内核中，是多
线程的结构，就是说内核中同时运行多个线程并共享内核内存空间等。

内核线程我觉得比较难以理解。xv6内核中的内核线程由regs、stack组成，说白了，CPU数量是有限的，
运行过程中肯定是要进行线程切换的，那么内核线程要想恢复运行，必须在切换的时候将内核线程的状态
保存起来。xv6中内核线程有（1）每个CPU包含的调度器scheduler线程，（2）每个进程在内核中的线程。

# 0x01 用户空间切换到内核空间

这里记录xv6中一个用户进程触发系统调用后返回结果的过程。

## 1. 一个简单的用户程序

编写一个简单的用户程序，有一个write系统调用，在“标准输出”输出一个字符a并回车，如下：

```c
// user/hello.c
#include "kernel/types.h"
#include "kernel/stat.h"
#include "user/user.h"

int main(){
    write(1,"a\n",2); // write系统调用会切换到内核空间
    return 0;
}
```

其中write函数的声明在user/user.h中

```c
int write(int, const void*, int);
```

write函数的定义在user/usys.S中：

```c
.global write
write:
 li a7, SYS_write
 ecall
 ret
```

当用户程序执行到write的时候，a0, a1, a2 会保存传入参数，a7保存系统调用的id，
然后执行ecall。

修改Makefile，将hello.c文件加入到其中，就可以进行调试测试。

```
// 在 Makefile中添加hello编译
UPROGS += $U/_hello
```

如果我们执行 make 之后，可以看到 user/hello.asm 中的 hello.c 生成的 asm 文件：

```
 #...
  17     write(1,"a\n",2);
  18    8:   4609                    li  a2,2
  19    a:   00000597            auipc   a1,0x0
  20    e:   7e658593            addi    a1,a1,2022 # 7f0 <malloc+0xea>
  21   12:   4505                    li  a0,1
  22   14:   00000097            auipc   ra,0x0
  23   18:   2dc080e7            jalr    732(ra) # 2f0 <write>
 #...
 539 00000000000002f0 <write>:
 540 .global write
 541 write:
 542  li a7, SYS_write
 543  2f0:   48c1                    li  a7,16
 544  ecall
 545  2f2:   00000073            ecall
 546  ret
 547  2f6:   8082                    ret
 #...
```

## 2. ecall 切换到内核

write 函数调用 ecall 之后，就会陷入到内核中。在 xv6-riscv book rev3 文档中有明确的说明。

(1) 关闭中断，当然只是关闭该CPU的中断，其他CPU不会影响；

(2) 把pc寄存器值保存到epc；

(3) 保存当前mode到sstatus的SPP位，这里就是将U-mode保存；

(4) trap 的原因保存到scause中，syscall对应的cause id = 8；

(5) U-mode切换为S-mode；

(6) stvec中的值拷贝到pc寄存中；

然后继续执行。上述的过程都是硬件执行的，对于内核来说无法控制过程，只能应用上面的结果。


从这里看ecall执行之后，pc会指向stvec中的值。在$stvec上设置一个break，

![](/images/2022-11-21-05-xv6-riscv-context-switch/stvec.png)

继续执行，就切换到 trampoline 页，也就是 MAXVM 的最后一页。

![](/images/2022-11-21-05-xv6-riscv-context-switch/trampoline.png)

trampoline 页就是将 trampoline.S 文件生成的执行文件放到里面，它内部有2个符号，uservec和userret，
uservec就是从用户空间进入内核要执行的第一段代码。

uservec 保存用户空间的寄存器（从ra到t6）和其他一些内容到 `p->trapframe`，这个trapframe就是
用于保存用户进程的状态。然后切换到 usertrap():

![](/images/2022-11-21-05-xv6-riscv-context-switch/uservec.png)

得到usertrap的地址，赋值到t0，但是我们没办法直接获得usertrap符号的地址，那是因为
到现在为止，还没有切换到内核页表。也就是说现在虽然S-mode在运行，但是仍然在用户页表
中执行。现在可以说是操作系统非常奇怪的状态，也可以说是操作系统的用户和内核的切换
过程中，非常的脆弱，任何一点问题都会导致panic。

![](/images/2022-11-21-05-xv6-riscv-context-switch/uservec-2.png)

这下就终于进入到 trap.c:usertrap() 里了，有一个sepc寄存器的处理，从前面硬件操作中可以看到
epc已经设置为用户进程ecall时候的pc值了，这里需要将返回的pc值（p->trapframe->epc）准备好，
可以想象得到，我们是因为 syscall 进入到了内核，所以 p->trapframe->epc = $sepc+4。（为啥+4，
因为ecall指令正好占用4个字节。）

![](/images/2022-11-21-05-xv6-riscv-context-switch/usertrap-syscall.png)

使用GDB调试也可看到现在 p->trapframe->epc 已经保存了用户进程 ecall 指令的位置，未来返回
的时候再加4，这样就到了ecall下一条指令。

![](/images/2022-11-21-05-xv6-riscv-context-switch/usertrap-sepc.png)

设置好 p->trapframe->epc 之后，打开中断。（可以被打断执行了，这之前的所有操作，都是不可打断的。）

然后切换到 syscall() 函数。

![](/images/2022-11-21-05-xv6-riscv-context-switch/syscall.png)

syscall()函数是一个分配器，num 对应的系统调用的id，正如前面我们看到的 write 对应的id=16。
然后syscall切换到数组函数对应的sys_write函数执行真正的工作，并将返回值写到 p->trapframe->a0 中。

![](/images/2022-11-21-05-xv6-riscv-context-switch/sys_write.png)


下一篇继续...

# 参考

1. [book-riscv-rev3.pdf](https://pdos.csail.mit.edu/6.1810/2022/xv6/book-riscv-rev3.pdf)
