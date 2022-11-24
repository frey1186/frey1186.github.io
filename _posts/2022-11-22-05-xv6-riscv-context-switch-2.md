---
layout: post
title: 05 xv6-riscv Context Switch 2
date: 2022-11-22 08:45
mdate: 2022-11-22 08:49
tags: xv6 os
categories: os
---


继续上一篇的 context switch 的调试。系统调用的过程后面再详细说明，这里就返回结果了。

# 0x02 内核空间切换到用户空间

当前的函数调用关系如下：

![](/images/2022-11-22-05-xv6-riscv-context-switch-2/sys_write-bt.png)

syscall 的返回值写到了 trapframe 中的 a0，此时已经完成了hello.c内write函数的打印任务
可以看到qemu控制台上已经显示了字符a和回车。

![](/images/2022-11-22-05-xv6-riscv-context-switch-2/syscall-ret.png)

![](/images/2022-11-22-05-xv6-riscv-context-switch-2/bt-syscall.png)

完成后返回到 usertrapret() 函数，它是返回用户空间的必经过程。主要完成下面几件事情：

(1) 首先关闭中断。之前系统调用syscall函数的时候打开的中断，现在又到了操作系统
的关键阶段，状态很微妙，不能被打扰，所以关闭中断；

(2) 保存 `p->trapframe->kernel_satp = r_satp()`，将当前的satp页表首地址保存起来，
这是在返回用户空间需要保存内核页表地址；

(3) `p->trapframe->kernel_sp = p->kstack + PGSIZE`，保存用户进程的内核线程堆栈空间

(4) `p->trapframe->kernel_trap = (uint64)usertrap` 保存usertrap的地址，这个地址是
内核页表下的usertrap地址，其实也是物理地址；其实satp和usertrap每个进程的trapframe
保存的值都是一样的。

(5) `p->trapframe->kernel_hartid = r_tp()`, 这里为啥要保存tp寄存器？tp中保存了当前
hartid，但是用户进程是不能访问mhartid的，所以将这个值保存到tp中。给他保存在trapframe
中使为了让用户进程知道自己运行在哪个hartid中。另外，scheduler 选择进程运行的时候，
需要将scheduler线程运行的hartid写到进程trapframe中的`kernel_hartid`中。

(6) 修改 sstatus 寄存器的 SPP 值，准备返回U-mode；

(7) 准备好用户页表地址，作为 userret 函数的参数，进入到 userret

userret 是返回 U-mode 的最后阶段。userret 在内核空间中有两个地方，1份作为.text保存
在了内核代码段，另1份是映射到了 trampoline 页，和用户空间共享。这里运行的必须是第二份，
否则无法切换到U-mode。

![](/images/2022-11-22-05-xv6-riscv-context-switch-2/usertrapret.png)


userret相对比较简单。进入userret 就开始切换 satp 到用户进程的页表。

```c
# switch to the user page table.
sfence.vma zero, zero
csrw satp, a0
sfence.vma zero, zero
```

![](/images/2022-11-22-05-xv6-riscv-context-switch-2/switch-satp.png)

然后从内存中恢复用户进程使用的所有寄存器，最后调用sret 返回到用户进程。

![](/images/2022-11-22-05-xv6-riscv-context-switch-2/userret-sret.png)

sret 返回之后会切换到 0x2f6 地址，从 user/hello.asm 中可以看到，马上就可以返回到
ecall 之后的ret了，然后再返回到 hello.c 。

这样就完成了一次完整的用户空间通过系统调用陷入内核，并返回到用户空间。这里没有详细
说内核函数`sys_write`的执行过程，后续在补充吧。






