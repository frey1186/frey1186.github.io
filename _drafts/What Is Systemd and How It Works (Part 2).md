### What Is Systemd and How It Works (Part 2)

 

**systemd**

 

 

part2

 

http://ktaraghi.blogspot.ca/2013/11/what-is-systemd-and-how-it-works-part-1.html

 

**[Service], [Socket]**

 

[![img](http://3.bp.blogspot.com/-Rp0PxVkUWKc/Ur5K6qJZP6I/AAAAAAAAAcA/Tfm1A13QLyQ/s640/systemd1-part2.png)](http://3.bp.blogspot.com/-Rp0PxVkUWKc/Ur5K6qJZP6I/AAAAAAAAAcA/Tfm1A13QLyQ/s1600/systemd1-part2.png)

 

**[Service]**

 

Type=

 

**simple, forking, oneshot, dbus, notify or idle**

 

**simple**

 

ExecStart=

 

 

**forking**

 

 

ExecStart=

 

 

PIDFile=

 

**dbus**

 

 

 

**notify**

 

PIDFile=

 

Type=

 

 

forking

BusName=

 

Type=

 

 

dbus

ExecStart=

ExecStartPre=, ExecStartPost= 

ExecReload=

ExecStop=

TimeoutStartSec=

Restart=

 

**no, on-success, on-failure, on-abort, or always**

 

**no**

 

 

**on-success**

 

 

**on-failure**

 

 

**on-abort**

 

 

**always**

 

**PermissionsStartOnly=**

RootDirectoryStartOnly=

[![img](http://4.bp.blogspot.com/-u14bO77yN4Q/Ur5PLS3Fx7I/AAAAAAAAAcM/ZgHK8L2CyAo/s640/systemd2-part2.png)](http://4.bp.blogspot.com/-u14bO77yN4Q/Ur5PLS3Fx7I/AAAAAAAAAcM/ZgHK8L2CyAo/s1600/systemd2-part2.png)

[![img](http://2.bp.blogspot.com/-e4vxR_bvw_Y/Ur5PfqsLT0I/AAAAAAAAAcU/nyhofEv6TiY/s640/systemd3-part2.png)](http://2.bp.blogspot.com/-e4vxR_bvw_Y/Ur5PfqsLT0I/AAAAAAAAAcU/nyhofEv6TiY/s1600/systemd3-part2.png)

 

*.socket*

 

 

Socket

 

 

Accept=

 

 

[Socket]

 

ListenStream=, ListenDatagram=, ListenSequentialPacket=

Accept= 

 

MaxConnections=

Service=

 

[![img](http://2.bp.blogspot.com/-zGmKfgOYMag/Ur5SkC-lDGI/AAAAAAAAAcg/1tRZswpN1XQ/s640/systemd3-2-part2.png)](http://2.bp.blogspot.com/-zGmKfgOYMag/Ur5SkC-lDGI/AAAAAAAAAcg/1tRZswpN1XQ/s1600/systemd3-2-part2.png)

[![img](http://1.bp.blogspot.com/-ovpUD5xFgXc/Ur5Sv8qYaAI/AAAAAAAAAco/pJc_VWK3LhU/s640/systemd4-part2.png)](http://1.bp.blogspot.com/-ovpUD5xFgXc/Ur5Sv8qYaAI/AAAAAAAAAco/pJc_VWK3LhU/s1600/systemd4-part2.png)