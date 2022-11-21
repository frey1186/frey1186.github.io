## **OpenMP简介**

- https://blog.csdn.net/magicbean2/article/details/75530667
- https://computing.llnl.gov/tutorials/openMP/#EnvironmentVariables

**（这篇翻译只涉及与C/C++相关的代码和示例，忽略了与Fortran相关的代码和示例，感兴趣的读者可以参考原文）**

### **1 摘要**

OpenMP是由一组计算机硬件和软件供应商联合定义的应用程序接口（API）。OpenMP为基于共享内存的并行程序的开发人员提供了一种便携式和可扩展的编程模型，其API支持各种架构上的C/C++和Fortran。本教程介绍了OpenMP 3.1的大部分主要功能，包括并行区域，工作共享，同步和数据环境的构造和指令。我们同时也包含了对运行时库函数 （Runtime library）和环境变量的介绍。本教程包括C和Fortran的示例代码和实验练习（译注：译者在这里忽略了Fortran语言的示例代码和实验练习）。

先决条件：本教程非常适合那些正在使用OpenMP进行并行编程的人员，需要对C或者Fortran语言中的并行编程有一定了解。对于并行编程的一般概念尚不了解的读者，[EC3500: Introduction to Parallel Computing ](https://computing.llnl.gov/tutorials/parallel_comp/)可能会非常有帮助（译注：译者在此博客上也翻译了这篇帖子，请参见 [[并行计算\] 1. 并行计算简介](http://blog.csdn.net/magicbean2/article/details/75174859)）。

### **2. 介绍**

![这里写图片描述](https://computing.llnl.gov/tutorials/openMP/images/openmpLogo.200pix.gif)

**OpenMP是：** 
一组应用程序接口（Application Program Interface, API）,可以用来显式地指导多线程、共享内存式程序的并行化。

由如下三个主要API组件构成：

1） 编译器指令；

2） 运行时库函数；

3） 环境变量。

是 **Open Multi-Processing** 的简称。

**OpenMP不是：**

- OpenMP不是分布式内存并行系统；
- 需要所有供应商一致地实现；
- 保证最有效地利用共享内存；
- 需要程序员去显式地检查数据依赖性、数据冲突、竞争条件、思索，或者导致程序无法保持一致性的代码序列；
- 支持并行I/O操作，但程序员需要负责保证I/O的同步。

**OpenMP的目标：**

- 标准化：1）在各种共享内存架构/平台之间提供一套标准；2）由一批主要的计算机硬件和软件供应商联合定义和支持。
- 精简性：1）位共享内存机器上的编程提供一套简单而有限的指令；2）主要的并行化仅仅通过3-4个指令就可以实现；3）显然，随着新版本的不断发布，该目标变得越来越没有意义。
- 易用性：1）提供了对串行程序进行增量并行的能力，而不像消息传递库那样需要全有或全无的方法（all or nothing approach）；2）提供了实现粗粒度和细粒度并行化的能力。
- 可移植性：1）该API基于C/C++和Fortran进行定义；2）提供了公开的API和会员论坛；3）已经在大多数计算平台上实现，包括Unix/Linux平台和Windows平台。

**历史：**

在90年代早期，共享内存机器的供应商提供了类似的，基于指令式的对Fortran语言的扩展：1）用户可以对一段串行的Fortran程序通过指令进行增量修改，指定需要并行化的部分；2）编译器将自动地对这些循环通过跨SMP处理器进行并行化。这种实现在功能上是相似的，但是内部却存在不一致。

第一次标准化的尝试是1994年的ANSI X3H5草稿。它从来未被实施，很大程度上是由于当时大家对分布式内存机器更感兴趣。

但此后不久，更新的共享式内存机器架构开始变得主流。从1997年开始，OpenMP标准开始制定，接过了ANSI X3H5的遗产。由OpenMP架构审查委员会（ARB）领导的原始ARB成员和贡献者如下所示（免责声明：以下合作伙伴名称均来自 [OpenMP网站](http://www.openmp.org/)）。

| APR成员                                | 程序开发者                                       | 软件供应商                         |
| -------------------------------------- | ------------------------------------------------ | ---------------------------------- |
| Compaq / Digital                       | ADINA R&D, Inc.                                  | Absoft Corporation                 |
| Hewlett-Packard Company                | ANSYS, Inc.                                      | Edinburgh Portable Compilers       |
| Intel Corporation                      | Dash Associates                                  | GENIAS Software GmBH               |
| International Business Machines (IBM)  | Fluent, Inc.                                     | Myrias Computer Technologies, Inc. |
| Kuck & Associates, Inc. (KAI)          | ILOG CPLEX Division                              | The Portland Group, Inc. (PGI)     |
| Silicon Graphics, Inc.                 | Livermore Software Technology Corporation (LSTC) |                                    |
| Sun Microsystems, Inc.                 | MECALOG SARL                                     |                                    |
| U.S. Department of Energy ASCI program | Oxford Molecular Group PLC                       |                                    |
|                                        | The Numerical Algorithms Group Ltd.(NAG)         |                                    |

**发布历史：**

OpenMP目前仍然在不断的演进中——新的构件和特征在新版本中不断被添加。最开始，C和Fortran的API定义被分开发布，但从2005年开始，它们被一起发布。下面的列表总结了OpenMP的发布历史。

| 时间       | 版本        |
| ---------- | ----------- |
| 1997年10月 | Fortran 1.0 |
| 1998年10月 | C/C++ 1.0   |
| 1999年11月 | Fortran 1.1 |
| 2000年11月 | Fortran 2.0 |
| 2002年3月  | C/C++ 2.0   |
| 2005年5月  | OpenMP 2.5  |
| 2008年5月  | OpenMP 3.0  |
| 2011年7月  | OpenMP 3.1  |
| 2013年7月  | OpenMP 4.0  |
| 2015年11月 | OpenMP 4.5  |

注意：本指南基于OpenMP 3.1，所有此后新版本的语法和特征并没有包含在此。

**参考资料：**

- OpenMP官方网站：[OpenMP.org](http://www.openmp.org/)，包含API定义，常见问题，报告，讨论，多媒体，日程，会员应用等。
- 维基百科：[en.wikipedia.org/wiki/OpenMP](https://en.wikipedia.org/wiki/OpenMP)。

### **3. OpenMP编程模型**

**共享内存模型：** OpenMP专为多处理器/多核机器而设计。其底层架构可以是共享内存的UMA或者NUMA。

![这里写图片描述](https://computing.llnl.gov/tutorials/openMP/images/shared_mem.gif) 
统一内存访问（Uniform Memory Access）

![这里写图片描述](https://computing.llnl.gov/tutorials/openMP/images/numa.gif) 
非统一内存访问

**基于线程的并行化：** 1）OpenMP程序通过使用线程来完成并行化；2）线程是可由操作系统调度的最小处理单元，其特点是可以安排自主运行的子程序；3）线程存在于单个进程的资源中，如果没有这个进程，那么线程也就不存在了；4）通常，线程数与机器处理器/内核的数量相匹配，但是线程的实际使用也取决于具体的应用程序。

**显式并行化：** 1）OpenMP是一个显式的（而不是自动的）编程模型，为编程者提供了对并行化的完全控制；2）并行化可以简单到仅仅为一段串行程序添加几条编译器指令……3）或者复杂到插入子程序，以建立多层次的并行机制、锁甚至嵌套锁。

**分叉-合并模型：** 1）OpenMP采用分叉-合并模型（fork-join）实现并行化。2）所有的OpenMP程序都从一个 **主线程** 开始。主线程串行执行，直到遇到第一个**并行区域**。3）**分叉**：之后主线程将创建一组并行线程。4）并行区域内的代码被用大括号包围起来，然后在多个并行线程上被并行执行。5）**合并**：当并行线程执行完成并行区域内的代码之后，它们进行同步并且自动结束，只剩下主线程。6）并行区域的数量以及并行线程的数量都可以是任意的。

![这里写图片描述](https://computing.llnl.gov/tutorials/openMP/images/fork_join2.gif)

**基于编译器指令：** 大多数OpenMP的并行化都是通过在C/C++或者Fortran中嵌入编译器指令而实现的。

**嵌套并行：** 1）API运行在并行区域内再次嵌入并行区域；2）软硬件实现中可能支持，也可能不支持此功能。

**动态线程：** 1）API也提供了运行时环境，来动态第更改用于执行并行区域的线程数，在有可能的情况下尽可能地有效利用已有资源；2）软硬件实现中可能支持，也可能不支持此功能。

**输入输出 (I/O)：** 1）OpenMP没有对并行I/O做出规定，所以对于多个线程尝试读写同一个文件的情况要特别小心；2）但如果每个线程对不同的文件进行I/O操作，则问题并不重要；3）编程者有完全责任确保I/O在多线程中被正确地执行。

**内存模型：频繁更新（flush）？** 1）OpenMP在线程内存中提供了一种“松弛一致性”（relaxed-consistency）和“临时视图”（temporary view）。那就是说，线程可以“缓存”它们的数据，而不必要在任何时刻都保持内存数据的实时精确一致性；2）在所有线程都查看共享变量的关键时刻，编程者需要确保所有所有线程都根据需要更新了共享数据。3）更多关于这个……

### **4. OpenMI API总览**

**三类组件：** OpenMP API包含三个不同的组件：

- 编译器指令（44个）；
- 运行时库函数（35个）；
- 环境变量（13个）。

由应用程序开发者决定如何使用这些组件。在最简单的情况下，仅仅需要它们中的几个就可以完成并行化。

对所有API组件的实现方式可能会有所不同。例如某种实现可以表示它支持嵌套并行化，但是API却可能让它们只限于主线程。这并不是编程者所期待的？

**编译器指令：** 编译器指令在你的源代码中可能被显示为注释，并且被编译器所忽略，除非你明显地告诉编译器——通常情况下是设置适当的编译器标识，这将在 [5. OpenMP程序编译](https://blog.csdn.net/magicbean2/article/details/75530667#sec_5) 中进行讨论。

OpenMP的编译器指令的目标主要有：1）产生一个并行区域；2）划分线程中的代码块；3）在线程之间分配循环迭代；4）序列化代码段；5）同步线程间的工作。

编译器指令的语法如下：

```
sentinel directive-name [clause, ...]
```

例如下面的指令，我们将在随后详细介绍这些指令。

```
#pragma omp parallel default(shared) private(beta,pi)
```

**运行时库函数：** OpenMP API中的运行时库函数是不断增长的，其主要目标包括：

1）设置和查询线程数；

2）查询线程的唯一标识符（ID），线程的祖先标识符，或者线程组的大小等；

3）设置和查询动态线程的属性；

4）查询是否在并行须臾，以及在什么级别的并行区域中；

5）设置和查询嵌套并行；

6）设置、初始化以及终止锁或者嵌套锁；

7）查询挂钟时间和分辨率。

对C/C++而言，所有的运行时库函数都是子程序。例如：

```
#include <omp.h>
int omp_get_num_threads(void)
```

注意对于C/C++，你通常需要包含头文件`<omp.h>`，并且是大小写敏感的。运行时库函数将在 [7. 运行时库函数](https://blog.csdn.net/magicbean2/article/details/75530667#sec_7) 一节中简单讨论，更多的细节可以参考 [附录A：运行时库函数](https://blog.csdn.net/magicbean2/article/details/75530667#app_A)。

**环境变量：** OpenMP提供了一些环境变量，用来在运行时对并行代码的执行进行控制。这些环境变量可以控制：

1）设置线程数；

2）指定循环如何划分；

3）将线程绑定到处理器；

4）启用/禁用嵌套并行，设置最大的嵌套并行级别；

5）启用/禁用动态线程；

6）设置线程堆栈大小；

7）设置线程等待策略。

设置OpenMP的环境变量与设置其它环境变量是一样的，它取决于你使用的是什么Shell。例如：

| Shell名称 | 设置方法                 |
| --------- | ------------------------ |
| csh/tcsh  | setenv OMP_NUM_THREADS 8 |
| sh/bash   | export OMP_NUM_THREADS=8 |

关于OpenMP环境变量的详细讨论可见：[8. 环境变量](https://blog.csdn.net/magicbean2/article/details/75530667#sec_8)。

**OpenMP的一个代码结构示例：**

```
#include <omp.h>
main ()
{
   int var1, var2, var3;
   Serial code 
         .
         .
         .
   Beginning of parallel region. Fork a team of threads.
   Specify variable scoping 

   #pragma omp parallel private(var1, var2) shared(var3) 
   {
      Parallel region executed by all threads 
                 .
      Other OpenMP directives
                 .
      Run-time Library calls
                 .
      All threads join master thread and disband
   }
   Resume serial code
         .
         .
         .
}
```

### **5. OpenMP程序编译**

**LC OpenMP实现：** 截止2017年6月，LC默认编译器的文档声称对OpenMP的支持如下：

| 平台         | 编译器               | 版本标识  | 默认版本        | 支持版本                |
| ------------ | -------------------- | --------- | --------------- | ----------------------- |
| **Linux**    | Intel C/C++, Fortran | –version  | 16.0.3          | OpenMP 4.0              |
|              | GNU C/C++, Fortran   | –version  | 4.4.7 (TOSS 2)  | OpenMP 3.0              |
|              |                      |           | 4.9.3 (TOSS 3)  | OpenMP 4.0              |
|              | PGI C/C++, Fortran   | -v        | 8.0.1 (TOSS 2)  | OpenMP 3.0              |
|              |                      | –version  | 16.9-0 (TOSS 3) | OpenMP 3.1              |
|              | Clang C/C++          | –version  | 3.7.0 (TOSS 2)  | OpenMP 3.1              |
|              |                      |           | 4.0.0 (TOSS 3)  | Some OpenMP 4.0 and 4.5 |
| **BG/Q**     | IBM XL C/C++         | -qversion | 12.1            | OpenMP 3.1              |
|              | IBM XL Fortran       | -qversion | 14.1            | OpenMP 3.1              |
|              | GNU C/C++, Fortran   | –version  | 4.4.7           | OpenMP 3.0              |
| **CORAL EA** | IBM XL C/C++         | -qversion | 14.01 beta      | OpenMP 4.5              |
|              | IBM XL Fortran       | -qversion | 16.01 beta      | OpenMP 4.5              |
|              | GNU C/C++            | –version  | 4.9.3           | OpenMP 4.0              |
|              | GNU Fortran          | –version  | 4.8.5           | OpenMP 3.1              |
|              | PGI C/C++, Fortran   | -V        | 17.4-0          | OpenMP 3.1              |
|              |                      | –version  | 17.4-0          | OpenMP 3.1              |
|              | Clang C/C++          | –version  | 4.0 beta        | OpenMP 4.5              |
|              | xlflang Fortran      | –version  | 4.0 beta        | OpenMP 4.5              |

为了查看所有的LC编译器版本，请使用下述命令：

> TOSS 2, BG/Q：`use -l compilers` 
> TOSS 3, CORAL EA：`module avail`

可以在这里查看编译器对OpenMP的支持情况：<http://openmp.org/wp/openmp-compilers/>。

**编译：** 所有的LC编译器都需要你使用适当的编译器标识来“打开”OpenMP的编译选项。下面的表格给出了每种编译器需要使用的编译器标识。关于MPI的编译器命令可以参见 [这里](https://computing.llnl.gov/tutorials/mpi/#BuildScripts)。

| 编译器平台    | 编译器命令         | OpenMP标识0 |
| ------------- | ------------------ | ----------- |
| **Intel**     | icc                | -qopenmp    |
| Linux         | icpc               | -openmp     |
|               | ifort              |             |
| **GNU**       | gcc                | -fopenmp    |
| Linux         | g++                |             |
| IBM Blue Gene | g77                |             |
| CORAL EA      | gfortran           |             |
| **PGI**       | pgcc               | -mp         |
| Linux         | pgCC               |             |
| CORAL EA      | pgf77              |             |
|               | pgf90              |             |
| **Clang**     | clang              | -fopenmp    |
| Linux         | clang++            |             |
| CORAL EA      |                    |             |
| **xlflang**   | xlflang            |             |
| CORAL EA      |                    |             |
| **IBM XL**    | bgxlc_r, bgcc_r    | -qsmp=omp   |
| Blue Gene *   | bgxlC_r, bgxlc++_r |             |
|               | bgxlc89_r          |             |
|               | bgxlc99_r          |             |
|               | bgxlf_r            |             |
|               | bgxlf90_r          |             |
|               | bgxlf95_r          |             |
|               | bgxlf2003_r        |             |
| **IBM XL**    | xlc_r              | -qsmp=omp   |
| CORAL EA *    | xlC_r, xlc++_r     |             |
|               | xlf_r              |             |
|               | xlf90_r            |             |
|               | xlf95_r            |             |
|               | xlf2003_r          |             |
|               | xlf2008_r          |             |

\* 请确保采用线程安全的编译器——它的名字以 **_r** 结尾。

编译器文档：

- Intel和PGI：其编译器文档可参见：/opt/compilername。更多信息可参见Intel和PGI的网页。
- IBM BlueGene：[www-01.ibm.com/software/awdtools/xlcpp](https://blog.csdn.net/magicbean2/article/details/www-01.ibm.com/software/awdtools/xlcpp)。
- GNU：<http://www.gnu.org/>。
- Clang：<http://clang.llvm.org/docs/>。

### **6. OpenMP指令**

#### **6.1 Fortran指令格式**

略。

#### **6.2 C/C++指令格式**

**格式：**

| pragma omp                           | directive-name                                               | [clause, …]                                                  | newline                              |
| ------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------ |
| 所有OpenMP C/C++指令都需要由此开头。 | 一个合法的OpenMP指令。需要出现在pragma之后，所有其它从句之前。 | 可选。从句可以以任意次序出现，并且可以在需要的时候重复出现出现（特殊情况除外）。 | 必须。先于本指令附带的结构化块出现。 |

**示例：**

```
#pragma omp parallel default(shared) private(beta,pi)
```

**一般规则**：

1）大小写敏感；

2）OpenMP指令遵循C/C++指令的标准约定；

3）每个指令只能指定一个指令名；

4）每个指令最多只适用于一个后续的声明，而且该后续声明必须是一个结构化的块；

5）在之领航的末尾通过使用反斜杠“\”转移换行符，可以在后续行上“延续”长指令行。

#### **6.3 指令有效范围**

**静态（词汇）范围：**

- 代码以本文的方式包含在指令之后的结构化块中；
- 指令的静态范围不跨越多个例程或者代码文件。

**孤立指令：**

- 独立于另一个封装指令的OpenMP指令被称为是一个孤立指令。它存在于另一个指令的静态（词法）范围之外；
- 独立指令将跨越例程或者可能的代码文件。

**动态范围：**

- 指令的动态范围包括其静态（词法）范围以及孤立指令的范围。

**示例：**

```
#pragma omp parallel for
for (int i = 0; i < 10; ++i) {
    sub_routine_1();
    sub_routine_2();
}

sub_routine_1() {
    #pragma omp critical
    {
        do_something_1();
    }
}

sub_routine_2() {
    #pragma omp sections
    {
        do_something_2();
    }
}
```

- 静态扩展：for指令在封闭并行块内发生；
- 孤立指令：CRITICAL和SECTIONS指令在封闭并行块外发生；
- 动态扩展：CRITICAL和SECTIONS指令在for和PARALLEL指令的动态上下文中发生。

**为什么重要？**

- OpenMP定义了大量的有效范围规则，指定指令之间如何合并和相互嵌套；
- 如果OpenMP绑定和嵌套规则被忽略，则可能会导致非常或者不正确的程序结果；
- 更多规则请参见：[6.12 数据范围/属性从句](https://blog.csdn.net/magicbean2/article/details/75530667#sec_6_12)。

#### **6.4 并行区域构建**

**目标：**并行区域是指一个可以被多个线程执行的代码块。这是OpenMP并行构建的基础。

**格式：**

```
#pragma omp parallel [clause ...]  newline 
                     if (scalar_expression) 
                     private (list) 
                     shared (list) 
                     default (shared | none) 
                     firstprivate (list) 
                     reduction (operator: list) 
                     copyin (list) 
                     num_threads (integer-expression)


   structured_block
```

**注意事项：**

- 当一个线程执行到并行指令时，它创建一组线程，并自己成为线程组的主线程。主线程是该组线程中的一员，并且其线程编号为0；
- 从并行区域开始，代码将会被复制，并且不同的线程将会执行代码的不同副本；
- 在并行区域结束之处有一个隐式的屏障。在屏障之后只有主线程会继续执行；
- 如果任何一个线程在并行区域中终止，则组中的所有线程都将终止。截止此时所完成的工作是没有定义的。

**多少个线程？** 并行区域中的线程数取决于如下因素，其优先级依次为：

1. 对 **IF** 从句的验算；
2. 对 **NUM_THREADS** 从句的设置；
3. 对`omp_set_num_threads()` 库函数的使用；
4. 对 **OMP_NUM_THREADS** 环境变量的设置；
5. 默认实现：通常是CPU的数量或者其内核的数量，当然也可以是动态的。

线程编号从0（主线程）到 *N-1*。

**动态线程：**

- 采用`omp_get_dynamic()` 来确定动态线程是否被启动；
- 如果被支持，则可以采用如下两种方法来启动动态线程：1）库函数`omp_set_dynamic()`；2）设置环境变量 **OMP_DYNAMIC** 为TRUE。

**嵌套并行区域：**

- 采用库函数`omp_get_nested()` 来确定嵌套并行区域是否被启动；
- 可以采用如下两种方法启动嵌套并行区域：1）库函数`omp_set_nested()`；2）设置环境变量**OMP_NESTED** 为TRUE。
- 如果嵌套并行区域不被支持，那么嵌套在其它并行区域中的一个并行区域将导致新创建一个新组，改组中默认只包含一个线程。

**从句：**

- **IF** 从句：从句中表达式必须为验算为TRUE，以便于线程组可以被创建。否则，区域内的代码将会被主线程串行执行。
- 其它从句将会在后面加以描述，请见：[6.12 数据范围/属性从句](https://blog.csdn.net/magicbean2/article/details/75530667#sec_6_12)。

**限制：** 1）并行区域必须是一个结构化的块，不能跨越多个例程或者代码文件；2）在并行区域内采用分支（goto）是非法的；3）仅仅可以使用一个 **IF** 从句；4）仅仅允许使用一个**NUM_THREADS**；5）程序不能依赖于从句出现的次序。

**一个并行区域的例子：** 一个简单的“Hello World”程序：1）每个线程执行并行区域内的所有代码；2）OpenMP库函数被用来获取线程ID以及总线程数。

```
#include <omp.h>

main(int argc, char *argv[]) {
    int nthreads, tid;
    /* Fork a team of threads with each thread having a private tid variable */
    #pragma omp parallel private(tid)
    {
       /* Obtain and print thread id */
       tid = omp_get_thread_num();
       printf("Hello World from thread = %d\n", tid);

       /* Only master thread does this */
       if (tid == 0) {
           nthreads = omp_get_num_threads();
           printf("Number of threads = %d\n", nthreads);
       }
    }  /* All threads join master thread and terminate */
}
```

#### **6.5 OpenMP练习1**

**总览：**

- 使用你的用户名和OTP令牌登录讲习班的集群系统；
- 将练习文件复制到您的主目录下；
- 熟悉LC和OpenMP环境；
- 编写一个简单的“Hello World”OpenMP程序；
- 成功编译你的程序；
- 成功运行你的程序；
- 修改用户运行程序的线程数。

点击[ GO TO THE EXERCISE HERE](https://computing.llnl.gov/tutorials/openMP/exercise.html) 开始，大约需要20分钟。

#### **6.6 工作共享构造**

工作共享构造将一段封闭代码划分给当前组内的线程；工作共享构造并不会启动新的线程；在进入工作共享构造之处没有隐含的屏障，但是在工作共享手造结束之处存在隐含的障碍。

**工作共享构造的分类：**

| Do/For                                                       | SECTIONS                                                     | SINGLE                                                       |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| 在组线程成员之间分享循环迭代。这种构造代表一种“数据并行”     | 将工作分解为独立的部分，每个部分由一个线程执行，代表一种“功能并行” | 将一段代码串行执行。该部分的所有代码都由一个线程独立完成     |
| ![这里写图片描述](https://computing.llnl.gov/tutorials/openMP/images/work_share1.gif) | ![这里写图片描述](https://computing.llnl.gov/tutorials/openMP/images/work_share2.gif) | ![这里写图片描述](https://computing.llnl.gov/tutorials/openMP/images/work_share3.gif) |

**限制条件：** 1）工作共享结构必须在并行区域内动态封闭，以便指令并行执行；2）工作共享结构必须由组内成员全部遇到或者全部都没遇到；3）一个组的所有成员必须以相同的顺序遇到连续的工作共享结构。

##### **6.6.1 DO/for指令**

**目标：** DO/For指令指定紧随其后的循环迭代必须由组内线程并行执行。这里假设并行区域已经启动，否则这些循环迭代将只会在单个处理器上串行执行。

**形式：**

```
#pragma omp for [clause ...]  newline 
                schedule (type [,chunk]) 
                ordered
                private (list) 
                firstprivate (list) 
                lastprivate (list) 
                shared (list) 
                reduction (operator: list) 
                collapse (n) 
                nowait 

   for_loop
```

**从句：**

- SCHEDULE：定义迭代循环如何在一组线程之间进行分配。其默认调度策略是取决于具体实现的。关于某种调度策略比其它策略更优的详细讨论请参见：http://forum.openmp.org/forum/viewtopic.php?f=3&t=83



  - *静态的（STATIC）*：循环迭代被划分成为大小为`chunk` 的一系列块，然后这些块被静态地分配给不同的线程。如果`chunk` 没有被明确定义，则迭代被平均（如果可能）并且连续第分配给组内线程。
  - *动态的（DYNAMIC）*：循环迭代被划分成为大小为`chunk` 的一系列块，并在线程之间动态调度；当一个线程完成一个块时，它被动态地分配给另外一个块。默认的`chunk` 大小为1。
  - *有指导的（GUIDED）*：当线程发出请求时，迭代被动态地分配给发出请求的线程，直到没有块被分配为止。与动态分配方式（DYNAMIC）类似，只是每次线程提供一个工作包时，其大小都会减小。初始块的大小与`number_of_iterations / number_of_threads` 成正比；随后的块与`number_of_iterations_remaining / number_of_threads` 成正比；参数`chunk` 定义最小块大小，默认大小为1。
  - *运行时的（RUNTIME）*：调度策略由环境变量`OMP_SCHEDULE` 推迟到运行时为止。为这一类型的调度策略指定`chunk` 大小是非法的。
  - *自动的（AUTO）*：将调度决定委托给编译器和/或运行时系统。

- **NO WAIT / nowait**：如果指定，那么线程在并行循环结束时不同步。

- **ORDERED**：执行循环的迭代必须像在串行程序中一样执行。

- **COLLAPSE**：指定嵌套循环中的循环应该被折叠成一个大的迭代空间，并根据SCHEDULE子句进行划分。所有关联循环中的迭代的执行顺序确定了折叠迭代空间中的迭代顺序。

关于其余从句的详细描述请参见：[6.12 数据范围/属性从句](https://blog.csdn.net/magicbean2/article/details/75530667#sec_6_12)。

**限制条件：**

- DO循环不能是DO WHILE循环，或者没有循环控制的循环。此外，循环迭代变量必须是整数，所有线程的循环控制参数必须相同。
- 程序的正确性不能取决于哪个线程执行哪个特定的迭代。
- 在与DO/For指令相关联的循环中，分支（goto）语句时非法的。
- 必须将块大小指定为循环不变的整数表达式，因为在其不同线程的评估期间没有同步。
- ORDERED, COLLAPSE和SCHEDULE子句可能均会出现一次。
- 有关其他的限制条件，请参考OpenMP的说明文档。

**示例：**

一个简单的向量加程序：

1）数组A, B, C以及变量N将被所有线程共享；

2）变量I将成为不同线程内的私有变量，每个线程将会拥有其唯一的副本；

3）循环迭代将会被动态地在线程之间分配，其块大小为`CHUNK`；

4）线程在完成它们各自的块之后将不会同步（NOWAIT）。

```
#include <omp.h>
#define N 1000
#define CHUNKSIZE 100

main(int argc, char *argv[]) {
    int i, chunk;
    float a[N], b[N], c[N];

    /* Some initializations */
    for (i=0; i < N; i++)
       a[i] = b[i] = i * 1.0;
    chunk = CHUNKSIZE;

    #pragma omp parallel shared(a,b,c,chunk) private(i)
    {
        #pragma omp for schedule(dynamic,chunk) nowait
        for (i=0; i < N; i++)
            c[i] = a[i] + b[i];
    }   /* end of parallel region */
}
```

##### **6.6.2 SECTIONS指令**

**目标：** SECTIONS指令是一个非迭代的工作共享结构，它表明封闭的代码段将在组内线程之间划分。独立的SECTION指令被嵌套在SECTIONS指令内。每个SECTION由组内的一个线程执行一次，不同的SECTION部分可能会由不同的线程来执行。如果某个线程执行的足够快并且实现中也允许这样，那么一个线程也有可能在实际中执行多个SECTION部分。

**格式：**

```
#pragma omp sections [clause ...]  newline 
                     private (list) 
                     firstprivate (list) 
                     lastprivate (list) 
                     reduction (operator: list) 
                     nowait
  {
  #pragma omp section   newline 
     structured_block

  #pragma omp section   newline 
     structured_block
  }
```

**从句：**

- 在每个SECTIONS指令的末尾都会有一个隐含的屏障，除非子句 `NOWAIT/nowait` 被明确指定。
- 从句将会在后续章节[6.12 数据范围/属性从句](https://blog.csdn.net/magicbean2/article/details/75530667#sec_6_12)中被详细讨论。

**问题：**

- 如果线程数和SECTION指令个数不相同怎么办？如果线程更多呢？如果SECTION指令更多呢？ 
  **答案**：如果线程数更多，那么某些线程将不会执行SECTION指令；如果SECTION指令更多，那么某些线程将会执行多个SECTION指令。
- 哪个线程执行哪个SECTION指令？ 
  **答案**：这个取决于具体实现，而且不同的执行过程分配也有可能不同。

**限制：**

- 分支（goto）进出区块是非法的；
- SECTION指令必须在封闭的SECTIONS指令的作用范围内发生（无孤立的SECTION指令）。

**示例：**

这里给出一个简单的程序，用以说明不同的线程将会执行不同块中的工作。

```
#include <omp.h>
#define N 1000

main(int argc, char *argv[]) {
    int i;
    float a[N], b[N], c[N], d[N];

    /* Some initializations */
    for (i=0; i < N; i++) {
        a[i] = i * 1.5;
        b[i] = i + 22.35;
    }

    #pragma omp parallel shared(a,b,c,d) private(i)
    {
        #pragma omp sections nowait
        {
            #pragma omp section
            for (i=0; i < N; i++)
                c[i] = a[i] + b[i];

            #pragma omp section
            for (i=0; i < N; i++)
                d[i] = a[i] * b[i];
        }  /* end of sections */
    }  /* end of parallel region */
}
```

##### **6.6.3 SINGLE指令**

**目标：** SINGLE指令指定所附代码仅由组内的一个线程来执行。这在处理非线程安全的代码部分（如I/O时）可能会很有用。

**格式：**

```
#pragma omp single [clause ...]  newline 
                   private (list) 
                   firstprivate (list) 
                   nowait

     structured_block123456
```

**从句：**

- 在组内不执行SINGLE指令的线程将会在代码块结束处等待，除非`NOWAIT/nowait` 被明确指定。
- 从句将会在后续章节[6.12 数据范围/属性从句](https://blog.csdn.net/magicbean2/article/details/75530667#sec_6_12)中被详细讨论。

**限制：**

- 分支（goto）进出SINGLE区块是非法的；

#### **6.7 并行作业共享构建**

OpenMP提供了三个只是提供便利的指令：1）PARALLEL DO / parallel for；2）PARALLEL SECTIONS；3）PARALLEL WORKSHARE (仅限于FORTRAN)。

在大多数情况下，这些指令与后面紧随着单独工作共享指令的单独PARALLEL的行为相同。

大多数适用于这两条指令的规则，从句或者限制都有效，更多详细信息可以参考OpenMP API。

使用PARALLEL DO/parallel组合指令的示例如下所示。

```
#include <omp.h>
#define N           1000
#define CHUNKSIZE   100

main(int argc, char *argv[]) {
    int i, chunk;
    float a[N], b[N], c[N];

    /* Some initializations */
    for (i=0; i < N; i++)
        a[i] = b[i] = i * 1.0;
    chunk = CHUNKSIZE;

    #pragma omp parallel for shared(a,b,c,chunk) private(i) schedule(static,chunk)
    for (i=0; i < n; i++)
        c[i] = a[i] + b[i];
}
```

#### **6.8 任务构建**

**目标：**

 1）TASK指令定义了一个显式任务，该任务可以由遇到的线程执行，或者由组内的任务其它线程延迟执行。

2）任务的数据环境由数据共享属性从句确定。

3）任务的执行需要进行任务调度——有关详细信息可以参考 OpenMP 3.1文档说明。

4）另请参阅OpenMP 3.1文档中的taskyield指令和taskwait指令。

**格式：**

```
#pragma omp task [clause ...]  newline 
                   if (scalar expression) 
                   final (scalar expression) 
                   untied
                   default (shared | none)
                   mergeable
                   private (list) 
                   firstprivate (list) 
                   shared (list) 

     structured_block1234567891011
```

**从句和限制：**

- 详细内容请参阅OpenMP 3.1说明文档。

#### **6.9 OpenMP练习2**

**总览：**

- 如果你还没有登录LC讲习班集群，请首先登录；
- 请浏览，编译和运行工作共享DO/For构建示例；
- 请浏览，编译和运行工作共享 SECTIONS构建示例。

点击[ GO TO THE EXERCISE HERE](https://computing.llnl.gov/tutorials/openMP/exercise.html#Exercise2) 开始，大约需要20分钟。

#### **6.10 同步构建**

思考如下一个简单示例：两个线程或者两个不同的处理器同时试图去对变量x进行自增操作（x的初始值为0）。

**线程1：**

```
increment(x) {
    x = x + 1;
}
THREAD 1:
10  LOAD A, (x address)
20  ADD A, 1
30  STORE A, (x address)1234567
```

**线程2：**

```
increment(x)
{
    x = x + 1;
}
THREAD 2:
10  LOAD A, (x address)
20  ADD A, 1
30  STORE A, (x address)12345678
```

一种可能的执行序列是：1）线程1在寄存器A上加载x的值；2）线程1在寄存器上加1；3）线程2在寄存器A上加载x的值；4）线程2在寄存器上加1；5）线程1将寄存器A上的值存储回x；6）线程2将寄存器A上的值存储回x。

此时x的值为1，而不是2。为了避免类似情况的发生，对x的自增运算必须在线程之间被同步，以保证运算结果的正确性。

OpenMP提供了多种同步机制，以控制每个线程相对于其它线程如何执行。

##### **6.10.1 MASTER指令**

**目标：**

- MASTER指令指定该区域只能被主线程执行。所有其它线程将会自动跳过这一段代码。
- 在该指令之后没有隐式的屏障（意味着其余线程不需要在此进行同步）。

**格式：**

```
#pragma omp master  newline

   structured_block123
```

**限制：**

- 分支（goto）进出MASTER区块是非法的。

##### **6.10.2 CRITICAL指令**

**目标：**

- CRITICAL指令指定该区块一次只能由一个线程执行。

**格式：**

```
#pragma omp critical [ name ]  newline

   structured_block123
```

**注意事项：**

- 如果一个线程当前正在CRITICAL区域内执行，如果另一个线程到达CRITICAL区域并尝试执行它，那么后到的线程将被阻塞，直到第一个线程退出该CRITICAL区域。
- 可选名称允许多个CRITICAL区块同时存在：1）名称将被作为全局标识符。具有相同名字的不同CRITICAL区块将会被认为是同一区块；2）所有匿名的CRITICAL区块将会被认为是同一个区块。

**限制：**

- 分支进出（goto）CRITICAL区块是非法的。

**示例：** 组内所有的线程都试图去并行执行。但是由于CRITICAL区块的存在，任何时刻最多只能有一个线程去执行自增操作。

```
#include <omp.h>

main(int argc, char *argv[]) {
    int x = 0;
    #pragma omp parallel shared(x) 
    {
        #pragma omp critical 
        x = x + 1;
    }  /* end of parallel region */
}12345678910
```

##### **6.10.3 BARRIER指令**

**目标：**

- BARRIER指令同步组内的所哟线程；
- 当到达一个BARRIER指令处时，一个线程将在该处等待直到所有线程到达该处。然后所有线程开始并发执行barrier之后的代码。

**格式：**

```
#pragma omp barrier  newline1
```

**限制：**

- 所有组内的线程必须执行BARRIER区域内的代码；
- 对于组内的线程，遇到工作共享区域和屏障区域的顺序必须相同。

##### **6.10.4 TASKWAIT指令**

**目标：**

- OpenMP 3.1的新特征；
- TASKWAIT指令指定在当前任务开始后生成的子任务之前需要等待（译注：这段话很拗口，也没明白在讲什么。。。）。

**格式：**

```
#pragma omp taskwait  newline1
```

**限制：**

- 由于taskwait结构没有C语言作为其语法的一部分，因此在程序中的位置会有一些限制，taskwait指令只能放在允许基础语言语句的位置。taskwait指令可能不能被放在if，while，do，switch或者label之后的语句处，详细信息请参考OpenMP 3.1文档说明。

##### **6.10.5 ATOMIC指令**

**目标：**

- ATOMIC指令指定特定的内存位置必须为原子更新，而不是让多个线程尝试写入它。事实上，该指令提供了一个最小单位的CRITICAL区域。

**格式：**

```
#pragma omp atomic  newline

   statement_expression123
```

**限制：**

- 该指令仅仅适用于紧随于其后的一行执行语句；
- 该指令必须遵从特定的语法格式。请参考最新OpenMP标准对其定义。

##### **6.10.6 FLUSH指令**

**目标：**

- FLUSH指令定义了一个同步点，在该同步点处，实现必须提供一致的内存视图。此时线程可见的变量将被写回内存。
- 关于OpenMP内的这一指令在论坛内也已经进行了大量讨论。如果你希望咨询更多信息，并且发现有些很难理解？那么依据API：*如果两个不同线程执行的两个flush集合的交集不是空的，那么两个刷新必须按照所有线程看到的顺序完成*。还是一头雾水？
- 这里引用一下openmp.org中的一个FAQ： 
  **Q17**：缓存一致系统上是否需要flush指令？ 
  **A17**：是的，必须使用flush指令。请参照OpenMP规范中的例子以及它的用途。该指令将指示编译器必须将该变量写入/从存储系统读取的，即该变量不能通过代码中的flush语句保存在本地CPU寄存器中。高速缓存一致性确保如果一个CPU执行存储器的读或者写指令，则系统中的所有其它CPU在访问该存储器地址时将获得相同的值。所有缓存将显示一个连贯值。然而在OpenMP标准中，必须有一种方式来指示编译器实际执行读写机器指令，而不是延迟它。在循环中生成有效的机器语言代码时，将循环中的变量保留在寄存器中是非常常见的。

有关更详细信息，请参阅最新的OpenMP规范。

**格式：**

```
#pragma omp flush (list)  newline1
```

**注意事项：**

- 可选列表包含将被刷新的命名变量列表，以避免刷新所有变量。对于列表中的指针，请注意是指针本身被刷新，而不是其指向的对象。
- 实现必须确保所有线程对线程可见变量的任何先前的修改都是可见的，即编译器必须将值从寄存器恢复到内存；硬件可能需要刷新“写入缓冲区”等。
- FLUSH指令隐含在下表所示的指令中。如果存在NOWAIT从句，则不会隐含该指令。

```
barrier 
parallel - upon entry and exit 
critical - upon entry and exit 
ordered - upon entry and exit 
for - upon exit 
sections - upon exit 
single - upon exit 1234567
```

##### **6.10.7 ORDERED指令**

**目标：**

- ORDERED指令指定封闭循环中的迭代顺序将与其对应的串行代码的执行顺序完全一样；
- 如果某个线程执行某个迭代时，发现其之前的迭代尚未完成，那么该线程将等待；
- 在DO/For循环中加入ORDERED从句来实现；
- ORDERED指令提供了一种在循环中应用排序的“微调”方式；否则，该排序不是必须的。

**格式：**

```
#pragma omp for ordered [clauses...]
   (loop region)

#pragma omp ordered  newline

   structured_block

   (endo of loop region)12345678
```

**限制：**

- ORDERED指令只能出现在for（C++）的动态上下文中；
- 任何时刻只能顺次地有一个线程在执行；
- 分支（goto）进出ORDERED区块是非法的；
- 循环中的迭代不能多次执行相同的ORDERED指令，并且不能执行多个ORDERED指令；
- 包含ORDERED指令的循环必须是带有ORDERED从句的循环。

#### **6.11 THREADPRIVATE指令**

**目标：** THREADPRIVATE指令用于在执行并行区域时，将全局变量（C/C++）变为线程的本地变量。

**格式：**

```
#pragma omp threadprivate (list)1
```

**注意事项：** 该指令必须在声明列出的变量/公共块之后出现。然后每个线程都将获得自己的变量/公共块的副本，所以一个线程写入的数据对于其它编程而言是不可见的。例如：

```
#include <omp.h> 

int  a, b, i, tid;
float x;

#pragma omp threadprivate(a, x)
main(int argc, char *argv[]) {
    /* Explicitly turn off dynamic threads */
    omp_set_dynamic(0);
    printf("1st Parallel Region:\n");
    #pragma omp parallel private(b,tid)
    {
        tid = omp_get_thread_num();
        a = tid;
        b = tid;
        x = 1.1 * tid +1.0;
        printf("Thread %d:   a,b,x= %d %d %f\n",tid,a,b,x);
    }  /* end of parallel region */

    printf("************************************\n");
    printf("Master thread doing serial work here\n");
    printf("************************************\n");

    printf("2nd Parallel Region:\n");
    #pragma omp parallel private(tid)
    {
        tid = omp_get_thread_num();
        printf("Thread %d:   a,b,x= %d %d %f\n",tid,a,b,x);
    }  /* end of parallel region */
}
```

```
 Output:

 1st Parallel Region:
 Thread 0:   a,b,x= 0 0 1.000000
 Thread 2:   a,b,x= 2 2 3.200000
 Thread 3:   a,b,x= 3 3 4.300000
 Thread 1:   a,b,x= 1 1 2.100000
 ************************************
 Master thread doing serial work here
 ************************************
 2nd Parallel Region:
 Thread 0:   a,b,x= 0 0 1.000000
 Thread 3:   a,b,x= 3 0 4.300000
 Thread 1:   a,b,x= 1 0 2.100000
 Thread 2:   a,b,x= 2 0 3.200000
```

在首次进入并行区域时，除非在PARALLEL指令中制定了COPYIN从句，否则THREADPRIVATE变量和公共块中的数据应该被视为未定义。

THREADPRIVATE变量与PRIVATE变量（稍后将讨论）不同，因为它们能够在代码的不同并行区域之间持续存在。

**限制：**

- 只有当动态线程机制为“关闭”且不同并行区域中的线程数保持不变时，才能保证THREADPRIVATE对象中的数据保持不变。动态线程的默认设置未定义；
- THREADPRIVATE指令必须在线程私有变量/公共块的每个声明之后出现。

#### **6.12 数据范围属性从句**

也被成为*数据共享属性从句*。对数据范围的理解和使用是OpenMP编程的一个重要考虑因素。由于OpenMP是基于共享内存编程模型的，所以大多数变量在默认情况下都是共享的。

全局变量包括：

- （C/C++）文件范围内的变量，静态变量。

私有变量包括：

- 循环索引变量（译注：也就是我们编程中常用的i，j等）；
- 从并行区域中调用的子程序的栈变量。

OpenMP数据范围属性从句用来显式定义各个变量的有效范围，它们包括：

- PRIVATE
- FIRSTPRIVATE
- LASTPRIVATE
- SHARED
- DEFAULT
- REDUCTION
- COPYIN

数据范围属性从句和一些指令（PARALLEL, DO/for以及SECTIONS）等被一起使用，以控制封闭区域内的变量的有效范围。

这些构造提供了并行构造运行时控制数据环境的能力：

- 它们定义了哪些数据变量以什么方式从串行区域中被转移到并行区域中（以及转移回串行区域）；
- 它们定义了哪些变量将会对所有线程可见，以及哪些变量将会仅仅成为线程内的可见变量。

数据范围属性从句仅仅在其词汇/静态范围内有效。

重要提示：有关次主题的重要细节和讨论，请参阅最新的OpenMP规范。

位便于查阅，我们提供了一张表格[6.13 从句/指令总结](https://blog.csdn.net/magicbean2/article/details/75530667#sec_6_13)。

##### **6.12.1 PRIVATE从句**

**目标：**

- PRIVATE从句指定列表中的变量属于每个线程的私有变量。

**格式：**

- `private (list)`

**注意事项：**

- PRIVATE变量的行为如下：


  ​

  - 对组内每个线程，将会定义一个同类型的对象；
  - 所有对原有对象的引用将会被新对象所替代；
  - 在PRIVATE中定义的变量，在每个线程内部将会被认为是没有初始化的。

- PRIVATE和THREADPRIVATE的对比如下：

| 类型   | PRIVATE                             | THREADPRIVATE                    |
| ------ | ----------------------------------- | -------------------------------- |
| 数据项 | 变量                                | 变量                             |
| 声明处 | 共享任务区域的开始处                | 每个采用块的例程处或者全局文件处 |
| 一致性 | 不保证一致性                        | 保证一致性                       |
| 扩展   | 仅限于词汇-除非作为子程序的参数传递 | 动态                             |
| 初始化 | 采用FIRSTPRIVATE                    | 采用COPYIN                       |

##### **6.12.2 SHARED从句**

**目标：**

- SHARED从句指定其列表中的数据将会在所有线程中间共享。

**格式：**

```
shared (list)1
```

**注意事项：**

- 所有被共享的数据仅仅存在于一块内存中，并且所有线程都可以对该内存地址进行读取；
- 编程者需要负责对共享数据的正确存取（例如采用CRITICAL指令等）。

##### **6.12.3 DEFAULT从句**

**目标：**

- DEFAULT从句允许用户为任何并行区域的词法范围中的所有变量指定默认范围。

**格式：**

```
default (shared | none)1
```

**注意事项：**

- 特定变量可以使用PRIVATE, FIRSTPRIVATE, LASTPRIVATE和REDUCTION子句来免除默认值；
- C/C++OpenMP规范不包括private或firstprivate作为可能的默认值，然而实际实现中可以提供这个选项。
- 使用NONE作为默认值时，需要编程者显示地为所有变量指定范围。

**限制：**

- 在一个PARALLEL指令中只可以指定一个DEFAULT从句。

##### **6.12.4 FIRSTPRIVATE从句**

**目标：**

- FIRSTPRIVATE子句包含了PRIVATE子句的功能以及自动为列表中的变量初始化的功能。

**格式：**

```
firstprivate (list)1
```

**注意事项：**

- 列表中的变量在进入并行或者工作共享结构之前，将被初始化为其原始对象的值。

##### **6.12.5 LASTPRIVATE从句**

**目标：**

```
 - LASTPRIVATE从句包含了PRIVATE从句的功能以及从最后一个循环或者section中向原始对象变量赋值的功能。
12
```

**格式：**

```
lastprivate (list)1
```

**注意事项：**

- 复制回原始变量对象的值是从封闭结构的最后（顺序）迭代或者部分获得的（译注：也就是说从串行情况下的最后一个迭代复制，而不是并行情况下最后结束的那个迭代复制）。例如，执行DO部分的最后一次迭代的线程，或者执行最后一个SECTION的线程将会执行赋值操作，将其线程内的变量值赋回原始对象。

##### **6.12.6 COPYIN从句**

**目标：**

- COPYIN从句提供了一种方法，将所有THREADPRIVATE变量赋予相同的值。

**格式：**

```
copyin (list)1
```

**注意事项：**

- 列表中包含了所有需要被赋值的变量；
- 主线程中的变量将作为复制源，组内线程在进入并行构造区域时被初始化为其值。

##### **6.12.7 COPYPRIVATE从句**

**目标：**

- COPYPRIVATE从句用于将单个线程获取的变量值广播到其它线程的中的私有变量的所有实例；
- 它与SINGLE指令相关联。
- 有关其它讨论和示例，请参阅最新的OpenMP规范文档。

**格式：**

```
copyprivate (list)1
```

##### **6.12.8 REDUCTION从句**

**目标：**

- REDUCTION子句对列表中出现的变量执行规约操作。
- 该指令为每个线程创建并初始化每个列表变量的私有副本。在规约结束时，REDUCTION变量应用于共享变量的所有私有副本，并将最终结果写入全局共享变量中。

**格式：**

```
reduction (operator: list)1
```

| 操作     | 操作符 | 初始值   |
| -------- | ------ | -------- |
| 加法     | +      | 0        |
| 乘法     | *      | 1        |
| 减法     | -      | 0        |
| 逻辑与   | &&     | 0        |
| 逻辑或   | \|\|   | 0        |
| 按位与   | &      | 1        |
| 按位或   | \|     | 0        |
| 按位异或 | ^      | 0        |
| 相等     |        | true     |
| 不等     |        | false    |
| 最大值   | max    | 最小负值 |
| 最小值   | min    | 最大正值 |

**REDUCTION实例：向量点乘**

- 并行循环迭代将相同大小的块分给团队中的每个线程（SHEDULE STATIC）;
- 在并行循环结构的末尾，所有线程都将添加“result”的值来更新主线程的全局副本。

```
#include <omp.h>

main(int argc, char *argv[]) {
    int i, n, chunk;
    float a[100], b[100], result;

    /* Some initializations */
    n = 100;
    chunk = 10;
    result = 0.0;
    for (i=0; i < n; i++) {
        a[i] = i * 1.0;
        b[i] = i * 2.0;
    }

    #pragma omp parallel for default(shared) private(i) \  
   schedule(static,chunk) reduction(+:result)  
   for (i=0; i < n; i++) {
       result = result + (a[i] * b[i]);
   }
   printf("Final result= %f\n",result);
}12345678910111213141516171819202122
```

**限制条件：**

- 列表项的类型必须对缩减运算符有效；
- 列表项/变量不能被声明为共享或者私有；
- 规约操作可能不满足实数的结合律；
- 有关其它限制，请参阅OpenMP API标准。

#### **6.13 从句/指令总结**

- 下表总结了从句与OpenMP指令之间的兼容性关系。

| 从句         | PARALLEL | DO/For | SECTIONS | SINGLE | PARALLEL DO/For | PARALLEL SECTIONS |
| ------------ | -------- | ------ | -------- | ------ | --------------- | ----------------- |
| IF           | yes      |        |          |        | yes             | yes               |
| PRIVATE      | yes      | yes    | yes      | yes    | yes             | yes               |
| SHARED       | yes      | yes    |          |        | yes             | yes               |
| DEFAULT      | yes      |        |          |        | yes             | yes               |
| FIRSTPRIVATE | yes      | yes    | yes      | yes    | yes             | yes               |
| LASTPRIVATE  |          | yes    | yes      |        | yes             | yes               |
| REDUCTION    | yes      | yes    | yes      |        | yes             | yes               |
| COPYIN       | yes      |        |          |        | yes             | yes               |
| COPYPRIVATE  |          |        |          | yes    |                 |                   |
| SCHEDULE     |          | yes    |          |        | yes             |                   |
| ORDERED      |          | yes    |          |        | yes             |                   |
| NOWAIT       |          | yes    | yes      | yes    |                 |                   |

- 以下OpenMP指令不接受从句：
  - MASTER
  - CRITICAL
  - BARRIER
  - ATOMIC
  - FLUSH
  - ORDERED
  - THREADPRIVATE
- 在不同实现中指令支持的从句可能会有所不同。

#### **6.14 指令绑定和嵌套规则**

> 本节可主要作为管理OpenMP指令和绑定规则的快速参考。要了解其它规则，用户可参考其实现文档以及OpenMP标准。

**指令绑定：**

- 如果存在动态封闭区域，则DO/For, SECTIONS, SINGLE, MASTER和BARRIER指令绑定到该区域。如果当前没有执行任何并行区域，则这些指令不起作用；
- ORDERED指令绑定到动态封闭的DO/For中；
- ATOMIC指令在所有线程中强制执行ATOMIC指令的独占访问，而不仅仅是当前组；
- CRITICAL指令在所有线程中强制执行CRITICAL指令的独占访问，而不仅仅是当前组；
- 指令不能绑定到最接近的PARALLEL之外的任何指令。

**指令嵌套：**

- 作业共享区域可能不会紧密嵌套在作业共享、显式任务、critical，ordered，atomic或者主区域内；
- 屏障区域可能不会紧密嵌套在作业共享、显式任务、critical，ordered，atomic或者主区域内；
- 主区域可能不会紧密嵌套在作业共享、原子或者显式任务区域内；
- 有序区域可能不会紧密嵌套在critical，atomic或者显式任务区域内；
- 有序区域必须使用ordered从句紧密嵌套在循环区域（或者并行循环区域）内；
- critical区域可能不会在具有相同名称的关键区域内嵌套。请注意，此限制不足以防止死锁；
- parallel，flush，critical，atomic，taskyield和显式任务区域可能不会紧密嵌套在原子区域内。

### **7. 运行时库函数**

OpenMP API的运行时库函数仍然在不断增长中。这些运行时库函数的目标各异，如下表所示：

| 库函数                      | 目标                                                         |
| --------------------------- | ------------------------------------------------------------ |
| OMP_SET_NUM_THREADS         | 设置在下一个并行区域中使用的线程数                           |
| OMP_GET_NUM_THREADS         | 返回当前处于执行调用的并行区域中的线程数                     |
| OMP_GET_MAX_THREADS         | 返回调用OMP_GET_NUM_THREADS函数可以返回的最大值              |
| OMP_GET_THREAD_NUM          | 返回组内线程的线程号（译注：不要和线程总数搞混）             |
| OMP_GET_THREAD_LIMIT        | 返回可用于程序的最大OpenMP线程数                             |
| OMP_GET_NUM_PROCS           | 返回程序可用的处理器数                                       |
| OMP_IN_PARALLEL             | 用于确定正在执行的代码是否是并行的                           |
| OMP_SET_DYNAMIC             | 启动或者禁用可执行并行区域的线程数（由运行时系统）的动态调整 |
| OMP_GET_DYNAMIC             | 用于确定是否启动了动态线程调整                               |
| OMP_SET_NESTED              | 用于启用或者禁用嵌套并行                                     |
| OMP_GET_NESTED              | 用于确定嵌套并行是否被弃用                                   |
| OMP_SET_SCHEDULE            | 当“运行时”被用作OpenMP指令中的调度类型时，设置循环调度策略   |
| OMP_GET_SCHEDULE            | 当“运行时”被用作OpenMP指令中的调度类型时，返回循环调度策略   |
| OMP_SET_MAX_ACTIVE_LEVELS   | 设置嵌套并行区域的最大数量                                   |
| OMP_GET_MAX_ACTIVE_LEVELS   | 返回嵌套并行区域的最大数量                                   |
| OMP_GET_LEVEL               | 返回嵌套并行区域的当前级别                                   |
| OMP_GET_ANCESTOR_THREAD_NUM | 给定当前线程的嵌套级别，返回其祖先线程的线程号               |
| OMP_GET_TEAM_SIZE           | 给定当前线程的嵌套级别，返回其线程组的大小                   |
| OMP_GET_ACTIVE_LEVEL        | 返回包含调用任务的的嵌套活动并行区域的数量                   |
| OMP_IN_FINAL                | 如果在最终任务区域中执行该例程，则返回true；否则返回false    |
| OMP_INIT_LOCK               | 初始化与锁变量相关联的锁                                     |
| OMP_DESTROY_LOCK            | 解除给定的锁变量与所有锁的关联                               |
| OMP_SET_LOCK                | 获取锁的所有权                                               |
| OMP_UNSET_LOCK              | 释放锁                                                       |
| OMP_TEST_LOCK               | 尝试设置锁，但是如果锁不可用，则不会阻止                     |
| OMP_INIT_NEST_LOCK          | 初始化与锁定变量关联的嵌套锁                                 |
| OMP_DESTROY_NEST_LOCK       | 将给定的嵌套锁变量与所有锁解除关联                           |
| OMP_SET_NEST_LOCK           | 获取嵌套锁的所有权                                           |
| OMP_UNSET_NEST_LOCK         | 释放嵌套锁                                                   |
| OMP_TEST_NEST_LOCK          | 尝试设置嵌套锁，但如果锁不可用，则不会阻止                   |
| OMP_GET_WTIME               | 提供便携式挂钟计时程序                                       |
| OMP_GET_WTICK               | 返回连续时钟之间的秒数（双精度浮点值）                       |

对于C/C++而言，所有的运行时坤函数相当于子程序，例如下面的代码：

```
#include <omp.h>
int omp_get_num_threads(void)12
```

对于C/C++而言，你通常需要包含`<omp.h>` 头文件。

对于锁运行时/函数而言：

- 锁变量必须通过所运行时来进行存取；
- 对于C/C++而言，根据所使用的函数，锁变量的类型必须为`omp_lock_t` 或者`omp_nest_lock_t` 。

实现注意事项：

- 实现中可能并不支持所有的OpenMP API功能。例如，如果支持嵌套并行，那么可能只是名义上的，因为嵌套的并行区域可能只有一个线程。
- 有关相信信息，请查阅具体实现文档——或者如果在文档中找不到时用实验检测。

关于运行时函数的更详细讨论请见：[附录A：运行时库函数](https://blog.csdn.net/magicbean2/article/details/75530667#app_A)。

### **8. 环境变量**

OpenMP提供了如下环境变量，以用于对并行代码的控制。所有环境变量的名称都是大写的，而赋予它们的值则是大小写不敏感的。

**OMP_SCHEDULE**：仅仅适用于for, parallel for指令在调度从句被设置为RUNTIME的情况。该变量的值确定了处理器中的循环迭代如何被调度。例如：

```
setenv OMP_SCHEDULE "guided, 4" 
setenv OMP_SCHEDULE "dynamic"12
```

**OMP_NUM_THREADS**：设置在运行中可用的最大线程数，例如：

```
setenv OMP_NUM_THREADS 81
```

**OMP_DYNAMIC**：启用或者禁用在执行并行区域时可用线程数的动态调整。其合法的值为TRUE或者FALSE。例如：

```
setenv OMP_DYNAMIC TRUE1
```

**OMP_PROC_BIND**：启用或者禁用与处理器绑定的线程，有效值为TRUE或者FALSE。例如：

```
setenv OMP_PROC_BIND TRUE1
```

**OMP_NESTED**：启用或者禁用嵌套并行，其有效值为TRUE或者FALSE。例如：

```
setenv OMP_NESTED TRUE1
```

**OMP_STACKSIZE**：用于控制所创建的线程（非主线程）的栈空间大小。例如：

```
setenv OMP_STACKSIZE 2000500B 
setenv OMP_STACKSIZE "3000 k " 
setenv OMP_STACKSIZE 10M 
setenv OMP_STACKSIZE " 10 M " 
setenv OMP_STACKSIZE "20 m " 
setenv OMP_STACKSIZE " 1G" 
setenv OMP_STACKSIZE 200001234567
```

**OMP_WAIT_POLICY**：为OpenMP的实现提供一种关于等待线程所需行为的提示。一个兼容的OpenMP实现可能会也可能不会遵循环境变量的设置。其有效值为ACTIVE或者PASSIVE。ACTIVE指定等待线程主要是活动的，即在等待时消耗处理器周期；PASSIVE指定等待线程主要是被动的，即等待时不消耗处理器周期。ACTIVE和PASSIVE行为的细节是实现定义的。例如：

```
setenv OMP_WAIT_POLICY ACTIVE 
setenv OMP_WAIT_POLICY active 
setenv OMP_WAIT_POLICY PASSIVE 
setenv OMP_WAIT_POLICY passive1234
```

**OMP_MAX_ACTIVE_LEVELS**：控制活动嵌套并行区域的最大数量。此环境变量的值必须为非负整数。如果OMP_MAX_ACTIVE_LEVELS的请求值大于实现可支持的活动嵌套并行级别的最大数量，后者该值不是非负整数，则程序的行为是实现定义的。例如：

```
setenv OMP_MAX_ACTIVE_LEVELS 21
```

**OMP_THREAD_LIMIT**：设置用于整个OpenMP程序的线程数。此环境变量的值必须为正整数。如果OMP_THREAD_LIMIT的请求值大于实现可以支持的线程数，或者该值不是正整数，则程序的行为是实现定义的。例如：

```
setenv OMP_THREAD_LIMIT 81
```

### **9. 线程栈大小和线程绑定**

**线程栈大小：**

- OpenMP标准并没有指定线程应具有多少堆栈空间。因此，默认的线程堆栈大小在各种实现中将有所不同。
- 默认线程堆栈大小可能会很容易耗尽，并且在编译器之间不可移植。以LC编译的以前版本为例：

| 编译器              | 栈大小估计 | 数组大小估计（双精度浮点数） |
| ------------------- | ---------- | ---------------------------- |
| Linux icc, ifort    | 4 MB       | 700 x 700                    |
| Linux pgcc, pgf90   | 8 MB       | 1000 x 1000                  |
| Linux gcc, gfortran | 2 MB       | 500 x 500                    |

\- 超过其堆栈分配的线程有可能会也有可能不会发生故障。当数据被破坏时，应用程序也有可能会继续运行。 
\- 静态链接代码可能会受到进一步的堆栈限制。 
\- 用户的登录shell也有可能会限制堆栈大小。 
\- 如果你的OpenMP环境支持OpenMP 3.0 OMP_STACKSIZE环境变量（上一节所述），则可以在程序执行之前使用它来设置线程堆栈大小。例如：

```
setenv OMP_STACKSIZE 2000500B
setenv OMP_STACKSIZE "3000 k "
setenv OMP_STACKSIZE 10M
setenv OMP_STACKSIZE " 10 M "
setenv OMP_STACKSIZE "20 m "
setenv OMP_STACKSIZE " 1G"
setenv OMP_STACKSIZE 200001234567
```

- 否则，在LC下，你可以使用使用下面的Linux集群方法。该示例显示将线程堆栈大小设置为12 MB，并且最为预防措施，将shell堆栈大小设置为unlimited。

```
// csh/tcsh：
setenv KMP_STACKSIZE 12000000
limit stacksize unlimited

// ksh/sh/bash
export KMP_STACKSIZE = 12000000
ulimit -s unlimited 1234567
```

**线程绑定：**

- 在某些情况下，如果程序的线程绑定到处理器/内核，程序将执行得更好。
- 将线程绑定到处理器意味着操作系统在调度线程时，将保证它们始终在同一个处理器上运行。否则可以将线程调度为在任何处理器上执行，并且在每个时间片之间在处理器之间“反弹”。
- 该机制也被成为“线程亲和性”（thread affinity）或者“处理器亲和性”（processor affinity）。
- 将线程绑定到处理器可以导致更好地缓存利用率，从而减少昂贵的内存访问。这是将线程绑定到处理器的主要动机。
- 根据你的平台，操作系统，编译器以及OpenMP实现，将线程绑定到处理器可以通过几种不同的方式完成。
- OpenMP 3.1 API提供了一个环境变量来设置将处理器绑定。例如：

```
setenv OMP_PROC_BIND  TRUE
setenv OMP_PROC_BIND  FALSE12
```

- 在更高层次上，进程也可以绑定到处理器上。
- 有关LC Linux集群上处理器的进程和线程绑定的更多相信信息，请访问[这里](https://lc.llnl.gov/confluence/display/TLCC2/mpibind)。

### **10. OpenMP的监听，调试以及性能分析工具**

**线程的监听和调试：**

调试器处理线程的能力各不相同。TotalView挑食其实LC推荐的并行程序调试器，它非常适合监控和调试多线程程序。

使用OpenMP代码的TotalView会话的示例屏幕截图如下所示：

1. 主线程堆栈跟踪窗格显式原始例程；
2. 进程/线程状态可以区分线程；
3. 主线程推展框架窗格显式共享变量；
4. 工作线程堆栈跟踪窗格显式例程的概要；
5. 工作线程堆栈框架窗格；
6. 显式所有线程的根窗口；
7. 线程窗格显式所有线程以及选中的线程。

![这里写图片描述](https://computing.llnl.gov/tutorials/openMP/images/openmpWindows.gif)

更详细的信息可以参见：[TotalView Debugger tutorial](https://computing.llnl.gov/tutorials/totalview/index.html)。

Linux ps命令提供了几个用于查看线程信息的标志，一些例子如下所示。有关更详细信息，请参见：[Linux User’s Manual](https://computing.llnl.gov/tutorials/pthreads/man/ps.txt)。

```
% ps -Lf 
UID        PID  PPID   LWP  C NLWP STIME TTY          TIME CMD
blaise   22529 28240 22529  0    5 11:31 pts/53   00:00:00 a.out
blaise   22529 28240 22530 99    5 11:31 pts/53   00:01:24 a.out
blaise   22529 28240 22531 99    5 11:31 pts/53   00:01:24 a.out
blaise   22529 28240 22532 99    5 11:31 pts/53   00:01:24 a.out
blaise   22529 28240 22533 99    5 11:31 pts/53   00:01:24 a.out

% ps -T 
  PID  SPID TTY          TIME CMD
22529 22529 pts/53   00:00:00 a.out
22529 22530 pts/53   00:01:49 a.out
22529 22531 pts/53   00:01:49 a.out
22529 22532 pts/53   00:01:49 a.out
22529 22533 pts/53   00:01:49 a.out

% ps -Lm 
  PID   LWP TTY          TIME CMD
22529     - pts/53   00:18:56 a.out
    - 22529 -        00:00:00 -
    - 22530 -        00:04:44 -
    - 22531 -        00:04:44 -
    - 22532 -        00:04:44 -
    - 22533 -        00:04:44 -123456789101112131415161718192021222324
```

LC的Linux集群还提供了监视结点上的进程的最高级命令。如果与-H标志一起使用，则进程中包含的线程将可见。top -H命令的示例如下所示。父进程是PID 18010，它产生三个线程，如PID 18012， 18013和18014所示。

![这里写图片描述](https://computing.llnl.gov/tutorials/pthreads/images/topH.gif)

**性能分析工具：**

- 有多种可用于OpenMP程序的性能分析工具，搜索网页会得到丰富的信息。

- 在LC中，支持的计算工具列表可以在以下网址中找到<https://hpc.llnl.gov/software/development-environment-software>。

- 这些工具的复杂性，功能和学习曲线差别很大，对它们的详细介绍超出了本教程的范围。

- 一些值得研究的工具，尤其是针对OpenMP代码而言，包括：


  ​

  - Open | Speedshop
  - TAU
  - PAPI
  - Intel VTune Amplifier
  - ThreadSpotter

### **11. OpenMP练习**

总览：

- 如果尚未登录LC讲习班集群，请登录；
- 查看，编译和运行孤立指令示例（Orphaned directive example）;
- 获取OpenMP实现环境信息；
- 混合OpenMP + MPI程序；
- 查看“bug”程序。

点击[ GO TO THE EXERCISE HERE](https://computing.llnl.gov/tutorials/openMP/exercise.html#Exercise3) 开始，大约需要20分钟。

### **12. 参考文献和更多信息**

- 作者：[Blaise Barney](mailto:blaiseb@llnl.gov)；
- OpenMP官方网站，包含C/C++ API的详细文档：[www.openmp.org](https://blog.csdn.net/magicbean2/article/details/www.openmp.org)。

### **附录A：运行时库函数**

**OMP_SET_NUM_THREADS**

目标：

- 设置将在下一个并行区域中使用的线程数，其值必须是一个正整数。

格式：

```
#include <omp.h>
void omp_set_num_threads(int num_threads)
```

注意事项：

- 动态线程机制将会修改此例程的效果：


  

  - 启用：指定动态线程机制可以用于并行区域的最大线程数；
  - 禁用：指定在下次调用此例程之前正确使用的线程数。

- 该例程只能从代码的串行部分调用。

- 此调用优先于OMP_NUM_THREADS环境变量。

**OMP_GET_NUM_THREADS**

目标：

- 返回当前组在执行并行区域时所调用的线程数。

格式：

```
#include <omp.h>
int omp_get_num_threads(void)12
```

注意事项及限制条件：

- 如果这个调用是从程序的串行部分或者被序列化的嵌套并行区域进行的，它将返回1。
- 默认的线程数是依赖于具体实现的。

**OMP_GET_MAX_THREADS**

目标：

- 返回调用OMP_GET_NUM_THREADS函数可以返回的最大值。

```
#include <omp.h>
int omp_get_max_threads(void)12
```

注意事项及限制条件：

- 通常反映由OMP_NUM_THREADS环境变量或者OMP_SET_NUM_THREADS()库函数例程设置的线程数。
- 可以从串行和并行的代码区域调用。

**OMP_GET_THREAD_NUM**

目标：

- 返回队列中的线程的线程号。改数字将在0和OMP_GET_NUM_THREADS-1之间。组内的主线程的线程号是0。

格式：

```
#include <omp.h>
int omp_get_thread_num(void)12
```

注意事项及限制条件：

- 如果从嵌套的并行区域或者串行区域调用，则此函数将返回0。

**OMP_GET_THREAD_LIMIT**

目标：

- 返回可用于程序的最大OpenMP线程数。

格式：

```
#include <omp.h>
int omp_get_thread_limit (void)12
```

注意事项：

- 可同时参考OMP_THREAD_LIMIT环境变量。

**OMP_GET_NUM_PROCS**

目标：

- 返回程序可用的处理器个数。

格式：

```
#include <omp.h>
int omp_get_num_procs(void)12
```

**OMP_IN_PARALLEL**

目标：

- 可以调用以确定正在执行的代码段是否是并行的。

格式：

```
#include <omp.h>
int omp_in_parallel(void)12
```

注意事项及限制条件：

- 对于C/C++，如果并行，它将返回非零整数，否则将返回0。

**OMP_SET_DYNAMIC**

目标：

- 启用或者禁用可执行并行区域的线程数（由运行时系统）的动态调整。

格式：

```
#include <omp.h>
void omp_set_dynamic(int dynamic_threads)12
```

注意事项及限制条件：

- 对C/C++，如果dynamic_threads计算为非零值，则启用机制，否则禁用。
- OMP_SET_DYNAMIC子例程优先于OMP_DYNAMIC环境变量。
- 默认设置取决于具体实现。
- 必须从程序的串行部分开始调用。

**OMP_GET_DYNAMIC**

目标：

- 用于确定是否启用了动态线程调整。

格式：

```
#include <omp.h>
int omp_get_dynamic(void)12
```

注意事项及限制条件：

- 对于C/C++，如果启用了动态线程调整，则返回非零值，否则返回0。

**OMP_SET_NESTED**

目标：

- 用于启用或者禁用嵌套并行。

格式：

```
#include <omp.h>
void omp_set_nested(int nested)12
```

注意事项及限制条件：

- 对于C/C++，如果嵌套求值为非0，嵌套并行将启用，否则禁用。
- 默认值为禁用嵌套并行。
- 此调用优先于OMP_NESTED环境变量。

**OMP_GET_NESTED**

目标：

- 用于确定嵌套并行是否启用。

格式：

```
#include <omp.h>
int omp_get_nested (void)12
```

注意事项及限制条件：

- 对于C/C++，如果启用嵌套并行性，则返回非零值，否则返回0。

**OMP_SET_SCHEDULE**

目标：

- 此例程设置用于循环指令运行时的时间调度策略。

格式：

```
#include <omp.h>
void omp_set_schedule(omp_sched_t kind, int modifier)12
```

**OMP_GET_SCHEDULE**

目标：

- 此例程返回在循环指令指定运行时调度时应用的调度策略。

格式：

```
#include <omp.h>
void omp_get_schedule(omp_sched_t * kind, int * modifier )12
```

**OMP_SET_MAX_ACTIVE_LEVELS**

目标：

- 此例程限制嵌套活动并行区域的数量。

格式：

```
#include <omp.h>
void omp_set_max_active_levels (int max_levels) 12
```

注意事项及限制条件：

- 如果所请求的并行级别的数量超过实现所支持的并行级数，则该值将被设置为实现所支持的并行级别数。
- 该程序仅在从程序的顺序部分调用时才具有效果。当在显式并行区域内调用时，此例程的作用就是具体实现相关的。

**OMP_GET_MAX_ACTIVE_LEVELS**

目标：

- 此例程返回嵌套活动并行区域的最大数量。

格式：

```
#include <omp.h>
int omp_get_max_active_levels(void) 12
```

**OMP_GET_LEVEL**

目标：

- 此例程返回包含该调用任务的嵌套并行区域的数量。

格式：

```
#include <omp.h>
int omp_get_level(void) 12
```

注意事项及限制条件：

- omp_get_level例程返回包含调用任务的嵌套并行区域（无论是活动的还是非活动的）中除去隐式并行区域的数量。该例程总是返回非负整数。如果从程序的串行部分调用，则返回0。

**OMP_GET_ANCESTOR_THREAD_NUM**

目标：

- 给定当前线程的嵌套级别，该例程返回祖先或者当前线程的线程号。

格式：

```
#include <omp.h>
int omp_get_ancestor_thread_num(int level) 12
```

注意事项和限制条件：

- 如果所请求的嵌套级别超出范围0和由omp_get_level子程序返回的当前线程的嵌套级别，则该例程反悔-1。

**OMP_GET_TEAM_SIZE**

目标：

- 给定当前线程的给定嵌套级别，此例程返回祖先或者当前线程所属组的大小。

格式：

```
#include <omp.h>
int omp_get_team_size(int level); 12
```

注意事项和限制条件：

- 如果所请求的嵌套级别在0和由omp_get_level例程返回的当前线程的嵌套级别之外，则该例程返回-1。非活动并行区域被认为像单线程执行的活动并行区域一样。

**OMP_GET_ACTIVE_LEVEL**

目标：

- omp_get_active_level例程返回包含该调用任务的活动嵌套并行区域的数量。

格式：

```
#include <omp.h>
int omp_get_active_level(void);12
```

注意事项和限制条件：

- 该例程总是返回一个非负整数。如果从程序的串行部分调用，则返回0。

**OMP_IN_FINAL**

目标：

- 如果程序在最终任务区域中执行，则此例程反悔true；否则返回false。

格式：

```
#include <omp.h>
int omp_in_final(void) 12
```

**OMP_INIT_LOCK** 
**OMP_INIT_NEST_LOCK**

目标：

- 该子例程初始化与锁变量相关联的锁。

格式：

```
#include <omp.h>
void omp_init_lock(omp_lock_t *lock)
void omp_init_nest_lock(omp_nest_lock_t *lock)123
```

注意事项及限制条件：

- 初始状态是解锁状态。

**OMP_DESTROY_LOCK** 
**OMP_DESTROY_NEST_LOCK**

目标：

- 该子程序将给定的锁变量与所有锁解除关联。

格式：

```
#include <omp.h>
void omp_destroy_lock(omp_lock_t *lock)
void omp_destroy_nest_lock(omp_nest_lock_t *lock)123
```

注意事项及限制条件：

- 使用未初始化的锁变量调用此例程是非法的。

**OMP_SET_LOCK** 
**OMP_SET_NEST_LOCK**

目标：

- 该子程序强制执行线程等待，直到指定的锁可用。一个线程在可用时被授予锁的使用权。

格式：

```
#include <omp.h>
void omp_set_lock(omp_lock_t *lock)
void omp_set_nest__lock(omp_nest_lock_t *lock)123
```

注意事项和限制条件：

- 使用未初始化的锁变量调用此例程是非法的。

**OMP_UNSET_LOCK** 
**OMP_UNSET_NEST_LOCK**

目标：

- 该子程序从执行子程序中释放锁。

格式：

```
#include <omp.h>
void omp_unset_lock(omp_lock_t *lock)
void omp_unset_nest__lock(omp_nest_lock_t *lock)123
```

注意事项和限制条件：

- 使用未初始化的锁变量调用此例程是非法的。

**OMP_TEST_LOCK** 
**OMP_TEST_NEST_LOCK**

目标：

- 此子程序尝试设置锁，但如果锁定不成功，则不会阻塞。

格式：

```
#include <omp.h>
int omp_test_lock(omp_lock_t *lock)
int omp_test_nest__lock(omp_nest_lock_t *lock)123
```

注意事项和限制条件：

- 对于C/C++，如果锁设置成功，则返回非零值，否则返回0。
- 使用未初始化的锁变量调用此例程是非法的。

**OMP_GET_WTIME**

目标：

- 提供可移植的挂钟计时程序。
- 返回一个从过去某个时间点经过的秒数的双精度浮点值。通常以“pair”的形式使用，在第二次调用的值中减去第一次调用的值，就可以获得代码块的经过时间。
- 设计为“每个线程”一次。因此在一个组内的所有线程中可能不是全局一致的——取决于线程与其他线程相比的行为。

格式：

```
#include <omp.h>
double omp_get_wtime(void) 12
```

**OMP_GET_WTICK**

目标：

- 提供可移植的挂钟计时程序。
- 返回一个表示连续时钟秒数的双精度浮点值。

格式：

```
#include <omp.h>
double omp_get_wtick(void) 12
```

