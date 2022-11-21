Win2012R2具备四种运行模式简单的说就是：

- GUI+桌面体验  （Win8.1桌面模式）  
- serverwithGUI   （基础桌面模式）
- Minimal Server   （Server Core+ServerManager+MMC）
- Server Core   （命令行模式）

安装时只有2个选项就是Server Core 和serverwithGUI  ，不过Server2012改进得已经可以在这四种模式之间随意切换而不需要重装整个系统了，我们可以装了系统之后用powershell随意的切换运行模式：

1, 比如我们安装系统时选择Server Core ，安装完以后想切换到Minimal模式，运行以下Powershell命令安装模块：

install-windowsfeature server-gui-mgmt-infra

2，重启后进入Minimal模式了除了Sconfig之外还可以使用图形界面的服务器管理器和MMC，想进一步切换到基础桌面模式，我们运行以下powershell命令来安装模块：

install-windowsfeature server-gui-shell

3，重启后就是serverwithGUI模式了，如果想要Windows8.1桌面体验：

install-windowsfeature desktop-experience

4，如果想从GUI模式切换回Server Core模式，可以运行以下命令：

uninstall-windowsfeature user-interfaces-infra



Win2012R2 Server Core基本操作：

1. 配置ip地址

   ```bash
   查看连接名称：
   netsh interface ip show 
   配置IP地址
   netsh interface ip set address 连接名 static 要修改的IP 子网掩码 网关 1
   ```


2. 配置dns

   ```bash
   netsh interface ip set dns "网络连接" static DNS地址
   ```

3. 修改主机名

   ```bash
   wmic  computersystem where “name=‘WINXXXXXXX’” call rename new_name 
   ```

   或者

   ​

4. 挂载共享

   如共享`\\192.168.30.134\media`，使用用户xny，完事会提示输入密码

   ```bash
   cmd /c net use z: \\192.168.30.134\media /user:xny
   ```

5. 加入AD域

   ```
   wmic computersystem where name="psmserver" call joindomainOrWorkgroup name="f.com" username="f.com\administrator" password="12345678aA" Fjoinoptions=1
   ```

   - Fjoinoptions=1  表示首次加入域，不指定用户名和密码的话就是加入工作组
   - Fjoinoptions=32 表示加新域，无论之前在工作组还是域

​       方法二：

​	

```bash
netdom  
```



启用或关闭防火墙

```bash
Netsh firewall set opmode ENABLE|DISABLE 
```





打开远程桌面：

C:\Windows\System32>cscript SCregEdit.wsf /Ar 0



关闭自动更新：

C:\Windows\System32>cscript SCregEdit.wsf /Au 1

打开自动更新

C:\Windows\System32>cscript SCregEdit.wsf /Au 4



安装.net3.5 

```bash
# 查看可安装的包
Get-WindowsFeature
# 安装.net3.5 ,-source 可以指定安装光盘位置
Install-WindowsFeature NET-Framework-Core –Source D:\Sources\sxs
```





windows 2008 r2 core

- install powershell

  ```bash
  # get
  dism /online /get-feature |more
  # online
  dism /online /enable-feature /featurename:<component>
  ```

  ​

dism /online /get-features /format:table | find /I "已启用"



For Windows 2003 running IIS 6.0, the following sequence of commands are required to reconfigure 64-bit IIS to 32-bit mode:

 

\1. On the Windows 2003 Server, open a DOS prompt 
\2. Type the following commands:
cscript.exe %SYSTEMDRIVE%\Inetpub\AdminScripts\adsutil.vbs set W3SVC/AppPools/Enable32BitAppOnWin64 1

 

%WINDIR%\Microsoft.NET\Framework\v2.0.50727\aspnet_regiis.exe –i –enable

iisreset

For Windows 2008 running IIS 7.0, follow these steps:

 

\1. Open 'Internet Information Services (IIS) Manager' snapin under Administrative tools.
\2. Expand the server and click on 'Application Pools' to display available applicaiton pools in center panel.
\3. Right-click on 'DefaultAppPool' and select 'Advanced Settings'.
\4. Change the value of 'Enable 32-bit Applications' from False to True. Click OK.
\5. In the Actions panel on the right side, click "Set applicaton pool defaults" and do as in step 4 again.
\6. Restart IIS service by highlighting IIS server name in left panel and clicking Restart under Actions panel.



diskpart使用：

2  输入 diskpart

3  list disk  查看都有哪些磁盘

4  select disk 1(选择要格式化的磁盘前面的编号；

DISKPART> SELECT DISK n
DISKPART> ATTRIBUTES DISK CLEAR READONLY
DISKPART> ONLINE DISK
DISKPART> CONVERT MBR



6，DISKPART> create partition primary

DiskPart 成功地创建了指定分区。

7，DISKPART> format fs=ntfs quick lable=data

为此命令指定的参数无效。
有关此命令类型的详细信息，请使用 HELP FORMAT 命令,

8，DISKPART> format fs=ntfs quick label=data

  100 百分比已完成

DiskPart 成功格式化该卷。

9，DISKPART> assign

DiskPart 成功地分配了驱动器号或装载点。

DISKPART> exit

退出 DiskPart...





```bash
1.修改hostname（未加入域）

netdom renamecomputer %computername% /NewName:SQLServer /reboot:0

2.重命名网络适配器

netsh interface set interface name="local area connection" newname="Internal"

3.修改静态ip

netsh interface ipv4 set address name=Internal static 192.168.1.202 255.255.255.0 192.168.1.1

4.修改dns


netsh interface ipv4 set dnsserver name=Internal static 61.139.2.69 primary

5.安装.NET Framework
dism /online /enable-feature /featurename：NetFx2-ServerCore

dism /online /enable-feature /featurename：NetFx3-ServerCore

6.配置Web服务器角色

dism /online /enable-feature /featurename：IIS-WebServerRole

7.为服务器安装IIS-ASPNET角色


dism /online /enable-feature /featurename：IIS-ISAPIFilter

dism /online /enable-feature /featurename：IIS-ISAPIExtensions

dism /online /enable-feature /featurename：IIS-NetFxExtensibility

dism /online /enable-feature /featurename：IIS-ASPNET

8.验证IIS服务是否已经开始运行

sc query w3svc
9.安装IIS管理服务

dism /online /enable-feature /featurename：IIS-ManagementService

10.安装WAS-WindowsActivationService和WAS-ConfigurationAPI


dism /online /enable-feature /featurename：WAS-WindowsActivationService

dism /online /enable-feature /featurename：WAS-ConfigurationAPI

11.更改注册表键值来激活管理服务

Reg Add HKLM\Software\Microsoft\WebManagement\Server /V EnableRemoteManagement /T REG_DWORD /D 1

12.启用IIS管理服务

net start wmsvc

13.验证IIS管理服务是否已经开始运行

sc query wmsvc
```

