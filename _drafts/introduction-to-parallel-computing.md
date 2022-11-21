## **并行计算简介**

- https://blog.csdn.net/magicbean2/article/details/75174859
- https://computing.llnl.gov/tutorials/parallel_comp/

> 劳伦斯·利弗摩尔(LawrenceLivermore)国家实验室  https://computing.llnl.gov



### **1 摘要**

最近项目需要实现程序的并行化，刚好借着翻译这篇帖子的机会，了解和熟悉并行计算的基本概念和程序设计。帖子的原文见[这里](https://computing.llnl.gov/tutorials/parallel_comp/)。

这篇帖子旨在为并行计算这一广泛而宏大的话题提供一个非常快速的概述，作为随后教程的先导。因此，它只涵盖了并行计算的基础知识，实用于刚刚开始熟悉该主题的初学者。我们并不会深入讨论并行计算，因为这将花费大量的时间。本教程从对并行计算是什么以及如何使用开始，讨论与其相关的概念和术语，然后解析并行内存架构(parallel memory architecture)以及编程模型(programming models)等。这些主题之后是一系列关于设计和运行并行计算程序的复杂问题的实践讨论。最后，本教程给出了几个并行化简单串行程序的示例。

### **2 概述**

#### **2.1 什么是并行计算？**

**串行计算：** 传统的软件通常被设计成为串行计算模式，具有如下特点：

- 一个问题被分解成为一系列离散的指令；
- 这些指令被顺次执行；
- 所有指令均在一个处理器上被执行；
- 在任何时刻，最多只有一个指令能够被执行。 
  ![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/serialProblem.gif) 
  例如， 
  ![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/serialProblem2.gif)

**并行计算：** 简单来讲，并行计算就是同时使用多个计算资源来解决一个计算问题：

- 一个问题被分解成为一系列可以并发执行的离散部分；
- 每个部分可以进一步被分解成为一系列离散指令；
- 来自每个部分的指令可以在不同的处理器上被同时执行；
- 需要一个总体的控制/协作机制来负责对不同部分的执行情况进行调度。 
  ![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/parallelProblem.gif) 
  例如， 
  ![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/parallelProblem2.gif)

这里的 **计算问题** 需要具有如下特点：

- 能够被分解成为并发执行离散片段；
- 不同的离散片段能够被在任意时刻执行；
- 采用多个计算资源的花费时间要小于采用单个计算资源所花费的时间。

这里的 **计算资源** 通常包括：

- 具有多处理器/多核(multiple processors/cores)的计算机；
- 任意数量的被连接在一起的计算机。

**并行计算机：** 
通常来讲，从硬件的角度来讲，当前所有的单机都可以被认为是并行的：

- 多功能单元（L1缓存，L2缓存，分支，预取，解码，浮点数，图形处理器，整数等）
- 多执行单元/内核
- 多硬件线程 
  ![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/bgqComputeChip.jpg) 
  IBM BG/Q Compute Chip with 18 cores (PU) and 16 L2 Cache units (L2)

通过网络连接起来的多个单机也可以形成更大的并行计算机集群: 
![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/nodesNetwork.gif)

例如，下面的图解就显示了一个典型的LLNL并行计算机集群：

- 每个计算结点就是一个多处理器的并行计算机；
- 多个计算结点用无限宽带网络连接起来；
- 某些特殊的结点（通常也是多处理器单机）被用来执行特定的任务。 
  ![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/parallelComputer1.gif)

#### **2.2 为什么要并行计算？**

**真实世界就是高度并行的：**

- 自然界中的万事万物都在并发的，按照其内在时间序列运行着；
- 和串行计算相比，并行计算更适用于对现实世界中的复杂现象进行建模，模拟和理解；
- 例如，可以想象对这些进行顺序建模： 
  ![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/realWorldCollage1.jpg) 
  ![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/realWorldCollage2.jpg) 
  ![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/realWorldCollage3.jpg)

**主要理由：**

- 节约时间和成本：1）理论上来讲，在一个任务上投入更多的资源有利于缩短其完成时间，从而降低成本；2）并行计算机可以由大量廉价的单机构成，从而节约成本。 
  ![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/timeMoney2.jpg)
- 解决更大规模更复杂的问题：1）很多问题的规模和复杂度使得其难以在一个单机上面完成；2）一个有趣的例子：([Grand Challenge Problems](https://blog.csdn.net/magicbean2/article/details/en.wikipedia.org/wiki/Grand_Challenge))。3）网页搜索引擎/数据库每秒处理百万级别的吞吐量。 
  ![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/biggerProblems.jpg)
- 提供并发性：1）单个计算资源某个时间段只能做一件事情，而多计算资源则可以同时做多件事情；2）协同网络可以使得来自世界不同地区的人同时虚拟地沟通。 
  ![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/collaborativeNetworks.jpg)
- 利用非局部的资源：1）可以利用更广范围中的网络资源；2）SETI@home的例子；以及3）Folding@home的例子。 
  ![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/SETILogo.jpg)
- 更好地利用并行硬件：1）现代计算机甚至笔记本电脑在架构上都属于多处理器/多核的；2）并行软件已经适用于多核的并行硬件条件，例如线程等；3）在大多数情况下，运行在现代计算机上的串行程序实际上浪费了大量的计算资源。
- ![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/xeon5600processorDie3.jpg)

**并行计算的未来：**

- 在过去的二十多年中，快速发展的网络，分布式系统以及多处理器计算机架构（甚至在桌面机级别上）表明并行化才是计算的未来；
- 在同一时期，超级计算机的性能已经有了至少50万倍的增加，而且目前还没有达到极限的迹象；
- 目前的峰值计算速度已经达到了10181018/秒。 
  ![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/top500.1993-2016.gif)

#### **2.3 谁都在使用并行计算？**

**科学界和工程界：**

从历史上来讲，并行计算就被认为是“计算的高端”，许多科学和工程领域的研究团队在对很多领域的问题建模上都采用了并行计算这一模式，包括：大气与地球环境、应用物理、生物科学、遗传学、化学、分子科学、机械工程、电气工程、计算机科学、数学、国防和武器研发等。 
![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/simulations01.jpg)

**工业界和商业界：**

如今，商业应用为更快速计算机的研发提供了更强劲的动力。这些商业应用程序需要以更复杂的方式处理大量数据，例如：大数据、数据库、数据挖掘、石油勘探、网页搜索引擎、基于web的商业服务、医学成像和诊断、跨国公司管理、高级图形学技术以及虚拟现实、网络视频和多媒体技术、协同工作环境等。 
![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/simulations02.jpg)

**全球应用：** 
并行计算目前在实际上被广泛采用于大量应用中。 
![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/top500Apps.gif)

### **3 概念和术语**

#### **3.1 冯诺依曼体系结构**

以匈牙利数学家约翰·冯诺依曼命名的这一计算机体系结构，出现在他1945年发表的一篇论文中。这也通常被称为“存储程序计算机”——程序指令和数据都被保存在存储器中，这与早期通过“硬接线”编程的计算机不同。从此以后，所有的计算机走遵从这一基本架构： 
![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/vonNeumann1.gif) ![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/vonNeumann2.jpg) 
\- 四个组成部分：1）内存；2）控制器；3）处理器；4）输入输出。 
\- 读写操作：支持随机存储的内存用来同时保存程序指令和数据：1）程序指令用来指导计算机操作；2）数据是程序用来操作的对象。 
\- 控制器：从内存中读取指令或者数据，对这些指令进行解码并且顺序执行这些指令。 
\- 处理器：提供基本的算术和逻辑操作。 
\- 输入输出设备：是人机交互的接口。

那么冯诺依曼体系结构和并行计算有什么关系呢？答案是：并行计算机仍然遵从这一基本架构，只是处理单元多于一个而已，其它的基本架构完全保持不变。

#### **3.2 弗林的经典分类**

有不同的方法对并行计算机进行分类（具体例子可参见[并行计算分类](https://computing.llnl.gov/tutorials/parallel_comp/parallelClassifications.pdf)）。

一种被广泛采用的分类被称为弗林经典分类，诞生于1966年。弗林分类法从**指令流**和**数据流**两个维度区分多处理器计算机体系结构。每个维度有且仅有两个状态：**单个**或者**多个**。

下面个矩阵定义了弗林分类的四个可能状态： 
![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/flynnsTaxonomy.gif)

**单指令单数据(SISD)：** SISD是标准意义上的串行机，具有如下特点：1）单指令：在每一个时钟周期内，CPU只能执行一个指令流；2）单数据：在每一个时钟周期内，输入设备只能输入一个数据流；3）执行结果是确定的。这是最古老的一种计算机类型。 
![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/sisd2.gif) ![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/univac1.LLNL.200pix.jpg)

**单指令多数据(SIMD)：** SIMD属于一种类型的并行计算机，具有如下特点：1）单指令：所有处理单元在任何一个时钟周期内都执行同一条指令；2）多数据：每个处理单元可以处理不同的数据元素；3）非常适合于处理高度有序的任务，例如图形/图像处理；4）同步（锁步）及确定性执行；5）两个主要类型：处理器阵列和矢量管道。 
![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/simd3.gif)

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/simd.gif)

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/simd2.gif)

**多指令单数据(MISD)：**MISD属于一种类型的并行计算机，具有如下特点：1）多指令：不同的处理单元可以独立地执行不同的指令流；2）单数据：不同的处理单元接收的是同一单数据流。这种架构理论上是有的，但是工业实践中这种机型非常少。 
![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/misd4.gif) ![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/misd.gif)

**多指令多数据(MIMD)：** MIMD属于最常见的一种类型的并行计算机，具有如下特点：1）多指令：不同的处理器可以在同一时刻处理不同的指令流；2）多数据：不同的处理器可以在同一时刻处理不同的数据；3）执行可以是同步的，也可以是异步的，可以是确定性的，也可以是不确定性的。这是目前主流的计算机架构类型，目前的超级计算机、并行计算机集群系统，网格，多处理器计算机，多核计算机等都属于这种类型。值得注意的是，许多MIMD类型的架构中实际也可能包括SIMD的子架构。 
![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/mimd2.gif) ![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/mimd.gif)

#### **3.3 一些常见的并行计算术语**

和其它一些领域一样，并行计算也有自己的“术语”。下面列出了与并行计算相关联的一些常用术语，其中大部分术语我们在后面还会进行更详细的讨论。

- **结点(Node)：** 也就是一个独立的“计算机单元”。通常由多个CPU处理器/处理内核，内存，网络接口等组成。结点联网在一起以构成超级计算机。
- **中央处理器/套接字/处理器/核(CPU / Socket / Processor / Core)：** 这些术语也取决于我们讨论的语境。在过去，中央处理器通常是计算机中的一个单个执行单元。之后多处理器被植入到一个结点中。接着处理器又被设计成为多核，每个核成为一个独立的处理单元。具有多核的中央处理器有时候又被称为“套接字”——实际上也没有统一标准。所以目前来讲，我们称一个结点上具有多个中央处理器，每个中央处理器上又具有多个内核。 
  ![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/nodeSocketCores.jpg)
- **任务(Task)：** 任务通常是指一个逻辑上离散的计算工作部分。一个任务通常是一段程序或者一段类似于程序的指令集合，可以由一个处理器进行处理。一个并行程序通常由多个任务构成，并且可以运行在多个处理器上。
- **流水线(Pipelining)：** 可以将任务分解成为不同的步骤，并且由不同的处理单元完成，里面有输入流通过。这非常类似于一个装配线，属于一种类型的并行计算。
- **共享内存(Shared Memory)：** 从严格的硬件角度来讲，共享内存描述了一种计算机架构，其中所有的处理器都可以对共同的物理内存进行直接存取（通常是通过总线）。从编程的角度来讲，共享内存描述了一种模型，其中所有的并行任务都具有同一内存形态，并且都可以直接对同一内存区域进行直接定位和存取，而无论该物理内存实际上在哪里（也许在千里之外的另外一个计算机上？）。
- **对称多处理器(Symmetric Multi-Processor (SMP))：** 属于一种共享内存的硬件架构，并且不同的处理器对内存以及其它资源都具有同等的访问权限（个人理解，就是不同处理器在角色上没有任何区别）。
- **分布式内存(Distributed Memory)：** 在硬件中，表示基于网络的内存存取方式；在编程模型中，表示任务仅仅能够从逻辑上“看到”本机上的内存，但是在其它任务执行的时候，必须通过通讯才能对其它任务所运行的机器上的内存进行存取。
- **通讯(communications)：** 并行任务通常需要数据交换。实现数据交换的方式有多种，例如通过共享内存或者通过网络。但是通常意义上，数据交换指的就是通讯，而无论其实现方式。
- **同步(Synchronization)：** 指的是并行任务之间的实时协调，通常伴随着通讯(communication)。同步通常由在程序中设立同步点来实现，也就是说，在其它任务没有执行到这一同步点的时候，某一任务不能进一步执行后面的指令。同步通常涉及到需要等待其它任务的完成，因此有时候会增加并行程序的执行时间。
- **粒度(Granularity)：** 在并行计算中，粒度定量地描述了计算与通讯的比率。**粗粒度**表示在通讯过程中需要做大量的计算性工作；**细粒度**则表示在通讯过程中需要做的计算性工作并不多。
- **加速比(Observed Speedup)：** 这是检测并行计算性能的最简单并且最被广泛使用的度量策略，其定义如下：串行计算的时钟周期数并行计算的时钟周期数串行计算的时钟周期数并行计算的时钟周期数。
- **并行开销(Parallel Overhead)：** 指的是相对于做实际计算，做协调并行任务所需要花费的时间总数。影响并行开销的因素主要包括：1）任务启动时间；2）同步；3）数据通讯；4）由并行语言，链接库，操作系统等因素而导致的软件开销；5）任务终止时间。
- **大规模并行(Massive Parallel)：** 指那些包含并行系统的硬件——拥有很多的处理元件。这里的“很多”可能会随着硬件条件的进步而不断增加，但目前，最大的并行系统所拥有的处理元件高达上百万件。
- **尴尬并行(Embarrassingly Parallel)：** 指的是同时解决很多类似而又独立的任务，其中任务之间几乎没有需要协调的地方。
- **可扩展性(Scalability)：** 指的是并行系统（包括软件和硬件）通过添加更多资源来成比例增加并行速度的能力。影响可扩展性的因素主要包括：1）硬件，尤其是内存-处理器带宽以及网络通讯的质量和速度；2）应用算法；3）相对并行开销；4）具体应用的特征。

#### **3.4 并行程序的缺陷和代价**

**阿姆达尔定律：** 阿姆达尔定律说一个程序的加速比潜力由其可以并行的部分所占的比例而决定，即： 
speedup=11−Pspeedup=11−P. 
如果没有代码可以被并行，那么p = 0，所以加速比为1。如果所有的代码都可以被并行，那么 p = 1，加速比为无穷大（当然只是理论上而言）。如果50%的代码可以被并行，那么最大的加速比为2，意味着的运行速度最快可以被加速到2倍。

如果引入并行程序中的处理器个数，则加速比可以被重新定义为： 
speedup=1PN+S=11−P+PNspeedup=1PN+S=11−P+PN， 
其中P仍然是并行代码所占的比例，N是处理器个数，S是串行代码所占比例（S = 1 - P）。 
![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/amdahl1.gif) ![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/amdahl2.gif)

| N      | P = 0.50 | p = 0.90 | p = 0.95 | p = 0.99 |
| ------ | -------- | -------- | -------- | -------- |
| 10     | 1.82     | 5.26     | 6.89     | 9.17     |
| 100    | 1.98     | 9.17     | 16.80    | 50.25    |
| 1000   | 1.99     | 9.91     | 19.62    | 90.99    |
| 10000  | 1.99     | 9.91     | 19.96    | 99.02    |
| 100000 | 1.99     | 9.99     | 19.99    | 99.90    |

之后我们就迅速意识到并行计算的极限所在，例如上表所示。

> “注明引言：”你可以花费一生的时间使得你的代码的95%都可以被并行，然而你如论投入多少处理器，都不会获得20倍的加速比。

然而，某些问题我们可以通过增加问题的大小来提高其性能。例如：

| 类型       | 时间 | 比例 |
| ---------- | ---- | ---- |
| 2D网格计算 | 85秒 | 85%  |
| 串行比例   | 15秒 | 15%  |

我们可以增加网格的维度，并且将时间步长减半。其结果是四倍的网格点数量，以及两倍的时间步长。之后的花费时间将变为：

| 类型       | 时间  | 比例   |
| ---------- | ----- | ------ |
| 2D网格计算 | 680秒 | 97.84% |
| 串行比例   | 15秒  | 2.16%  |

比起具有固定并行时间百分比的问题，那些可以随着问题规模增大而不断提高并行时间百分比的问题在并行化的意义上更具有可扩展性（复习一下可扩展性的定义^_^）。

**复杂性：** 通常而言，并行计算的程序要比相应的串行计算程序更加复杂，也许复杂一个量级。你不仅需要同时执行不同的指令流，而且需要注意他们之间数据的通信。复杂性通常由涉及软件开发周期各个方面的时间来确定，主要包括：1）设计；2）编码；3）调试；4）调参；5）维护。

遵循良好的软件开发实践对并行应用开发是至关重要的，尤其是在除你之外的其他人还需要和你合作的情况下。

**可移植性：** 由于一些API的标准化，例如MPI，POSIX线程以及OpenMP，并行程序的可移植性问题并不像过去那么严重，然而：

- 所有串行程序中所遇到的可移植性问题都会出现在相应的并行程序中。
- 尽管一些API已经被标准话，但是在一些细节的实现上任然有差异，有时候这些细节实现会影响到可移植性。
- 操作系统也会是导致可移植性的关键因素。
- 硬件架构的不同有时候也会影响到可移植性。

**资源需求：** 
并行编程的主要目标就是降低时钟等待时间。然而要做到这一点，需要更多的CPU时间。例如，一个在8个处理器上跑了一个小时的并行程序实际上花费了8小时的CPU时间。

并行程序所需要的内存开销往往要大于相对应的串行程序，这是因为我们有时候需要复制数据，以满足库和子系统对并行算法的要求。

对于运行时间较短的并行陈顾，实际性能反而有可能比相对应的串行程序有所降低。这是由于并行环境的建立，任务创建，通讯，任务结束等在这个运行时间中有可能会占有比较大的比例。

**可扩展性：** 
基于时间和解决方案的不同，可以将扩展性分为**强可扩展性**和**弱可扩展性**：

**强可扩展性**的特点是：1）在更多处理器被加入的时候，问题本身的规模不会增加；2）目标是将同一问题运行的更快；3）理想状态下，相比于对应的串行程序，运行时间为1/P。

**弱可扩展性**的特点是：1）随着更多处理器被加入，每个处理上需要处理的问题规模保持一致；2）目标是在相同的时间内解决更多规模的问题；3）理想状态下，在相同时间内，可以解决的问题规模增加为原问题规模的P倍。

并行程序的性能提高取决于一系列相互依赖的因素，简单地增加更多的处理器并不一定是唯一的方法。

此外，某些问题可能本身存在扩展性的极限，因此添加更多的资源有时候反而会降低性能。这种情形会出现在很多并行程序中。

硬件在可扩展性方面也扮演者重要角色，例如：1）内存-CPU之间的带宽；2）通讯网络的带宽；3）某个机器或者某个机器集合中的内存大小；4）时钟处理速度。

支持并行的库或者子系统同样也会限制并行程序的可扩展性。 
![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/strongWeakScaling.gif)

### **4 并行计算机的内存架构**

#### **4.1 共享内存**

**一般特征：** 共享内存的并行计算机虽然也分很多种，但是通常而言，它们都可以让所有处理器以全局寻址的方式访问所有的内存空间。多个处理器可以独立地操作，但是它们共享同一片内存。一个处理器对内存地址的改变对其它处理器来说是可见的。根据内存访问时间，可以将已有的共享内存机器分为**统一内存存取**和**非统一内存存取**两种类型。

**统一内存存取(Uniform Memory Access)：** 目前更多地被称为*对称多处理器机器(Symmetric Multiprocessor (SMP))*，每个处理器都是相同的，并且其对内存的存取和存取之间都是无差别的。有时候也会被称为CC-UMA (Cache coherent - UMA)。缓存想干意味着如果一个处理器更新共享内存中的位置，则所有其它处理器都会了解该更新。缓存一致性是在硬件级别上实现的。

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/shared_mem.gif)

**非统一内存存取(Non-Uniform Memory Access)：** 通常由两个或者多个物理上相连的SMP。一个SMP可以存取其它SMP上的内存。不是所有处理器对所有内存都具有相同的存取或者存取时间。通过连接而进行内存存取速度会更慢一些。如果缓存相缓存想干的特性在这里仍然被保持，那么也可以被称为CC-NUMA。

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/numa.gif)

