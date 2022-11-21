# Lustre管理条带(Striping)和空闲空间



# 1. striping工作原理

在lustre文件系统中，mds通过round-robin或者weight方式为ost分配对象。通常情况下，会使用round-robin方式，但是当各个ost之间存在一定使用空间差异（默认17%）时将开始使用weight方式，这将会降低性能，直到空间平衡为止。

文件只能被条带化到有限的ost上，这取决于mdt上保存属性的最大数量。

| MDT类型                         | 文件条带最大数量 |
| ------------------------------- | ---------------- |
| ldiskfs without ea_inode        | 160 OSTs         |
| ldiskfs with ea_inode/zfs-based | 2000 OSTs        |



# 2. lustre striping



使用striping的原因：

- 提供高带宽访问；
- 提供超出oss带宽的性能；
- 提供超大文件的存储空间；

尽量避免使用striping的原因：

- 增加消耗：striping意味着增加更多的锁和额外的网络消耗；
- 增加风险：其中一个ost损坏导致整个文件不能用；



## 2.1 选择stripe size

选择stripe size是个技术活：

- stripe size应该是page size的倍数：在ia64和ppc64最大page size是64K，所以stripe size应该是64k的倍数；
- 最小的推荐stripe size是512KB：lustre在网络中发送的最小chunks是1MB，如果选择更小的stripe size会降低性能；
- 使用高速网络的顺序IO使用stripe size为1MB-4MB最佳：大于4MB会导致更长的锁时间；
- 最大stripe size是4GB：大的stripe size可以提高访问大文件的性能；
- Choose a stripe pattern that takes into account the write patterns of your application；



# 3. setstripe

- `lfs setstripe`创建一个新条带化文件或目录

  ```bash
  lfs setstripe [--size|-s stripe_size] [--count|-c stripe_count] [--index|-i start_ost] [--pool|-p pool_name] filename|dirname”
  ```

  - `stripe_size`：设置为`0`默认1MB，其他值必须是64KB的倍数；
  - `stripe_count`：设置为`0`默认1，`-1`表示所有OSTs；
  - `start_ost`：设置为`-1`默认允许mds选择，从OST0开始；
  - 如果选择的ost不可用或者降级模式，mds会静默选择其他ost；

- 为单个文件设置stripe

  设置stripe size：

    ```bash
  # lfs setstripe -s 4M /mnt/lustre/new_file
    ```

    查看：

    ```bash
  # lfs getstripe /mnt/lustre/new_file
    ```

    设置stripe count：

    ```bash
  # 在所有ost上条带
  # lfs setstripe -c -1 /mnt/lustre/full_stripe
    ```

- 为一个目录设置stripe

	- 使用`lfs setstripe`创建一个新目录或已经存在的目录，参数与文件一样；
	- 如果没有指定stripe，就继承父目录的stripe设置；

- 为一个文件系统设置stripe

    - 设置文件系统跟目录stripe属性即可；

- 在指定的OST上创建文件

    ```bash
    # lfs setstripe --count 1 --index 0 file1
    ```



# 4. getstripe

```bash
# lfs getstripe /mnt/lustre
```

查找文件：

```bash
# lfs find [--recursive | -r] file|directory ...
```

