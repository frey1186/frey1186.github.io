# [HPDD-discuss] Error when attempting to mount ZFS with Lustre

Jeff Slapp

 

Jeff.Slapp at DataCore.com 

Wed Dec 28 13:11:53 PST 2016

- Previous message (by thread): [[HPDD-discuss\] Error when attempting to mount ZFS with Lustre](https://lists.01.org/pipermail/hpdd-discuss/2016-December/003047.html)
- Next message (by thread): [[HPDD-discuss\] Lustre Client hanging on mount](https://lists.01.org/pipermail/hpdd-discuss/2016-December/003049.html)
- **Messages sorted by:** [[ date \]](https://lists.01.org/pipermail/hpdd-discuss/2016-December/date.html#3048) [[ thread \]](https://lists.01.org/pipermail/hpdd-discuss/2016-December/thread.html#3048) [[ subject \]](https://lists.01.org/pipermail/hpdd-discuss/2016-December/subject.html#3048) [[ author \]](https://lists.01.org/pipermail/hpdd-discuss/2016-December/author.html#3048)

------

```
Thank you very much Marcin. I was able to get it working with your instructions. I am so glad I asked because if not, I would have never of figured out the precise order of operations to make this work. I am not a Linux expert by trade, I know enough to get around within the OS, but either this is a fairly complicated install process or I am severely lacking in my Linux understanding. ;-)

In either case, it appears to be working. Below are the exact steps I followed to get the system to where I needed it to be:

Using CentOS 7.3.1611 with the following roles enabled:
               File and Storage Server
               Guest Agents (if in a VM)
               Large System Performance
               Network File System Client
               Performance Tools
               Compatibility Libraries
               Development Tools

hostname {YOUR SERVER NAME}
yum -y install http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-8.noarch.rpm
yum clean all
vi /etc/yum.repos.d/lustre_server.repo
               [lustre-server]
               name=CentOS-$releasever - Lustre server
               baseurl=https://downloads.hpdd.intel.com/public/lustre/lustre-2.9.0/el7.3.1611/server/
               gpgcheck=0
kernel_version=`yum list --showduplicates kernel | grep lustre-server | awk '{print $2}'`
kernel_firmware_version=`yum list --showduplicates kernel-firmware | grep lustre-server | awk '{print $2}'`
yum -y install --nogpgcheck --setopt=protected_multilib=false kernel-${kernel_version} kernel-firmware-${kernel_firmware_version} kernel-devel-${kernel_version} kernel-headers-${kernel_version}
yum clean all
yum -y install yum-plugin-versionlock
yum versionlock add kernel
yum versionlock add kernel-firmware
yum versionlock add kernel-devel
yum versionlock add kernel-headers
yum clean all
yum-config-manager --disable lustre-server
yum -y install http://download.zfsonlinux.org/epel/zfs-release.el7_3.noarch.rpm
yum clean all
yum-config-manager --disable zfs
yum-config-manager --enable zfs-kmod
reboot
yum -y install wget
yum -y install rpm-build
yum -y install kmod-zfs-devel libzfs2-devel
yum -y install libselinux-devel libtool
rm -f lustre-2.9.0-1.src.rpm&& wget -q https://downloads.hpdd.intel.com/public/lustre/lustre-2.9.0/el7/server/SRPMS/lustre-2.9.0-1.src.rpm
rm -rf ~rpmbuild&& rpmbuild --rebuild --with zfs lustre-2.9.0-1.src.rpm
cd ~/rpmbuild/RPMS/`uname -m`/&& yum -y install kmod-lustre-osd-zfs-2.9.0* kmod-lustre-2.9.0* lustre-osd-zfs-mount-2.9.0* lustre-2.9.0* lustre-iokit*
modprobe zfs
echo "options lnet networks=tcp0(eth0)" > /etc/modprobe.d/lustre.conf
zpool create -f mgs01-pool mirror /dev/sd[b-c]
mkfs.lustre --mdt --mgs --backfstype=zfs --fsname=mgsZFS --index=0 --mgsnode=[MGS IP ADDRESS]@tcp0 mgs01-pool/mgsZFS
mkdir /mnt/mgsZFS
lctl dl
mount -t lustre mgs01-pool/mgsZFS /mnt/mgsZFS
lctl dl

Your instructions along with a very concise Lustre config guide (http://www.pinedalab.org/wp-content/uploads/2015/10/Lustre-Workshop.pdf), and I am up and running.

Hopefully this will help guide anyone else attempting to configure these two technologies together.

Cheers.

From: Jeff Slapp
Sent: Wednesday, December 28, 2016 8:16 AM
To: Marcin Dulak <marcin.dulak at gmail.com>
Cc: hpdd-discuss at lists.01.org
Subject: Re: [HPDD-discuss] Error when attempting to mount ZFS with Lustre

Excellent Marcin. I'll let you know how it goes. Thank you.

On Dec 27, 2016, at 6:14 PM, Marcin Dulak <marcin.dulak at gmail.com<mailto:marcin.dulak at gmail.com>> wrote:


On Tue, Dec 27, 2016 at 6:54 PM, Jeff Slapp <Jeff.Slapp at datacore.com<mailto:Jeff.Slapp at datacore.com>> wrote:
Thanks for the details Marcin. I missed that "-with zfs" switch... however I still receive the missing KSYM errors when attempting to install the kmod-lustre-osd-zfs module.
Note a similar discussion at http://lists.lustre.org/pipermail/lustre-discuss-lustre.org/2016-December/014110.html

Most likely you are on an unclean system - make sure you are installing the newly built RPMS and not the cached ones from the lustre repo.
Try the following Vagrantfile (available at https://gist.github.com/marcindulak/ff2683c78c841f2fa562ee4412dd0a3e):
vagrant up
Marcin

From: Marcin Dulak [mailto:marcin.dulak at gmail.com<mailto:marcin.dulak at gmail.com>]
Sent: Monday, December 26, 2016 5:25 PM
To: Jeff Slapp <Jeff.Slapp at DataCore.com<mailto:Jeff.Slapp at DataCore.com>>
Cc: Mohr Jr, Richard Frank (Rick Mohr) <rmohr at utk.edu<mailto:rmohr at utk.edu>>; hpdd-discuss at lists.01.org<mailto:hpdd-discuss at lists.01.org>

Subject: Re: [HPDD-discuss] Error when attempting to mount ZFS with Lustre

One has to specify --with zfs in order to build zfs support, moreover the BuildRequires are missing in the lustre.spec file, so one has to guess them.
The following seems to build after installing lustre kernel and booting into it. Have not tried if the build is functional.

# yum -y install http://download.zfsonlinux.org/epel/zfs-release.el7_3.noarch.rpm
# yum-config-manager --disable zfs
# yum-config-manager --enable zfs-kmod
# yum -y install kmod-zfs-devel libzfs2-devel
# yum -y install wget
# wget https://downloads.hpdd.intel.com/public/lustre/lustre-2.9.0/el7/server/SRPMS/lustre-2.9.0-1.src.rpm
# yum -y install rpm-build
# yum -y install libselinux-devel libtool
# uname -r
3.10.0-514.el7_lustre.x86_64
# rpm -qa | grep kernel | grep `uname -r`
kernel-devel-3.10.0-514.el7_lustre.x86_64
kernel-headers-3.10.0-514.el7_lustre.x86_64
kernel-3.10.0-514.el7_lustre.x86_64
# rpmbuild --rebuild --with zfs lustre-2.9.0-1.src.rpm
# yum -y install createrepo
# rpmbuild=`readlink -f ~/rpmbuild/RPMS`
# createrepo ${rpmbuild}
# cat <<END > /etc/yum.repos.d/lustre.repo
[lustre]
name=CentOS-$releasever - Lustre locally built RPMS
baseurl=file://${rpmbuild}
enabled=1
gpgcheck=0
END
# yum -y install kmod-lustre-osd-zfs* lustre
Marcin


On Mon, Dec 26, 2016 at 3:31 PM, Jeff Slapp <Jeff.Slapp at datacore.com<mailto:Jeff.Slapp at datacore.com>> wrote:
I just rebuilt the Lustre RPMs from source using rpmbuild. Interestingly, all RPMs were created except the one I need: kmod-lustre-osd-zfs-2.9.0-1.el7.x86_64.rpm.

-----Original Message-----
From: Jeff Slapp
Sent: Sunday, December 25, 2016 3:46 PM
To: 'Mohr Jr, Richard Frank (Rick Mohr)' <rmohr at utk.edu<mailto:rmohr at utk.edu>>
Cc: 'hpdd-discuss at lists.01.org<mailto:hpdd-discuss at lists.01.org>' <hpdd-discuss at lists.01.org<mailto:hpdd-discuss at lists.01.org>>
Subject: RE: [HPDD-discuss] Error when attempting to mount ZFS with Lustre

I suppose I would need someone from Intel to tell me if ZFS 0.6.5.8-1 is compatible with Lustre 2.9.0-1.

I was able to build ZFS from source (SPL and ZFS modules) under the Lustre kernel and everything went perfect right up to this step:

rpm -ivh kmod-lustre-osd-zfs-2.9.0-1.el7.x86_64.rpm. Same KSYM errors.

Please advise whether I should use a previous version of Lustre (i.e. 2.8).


-----Original Message-----
From: Jeff Slapp
Sent: Friday, December 23, 2016 12:18 PM
To: 'Mohr Jr, Richard Frank (Rick Mohr)' <rmohr at utk.edu<mailto:rmohr at utk.edu>>
Cc: hpdd-discuss at lists.01.org<mailto:hpdd-discuss at lists.01.org>
Subject: RE: [HPDD-discuss] Error when attempting to mount ZFS with Lustre

The pre-built Lustre RPMs were obtained here: https://downloads.hpdd.intel.com/public/lustre/latest-release/el7.3.1611/server/RPMS/x86_64/

I will investigate your suggestion. Thank you.

-----Original Message-----
From: Mohr Jr, Richard Frank (Rick Mohr) [mailto:rmohr at utk.edu<mailto:rmohr at utk.edu>]
Sent: Friday, December 23, 2016 11:30 AM
To: Jeff Slapp <Jeff.Slapp at DataCore.com<mailto:Jeff.Slapp at DataCore.com>>
Cc: hpdd-discuss at lists.01.org<mailto:hpdd-discuss at lists.01.org>
Subject: Re: [HPDD-discuss] Error when attempting to mount ZFS with Lustre


> On Dec 23, 2016, at 9:28 AM, Jeff Slapp <Jeff.Slapp at DataCore.com<mailto:Jeff.Slapp at DataCore.com>> wrote:
>
> ERROR 2 (in /var/log/messages):
>
> Dec 23 09:18:58 mds01 kernel: LustreError: 158-c: Can't load module 'osd-zfs'
>
> Dec 23 09:18:58 mds01 kernel: LustreError:
> 56472:0:(genops.c:314:class_newdev()) OBD: unknown type: osd-zfs
>
<snip>
>
> MODULES INSTALLED:
>
<snip>
> kmod-lustre-osd-zfs-2.9.0-1.el7.x86_64
>
> zfs-release-1-3.el7.centos.noarch
>
> zfs-0.6.5.8-1.el7.centos.x86_64
>
> libzfs2-0.6.5.8-1.el7.centos.x86_64
>
> libzfs2-devel-0.6.5.8-1.el7.centos.x86_64
>
> zfs-dkms-0.6.5.8-1.el7.centos.noarch
>
>
> NOTE: In  order to get the 'kmod-lustre-osd-zfs-2.9.0-1.el7.x86_64' module installed, I had to use 'rpm -ihv kmod-lustre-osd-zfs-2.9.0-1.el7.x86_64 -nodeps'. Without -nodeps, Idependency warnings about missing nearly two pages references to KSYM.

Are you using the pre-built Lustre RPMs from OpenSFS?  If so, see if the version of ZFS you have installed matches what the RPMs were built against.

--
Rick Mohr
Senior HPC System Administrator
National Institute for Computational Sciences http://www.nics.tennessee.edu

_______________________________________________
HPDD-discuss mailing list
HPDD-discuss at lists.01.org<mailto:HPDD-discuss at lists.01.org>
https://lists.01.org/mailman/listinfo/hpdd-discuss


-------------- next part --------------
An HTML attachment was scrubbed...
URL: <http://lists.01.org/pipermail/hpdd-discuss/attachments/20161228/2ab79919/attachment-0001.html>
```

------

- Previous message (by thread): [[HPDD-discuss\] Error when attempting to mount ZFS with Lustre](https://lists.01.org/pipermail/hpdd-discuss/2016-December/003047.html)
- Next message (by thread): [[HPDD-discuss\] Lustre Client hanging on mount](https://lists.01.org/pipermail/hpdd-discuss/2016-December/003049.html)
- **Messages sorted by:** [[ date \]](https://lists.01.org/pipermail/hpdd-discuss/2016-December/date.html#3048) [[ thread \]](https://lists.01.org/pipermail/hpdd-discuss/2016-December/thread.html#3048) [[ subject \]](https://lists.01.org/pipermail/hpdd-discuss/2016-December/subject.html#3048) [[ author \]](https://lists.01.org/pipermail/hpdd-discuss/2016-December/author.html#3048)

------

More information about the HPDD-discuss mailing list