**优点：**全局地址空间提供了一种用户友好的编程方式，并且由于内存与CPU的阶级程度，使得任务之间的数据共享既快速又统一。

**缺点：**最大的缺点是内存和CPU之间缺少较好的可扩展性。增加更多的CPU意味着更加共享内存和缓存想干系统上的存取流量，从而几何级别地增加缓存/内存管理的工作量。同时也增加了程序员的责任，因为他需要确保全局内存“正确”的访问以及同步。

#### **4.2 分布式内存**

**一般概念：** 分布式内存架构也可以分为很多种，但是它们仍然有一些共同特征。分布式内存结构需要通讯网络，将不同的内存连接起来。一般而言，处理器会有它们所对应的内存。一个处理器所对应的内存地址不会映射到其它处理器上，所以在这种分布式内存架构中，不存在各个处理器所共享的全局内存地址。 
![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/distributed_mem.gif)

由于每个处理器具有它所对应的局部内存，所以它们可以独立进行操作。一个本地内存上所发生的变化并不会被其它处理器所知晓。因此，缓存想干的概念在分布式内存架构中并不存在。

如果一个处理器需要对其它处理器上的数据进行存取，那么往往程序员需要明确地定义数据通讯的时间和方式，任务之间的同步因此就成为程序员的职责。尽管分布式内存架构中用于数据传输的网络结构可以像以太网一样简单，但在实践中它们的变化往往也很大。

