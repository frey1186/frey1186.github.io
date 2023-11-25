---
layout: post
title: 09-xv6-riscv-proc-state
date: 2022-12-07 17:30
mdate: 2022-12-07 17:30
tags: xv6 os
categories: os
---


xv6中进程的状态比真正的操作系统要少一些，有以下几种：

```c 
// proc.h: 82
enum procstate { UNUSED, USED, SLEEPING, RUNNABLE, RUNNING, ZOMBIE };
```

- UNUSED 和 USED

xv6中的进程用一个数组来表示 proc[NPROC] ，第一步是在进程初始化的时候，将所有的进程状态都置位 UNUSED (proc.c:procinit)。然后在必要的时候内核会调用 allocproc 分配一个进程，这时会将找到的那个proc数组成员作为新进程，将该进程的状态置为 USED 。 当然，分配一个进程还需要分配 pid，p->trapframe, p->pagetable, 设置 p->context 内容。

- RUNNABLE, RUNNING, SLEEPING

这三个状态是进程的主要状态，他们之间的切换最是关键。

- ZOMBIE










