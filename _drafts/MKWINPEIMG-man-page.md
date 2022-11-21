# MKWINPEIMG 帮助

Section: User Commands (1)

Updated: May 2012

Index

 

## NAME

mkwinpeimg - Make a customized bootable image of Windows PE

 

## SYNOPSIS

mkwinpeimg [ OPTIONS ]  IMAGE

[ ]()

## DESCRIPTION

**mkwinpeimg** is able to make a bootable image of Windows PE by taking filesfrom a mounted Windows DVD (Windows 7 or Windows 8) or the mounted ISO image forthe Windows Automated Installation Kit (WAIK). The **--windows-dir** and**--waik-dir** options are used to specify the locations of these mountedISOs. You only need one or the other. The files that **mkwinpeimg** willretrieve are *boot.wim*, *bootmgr*, *boot.sdi*, and *bcd*. Ifmaking an ISO image, the file *etfsboot.com* is also retrieved. Microsoftowns the rights to these files and they are not distributed with WIMLIB.

**mkwinpeimg** can currently make two types of bootable images. The defaultis to make a bootable disk image. The image is not partitioned and is formattedinto a FAT filesystem. **syslinux**(1) is required to make this type ofimage, as it is used to chainload *bootmgr*. Also, **mtools**(1) isrequired so that the FAT filesystem can be created without root privileges.

The other type of bootable image that **mkwinpeimg** can make is a bootableISO image. To make this type of image, give the **--iso** option.**mkisofs**(1) is required to make this type of image.

If you make a disk image, you could put it on a USB drive, and if you make anISO image, you could put it on a CD. In addition, both types of images can beloaded by the SYSLINUX or PXELINUX bootloaders using the MEMDISK module.

Windows PE itself is contained in the *boot.wim* file. **mkwinpeimg** canmodify this file before embedding it in a bootable image. The most usefulmodification is to specify an executable or batch file for Windows PE to executeas soon as it starts up. Use the **--start-script** *FILE* option tospecify such a file. You may also add arbitrary files to *boot.wim* byputting them in a directory, then specifying the **--overlay** *DIR*option.

**mkwinpeimg** can also make only a modified *boot.wim*, rather than abootable ISO or disk image, if the **--only-wim** option is given.

The Windows PE WIMs provided in Windows 7, Windows 8, and the WAIK are not thesame, but are all similar. The best one to use is likely the one from the WAIK,as that one is the smallest.

## OPTIONS

- **-i**, **--iso**

  Make an ISO image instead of a disk image.

- **-o**, **--only-wim**

  Make neither a disk image nor an ISO image; instead, only make a modified*boot.wim* file.

- **-W**, **--windows-dir**=*DIR*

  Use DIR as the location of the mounted Windows 7 or Windows 8 DVD. Default is/mnt/windows, then /mnt/windows7, then /mnt/windows8.

- **-A**, **--waik-dir**=*DIR*

  Get the boot files and boot.wim from the ISO of the Windows AutomatedInstallation Kit mounted on DIR instead of from the Windows 7 or Windows 8 DVD.

- **-s**, **--start-script**=*FILE*

  Add FILE to the root directory of Windows PE image and adjust\Windows\System32\winpeshl.ini to execute FILE when Windows PE starts up.

- **-w**, **--wim**=*WIM*

  Use WIM as the "boot.wim" file. Defaults to "sources/boot.wim" in the Windows DVDdirectory, or F1_WINPE.WIM from the WAIK if **--waik-dir** is specified.

- **-O**, **--overlay**=*DIR*

  Adds all the files in DIR to the Windows PE image.

- **-t**, **--tmp-dir**=*DIR*

  Use DIR for temporary files. Defaults to a directory made using \"mktemp**-d**\".

- **-h**, **--help**

  Display help.

- **-v**, **--version**

  Show version information.



## EXAMPLES

- mkwinpeimg --windows-dir=/media/windows winpe.img

Create a bootable disk image of Windows PE from the Windows DVD mounted on/media/windows.

- mkwinpeimg --iso --waik-dir=/media/waik --overlay=winpe_overlay winpe.iso

Create a bootable ISO of Windows PE from the WAIK mounted on /media/waik, andadd all the files in "winpe_overlay" to Windows PE's filesystem.

- mkwinpeimg --start-script=install.cmd --windows-dir=/media/windows /var/tftpboot/winpe.img

Create a bootable image of Windows PE from the Windows DVD mounted on/media/windows, add and make it execute "install.cmd" when it starts up.

In this example the image is created in the root directory of the TFTP server fornetwork booting.

[ ]()

## NOTES

Microsoft's licenses may limit the things that Windows PE can be used for, andthey may limit your rights to redistribute customized versions of Windows PE.

[ ]()

## REPORTING BUGS

Report bugs to ebiggers3AATTgmail.com.

[ ]()

## SEE ALSO

[imagex](http://rpm.pbone.net/index.php3/stat/45/idpl/18065763/numer/1/nazwa/imagex)(1)