**优点：** 1）内存可以随着处理器的数量而扩展，增加处理器的数量的同时，内存的大小也在成比例地增加；2）每个处理器可以快速地访问自己的内存而不会受到干扰，并且没有维护全局告诉缓存一致性所带来的开销；3）成本效益：可以使用现有的处理器和网络。

**缺点：** 1）程序员需要负责处理器之间数据通讯相关的许多细节；2）将基于全局内存的现有数据结构映射到该分布式内存组织可能会存在困难；3）非均匀的内存访问时间——驻留在远程结点上的数据比本地结点上的数据需要长的多的访问时间。

#### **4.3 混合分布式-共享内存**

**一般概念：** 目前世界上最大和最快的并行计算机往往同时具有分布式和共享式的内存架构。共享式内存架构可以是共线内存机器或者图形处理单元(GPU)。分布式内存组件可以是由多个共享内存/GPU连接而成的系统。每个结点只知道自己的内存，不知道网络上其它结点的内存。因此，需要在不同的机器上通过网络进行数据通讯。

从目前的趋势来看，这种混合式的内存架构将长期占有主导地位，并且成为高端计算在可见的未来中的最好选择。

**优缺点：**

1）继承了共享式内存和分布式内存的优缺点；

2）优点之一是可扩展性；

3）缺点之一是编程的复杂性。

### **5. 并行计算模型**

#### **5.1 概述**

常见的并行编程模型包括：共享内存模型（无线程），线程模型，分布式内存/消息传递模型，数据并行模型，混合模型，单程序多数据模型，多程序多数据模型。

并行计算模型是作为硬件和内存架构之上的一种抽象存在。虽然不一定显而易见，但这些模型并不和特定的机器和内存架构有关。事实上，任何一个并行计算模型从理论上来讲都可以实现在任何一种硬件上。下面是两个例子。

**在分布式内存架构上的共享内存模型。** 机器内存分布于网络上的不同结点，但是对于用户而言，看到的确实一个具有全局地址空间的共享内存。这种方法通常被称为“虚拟共享存储器”。 
![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/modelAbstraction1.gif) ![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/ksr1.gif)

**在共享内存架构上的分布式内存模型。** 最主要的是消息传递接口（MPI）。每个任务都可以直接访问跨所有机器的全局地址空间。然而，它们之间数据交换却是通过消息传递机制实现的，就像在分布式内存网络中所进行的那样。 
![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/modelAbstraction2.gif) ![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/sgiOrigin2000.jpg)

那么到底使用哪一种呢？这往往取决于现有条件以及用户的偏好。没有最好的模型，但对模型的实现质量却可能存在差别。下面我们将分别描述上面提到的各种并行计算模型，并且讨论它们在实践中的一些实现方式。

