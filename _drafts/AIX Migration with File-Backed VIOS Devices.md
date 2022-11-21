**AIX Migration with File-Backed VIOS Devices.**

** **

**Chris Gibson**

** **

In this scenario, I migrated an LPAR running AIX 5.3 TL7 SP3 to AIX 6.1. The migration was performed using ISO images located in the virtual media library on the VIOS. SAP/Oracle were installed on this system. The physical hardware was a JS22 blade running VIOS/IVM.

** **

**- Create an "iso" image of the AIX 6.1 DVD Install Media. This was done via a virtual CD, exported from a VIOS.**

 

\# dd if=/dev/cd0 of=/cg/AIX61DVD1.iso bs=1m

\# dd if=/dev/cd0 of=/cg/AIX61DVD2.iso bs=1m

 

**- Create the media library on the VIOS (IVM).**

** **

![img](http://gibsonnet.net/aix/AIX_Migration_with_File-Backed_VIOS_Devices_files/image002.jpg)

 

Filesystem    512-blocks      Free %Used    Iused %Iused Mounted on

/dev/hd4          524288    461952   12%     2528     5% /

/dev/hd2         8912896   1991904   78%    72364    24% /usr

/dev/hd9var      1572864   1308448   17%      524     1% /var

/dev/hd3         4718592   4598456    3%      227     1% /tmp

/dev/fwdump      1572864   1571960    1%        5     1% /var/adm/ras/platform

/dev/hd1        20971520  20942600    1%       57     1% /home

/proc                  -         -    -         -     -  /proc

/dev/hd10opt     4718592   3290232   31%    11253     3% /opt

**/dev/VMLibrary_LV   10485760  10442544    1%        4     1% /var/vio/VMLibrary**

 

**- Copy the images to the media library on the VIOS.**

 

\# set -o vi

\# cd /var/vio/VMLibrary

 

\# ls -ltr

total 0

drwxr-xr-x    2 root     system          256 Dec 03 11:08 lost+found

 

\# pwd

**/var/vio/VMLibrary**

 

\# df -g .

Filesystem    GB blocks      Free %Used    Iused %Iused Mounted on

/dev/VMLibrary_LV      5.00      4.98    1%        4     1% /var/vio/VMLibrary

 

\# scp 10.3.73.89:/cg/AIX61DVD1.iso .

AIX61DVD1.iso                                                            100% 3679MB  16.4MB/s   03:44

 

\# ls -ltr

total 8949056

drwxr-xr-x    2 root     system          256 Dec 03 11:08 lost+found

**-rw-r--r--    1 root     staff    3857645568 Dec 04 08:53 AIX61_DVD_1.iso**

**-rw-r--r--    1 root     staff     724271104 Dec 04 10:09 AIX61_DVD_2.iso**

 

**- List the contents of the media repository.**

 

$ lsrep

Size(mb) Free(mb) Parent Pool         Parent Size      Parent Free

​    5099      729 rootvg                   139776           110592

 

Name                                    File Size Optical         Access

**AIX61_DVD_1.iso                              3679 vtopt0          rw**

**AIX61_DVD_2.iso                               691 None            rw**

 

**- Map a virtual optical device to the client LPAR.**

 

$ mkvdev -fbo -vadapter vhost0

**vtopt0 Available**

 

$ lsmap -all

SVSA            Physloc                                      Client Partition ID

--------------- -------------------------------------------- ------------------

vhost0          U7998.61X.10071DA-V1-C11                     0x00000003

 

**VTD                   vtopt0**

**Status                Available**

**LUN                   0x8400000000000000**

**Backing device**

**Physloc******

 

VTD                   vtscsi0

Status                Available

LUN                   0x8200000000000000

Backing device        hdisk1

Physloc               U78A5.001.WIH076E-P1-C6-T2-W500507630608059A-L4000402D00000000

 

VTD                   vtscsi1

Status                Available

LUN                   0x8300000000000000

Backing device        hdisk2

Physloc               U78A5.001.WIH076E-P1-C6-T2-W500507630608059A-L4001402D00000000

 

VTD                   vtscsi2

Status                Available

LUN                   0x8100000000000000

Backing device        hdisk3

Physloc               U78A5.001.WIH076E-P1-C6-T2-W500507630608059A-L4000402E00000000

 

**- Load the image into the vtopt0 device.**

 

$ loadopt -vtd vtopt0 -disk AIX61_DVD_1.iso

$ lsmap -all

SVSA            Physloc                                      Client Partition ID

--------------- -------------------------------------------- ------------------

vhost0          U7998.61X.10071DA-V1-C11                     0x00000003

 

VTD                   vtopt0

Status                Available

LUN                   0x8400000000000000

**Backing device        /var/vio/VMLibrary/AIX61_DVD_1.iso**

Physloc

 

VTD                   vtscsi0

Status                Available

LUN                   0x8200000000000000

Backing device        hdisk1

Physloc               U78A5.001.WIH076E-P1-C6-T2-W500507630608059A-L4000402D00000000

 

VTD                   vtscsi1

Status                Available

LUN                   0x8300000000000000

Backing device        hdisk2

Physloc               U78A5.001.WIH076E-P1-C6-T2-W500507630608059A-L4001402D00000000

 

VTD                   vtscsi2

Status                Available

LUN                   0x8100000000000000

Backing device        hdisk3

Physloc               U78A5.001.WIH076E-P1-C6-T2-W500507630608059A-L4000402E00000000

 

**- Start the AIX migration. Boot from “SCSI” CD. Migrate AIX as “normal”.**

 

 

![img](http://gibsonnet.net/aix/AIX_Migration_with_File-Backed_VIOS_Devices_files/image004.jpg)

 

![img](http://gibsonnet.net/aix/AIX_Migration_with_File-Backed_VIOS_Devices_files/image006.jpg)

 

![img](http://gibsonnet.net/aix/AIX_Migration_with_File-Backed_VIOS_Devices_files/image008.jpg)

 

![img](http://gibsonnet.net/aix/AIX_Migration_with_File-Backed_VIOS_Devices_files/image010.jpg)

 

![img](http://gibsonnet.net/aix/AIX_Migration_with_File-Backed_VIOS_Devices_files/image012.jpg)

 

![img](http://gibsonnet.net/aix/AIX_Migration_with_File-Backed_VIOS_Devices_files/image014.jpg)

 

![img](http://gibsonnet.net/aix/AIX_Migration_with_File-Backed_VIOS_Devices_files/image016.jpg)

 

![img](http://gibsonnet.net/aix/AIX_Migration_with_File-Backed_VIOS_Devices_files/image018.jpg)

 

![img](http://gibsonnet.net/aix/AIX_Migration_with_File-Backed_VIOS_Devices_files/image020.jpg)

 

 

**- If prompted for disk 2, load the second image to vtopt0.**

 

$ loadopt -f -vtd vtopt0 -disk AIX61_DVD_2.iso