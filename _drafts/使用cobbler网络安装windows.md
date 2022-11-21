使用cobbler网络安装windows



Cobbler一般用于部署和安装Linux和Unix，很少用于部署windows，但是仍然有方法可以部署windows。那么部署需要哪些东西呢？

- 一台Technician设备，实际上就是一台windows服务器或者个人计算机，用于安装windows自动部署工具（AIK）。
- AIK（[The Windows Automated Installation Kit](http://www.microsoft.com/en-us/download/details.aspx?id=5753)），自定义安装的一个CD，可以用于管理windows镜像和定义安装应答文件等。
- curl工具，winPE从http服务器上获取数据比较困难。
- 一台部署好的cobbler服务器

准备上面几样东西之后，就可以开始使用cobbler部署windows系统了。

# 1.制作WinPE

首先在一台windows7或者windows server 2008的计算机上安装AIK工具，只需要执行“Windows AIK 安装程序”即可，其他工具不需要安装，制作WinPE的操作均在这台计算机上进行操作。

![](/Users/yangfeilong/github/yangfeiffei.github.io/images/install-windows-in-cobbler/733392-20180306140641955-2125925534.png)

在程序中选择AIK中的“部署工具命令提示”中，输入

```bash
copype amd64 c:\winpe
```

系统将会在C盘下面的winpe目录中自动创建一个64位的WinPE。

如果不需要修改的原装PE就是这样了，但是要实现自动的部署操作系统，还需要对PE进行一些调整。

要修改这个PE的话，需要将winpe.wim这个文件进行修改，先将这个镜像文件挂载到一个目录中

```bash 
imagex /mountrw c:\winpe\winpe.wim 1 c:\winpe\mount
```

- imagex 是一个挂载和卸载wim镜像的工具，可以使用/h 查看帮助；
- 这条命令就是将winpe.wim以可读写的方式挂载到了mount目录中，注意前面有一个1；

在安装操作系统之前需要进行其他一些操作，为了增加我们制作的这个WinPE的通用性，尽量避免经常修改。这里使用一个winpeshl.ini文件来处理。

> Winpeshl.ini controls whether a customized shell is loaded in Windows PE instead of the default Command Prompt window.

创建一个这样的文件`c:\winpe\mount\windows\system32\winpeshl.ini`

```bash
[LaunchApps]
wpeinit
%SYSTEMDRIVE%\local\init.cmd
```

其中wpeinit是初始化WinPE环境，包括加载驱动。init.cmd中为自定义脚本，进行安装操作系统的内容都将在这个脚本中获得。其中`%SYSTEMDRIVE%`是WinPE加载的根目录，一般会是`X：`，严谨一点，还是使用环境变量比较靠谱。

创建自定义脚本目录

```bash
mkdir c:\winpe\mount\local
```

创建定义主机名脚本`c:\winpe\mount\local\setsysname.cmd`

```bash
@echo off

set COBBLER_SERV=cobbler-server  #修改
set COBBLER_MAC=

for /f "tokens=1 delims= " %%H in ('nbtstat -n ^| find "UNIQUE"') do set COBBLER_HNAME=%%H
for /f "tokens=4 delims= " %%M in ('nbtstat -a %COBBLER_HNAME% ^| find "MAC Address"') do set COBBLER_MAC=%%M
for /f "tokens=1-6 delims=- " %%a in ('echo %COBBLER_MAC%') do set COBBLER_MAC=%%a:%%b:%%c:%%d:%%e:%%f

for /f "delims= " %%S in ('curl -s http://%COBBLER_SERV%/cblr/svc/op/autodetect/HTTP_X_RHN_PROVISIONING_MAC_0/eth0%%20%COBBLER_MAC%') do set COBBLER_SYSNAME=%%S
```

创建init脚本，`c:\winpe\mount\local\init.cmd`

```bash
@echo off

rem set COBBLER_SYSTEMNAME and COBBLER_SERV
%SYSTEMDRIVE%\local\setsysname.cmd

rem get the remainder of the init scripts
curl -s -o %TEMP%/mountmedia.cmd http://%COBBLER_SERV%/cblr/svc/op/script/system/%COBBLER_SYSNAME%/?script=mountmedia.cmd
curl -s -o %TEMP%/getks.cmd http://%COBBLER_SERV%/cblr/svc/op/script/system/%COBBLER_SYSNAME%/?script=getks.cmd
curl -s -o %TEMP%/runsetup.cmd http://%COBBLER_SERV%/cblr/svc/op/script/system/%COBBLER_SYSNAME%/?script=runsetup.cmd

rem run 'em
call %TEMP%\mountmedia.cmd
call %TEMP%\getks.cmd
call %TEMP%\runsetup.cmd
```

为了上面的脚本能够执行，需要curl工具复制到WinPE中，拷贝dlls和bin下面目录中的所有文件到`c:\winpe\mount\windows\system32`中即可。

卸载WIM，并将winpe.wim文件复制到ISO中

```bash
imagex /unmount c:\winpe\mount /commit
cp c:\winpe\winpe.wim c:\winpe\ISO\sources\boot.wim
```

将ISO文件夹下面的内容，封装为ISO文件

```bash
oscdimg -n -bc:\winpe\etfsboot.com c:\winpe\ISO c:\winpe\winpe_cobbler_amd64.iso
```









