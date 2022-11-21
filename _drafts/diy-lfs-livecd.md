







也许有非常多朋友想将自己制作的Linux系统应用到自己的实际工作生活中，但往往因为各种原因不能在你操作的机器上安装你要的系统，所以目前出现了 各种不同的LiveCD来解决各种应用方面的需求，可能有朋友对这种LiveCD的制作非常感兴趣，我结合我自己的认识和实际的应用经验总结了一套手工制 作LiveCD的方法，希望对想制作LiveCD或对这方面感兴趣的朋友有所帮助。
　　制作LiveCD的方法有非常多，我这里只介绍我实际制作LiveCD的方法，和通常制作LiveCD的软件有所不相同，不过效果类似，希望能起到抛砖引玉的效果，如果有什么建议或想法也欢迎一起探讨，一起提高水平。
　　更新，文章中难免出现一些错误或笔误，也有可能加入新内容，因此难免会进行修正或增删一些内容，如果本文被转载能在
www.linuxsir.org
的LFS版中或在本人的Blog中查看最新版本。

- linuxsir：

http://www.linuxsir.org/bbs/showthread.php?t=322970

- 我的Blog：

http://youbest.cublog.cn

　　如须转载请注明作者为孙海勇（冲天飞豹），并提供转载出处。
　　

## LiveCD原理分析

　　启动过程

1. 计算机启动光盘上的引导程式，这部分我采用grub来完成，当然还能使用如lilo，如果是其他非x86架构的机器也能用其他适合的引导程式。
2. 引导程式装入光盘上的Linux内核，并同时装入一个RAM disk，本文中采用grub的功能来完成，RAM disk使用的是initrd的方式，当然也能采用其他Linux支持的方式，不过可能启动脚本需要进行一定的修改。
3. 内核启动后转入到initrd中linuxrc，由linuxrc来完成各种初始化的操作。
4. linuxrc必须是个可执行文件，这里我们采用的是bash的脚本来完成，本文中的linuxrc主要是完成各种必须的文件加载、设备的识别及内核模块的加载，建立和准备好用户操作根目录环境
5. linuxrc运行结束后会进入根系统的/sbin/init继续执行，该程式将利用/etc/inittab文件来完成系统的启动过程
6. 启动完成，进入用户操作模式。

　　需要注意的地方
　　　　1)RAM disk的大小必须小于Linux中对RAM disk设置的大小，如果超过了必须重新设置内核并重新编译。
　　　　2)RAM disk所使用的文件系统必须是Linux内核内制支持的，在编译内核的时候不能把该文件系统编译成模块。
　　　　3)LiveCD在启动中或启动后会需要创建或写入一些文件，所以这部分文件就需要存放在能写入的文件系统中，这里我采用tmpfs的方式来存放 这些需要变动的文件，经过分析本文所制作的LiveCD需要修改的目录包括/etc、/home、/root、/var，对于/etc则将其打包并在系统 启动中的适当时机解压缩到一个能写入的空间中，而对于/home、/root、/var本文采用了动态生成生成的方式，当然这个没有必须的方法，这个需要 随具体情况来变化，也都能采用类似/etc的处理方式。
准备工作：
　　请按照LFS手册也能参考我写的《第二版　手把手教你怎么建立自己的Linux系统（LFS速成手册）》创建好一个基本的Linux系统，本文的内容将基于一个标准的LFS-6.3系统来完成全部工作。
编译安装必要的工具：

### 1、squashfs的内核补丁

　　本文创建的系统利用的是squashfs方式压缩文件系统，所以必须让内核支持squashfs
　　1)下载squashfs-3.3，并解压缩，在其目录中有linux kernel的补丁，找到你需要的内核补丁，因为LFS-6.3使用的是Linux-2.6.22.5这个版本，因此在内核的原始码目录中使用
　　　　　patch -Np1 -i /squashfs-3.3/kernel-patch/linux-2.6.22/squashfs-patch
　　2)重新设置内核，添加如下选项
　　　　　File systems -> Miscellaneous filesystems -> SquashFS 3.3

　　3)重新编译安装内核，使其支持squashfs

### 2、安装squashfs-tools

　　内核支持squashfs后，还需要有专门的工具来创建squasfs文件，该工具包含在squashfs软件包中，进入squashfs-tools
　　　　make
　　　　install -m 755 unsquashfs mksquashfs /usr/bin
目前系统已能创建并识别squashfs文件系统了。

### 3、安装cdrtools-2.01

　　安装这个包是为了使用其包含的命令mkisofs，这个是建立光盘映像的工具。编译该包能参考BLFS手册中该软件包部分。

```bash
patch -Np1 -i ../cdrtools-2.01-mkisofs_iconv-1.patch

patch -Np1 -i ../cdrtools-2.01-ascii-2.patch

make INS_BASE=/usr DEFINSUSR=root DEFINSGRP=root

make INS_BASE=/usr DEFINSUSR=root DEFINSGRP=root install &&

install -v -m755 -d /usr/share/doc/cdrtools-2.01 &&

install -v -m644 README* ABOUT doc/*.ps ＼

/usr/share/doc/cdrtools-2.01

```

　　　　
　　好，到目前为止，系统已具有了创建LiveCD的必要环境，下面就开始讲解创建一个简单的LiveCD的制作步骤。
准备工作目录：
代码:

```bash
mkdir -pv /opt/iso/{boot,modules}
cd /opt/iso
```

编译制作LiveCD专用的内核：
　　LiveCD能通过initrd来加载需要的设备驱动，因此建议将不是开始运行就需要的功能都制作成模块形式，这样能减少内核的体积，同时也能增加系统的灵活性。
　　内核必须功能（这些功能必须包含在内核本身，不能以模块的形式出现）
　　　　Automatic kernel module loading支持：
　　　　　　这样能方便今后加载模块。
　　　　RAM disk support：
　　　　　　initrd是采用RAM disk的方式使用的，因此内核必须支持该功能
　　　　　　同时，这里设定RAM disk的大小的时候为了方便今后可能的扩展，如果在使用的机器上内存不是非常紧张的话建议调整的大一些，我在这里把起调整为10M大小

　　　　ext2支持：
　　　　　　因为initrd.img本身是个ext2的文件系统，所以要想使用initrd就必须让内核能够识别出ext2文件系统。
　　内核必须的功能，但能使用模块的形式出现
　　　　loop支持：
　　　　　　squashfs需要loop的支持才能正常使用，因此必须包含此功能。
　　　　squashfs支持：
　　　　　　这里制作LiveCD的方法中，压缩的文件系统采用squashfs，所以内核也必须包含此功能。
　　非必须功能：
　　　　如网卡、声卡、磁盘驱动等，这些并不是一定需要的，能根据你的LiveCD的功能来进行取舍，如你需要制作一个应急修复盘，那么磁盘驱动方面就比较重要了，而声卡什么的则不是必须的了；而如果你是要制作一个桌面的LiveCD，那么声卡什么的则非常必要了。
　　编译内核，将内核文件放入/opt/iso/boot目录中，将模块放入/opt/iso/modules中。
制作LiveCD主系统：
　　LiveCD主系统用于提供各种软件，整个系统为了减少存放体积，一般使用压缩的文件系统，这里我使用squashfs来制作。
　　本文使用LFS-6.3的标准系统来制作LiveCD系统，如果你想制作的系统包含更多功能可能需要增加自己的软件后再制作压缩文件系统。
代码:

```bash
cd /
mksquashfs bin lib sbin usr SYSTEM
```


目前在根目录建立好了一个SYSTEM文件，该文件就是个经过squashfs压缩过的文件系统，将该文件放入“制作基地”中。
代码:

```bash 
mv /SYSTEM /opt/iso
```

制作initrd.img：
　　initrd.img的主要目的是为了在不同的机器环境下只加载适用于该机器的一些内核模块，如果将所有的内核模块都加入到内核文件本身中，那么内核 本身将会变的非常臃肿，且占用需要不必占用的资源，因此一般的LiveCD都将大量的驱动编译为模块形式，在必要的时候才将其加载到内存中，这个时候 initrd的作用就比较明显，initrd一般能用来检测系统的硬件来适当的加载各种驱动模块。
　　下面我们就制作一个简单的initrd的实现。
　　1)建立initrd

```bash
cd /opt/iso/boot

mkdir initrd

dd if=/dev/zero of=initrd.img bs=1M count=8

mkfs.ext2 initrd.img

mount -o loop initrd.img initrd　　

```

2)创建initrd下的目录

```bash 
export INITRD=/opt/iso/boot/initrd
cd ${INITRD}
mkdir bin boot dev etc lib proc sbin sys　　
```

3)确定initrd需要的东西
　　　　initrd其实是个最小化的Linux系统，但又必须包含一些检查硬件设备的功能。
　　　　1)一个shell，这里我就直接用bash了，如果你觉得大也能使用其他的shell，比如csh，或busybox中包含的shell。
　　　　　　 
代码:cp -a /bin/bash ${INITRD}/bin　　　　

2)linux kernel模块组，该模块组应该和引导用的内核相匹配，这里直接使用之前为LiveCD专门编译的内核生成的模块。
　　　　　　 
代码:mv /opt/iso/modules ${INITRD}/lib　　　　3)Udev，这里我就直接使用udev来进行硬件的检查，并自动加载必要的内核模块了。
　　　　　　 
代码:cp -a /lib/udev ${INITRD}/lib　　　　　　 
代码:cp -a /lib/firmware ${INITRD}/lib　　　　　　 
代码:cp -a /dev/{console,null} ${INITRD}/dev　　　　　　 
代码:cp -a /etc/udev ${INITRD}/etc　　　　4)modprobe，udev需要使用该命令工具来加载内核。
　　　　5)常用的一些命令。
　　4)编写linuxrc文件
　　　　initrd是从linuxrc文件开始运行的（这个是由内核决定的），那么我们所有的工作就从这个文件开始了
　　　　首先是一些特定的文件系统，后面的许多程式需要这些文件系统的支持
代码:cat > ${INITRD}/linuxrc  /sys/kernel/uevent_helper
echo "Starting Udev..."
/sbin/udevd --daemon
mkdir -p /dev/.udev/queue
/sbin/udevtrigger
/sbin/udevsettle