#### **5.2 共享内存模型（无线程）**

在这种并行计算模型中，处理器/任务共享内存空间，并且可以异步地对内存进行读写。很多机制被用来控制对内存的存取，例如锁/信号量等，用来解决访问冲突以及避免死锁。这应该是最简单的并行计算模型了。

从编程者的角度来看，这种模型的好处之一数据“拥有者”的缺失，所以他们不必明确地指定数据之间的通讯。所有的处理器都可以看到和平等地存取共享内存。程序开发将因此而变得容易。

性能方面的一个重要缺点是对**数据局部性**的理解和管理讲变得困难：1）保持数据的局部性将有利于减少内存的存取负担，缓存刷新次数以及总线流量。而当多个处理器使用同一数据时，这些负担将会经常发生；2）不幸的是，保持数据的局部性往往比较难以理解，并且其难度超过一般用户的水平。

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/sharedMemoryModel.gif)

**实现：** 单机共享内存机器，本地操作系统，编译器及其对应的硬件都支持共享内存编程。在分布式内存机器上，内存在物理上存在于网络上不同的结点上，但是可以通过特殊的硬件和软件，将其变为全局可见。

#### **5.3 线程模型**

这是共享内存编程的一种模式。在线程模型中，一个单个的“重量级”进程可以拥有多个“轻量级”的并发执行路径。例如下图所示：

- 主程序 **a.out** 在本地操作系统上运行。**a.out** 需要加载所有的系统和用户资源来运行，这是里面的“重量级”进程。
- **a.out** 首先执行一些串行工作，然后生成一系列任务（线程），而这些线程可以在操作系统中被并发地执行。
- 每个线程具有本地数据，但同时也共享 **a.out** 的所有资源。这节约了所有线程都复制程序资源的的开销。而每个线程同时也从全局内存中获益，因为它可以共享 **a.out** 的内存空间。
- 一个线程的工作可以被描述为主程序的一个子程序。任何线程都可以在其它线程运行的同时执行任何子程序。
- 线程之间的通讯通过全局内存来实现（对全局地址的更新）。这需要建立一种同步机制，以保证在同一时刻，不会有多个线程对同一块地址空间进行更新。
- 线程可以随时生成和结束，但是 **a.out** 却一直存在，以提供所需的共享资源，直到整个应用程序结束。

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/threadsModel2.gif)

**实现：** 从编程的角度来讲，线程的实现通常包括如下两个方面：

- 库函数或者子程序，这些库函数或者子程序可以在并行源代码中被调用；
- 嵌入在并行或者串行源代码中的一组编译器指令集合。

程序员需要同时定义上面的两个方面（尽管有时候编译器可以提供帮助）。

线程并不是一个新概念。之前硬件供应商就曾经实现过他们自己的线程。由于这些线程的实现各不相同，所以使得程序员很难开发可移植的多线程应用程序。

而标准化工作却导致了两种完全不同的线程实现方式：**POSIX Threads** 和 **OpenMP**。

**POSIX Threads**：由IEEE POSIX 1003.1c standard (1995)定义，仅支持C语言，是Unix/Linux操作系统的一部分，是基于库函数的，也通常被称为“Pthreads”。是非常明确的并行机制，需要程序员注意大量的细节。更多信息可见：[POSIX Threads tutorial](https://computing.llnl.gov/tutorials/pthreads/)。

**OpenMP**：是一个工业标准，有一组主要计算机硬件和软件提供商，组织和个人联合发起和定义，是基于编译器指令的，具有可移植性/跨平台性，目前支持的包括Unix和Windows平台，目前支持C/C++和Fortran语言。非常简单和医用，提供了“增量并行”，可以从串行代码开始。更多信息可见：[OpenMP tutorial](https://computing.llnl.gov/tutorials/openMP/)。

也有一些其它的常见线程实现，但是在这里没有讨论，包括：

- Microsoft threads
- Java, Python threads
- CUDA threads for GPUs

#### **5.4 分布式内存/消息传递模型**

这种模型具有如下特点：

- 在计算的过程中，每个任务都仅仅使用它们自身的本地内存。多个任务既可以寄宿在同一个物理机器上，也可以跨越不同的物理机器。
- 任务之间的数据交换是通过发送和接收消息而实现的。
- 数据传输通常需要不同进程之间的协同操作才能实现。例如，一个发送操作需要同时对应一个接收操作。

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/msg_pass_model.gif)

**实现：** 从编程的角度来讲，消息传递的实现通常包括子程序库。对这些子程序的调用往往就嵌入在源代码中。编程者负责并行机制的实现。

自从1980年代以来，出现了多种消息传递库函数。这些实现各不相同，导致编程者很难开发出移植性好的应用程序。自从1992年开始，MPI Forum形成，其主要目标是建立消息传递的标准接口。消息传递接口（Message Passing Interface (MPI)）的第一部分在1994年发布，第二部分在1996年发布，第三部分在2012年发布。所有的MPI说明可以参见 <http://mpi-forum.org/docs/>。MPI成为了事实上的消息传递的工业标准，取代了所有其它消息传递的实现。几乎所有流行的并行计算平台都存在MPI的实现，但并不是所有的实现都包含了MPI-1，MPI-2和MPI-3的所有内容。关于MPI的更多信息可以参见 [MPI tutorial](https://computing.llnl.gov/tutorials/mpi/)。

#### **5.5 数据并行模型**

通常也被称为“**全局地址空间分区**”（Partitioned Global Address Space (PGAS)）模型。具有如下特点：

- 地址空间被认为是全局的。
- 大多数的并行工作聚焦于在数据集上的操作。数据集通常被组织成为常用的结构，例如数组，数立方等。
- 一系列任务在同一块数据结构上操作，但是每个任务却操作在该数据结构的不同分区上。
- 每个任务在数据结构的不同分区上执行相同的操作，例如，“给每个数组元素加上4”。

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/data_parallel_model.gif)

在共享内存的架构下，所有的任务通过全局内存方式来对数据进行存取；在分布式内存架构下，根据任务分配，全局数据结构在物理或者逻辑上被进行分割。

**实现：** 目前，基于数据并行/PGAS模型，有如下几个相对有名的实现：

- **Coarray Fortran: **为了支持SPMD并行编程而在Fortran 95上做的一个小的扩展，是编译器相关的，更多信息可以参见：<https://en.wikipedia.org/wiki/Coarray_Fortran>。
- **Unified Parallel C (UPC):** 为了支持SPMD并行编程而在C语言基础上做的扩展，也是编译器相关的，更多信息可以参见：<http://upc.lbl.gov/>。

#### **5.6 混合模型**

混合模型指的是包含了至少两个我们前面提到的并行计算模型的模型。目前，最常见的混合模型的例子是消息传递模型（MPI）和线程模型（OpenMP）的结合：

- 线程使用本地数据完成计算密集型的任务；
- 不同的进程则在不同的结点上通过MPI完成数据通讯。

这种混合模型非常适合目前流行的硬件环境——多核计算机组成的集群系统。

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/hybrid_model.gif)

另外一种类似的，但原来越流行的例子是采用MPI和CPU-GPU的混合编程：

- 采用MPI的任务运行于CPU上，使用本地内存上的数据，但是通过网络与其它任务进行数据交换；
- 而计算密集型的核则被加载到GPU上进行计算；
- 而结点内部的内存和GPU上的数据交换则通过CUDA（或者类似的东西）进行数据交换。

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/hybrid_model2.gif)

其它混合模型还包括：

- MPI和Pthreads的混合；
- MPI和non-GPU加速器的混合。
- …

#### **5.7 单程序多数据模型(SPMD)和多程序多数据模型(MPMD)**

**单程序多数据模型(Single Program Multiple Data (SPMD))：** SPMD事实上是一种可以架构在其它并行编程模型之上的更“高级”的编程模型：

- 单程序：所有任务都执行同一个程序的拷贝，而这里的程序可以是线程，消息传递，数据并行甚至混合；
- 多数据：不同的任务操作于不同的数据。

SMPD通常需要指定任务的执行逻辑，也就是不同的任务可能会根据分支和逻辑关系，去执行整个程序的某个部分，也就是说，不是所有的任务都必须执行整个程序——有可能只是整个程序的某个部分。（译者注：如果不强调这一点，SPMD就退化成了数据并行模型了。）

而这种采用消息消息传递或者混合编程的SPMD模型，有可能是今天运行在多核集群系统上的最常见的并行计算模型了。

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/spmd_model.gif)

