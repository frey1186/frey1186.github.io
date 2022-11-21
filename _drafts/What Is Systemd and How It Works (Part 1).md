### What Is Systemd and How It Works (Part 1)

**systemd**

 is a system and service manager and recent Fedora is using systemd (Fedora 18 and above, I think). System startup is managed by systemd now and all original System V (init system for starting individual services) and Upstart service has been deprecated and phased out.

The old System V was using different scripts(daemons) sequentially in different runlevels. For example, System V starts ssh service in runlevel 5 after firewall and network service because ssh service depends on network service. This sequentially running of services make a slow startup and that’s why System V has been phased out. 

The new Systemd starts daemons at same time and this parallel running of daemons means a very fast startup. How come? Well, systemd uses sockets for all services. It sets up sockets for daemons and coordinates between them as they start up. So, when a daemon requires support from another daemon, systemd coordinate the data from their sockets . For example, daemon A starts and it needs a support from daemon B, however, daemon B has not started yet . Therefore, systemd writes daemon A’s request to daemon B’s socket(buffering) and it continues. So daemon A doesn’t need to wait for daemon B. As soon as daemon B starts, it will read its socket. This means parallel processing and system boots very fast. The socket activation was designed by Apple’s OS X system.

**systemd**

 is compatible with System V and actually systemd uses System V’s configurations and scripts as additional information files. If there is no any configuration file for systemd already, systemd will use System V scripts and configuration files to generate a corresponding configuration files. However, systemd configuration files always take precedence. For example, systemd uses /etc/fstab to generate corresponding systemd configuration file system or looks at /etc/rc.d directory to finds start and stop files and determines dependencies. 

Configuration for systemd tasks are defined in unit files. Therefore, systemd defines different units files for different tasks and each unit file has its own configuration file. Unit files are divided to the following categories:

service 

target 

socket 

device 

mount 

automount 

path 

snapshot 

swap 

timer

So, those unit files that are related to “service” have

** “.service”**

 extension or unit files related to “mount” have 

**“.mount” **

extension and so forth. An good example can be boot.mount or smb.service.

Now, inside each unit file, there are directives and configuration options. Some of these directives and options are common to all units and you can find it in systemd.unit man page. 

**man systemd.unit**

 

According to man page, this man page(systemd.unit) lists the common configuration options of all the unit types. These options need to be configured in the

 [Unit] 

or 

[Install]

 sections of the unit files. 

In addition, you can find a list of configuration options shared by services, sockets, mount and swap unit types in systemd.exec man page:

**man systemd.exec**

The execution specific configuration options are configured in the 

[Service], [Socket], [Mount], 

or

 [Swap]

sections in the unit files, depending on the unit type. 

### Unit file syntax

Well, a very comprehensive explanation exist in man page (man systemd.unit) for your reference. Here is a short, still very useful, explanation of [Unit] section in each unit files. Remember this part is common to all of them. Some common options under [Unit] section are:

**[Unit]**

**Description=** A descriptive information along with the unit name 

**Documentation=** A list of man pages referencing for this unit or its configuration 

**Requires=** According to man page, this configures requirement dependencies on other units. If this unit gets activated, the units listed here will be activated as well. If one of the other units gets deactivated or its activation fails, this unit will be deactivated. Note that requirement dependencies do not influence the order in which services are started or stopped. This has to be configured independently with the After= or Before= options. 

**Wants=** A weaker version of Requires=. A unit listed in this option will be started if the configuring unit is. However, if the listed unit fails to start up or cannot be added to the transaction this has no impact on the validity of the transaction as a whole. 

**Conflicts=** Configures negative requirement dependencies. If a unit has a Conflicts= setting on another unit, starting the former will stop the latter and vice versa. ** **

**Before= **Configures ordering dependencies between units. If a unit foo.service contains a setting “Before=bar.service” and both units are being started, bar.service's start-up is delayed until foo.service is started up. ** **

**After=** It is the inverse of “Before=” ** **

**AllowIsolate=** If true this unit may be used with the “systemctl isolate” command. Otherwise this will be refused. ** **

**ConditionPathExists=** a file existence condition is checked before a unit is started. If the specified absolute path name does not exist the condition will fail ** **

**ConditionPathIsDirectory=** is similar to ConditionPathExists= but verifies whether a certain path exists and is a directory 

Some common options under [Install] section are:

** **

**[Install] **** **

**Alias=**Additional names this unit shall be installed under. The names listed here must have the same suffix (i.e. type) as the unit file name. ** **

**Also=** Additional units to install/deinstall when this unit is installed/deinstalled ** **

