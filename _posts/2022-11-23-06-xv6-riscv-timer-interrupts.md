---
layout: post
title: 06 xv6-riscv 时钟中断的实现
date: 2022-11-23 17:13
mdate: 2022-11-26 10:29
tags: xv6 os
categories: os
---

riscv 中运行模式有M-mode、S-mode、U-mode三种，xv6-riscv主要使用了S-mode和U-mode两个。
其中S-mode运行内核，U-mode运行用户程序。



# 0x01 riscv运行模式之间的切换

xv6-riscv 中存在多个切换的过程，比如系统调用要从 U-mode 切换到 S-mode，内核完成任务有就
再次切换到 U-mode 。

## 1. 低级别向高级别切换

- ecall 指令，从 U-mode 切换到 S-mode； 其实也并不是直接切换到 S-mode，而是先切换到 M-mode，因为 M-mode的系统调用被委托给了 S-mode，所以由 S-mode 来处理；
- 时钟中断，xv6中时钟中断在 M-mode 中，由每个 cpu 定时产生，所以这里是 U-mode 切换到 M-mode 。
- 软件中断，同样，U-mode切换到委托的 S-mode。 xv6中的软件中断只是由 时钟中断 产生的。
- 设备中断，Uart 和 virtio 等，暂不说明；

## 2. 高级别向低级别切换

- mret，该指令执行后会设置权限级别=mstatus.MPP,mstatus.MIE = mstatus.MPIE; mstatus.MPIE = 1;pc = mepc;
- sret, 同上，mstatus替换为sstatus即可。

# 0x02 时钟中断的实现

时钟中断，也叫定时器中断，是本地中断，每个CPU都有，需要先初始化相关的寄存器。

## 1. timer 初始化

时钟中断初始化工作在设备一启动的时候就开始了，在kernel/start.c里timerinit()函数。 时钟中断是每个CPU单独执行，初始化也需要按CPU执行。

```c
   62 void
   63 timerinit()
   64 {
   65   // each CPU has a separate source of timer interrupts.
   66   int id = r_mhartid();
   67
   68   // ask the CLINT for a timer interrupt.
   69   int interval = 1000000; // cycles; about 1/10th second in qemu.
   70   *(uint64*)CLINT_MTIMECMP(id) = *(uint64*)CLINT_MTIME + interval;
   71
   72   // prepare information in scratch[] for timervec.
   73   // scratch[0..2] : space for timervec to save registers.
   74   // scratch[3] : address of CLINT MTIMECMP register.
   75   // scratch[4] : desired interval (in cycles) between timer interrupts.
   76   uint64 *scratch = &timer_scratch[id][0];
   77   scratch[3] = CLINT_MTIMECMP(id);
   78   scratch[4] = interval;
   79   w_mscratch((uint64)scratch);
   80
   81   // set the machine-mode trap handler.
   82   w_mtvec((uint64)timervec);
   83
   84   // enable machine-mode interrupts.
   85   w_mstatus(r_mstatus() | MSTATUS_MIE);
   86
   87   // enable machine-mode timer interrupts.
   88   w_mie(r_mie() | MIE_MTIE);
   89 }
```

kernel/memlayout.h 中定义了定时器相关的内存位置，这几个位置按照手册设置即可。CLINT_MTIME表示从系统启动之后的CPU 执行次数，即表示系统启动后到当前的时间。 CLINT_MTIMECMP 表示一个未来的时间，当不断增加的 CLINT_MTIME 与 CLINT_MTIMECMP 相等的时候，就产生一次定时器中断。

```c
// core local interruptor (CLINT), which contains the timer.
#define CLINT 0x2000000L
#define CLINT_MTIMECMP(hartid) (CLINT + 0x4000 + 8*(hartid))
#define CLINT_MTIME (CLINT + 0xBFF8) // cycles since boot.
```

其他的过程相对简单，主要是这里使用了一个数组来存放定时器相关信息(scratch数组)。
scratch数组包含5个元素：

- scratch[0,1,2] 保存三个寄存器，用来计算新的CLINT_MTIMECMP(id);
- scratch[3] = CLINT_MTIMECMP(id);
- scratch[4] = interval;