**多程序多数据模型(Multiple Program Multiple Data (MPMD))：**

和SPMD一样，多程序多数据模型实际上也是一种可以架构在其它并行编程模型基础上的“高级”并行编程模型：

- 多程序：任务可以同时执行不同的程序，这里的程序可以是线程，消息传递，数据并行或者它们的混合。
- 多数据：所有的任务可以使用不同的数据。

MPMD应用并不像SPMD应用那么常见，但是它可能更适合于特定类型的程序。

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/mpmd_model.gif)

### **6 并行程序设计**

#### **6.1 自动 vs. 手动并行化**

设计和实现并行程序是一个非常手动的过程，程序员通常需要负责识别和实现并行化，而通常手动开发并行程序是一个耗时，复杂，易于出错并且迭代的过程。很多年来，很多工具被开发出来，用以协助程序员将串行程序转化为并行程序，而最常见的工具就是可以自动并行化串行程序的并行编译器(parallelizing compiler)或者预处理器 (pre-processor)。

并行编译器通常以如下两种方式工作：

- **完全自动：** 由编译器分析源代码并且识别可以并行化的部分，这里的分析包括识别出哪些部分满足并行化的条件，以及权衡并行化是否真的可以提高性能。循环（包括do, for）通常是最容易被并行化的部分。
- **程序员指令：** 通过采用“编译器指令”或者编译器标识，程序员明确地告诉编译器如何并行化代码，而这可能会和某些自动化的并行过程结合起来使用。

最常见的由编译器生成的并行化程序是通过使用结点内部的共享内存和线程实现的（例如OpenMP）。

如果你已经有了串行的程序，并且有时间和预算方面的限制，那么自动并行化也许是一个好的选择，但是有几个重要的注意事项：1）可能会产生错误的结果；2）性能实际上可能会降低；3）可能不如手动并行那么灵活；4）只局限于代码的某个子集（通常是循环）；5）可能实际上无法真正并行化，由于编译器发现里面有依赖或者代码过于复杂。

接下来的部分仅适用于手动开发并行程序。

#### **6.2 理解问题和程序**

毫无疑问，开发并行程序的第一步就是理解你将要通过并行化来解决的问题。如果你是从一个已有的串行程序开始的，那么你需要首先理解这个串行程序。

在开始尝试开发并行解决方案之前，需要确定该问题是否真正可以被并行化。

- 一个容易被并行化的问题如下。该问题容易被并行化，因为每个分子构象都是独立且确定的。计算最小能量构象也是一个可以被并行化的问题。

> 计算数千个独立分子构象中每一个的势能，完成之后，找出能量构象最小的那一个。

- 一个不太可能被并行化的问题如下。由于F(n)同时依赖于F(n-1)和F(n-2)，而后者需要提前被计算出来。

> 采用如下公式计算菲波那切数列 （0,1,1,2,3,5,8,13,21,…）：F(n) = F(n-1) + F(n-2)。

识别程序的**关键点 (hotspots)**：

- 了解哪个部分完成了程序的大多数工作。大多数的科学和技术程序中，大多数的工作都是在某些小片段中完成的。
- 可以通过剖析器或者性能分析工具来帮助你分析。
- 专注于程序中这些关键点，忽略那些占用少量CPU的其余部分。

识别程序中的**瓶颈 (bottlenecks)**：

- 有没有导致程序不成比例地变慢的，或者导致并行程序停止或者延迟的部分？例如有时候输入输出操作会导致程序变慢。
- 有时候也可能通过重构程序，或者采用不同的算法来降低或者消除这些执行很慢的区域。

识别并行化的抑制因素。一个常见的类型是*数据依赖性 (data dependence)*，例如上面提到的菲波那切数列的例子。

如果可能的话，研究其它算法。这可能是设计并行程序的过程中最重要的一点。

利用成熟的第三方并行软件，或者高度成熟的数学库（例如IBM的ESSL，Intel的MKL，AMD的AMCL等）。

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/hotspotBottleneck2.jpg)

#### **6.3 分割 (Partitioning)**

设计并行程序的第一步就是将程序分解成为可以分配到不同任务中去的“块”。这被称为程序的分解 (decomposition) 或者分割 (partitioning)。通常有两种基本方法可以将并行任务进行分解：**域分解**和**功能分解**。

**域分解：** 在这种分割方式中，将数根据问题进行分解。每个并行任务操作数据的一部分。

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/domain_decomp.gif)

通常由不同的方式来对数据进行分割：

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/distributions.gif)

**功能分解：**

在这种方法中，重点在于要执行的计算，而不是计算所操纵的数据。问题根据要做的工作进行分解，然后每个任务执行整个工作的一部分。

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/functional_decomp.gif)

这种功能分解非常适合于可分为不同任务的问题，例如：

- **生态系统建模：** 每个程序计算给定组的人口，其中每个组的正常取决于其邻居的增长。锁着时间的推移，每个进程计算当前状态，然后与相邻群体交换信息。然后所有任务进行下一步计算。

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/functional_ex1.gif)

- **信号处理：** 音频信号数据集通过四个不同的计算滤波器，每个滤波器是一个单独的过程。第一段数据必须通过第一个滤波器，然后才能进入第二个滤波器。当这样做时，第二段数据通过了第一个滤波器。当第四个数据段处于第一个滤波器时（以及之后），四个任务都会变得很忙。

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/functional_ex2.gif)

- **气候建模：** 每个模型组件都可以被认为是一个单独的任务。箭头表示计算期间组件之间的数据交换：大气模型需要使用风速数据生成海洋模型；海洋模型使用海面温度数据生成大气模型等。

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/functional_ex3.gif)

在实践中将这两种分解方式结合起来是很自然的，也是很常见的。

#### **6.4 通讯 (Communications)**

任务之间的通讯需求取决于你的问题：

**不需要通讯的情况：** 一些程序可以被分解成为并发执行的任务，而这些任务之间不需要共享数据。这类问题往往被称为“尴尬并行”——任务之间不需要数据通讯。例如如果我们需要对下面一副图片的颜色进行取反（黑色的部分变为白色的，白色的变为黑色的），那么图像数据可以被简单地分解为多个任务，并且每个任务可以被独立地执行。

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/black2white.gif)

**需要通讯的情况：** 大多数并行程序并不像上一问题这么简单，任务之间确实需要共享数据。例如下面这幅热度扩散图需要一个任务知道其它任务在它的邻居方格中的计算结果。邻居数据的变化将直接影响到该任务的数据。

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/heat_partitioned.gif)

**设计通讯需要考虑的因素：** 在设计程序任务之间的通讯时，有大量的重要因素需要考虑：

- **通讯开销：** 1）任务间通讯几乎总是意味着开销。2）而可以用于计算的机器周期以及资源会转而用于对数据的封装和传输。3）频繁的通讯也需要任务之间的同步，这有可能会导致任务花费时间等待而不是执行。4）竞争通讯流量可能使可用的网络带宽饱和，从而进一步加剧性能问题。
- **延迟 vs. 带宽：** 1）*延迟* 指的是从A点到B点发送最小量的信息所需要花费的时间，通常以毫秒计。2）*带宽* 指的是单位时间内可以传输的数据总量，通常以M/S或者G/S来计。3）发送大量的短消息可能会导致延迟成为通讯的主要开销。通常情况下将大量小信息封装成为大消息会更加有效，从而提高通讯带宽的利用效率。
- **通讯可见性：** 1）在消息传递模型中，通讯往往是显式和可见的，并且在编程者的控制之下。2）在数据并行模型中，通讯对编程者来说往往是透明的，尤其是在分布式内存架构中。编程者往往甚至不能明确知道任务之间的通讯是如何完成的。
- **同步 vs. 异步通讯：** 1) 同步通讯需要共享数据的任务之间某种意义上的“握手”。这既可以由编程者显式地指定，也可以在底层被隐式地实现而不为编程者所知。2）同步通讯业常常被称为“阻塞通讯”，因为一些任务必须等待直到它们和其它任务之间的通讯完成。3）异步通讯允许任务之间独立地传输数据。例如任务1可以准备并且发送消息给任务2，然后立即开始做其它工作，它并不关心任务2什么时候真正受到数据。4）异步通讯也常常被称为“非阻塞通讯”，因为在通讯发生的过程中，任务还可以完成其它工作。5）在计算和通讯自由转换是异步通讯的最大优势所在。
- **通讯的范围：** 明确哪些任务之间需要通讯在设计并行代码的过程中是非常关键的。下面两种通讯范围既可以被设计为同步的，也可以被设计为异步的：1）*点对点通讯：* 涉及到两个任务，其中一个扮演消息发送者/生产者的角色，另外一个扮演消息接受者/消费者的角色。2）*广播通讯：* 涉及到多于两个任务之间的数据共享。这些任务通常处于一个组或者集合中。

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/collective_comm.gif)