**WantedBy=, RequiredBy=**  This option creates a symbolic link to the unit in a “.wants” subdirectory for the WantedBy unit. For example, assume the you enabled the rsyslog service. “WantedBy=multi-user.target” directive in syslog.service unit file creates a symbolic link in /etc/systemd/system/**multi-user.target.wants**/rsyslog.service to the actual rsyslog.service. Then, this unit file (rsyslog.service) is wanted/needed by multi-user.target unit file. In other words, all units that multi-user.target wants it would be in multi-user.target.wants directory. As you can see here, all WantsBy symbolic links are setup in the /etc/systemd/system directory. These symbolic links can be changed as you enable/disable a service. if you disable a service, it will remove the link.RequiredBy is a much stronger dependency. 

[![img](http://4.bp.blogspot.com/-p4RnpSkiI0Y/Uplll5t8HvI/AAAAAAAAAbY/8KvmPCt-_3o/s640/systemd1.png)](http://4.bp.blogspot.com/-p4RnpSkiI0Y/Uplll5t8HvI/AAAAAAAAAbY/8KvmPCt-_3o/s1600/systemd1.png)

​                                                                            Figure 1

Also, as I mentioned above, there are some configuration options shared by these four units as well: services, sockets, mount and swap (man systemd.exec). The execution specific configuration options are configured in the [Service], [Socket], [Mount], or [Swap] sections, depending on the unit type. Let’s take a look:

**WorkingDirectory=** Takes an absolute directory path. Sets the working directory for executed processes. ** **

**RootDirectory=** Takes an absolute directory path. Sets the root directory for executed processes, with the chroot system call. ** **

**User=, Group= **Sets the Unix user or group that the processes are executed as, respectively. ** **

**Nice=** Sets the default nice level (scheduling priority) for executed processes. **CPUSchedulingPriority=** Sets the CPU scheduling priority for executed processes. ** **

**UMask=** Controls the file mode creation mask. Default is 022. ** **

**Environment= **Sets environment variables for executed processes. Takes a space-separated list of variable assignments. ** **

**EnvironmentFile=** Similar to Environment= but reads the environment variables from a text file. The text file should contain new-line separated variable assignments. Empty lines and lines starting with ; or # will be ignored, which may be used for commenting. The argument passed should be an absolute file name or wildcard expression, optionally prefixed with **"-"**, which indicates that if the file does not exist it won't be read and no error or warning message is logged. ** **

**StandardOutput=** Set output to a log, console, or null. ** **

**SyslogFacility=** Sets the syslog facility to use when logging to syslog. One of kern, user, mail, daemon, auth, syslog, lpr, news, uucp, cron, authpriv, ftp, local0, local1, local2, local3, local4, local5, local6 or local7. ** **

**SyslogLevel= **Default syslog level to use when logging to syslog or the kernel log buffer. One of emerg, alert, crit, err, warning, notice, info, debug. ** **

**MemoryLimit=** Limit the overall memory usage of the executed processes to a certain size. **DeviceAllow=, DeviceDeny=** Control access to specific device nodes by the executed processes. 

Now, let’s take a look at some examples.

[![img](http://1.bp.blogspot.com/-uM6HjRexgr0/Uplm5BTvDxI/AAAAAAAAAbg/EAxjyJngAsw/s640/systemd2.png)](http://1.bp.blogspot.com/-uM6HjRexgr0/Uplm5BTvDxI/AAAAAAAAAbg/EAxjyJngAsw/s1600/systemd2.png)

​                                                                           Figure 2

Don’t worry about [service] section on this example now. I will explain specific configuration options in the [Service], [Socket], [Mount], and [Swap] sections in part 2. 
Another example:

[![img](http://1.bp.blogspot.com/-GUuco1YCNYU/UplnLvx6XQI/AAAAAAAAAbo/KAkMzESerHo/s640/systemd3.png)](http://1.bp.blogspot.com/-GUuco1YCNYU/UplnLvx6XQI/AAAAAAAAAbo/KAkMzESerHo/s1600/systemd3.png)

​                                                                              Figure 3

and

[![img](http://1.bp.blogspot.com/-WoZH_ysaByY/UplnbctQH0I/AAAAAAAAAbw/cAxM8-G2nkQ/s640/systemd4.png)](http://1.bp.blogspot.com/-WoZH_ysaByY/UplnbctQH0I/AAAAAAAAAbw/cAxM8-G2nkQ/s1600/systemd4.png)

​                                                                             Figure 4

and pretty much that’s it. I will explain the rest options and commands in part 2. Don’t forget to follow it. Hope you enjoyed. 



https://fedoraproject.org/wiki/Systemd/zh-cn