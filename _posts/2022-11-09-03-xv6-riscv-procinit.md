---
layout: post
title: 03-xv6-riscv-进程初始化
date: 2022-11-09 10:45
tags: xv6 os
categories: os
---


main函数中内存初始化完成后进行进程的初始化procinit()，初始化工作相对简单，
主要就是初始化锁、初始化进程的默认值比如状态、进程栈之类的。

```c
// initialize the proc table.
void
procinit(void)
{
  struct proc *p;
  // 初始化锁
  initlock(&pid_lock, "nextpid");
  initlock(&wait_lock, "wait_lock");
  // 初始化进程默认值
  for(p = proc; p < &proc[NPROC]; p++) {
      initlock(&p->lock, "proc");
      p->state = UNUSED;
      p->kstack = KSTACK((int) (p - proc));
  }
}
```

看起来并不复杂，但是关于进程的理解，之前我一直认为进程就是用户程序，这个理解应该
是有偏差的。我觉得应该说进程是内核提供的承载用户程序的容器，它是计算机资源的抽象，
让用户程序认为自己拥有了无限的CPU和巨大的资源，随意取用。

1. 进程是所有CPU全局共享的，所以只在第一个hart上初始化即可，不需要所有hart都执行。

2. 关于锁，关于进程的锁这里有3个，nextpid、wait_lock和进程内的lock。加锁是因为需要
操作一个共享的数据。(1)nextpid就是为了防止多个CPU同时执行分配pid出现并发问题而设置;
(2)wait_lock 修改父进程时使用；(3)进程内的锁为进程状态相关变量操作而设置；
后面单独在研究锁的问题。

3. 初始化进程的状态UNUSED，进程的状态很重要，它标识了该进程能否运行。进程的每个状态其实
关联了好几个变量的值，因此进程状态的操作是需要用锁保护的。

4. 关于进程的kstack，进程中包含的用户程序在用户空间运行，但是进程是在内核中运行的，所以说
进程在内核中需要单独的栈。那为啥不与内核使用相同的栈呢？进程有销毁的时候，需要清空相应的
栈，如果与内核使用相同的栈，销毁可能是个麻烦事。另外，内核的栈空间在没有打开分页的时候就
已经使用。


作为用户程序容器的进程就是由内核来分配和提供的，内核要维护进程的所有东西。内核
需要给每个进程创建一个结构体，估计这是操作系统中最重要的一个结构体。xv6进程的数据结构是
相对简单的，肯定比Linux的简单多了。

```c
struct proc {
  struct spinlock lock;

  // p->lock must be held when using these:
  enum procstate state;        // Process state
  void *chan;                  // If non-zero, sleeping on chan
  int killed;                  // If non-zero, have been killed
  int xstate;                  // Exit status to be returned to parent's wait
  int pid;                     // Process ID

  // wait_lock must be held when using this:
  struct proc *parent;         // Parent process

  // these are private to the process, so p->lock need not be held.
  uint64 kstack;               // Virtual address of kernel stack
  uint64 sz;                   // Size of process memory (bytes)
  pagetable_t pagetable;       // User page table
  struct trapframe *trapframe; // data page for trampoline.S
  struct context context;      // swtch() here to run process
  struct file *ofile[NOFILE];  // Open files
  struct inode *cwd;           // Current directory
  char name[16];               // Process name (debugging)
};
```

结构体中有pagetable_t pagetable，是每个进程单独的页表，当切换到用户程序执行的时候，
就需要进行页表的切换。

proc结构内容比较多，这里只说一部分关于xv6使用的栈空间：

- 内核使用的栈，在entry.S中就定义了，使用了一个数组，保存在了.bss中。每个CPU都定义
了4096的栈空间。
  
  ```c
  // start.c
  // entry.S needs one stack per CPU.
  __attribute__ ((aligned (16))) char stack0[4096 * NCPU];
  ```

- 内核中进程的栈（xv6中描述是process's kernel stack），放在TRAMPOLINE下面, 每个
  进程都有单独的一个4096大小的栈。但是，为啥要空2个PGSIZE呢，因为栈之间需要又有
  一个guard page，它的PTE_V被默认设为0，不可访问，用来防止栈的溢出。

  ```c
  //memlayout.h
  #define KSTACK(p) (TRAMPOLINE - ((p)+1)* 2*PGSIZE)
```


```c
  // proc.c 为进程的栈映射了物理页
  // Allocate a page for each process's kernel stack.
  // Map it high in memory, followed by an invalid
  // guard page.
  void
  proc_mapstacks(pagetable_t kpgtbl)
  {
    struct proc *p;
    
    for(p = proc; p < &proc[NPROC]; p++) { // 每个进程都需要，而且预先分配
      char *pa = kalloc(); // 分配物理page
      if(pa == 0)
        panic("kalloc");
      uint64 va = KSTACK((int) (p - proc)); // 计算虚拟地址
      kvmmap(kpgtbl, va, (uint64)pa, PGSIZE, PTE_R | PTE_W);  // 映射物理页到虚拟地址
    }
  }
  ```

- 用户程序中的栈，每个用户程序运行需要用户空间的自己的栈。