- **通讯的效率：** 通常编程者具有影响通讯性能的选择，这里列举其中一些：1）对于一个给定的模型，究竟应该采用哪一种实现？例如对于消息传递模型而言，一种MPI的实现可能在某个给定的硬件下比其它实现要快。2）什么采用什么类型的通讯操作？正如前面所提到的，异步通讯操作往往可以提高程序的整体性能。3）网络结构（network fabric）：某些平台可能会提供多于一个的网络结构。那么究竟哪一个最好？
- **开销和复杂性：**

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/helloWorldParallelCallgraph.gif)

最后需要意识到，上面提到的仅仅是需要注意的问题的一部分！

#### **6.5 同步 (Synchronization)**

管理工作的顺序和执行它的任务是大多数并行程序设计的关键，它也可能是提升程序性能的关键，通常也需要对某些程序进行“串行化”。

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/sychronization2.jpg)

**同步的类型：**

- **屏障：** 1）这通常意味着会涉及到所有任务；2）每个任务都执行自身的工作，直到它遇到屏障，然后它们就停止，或者“阻塞”；3）当最后一个任务到达屏障时，所有任务得以同步；4）接下来可能发生的事情就有所变化了。通常会执行一段串行代码，或者所有的任务在这里都结束了。
- **锁/信号量：** 1）可以涉及任意多个任务；2）通常用于对全局数据或者某段代码的存取串行化（保护），在任一时刻，只有一个任务可以使用锁/信号量；3）第一个任务会获得一个锁，然后该任务就可以安全地对该保护数据进行存取；4）其它任务可以尝试去获得锁，但必须等到当前拥有该锁的任务释放锁才行；5）可以是阻塞的也可以是非阻塞的。
- **同步通讯操作：** 1）仅仅涉及到执行数据通讯操作的任务；2）当一个任务执行数据通讯操作时，通常需要在参与通讯的任务之间建立某种协调机制。例如，在一个任务发送消息时，它必须收到接受任务的确认，以明确当前是可以发送消息的；3）在消息通讯一节中也已经说明。

#### **6.6 数据依赖性 (Data Dependencies)**

**定义：**

- **依赖：** 当语句的执行顺序影响程序的运行结果时，我们称程序语句之间存在依赖关系。
- **数据依赖：** 数据依赖是由不同任务多次存取相同的内存位置而产生的。

数据依赖也是并行程序设计中的关键，因为它是并行化中一个重要的抑制因素。

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/dependencies1.jpg)

**例子：**

- 循环相关的数据依赖：下面这段代码中，`A(J-1)` 必须在`A(J)` 之前被计算出来，因此说`A(J)` 与 `A(J-1)` 之间存在数据依赖，所以并行化在这里被抑制。如果任务2中有`A(J)`，任务1中有`A(J-1)`，那么要计算出正确的`A(J)` 则需要：1）**分布式内存架构**：任务2必须在任务1计算结束之后，从任务1处中获取`A(J-1)` 的值。2）**共享内存架构**：任务2在任务1完成对`A(J-1)` 的更新之后，对`A(J-1)` 进行读取。

```
DO J = MYSTART,MYEND
   A(J) = A(J-1) * 2.0
END DO123
```

- 循环无关的数据依赖：在下面的例子中并行化也同样被抑制。`Y`的值依赖于：1）**分布式内存架构：** 在任务之间是否需要或者何时需要对`X`的值的通讯。2）**共享内存架构：** 哪个任务最后存储`X`的值。

```
task 1        task 2
------        ------

X = 2         X = 4
  .             .
  .             .
Y = X**2      Y = X**31234567
```

尽管在并行程序设计中，对所有数据依赖的识别都是重要的，但循环相关的数据依赖尤其重要，因为循环往往是最常见的可并行化部分。

**处理方法：** 1）分布式内存架构：在同步点传输所需数据；2）共享式内存结构：在任务之间同步读写操作。

#### **6.7 负载均衡 (Load Balancing)**

负载均衡是指在任务之间分配大约相等数量的工作的做法，以便所有任务在所有时间保持繁忙，它也可以被认为是使任务空闲时间最小化。出于性能原因方面的考虑，负载均衡对并行程序很重要。例如如果所有恩物都收到屏障同步点的影响，那么最慢的任务将决定整体性能。

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/load_bal1.gif)

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/loadImbalance2.jpg)

**如何实现负载均衡：**

- **平均分配任务量：**

对于数组/矩阵而言，如果每个任务都执行相同或者类似的工作，那么在任务之间平均分配数据集；2）对于循环迭代而言，如果每个迭代完成的工作量大小类似，则在每个任务中分配相同或者类似的迭代次数；3）如果你的架构是由具有不同性能特征的机器异构组合而成，那么请确保使用某种性能分析工具来简则任何的负载不平衡，并相应调整工作。

- **采用动态任务分配方法：**

即使数据在任务之间被平均分配，但是某些特定类型的问题也会导致负载不平衡，如下面三个例子所示。

![img](https://computing.llnl.gov/tutorials/parallel_comp/images/sparseMatrix.gif) 
稀疏矩阵：某些任务会具有真实数据，而大多数任务对应的数据却为0。

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/adaptiveGrid.jpg) 
自适应网格：某些方格需要被细分，而其它的不需要。

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/n-body.jpg) 
N体模拟：粒子可能会跨任务域迁移，因此某些任务会需要承担更多的工作。

当每个任务的工作量是可变的，或者无法预测的，那么可以采用 **调度任务池 (Scheduler-task pool)** 方法。每当某个任务完成了它的工作，它就可以从工作队列中领取新的任务。

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/schedulerTaskPool.gif)

最终来看，可能需要设计一种在代码中动态发生和处理负载不平衡的算法。

#### **6.8 粒度 (Granularity)**

**计算通讯比 (computation / Communication Ratio)：** 在并行计算中，粒度是对计算与通讯的比例的定性度量。计算周期通常通过同步时间与通讯周期分离。

**细粒度并行化 (Fine-grain Parallelism)：** 1）在通讯事件之外进行相对较少的计算工作；2）计算通讯率较低；3）方便负载均衡；4）意味着较高的通讯开销以及较少的性能提升机会；5）如果粒度过细，任务之间的通讯和同步的开销可能需要比计算更长的时间。

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/granularity2.gif)

**粗粒度并行化 (Coarse-grain Parallelism)：** 1）在通讯/同步事件之外需要较大量的计算工作；2）较高的计算/通讯比；3）意味着较大的性能提升机会；4）难以进行较好的负载均衡。

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/granularity3.gif)

**最佳选择：** 最有效的粒度取决于具体算法及其所运行的硬件环境。在大多数情况下，与通讯/同步相关的开销相对于执行速度很高，因此具有粗粒度的问题是相对有利的。而从另外一方面来讲，细粒度则可以帮助减少由负载不均衡所造成的开销。

#### **6.9 输入输出 (I/O)**

**坏消息：** 1）I/O操作通常被认为是并行化的抑制剂；2）I/O操作通常比内存操作需要多个数量级的时间；3）并行I/O系统可能不成熟或者不适用于所有平台；4）在所有任务均可以看到相同文件空间的环境中，写操作可能导致文件被覆盖；5）读操作可能受到文件服务器同时处理多个读取请求的能力影响；6）必须通过网络进行的I/O操作（NFS，非本地）可能导致严重的性能瓶颈，甚至导致文件服务器崩溃。

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/memoryAccessTimes.gif)

**好消息：** 已经具有不少并行文件系统，例如：