为啥需要这三个uint64类型的寄存器，主要是执行汇编计算新CLINT_MTIMECMP(id)的需要，可以看kernel/kernelvec.S: timervec 里面的内容。我觉得也可以用C实现，就不需要这个复杂的scratch数组，
但整个过程可能未必比用timervec实现更简单。


## 2. timervec

在timerinit()里设置了mtvec寄存器的值为timervec函数的地址。那么在时钟中断到来的时候，就会切换到timervec。timervec主要工作也很简单，主要如下三点：

（1）设置新的CLINT_MTIMECMP值，准备好下一个时钟中断的条件；

（2）起一个软件中断，而且是S-mode级别的软件中断，就切换到了S-mode来处理。

（3）mret，返回用户空间。

最主要的是xv6的时钟中断并没有设置一个复杂的trap处理函数，它相当于把时钟中断委托给了S-mode的软件中断。
这里有一个特别的地方，时钟中断时不能被屏蔽的，但是S-mode软件中断是可以被打断或者关闭的。

有个疑惑： 为什么时钟中断要在M-mode下实现，而不是S-mode下实现？ 我想是因为在内核中有`关闭中断`的操作，如果S-mode中断被关闭了，那么可能出现永远没办法中断的情况。但是在M-mode启用时钟中断就不同，永远可能按时产生时钟中断。

## 3. 执行过程

启动GDB之后，给timerinit和timervec设置断点，先执行到timerinit

![](/images/2022-11-22-06-xv6-riscv-timer-interrupts/b-timervec.png)

使用n执行完成scratch赋值

![](/images/2022-11-22-06-xv6-riscv-timer-interrupts/print-scratch.png)

完成设置 mstatus 和 mie 之后

![](/images/2022-11-22-06-xv6-riscv-timer-interrupts/print-mstatus.png)

这就完成初始化，c执行到timervec，开始处理时钟中断，设置sip=2，可以触发S-mode软件中断。

![](/images/2022-11-22-06-xv6-riscv-timer-interrupts/set-sip.png)

然后恢复a0-a2三个寄存器，并mret返回到触发时钟中断的位置。

这个sip=2 S-mode的软件中断，那么什么时候能触发呢？ 如何触发？ 可以参考 ISA 文档中`4.1.3 sip`寄存器，
只有当前是 S-mode或更低级别，并且设置好status，sie相关bit后，才能触发。


# 0x03 软件中断

上一节说到timer中断处理函数将sip寄存器设置为2，即手动为S-mode添加一个中断，可见产生了一个S-mode下的软件中断。

![](/images/2022-11-22-06-xv6-riscv-timer-interrupts/sip-2.png)

因为设置sip的运行状态在M-mode，所以该中断不会被立即触发，待时钟中断返回后，即触发这个软件中断。

不管是用户空间(usertrap()函数),还是内核空间(kerneltrap()函数)都会达到 devintr()函数来选择不同的trap触发类型，可以查看scause的trap类型，S-mode软件中断的ID=1。

![](/images/2022-11-22-06-xv6-riscv-timer-interrupts/soft-intr.png)

所以有如下代码实现：

```c
// kernel/trap.c 
204   } else if(scause == 0x8000000000000001L){
205     // software interrupt from a machine-mode timer interrupt,
206     // forwarded by timervec in kernelvec.S.
207
208     if(cpuid() == 0){
209       clockintr();
210     }
211
212     // acknowledge the software interrupt by clearing
213     // the SSIP bit in sip.
214     w_sip(r_sip() & ~2);
215
216     return 2;
```


这里还有一个当CPU=0时候clockintr()的操作，为时钟中断计数ticks。

```c 
163 void
164 clockintr()
165 {
166   acquire(&tickslock);
167   ticks++;
168   wakeup(&ticks); // wakeup 这个比较复杂，后面再说
169   release(&tickslock);
170 }
``` 

对于这里软件中断（或者说时钟中断）最终devintr返回值是2，通过判断返回值，再进行时钟中断的相关动作，其实主要就是yield放弃CPU。


到这里时钟中断就基本完事了。

# 参考

- FU540-C000-v1.0.pdf
- riscv-privileged.pdf
