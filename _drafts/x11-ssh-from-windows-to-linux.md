





SSH的X11 Forwarding功能提供了一个非常好的方法，在你的本地主机上执行远程主机的GUI程序。比如你的开发环境可能是CentOS，你需要在CentOS下编码。但你的工作环境可能是Ubuntu，你在Ubuntu下收发邮件，浏览网页。你当然可以使用CentOS同时作为你的开发与工作环境，但你将不得不忍受CentOS陈旧的桌面系统及用户体验。你也可以通过SSH远程登录到你的CentOS系统，然后使用CLI程序（如Vim）完成你的工作，但如果能使用更方便的GUI程序时（如Eclipse），为什么不呢？现在我们来看看如何实现在Ubuntu上远程执行CentOS主机的GUI程序Eclipse。

**1. 术语简介**
Linux下执行一个GUI程序通常需要两个部分来协调完成，X server与X client。X server是专门负责显示用户界面的，它管理你的显示器，键盘以及鼠标，通常你看到的桌面系统即是由它在背后驱动的，X client则负责程序的逻辑，如果需要使用用户界面，则通过给X server发送请求来完成。通常情况下，X server与X client都运行在同一台机器上，例如我们在Ubuntu上运行任何GUI程序都是这样的。但因为X系统当初设计成是通过socket在X server与X client之间通信的，所以它们也可以运行在不同的机器上。
X11 Forwarding就提供了一个方法，在远程机器上执行X client程序（如Eclipse），但是在本地机器上显示（即运行X server）。
**2. 远程CentOS主机配置**
你需要在你的远程CentOS主机上配置OpenSSH服务，启用X11 Forwarding。在OpenSSH的配置文件中（/etc/ssh/sshd_config），打开如下两项：

```
AllowTcpForwarding yes
X11Forwarding yes

```

CentOS 5.x系列这两项是默认打开的。如果没有的话，打开这两个选项，然后重启sshd服务。
注意：
使用X11 Forwarding并不需要在远程主机上运行桌面系统，即执行startx。
使用X11 Forwarding需要安装rpm包xorg-x11-xauth，如果你在安装CentOS系统时，选择了安装X Window System，那这个包是默认安装的。

```
yum -y install xorg-x11-xauth xclock
#xclock 是用来测试gui输出的
/etc/init.d/sshd restart

```

**3. 本地Ubuntu主机配置**
在Ubuntu桌面下，已经有X server在运行了，所以不需要任何配置，只需打开终端，然后执行如下ssh命令登录远程CentOS：
ubuntu:~# ssh -X user@centos

登录进以后直接运行eclipse就可以了。
centos:~# eclipse

**其他设置**
在Ubuntu桌面下，对OpenSSH-Client的配置文件（/etc/ssh/ssh_config）修改，打开如下三项：

```
ForwardAgent yes
ForwardX11 yes
ForwardX11Trusted yes

```

同时允许远程连接

```
xhost +
```



<pre name="code" class="plain">Windows Registry Editor Version 5.00  
[HKEY_CLASSES_ROOT\ssh]  
@="ssh"  
"URL Protocol"=""  
[HKEY_CLASSES_ROOT\ssh\DefaultIcon]  
@="C:\\Progran\ Files\\OpenSSH\\ssh..exe"  
[HKEY_CLASSES_ROOT\ssh\shell]  
[HKEY_CLASSES_ROOT\ssh\shell\open]  
[HKEY_CLASSES_ROOT\ssh\shell\open\command]  
@="C:\\Progran\ Files\\OpenSSH\\ssh..exe\"%1\""  