- GPFS：通用并行文件系统 (General Parallel File System)（IBM），现在也被称为IBM Spectrum Scale。
- Lustre：针对Linux的集群（Intel）。
- HDFS：Hadoop分布式文件系统（Apache）。
- PanFS：Panasas ActiveScale File System for Linux clusters (Panasas, Inc.)
- 更多并行文件系统可以参加[这里](https://en.wikipedia.org/wiki/List_of_file_systems#Distributed_parallel_file_systems)。

作为MPI-2的一部分，1996年以来MPI的并行I/O编程借口规范已经可用。

**注意事项：** 1）尽可能减少整体I/O操作；2）如果你有权访问并行文件系统，请使用它；3）在大块数据上执行少量写操作往往比在小块数据上进行大量写操作有着更明显的效率提升；4）较少的文件比许多小文件更好；5）将I/O操作限制在作业的特定串行部分，然后使用并行通讯将数据分发到并行任务中。例如任务1可以读输入文件，然后将所需数据传送到其它任务。同样，任务2可以再从所有其它任务收到所需数据之后执行写入操作；6）跨任务的I/O整合——相比于很多任务都执行I/O操作，更好地策略是只让一部分任务执行I/O操作。

#### **6.10 调试 (Debugging)**

调试并行代码可能非常困难，特别是随着代码量的扩展。而好消息是有一些优秀的调试器可以提供帮助：1）Threaded - Pthreads和OpenMP；2）MPI；3）GPU/accelerator；4）Hybrid。

在LC集群上也安装有一些并行调试工具：1）TotalView (RogueWave Software)；2）DDT （Allinea）；3）Inspector（Intel）；4）Stack Trace Analysis Tool（STAT）（本地开发）。

更多的信息可以参考：[LC web pages](https://hpc.llnl.gov/software/development-environment-software)，[TotalView tutorial](https://computing.llnl.gov/tutorials/totalview/)。

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/debug1.gif)

#### **6.11 性能分析和调优 (Performance Analysis and Tuning)**

对于调试而言，并行程序的性能分析和调优比串行程序更具挑战性。幸运的是，并行程序性能分析和调优有很多优秀的工具。Livemore计算机用户可以访问这种类似工具，其中大部分都在集群系统上。一些安装在LC系统上的工具包括：

- LC’s web pages：<https://hpc.llnl.gov/software/development-environment-software>
- TAU: <http://www.cs.uoregon.edu/research/tau/docs.php>
- HPCToolkit: <http://hpctoolkit.org/documentation.html>
- Open|Speedshop: <http://www.openspeedshop.org/>
- Vampir / Vampirtrace: <http://vampir.eu/>
- Valgrind: <http://valgrind.org/>
- PAPI: <http://icl.cs.utk.edu/papi/>
- mpitrace：<https://computing.llnl.gov/tutorials/bgq/index.html#mpitrace>
- mpiP: <http://mpip.sourceforge.net/>
- memP: <http://memp.sourceforge.net/>

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/perfAnalysis.jpg)

### **7 并行示例**

#### **7.1 数组处理**

此示例演示了对二维数组元素的操作：将某个函数作用于二维数组中的每个元素，其中对每个数组元素的操作都是独立于其它数组元素的，并且该问题是计算密集型的。对于串行程序而言，我们依次对每个元素进行操作，其代码类似于：

```
do j = 1,n
  do i = 1,n
    a(i,j) = fcn(i,j)
  end do
end do12345
```

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/array_proc1.gif)

**问题：**

- 该问题是否可以被并行化？
- 如果对该问题进行分割？
- 需要数据通讯吗？
- 有没有数据依赖？
- 有没有同步需求？
- 是否需要考虑负载均衡？

**并行方案1：**

- 由于对元素的计算彼此之间是独立的，所以可以有“尴尬并行”的解决方案。
- 由于数组元素是均匀分布的，所以每个进程可以拥有阵列的一部分（子阵列）。1）可以选择最佳分配方案以实现高效的内存访问，例如选择步幅为1，或者选择合适的步幅以最大化缓存/内存使用。2）由于可以使单元跨越子阵列，所以分配方案的选择也取决于编程语言，有关选项可以参见第 6.3 节。
- 由于数组元素的计算是彼此独立的，所以不需要任务之间的通讯和同步。
- 由于任务之间的工作量是被平均分配的，所以不需要考虑负载均衡。
- 对数组分割之后，每个任务执行与其拥有的数据相对应的循环部分，其源代码类似于：
- 请注意只有外部循环变量与串行解决方案不同。

```
for i (i = mystart; i < myend; i++) {
  for j (j = 0; j < n; j++) {
    a(i,j) = fcn(i,j);
  }
}12345
```

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/array_proc2.gif)

**一种可能的解决方案：** 1）采用单程序多数据 (SPMD) 模型进行实现，每个任务执行相同的程序；2）主进程对数组进行初始化，将信息发送给子任务，并且接收计算结果；3）子进程接收到信息之后，执行计算任务，并且将结果发送给主进程；4）采用Fortran的存储结构，对数组进行块划分；5）伪代码如下所示。6）具体的C代码可以参见[MPI Program in C](https://computing.llnl.gov/tutorials/mpi/samples/C/mpi_array.c)：

```
find out if I am MASTER or WORKER

if I am MASTER

  initialize the array
  send each WORKER info on part of array it owns
  send each WORKER its portion of initial array

  receive from each WORKER results 

else if I am WORKER
  receive from MASTER info on part of array I own
  receive from MASTER my portion of initial array

  # calculate my portion of array
  do j = my first column,my last column 
    do i = 1,n
      a(i,j) = fcn(i,j)
    end do
  end do

  send MASTER results 

endif123456789101112131415161718192021222324
```

**并行方案2：**

上一个并行方案展示了静态负载均衡：1）每个任务执行固定量的工作；2）某些很快或者负载较轻的处理器将会拥有空闲时间，而最慢执行的任务最终决定整体性能。

如果所有任务在同一台机器上运行相同量的工作，那么静态负载均衡往往并不是一个主要问题。但是如果你确实有负载均衡方面的问题（某些任务比其它任务运行的快），那么你可以采用“任务池”(pool of tasks)模式。

**任务池模式：** 里面包含两个进程：

- **主进程：** 1）拥有任务池；2）如果得到请求，给工作进程发送工作任务；3）从工作进程出收集返回结果。
- **工作进程：** 1）从主进程处获取任务；2）执行计算任务；3）向主进程发送结果。

工作进程在运行之前不知道它将处理数组的哪一部分，以及它将执行多少任务。动态负载均衡发生在运行时：运行最快的任务将完成更多的任务。一段可能的源代码如下：

```
find out if I am MASTER or WORKER

if I am MASTER

  do until no more jobs
    if request send to WORKER next job
    else receive results from WORKER
  end do

else if I am WORKER

  do until no more jobs
    request job from MASTER
    receive from MASTER next job

    calculate array element: a(i,j) = fcn(i,j)

    send results to MASTER
  end do

endif123456789101112131415161718192021
```

**讨论：** 1）在上述任务池例子中，每个任务计算数组的某一个元素，计算与通讯比率是细粒度的；2）细粒度的解决方案为了减少任务空闲时间，往往会导致更多的通讯开销；3）更好地解决方案可能是在每个任务中分配更多的工作，“正确”的工作量依然是依赖于具体问题的。

#### **7.2 圆周率计算**

计算圆周率的方法有多种。我们这里采用蒙特卡洛方法来近似计算圆周率：1）在一个边长为 2r2r 的正方形中画一个半径为 rr 的内接圆；2）内接圆的面积是 πr2πr2，正方形的面积是 4r24r2；3）圆的面积与正方形的面积之比是 πr2/4r2=π/4πr2/4r2=π/4；4）如果你在正方形内随机地产生 NN个点，那么大约会有 N∗π/4N∗π/4 个点（MM）会位于内接圆内；5）所以 ππ 可以被近似为：N∗π/4=MN∗π/4=M，π/4=M/Nπ/4=M/N，π=4∗M/Nπ=4∗M/N；6）注意越多的点产生，则对 ππ的近似就越准确。

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/pi1.gif)

该问题的串行代码大约是这样的：

```
npoints = 10000
circle_count = 0

do j = 1,npoints
  generate 2 random numbers between 0 and 1
  xcoordinate = random1
  ycoordinate = random2
  if (xcoordinate, ycoordinate) inside circle
  then circle_count = circle_count + 1
end do

PI = 4.0*circle_count/npoints123456789101112
```

该问题是计算密集型的——大多数时间将花费在对循环的执行。

**问题：**

- 该问题是否可以被并行化？
- 如何对该问题进行分割？
- 任务之间是否需要通讯？
- 是否存在数据依赖？
- 任务之间是否有同步需求？
- 需要考虑负载均衡吗？

**解决方案：**