# 创建用户使用环境
# 在/SYSTEM中准备目录结构
export SYSTEM=/SYSTEM
mkdir -p ${SYSTEM}
mount -t tmpfs tmpfs ${SYSTEM}
mkdir -p ${SYSTEM}/{system,cdrom,dev,proc,sys,tmp,mnt,initrd,home,root}
chmod 0777 ${SYSTEM}/tmp
chmod 0700 ${SYSTEM}/root

# 搜索LiveCD所在的设备
for i in /proc/ide/hd*
do
    if test `cat $i/media` = "cdrom" ; then
        mount -t iso9660 /dev/`basename $i` ${SYSTEM}/cdrom 2>/dev/null
        if test $? = 0 ; then
            if [ -f ${SYSTEM}/cdrom/LABEL ] ; then
                if grep -q "Sunhaiyong’s LiveCD" ${SYSTEM}/cdrom/LABEL ; then
                    break;
                fi
            fi
            umount ${SYSTEM}/cdrom
        fi
    fi
done

# 加载squashfs压缩的主文件系统
mount -o loop -t squashfs ${SYSTEM}/cdrom/SYSTEM ${SYSTEM}/system
ln -s /system/bin ${SYSTEM}
ln -s /system/sbin ${SYSTEM}
ln -s /system/lib ${SYSTEM}
ln -s /system/usr ${SYSTEM}

# 将根目录从initrd转换到主系统
killall /sbin/udevd
echo 0x0100 > /proc/sys/kernel/real-root-dev
pivot_root ${SYSTEM} ${SYSTEM}/initrd
cd /

# 解压缩一些必要的目录和文件
tar xf /cdrom/etc.tar.bz2 -C /

#转移内核文件系统
mount --move /initrd/dev /dev
mount --move /initrd/proc /proc
mount --move /initrd/sys /sys
mkdir -p /var/{run,log,lock}
touch /var/run/utmp /var/log/{btmp,lastlog,wtmp}
chgrp utmp /var/run/utmp /var/log/lastlog
chmod 664 /var/run/utmp /var/log/lastlog

#结束
EOF
目前根据linuxrc用到的命令复制到initrd中
代码:cp -a /bin/{bash,bunzip,bzcat,bzip2,killall,chmod,cp,grep,mount,tar,ln,cat,mkdir} ${INITRD}/bin
cp -a /usr/bin/basename ${INITRD}/bin
cp -a /sbin/pivot_root ${INITRD}/sbin
cp -a /sbin/{udevd,udevsettle,udevtrigger,modprobe} ${INITRD}/sbin复制这些命令所需要的各种动态链接库，可通过ldd命令查看。
代码:cp -a /lib/ld-* ${INITRD}/lib/
cp -a /lib/libc-2.5.1.so ${INITRD}/lib/
cp -a /lib/libc.so.6 ${INITRD}/lib/
cp -a /lib/lib{dl,pthread,rt}-* ${INITRD}/lib/
cp -a /lib/lib{readline,history,ncursesw,dl,bz2,blkid,uuid,rt,pthread}.so* ${INITRD}/lib/
创建一些必要的文件
代码:touch ${INITRD}/etc/fstab创建LiveCD标签

代码:echo "Sunhaiyong’s LiveCD" > /opt/iso/LABEL卸载initrd，并将其压缩
代码:cd /opt/iso/boot
umount initrd
gzip -9 initrd.img
建立etc.tar.bz2文件
代码:cd /opt/iso
cp -a /etc ./能对etc目录进行特定的修改，然后打包压缩
代码:tar -cjf etc.tar.bz2 etc
rm -r etc
创建grub及启动选择
代码:cd /opt/iso
mkdir -p boot/grub
cp -a /usr/lib/grub/i386-pc/stage2_eltorito boot/grub创建menu.lst
代码:cd /opt/iso/boot/grub
cat > menu.lst 
生成iso文件
代码:cd /opt
mkisofs -R -b boot/grub/stage2_eltorito -no-emul-boot -boot-load-size 4 -boot-info-table -o mylivecd.iso iso
　　好了，目前在/opt目录下将出现一个mylivecd.iso文件，将这个文件烧录到光盘上，就能用来引导一台x86的机器了。
注意：
　　如果需要烧录光盘，建议你先用虚拟机来测试一下这个iso文件是否工作正常，避免不必要的浪费。:-)
　　将这个自己制作的LiveCD光盘插入光驱，非常快系统就会完成整个LiveCD的引导过程进入Login状态。
　　本文到目前为止只是完成了一个LiveCD的基本功能，用户能根据自己的需求增加各种功能，这些都能在主系统的后续引导过程中增加。

