#!/bin/bash

IP="192.168.88.21"
ISO_ALI="vsip"
ISO_NAME="VSIP-4.2-AVIC-x86_64.iso"
WORK_DIR="/root"
DHCP_IF="eth1"
# 0.pre-install
## change ip address
cat>/etc/sysconfig/network-scripts/ifcfg-$DHCP_IF<<EOF
DEVICE=$DHCP_IF
TYPE=Ethernet
ONBOOT=yes
BOOTPROTO=static
IPADDR=$IP
PREFIX=24
NAME=$DHCP_IF
EOF
/etc/init.d/network restart
## create local repo
mount -t iso9660 /dev/sr0 /mnt
rm -f /etc/yum.repos.d/*
cat>/etc/yum.repos.d/cdrom.repo <<EOF
[rhel-local]
name=local
baseurl=file:///mnt/
enabled=1
gpgcheck=0
EOF
yum clean all && yum makecache

## disable selinux
sed -i 's/^SELINUX=.*/SELINUX=disabled/' /etc/selinux/config
setenforce 0

## disable firewalld
service iptables stop
chkconfig iptables off

# 1.install httpd service
yum -y install httpd tftp-server dhcp
chkconfig httpd on
chkconfig xinetd on
chkconfig dhcpd on

## for dhcp config file
IP_SUBNET=`echo $IP|cut -d '.' -f 1-3`
cat>/etc/dhcp/dhcpd.conf <<EOF
subnet $IP_SUBNET.0 netmask 255.255.255.0 {
        range $IP_SUBNET.100 $IP_SUBNET.200;
        option subnet-mask 255.255.255.0;
        next-server $IP;
        filename "/$ISO_ALI/pxelinux.0";
       }
#group  {
#        filename "/vsip/pxelinux.0";
#        next-server 192.168.88.21;
#        host test3 { hardware ethernet 52:54:00:DF:58:60;fixed-address 192.168.88.99;}
#       }
EOF

echo "DHCPDARGS=$DH$DHCP_IF" >/etc/sysconfig/dhcpd

/etc/init.d/dhcpd restart

## for tftp-server config

sed -i '/disable/s/yes/no/' /etc/xinetd.d/tftp 
/etc/init.d/xinetd restart


# 2.pxe config
## mount iso
mkdir -p /var/www/html/$ISO_ALI
echo "mount -o loop $WORK_DIR/$ISO_NAME /var/www/html/$ISO_ALI" >> /etc/rc.local
mount -o loop $WORK_DIR/$ISO_NAME /var/www/html/$ISO_ALI

## copy isolinux file
mkdir -p /var/lib/tftpboot/$ISO_ALI
cp -r /var/www/html/$ISO_ALI/isolinux/* /var/lib/tftpboot/$ISO_ALI
mkdir /var/lib/tftpboot/$ISO_ALI/pxelinux.cfg
 #cp /var/lib/tftpboot/$ISO_ALI/isolinux.cfg /var/lib/tftpboot/$ISO_ALI/pxelinux.cfg/default
cp $WORK_DIR/pxelinux.0 /var/lib/tftpboot/vsip/

## change ks file
mkdir -p /var/www/html/ksconfig/
cp /var/lib/tftpboot/$ISO_ALI/all.ks /var/www/html/ksconfig/$ISO_ALI.ks
sed -i 's/cdrom/#cdrom/' /var/www/html/ksconfig/$ISO_ALI.ks
URL="url --url http://$IP/$ISO_ALI"
sed -i "/cdrom/a$URL" /var/www/html/ksconfig/$ISO_ALI.ks


## change grub cfg
cat>/var/lib/tftpboot/$ISO_ALI/pxelinux.cfg/default << EOF
default vesamenu.c32
timeout 600

display boot.msg

# Clear the screen when exiting the menu, instead of leaving the menu displayed.
# For vesamenu, this means the graphical background is still displayed without
# the menu itself for as long as the screen remains in graphics mode.
menu clear
menu background splash.png
menu title VSIP 4.2
menu vshift 8
menu rows 18
menu margin 8
#menu hidden
menu helpmsgrow 15
menu tabmsgrow 13

# Border Area
menu color border * #00000000 #00000000 none

# Selected item
menu color sel 0 #ffffffff #00000000 none

# Title bar
menu color title 0 #ff7ba3d0 #00000000 none

# Press [Tab] message
menu color tabmsg 0 #ff3a6496 #00000000 none

# Unselected menu item
menu color unsel 0 #84b8ffff #00000000 none

# Selected hotkey
menu color hotsel 0 #84b8ffff #00000000 none

# Unselected hotkey
menu color hotkey 0 #ffffffff #00000000 none

# Help text
menu color help 0 #ffffffff #00000000 none

# A scrollbar of some type? Not sure.
menu color scrollbar 0 #ffffffff #ff355594 none

# Timeout msg
menu color timeout 0 #ffffffff #00000000 none
menu color timeout_msg 0 #ffffffff #00000000 none

# Command prompt text
menu color cmdmark 0 #84b8ffff #00000000 none
menu color cmdline 0 #ffffffff #00000000 none

# Do not display the actual menu unless the user presses a key. All that is displayed is a timeout message.

menu tabmsg Press Tab for full configuration options on menu items.

menu separator # insert an empty line

#label node
#  menu label Install VSIP 4.2
#  kernel vmlinuz
#  #append initrd=initrd.img inst.stage2=hd:LABEL=VSIP-4.2-x86_64 ks=hd:LABEL=VSIP-4.2-x86_64:/isolinux/all.ks quiet

label node
  menu label Install VSIP 4.2 -auto
  kernel vmlinuz
  append initrd=initrd.img inst.ks=http://$IP/ksconfig/$ISO_ALI.ks quiet

menu separator # insert an empty line

label local
  menu label Boot from ^Local Drive
  localboot 0xffff

menu end
EOF