又一个容易被并行化的问题：1）每个点的计算都是独立的，不存在数据依赖；2）工作可以被平均分配，不需要考虑负载均衡；3）任务之间不需要通讯和同步。

并行化策略：1）将任务平均划分为相同大小的多个部分，用于在任务池中被执行；2）每个任务独立地完成任务；3）采用单程序多数据（SPMD）模型；4）其中一个任务作为主进程来收集计算结果，并且计算 ππ 的值。

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/pi2.gif)

下面是并行化之后的伪代码：

```
npoints = 10000
circle_count = 0

p = number of tasks
num = npoints/p

find out if I am MASTER or WORKER 

do j = 1,num 
  generate 2 random numbers between 0 and 1
  xcoordinate = random1
  ycoordinate = random2
  if (xcoordinate, ycoordinate) inside circle
  then circle_count = circle_count + 1
end do

if I am MASTER

  receive from WORKERS their circle_counts
  compute PI (use MASTER and WORKER calculations)

else if I am WORKER

  send to MASTER circle_count

endif1234567891011121314151617181920212223242526
```

C语言的示例程序可以参考这里：[MPI Program in C](https://computing.llnl.gov/tutorials/mpi/samples/C/mpi_pi_reduce.c)。

#### **7.3 简单热方程**

大多数并行计算问题需要任务之间的通讯，其中一大部分问题需要“相邻”任务之间的通讯。

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/heat_initial.gif)

二维热方程问题描述了在给定初始温度分布以及边界条件的情况下，温度随着时间的变化。有限差分方案可以采用数值方法求解正方形区域内的热扩散方程：

- 二维数组的元素用来表示正方形区域内的点的温度；
- 边界处的初始问题是0，中心点的问题最高；
- 边界处的问题会保持为0；
- 采用时间步长算法。

每个元素的文图的计算取决于它的邻居的温度：

Ux,y=Ux,y+Cx∗(Ux+1,y+Ux−1,y−2∗Ux,y)+Cy∗(Ux,y−1+Ux,y−1−2∗Ux,y)Ux,y=Ux,y+Cx∗(Ux+1,y+Ux−1,y−2∗Ux,y)+Cy∗(Ux,y−1+Ux,y−1−2∗Ux,y).

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/heat_equation.gif)

串行程序的代码可能使这个样子：

```
do iy = 2, ny - 1
  do ix = 2, nx - 1
    u2(ix, iy) =  u1(ix, iy)  +
        cx * (u1(ix+1,iy) + u1(ix-1,iy) - 2.*u1(ix,iy)) +
        cy * (u1(ix,iy+1) + u1(ix,iy-1) - 2.*u1(ix,iy))
  end do
end do1234567
```

**问题：**

- 该问题是否可以被并行化？
- 如何对该问题进行分割？
- 任务之间是否需要通讯？
- 是否存在数据依赖？
- 任务之间是否需要同步？
- 是否需要考虑负载均衡？

**解决方案：**

该问题更具有挑战性。因为存在数据依赖，所以需要任务之间的通讯和同步。整个数组需要被风格成为子数组，并分配给不同任务，每个任务拥有整个数组的一部分。由于任务量是均匀划分的，所以不需要考虑负载均衡。

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/heat_partitioned.gif)

确定数据依赖：1）一个任务的 *内部元素* 和其它任务之间不存在数据依赖；2）一个任务的 *边界元素* 则和它的邻居任务之间需要产生数据通讯。

采用单程序多数据模型（SPMD）进行实现：1）主进程向工作进程发送初始信息，然后等待并收集来自工作进程的计算结果；2）工作进程在特定的时间步长内计算结果，并与邻居进程之间进行数据交换。伪代码如下：

```
find out if I am MASTER or WORKER

if I am MASTER
  initialize array
  send each WORKER starting info and subarray
  receive results from each WORKER

else if I am WORKER
  receive from MASTER starting info and subarray

  # Perform time steps
  do t = 1, nsteps
    update time 
    send neighbors my border info
    receive from neighbors their border info 
    update my portion of solution array

  end do

  send MASTER results

endif12345678910111213141516171819202122
```

示例程序可以参加：[MPI Program in C](https://computing.llnl.gov/tutorials/mpi/samples/C/mpi_heat2D.c)。

#### **7.4 一维波动方程**

在这个例子中，我们计算经过指定时间量之后，一维波动曲线的振幅。其中的计算会涉及到：1）y轴上的振幅；2）x轴上的位置索引i；3）沿着波动曲线的节点；4）以离散时间步长更新振幅。

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/wave3.gif)

这里需要求解的是如下一维波动方程，其中c是常数。

```
A(i,t+1) = (2.0 * A(i,t)) - A(i,t-1) + (c * (A(i-1,t) - (2.0 * A(i,t)) + A(i+1,t)))1
```

我们注意到，t时刻的振幅取决于前一刻的时间步长(t, t-1)以及相邻点(i - 1, i + 1)。

**问题：**

- 该问题是否可以被并行化？
- 如何对该问题进行分割？
- 任务之间是否需要通讯？
- 人物之间是否存在数据依赖？
- 任务之间是否需要同步？
- 是否需要考虑负载均衡？

**解决方案：**

这是涉及到数据依赖的另外一个例子，其并行方案将会涉及到任务见的通讯和同步。整个振幅阵列被分割并分配给所有的子任务，每个任务拥有总陈列的相等的部分。由于所有点需要相等的工作，所以我们应该均匀地分配节点。我们可以将工作分成多个块，并且允许每个任务拥有大多数连续的数据点。而通讯只需要在数据边界上进行，块大小越大，则所需的通信越少。

![这里写图片描述](https://computing.llnl.gov/tutorials/parallel_comp/images/wave4.gif)

采用单程序多数据（SPMD）模型的实现：1）主进程向工作进程发送初始信息，并且等到各个工作进程返回计算结果；2）工作进程对特定步长之内的任务进行计算，并且在必要的时候和邻居进程进行数据通讯。其伪代码如下：

```
find out number of tasks and task identities

#Identify left and right neighbors
left_neighbor = mytaskid - 1
right_neighbor = mytaskid +1
if mytaskid = first then left_neigbor = last
if mytaskid = last then right_neighbor = first

find out if I am MASTER or WORKER
if I am MASTER
  initialize array
  send each WORKER starting info and subarray
else if I am WORKER`
  receive starting info and subarray from MASTER
endif

#Perform time steps 
#In this example the master participates in calculations
do t = 1, nsteps 
  send left endpoint to left neighbor
  receive left endpoint from right neighbor
  send right endpoint to right neighbor
  receive right endpoint from left neighbor

  #Update points along line
  do i = 1, npoints
    newval(i) = (2.0 * values(i)) - oldval(i) 
    + (sqtau * (values(i-1) - (2.0 * values(i)) + values(i+1))) 
  end do

end do

#Collect results and write to file
if I am MASTER
  receive results from each WORKER
  write results to file
else if I am WORKER
  send results to MASTER
endif 123456789101112131415161718192021222324252627282930313233343536373839
```

程序示例可以参见：[MPI Program in C](https://computing.llnl.gov/tutorials/mpi/samples/C/mpi_wave.c)。

### **8 参考文献和更多信息**

- 作者：[Blaise Barney](mailto:blaiseb@llnl.gov)，Livermore Computing.

- 在万维网上搜索“parallel programming”或者“parallel computing”将会获得大量信息。

- 推荐阅读：


  ​

  - ”Designing and Building Parallel Programs”. Lan Foster. <http://www.mcs.anl.gov/~itf/dbpp/>
  - “Introduction to Parallel Computing”. Ananth Grama, Anshul Gupta, George Karpis, Vpin Kumar. <http://www-users.cs.umn.edu/~karypis/parbook/>
  - “Overview of Recent Supercomputers”. A.J. van der Steen, Jack Dongarra. [OverviewRecentSupercomputers.2008.pdf](https://computing.llnl.gov/tutorials/parallel_comp/OverviewRecentSupercomputers.2008.pdf)

- 图片/图像由作者以及其它LLNL成员创建，或者从不涉及版权的政府或公领域（）获取，或者经所有者同意从其演示文稿或者网页上获取。

- 历史：该材料有下面的资源演化而来，而这些资源将不再被维护或者不再可用。


  ​

  - Tutorials located in the Maui High Performance Computing Center’s “SP Parallel Programming Workshop”.
  - Tutorials located at the Cornell Theory Center’s “Education and Training” web page.