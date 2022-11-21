install windows7 over PXE



# 1.make winPE with AIK in Linux

### Using standard tools

- From the AIK installation file `KB3AIK_EN.iso`, provided in the form of a UDF disk image, use `7z` (from [p7zip](http://sourceforge.net/projects/p7zip)) to extract the files `wAIKX86.msi` and `WinPE.cab`
- use `7z` or `cabextract` to unpack these files into `/tmp/wAIKX86.msi/` and `/tmp/WinPE.cab/` respectively
- create a bootable WinPE *.iso image `/tmp/winpe3_x86.iso`

```
cd /tmp
mkdir -p winpe3_x86/boot
mkdir -p winpe3_x86/sources
cp wAIKX86.msi/F_WINPE_X86_etfsboot.com winpe3_x86/etfsboot.com
cp wAIKX86.msi/F1_BOOTMGR winpe3_x86/bootmgr
cp wAIKX86.msi/F_WINPE_X86_bcd winpe3_x86/boot/bcd
cp wAIKX86.msi/F_WINPE_X86_boot.sdi winpe3_x86/boot/boot.sdi
cp WinPE.cab/F1_WINPE.WIM winpe3_x86/sources/boot.wim
genisoimage -sysid "" -A "" -V "Microsoft Windows PE (x86)" -d -N -b etfsboot.com -no-emul-boot \
 -c boot.cat -hide etfsboot.com -hide boot.cat -o winpe3_x86.iso winpe3_x86
```



### Using wimlib

- Download, build and install wimlib

   

  https://wimlib.net/

   

  Current release: wimlib-1.9.0 (released January 31, 2016)

  - On Debian-based systems:

```
   sudo apt-get install debhelper autotools-dev pkg-config libfuse-dev libxml2-dev libssl-dev ntfs-3g-dev attr-dev attr
   wget https://wimlib.net/downloads/wimlib-1.9.0.tar.gz
   tar -xzf wimlib-1.9.0.tar.gz
   cd wimlib-1.9.0
   dpkg-buildpackage -uc -us -rfakeroot
   sudo dpkg -i ../wimlib_1.9.0-1_amd64.deb ../wimtools_1.9.0-1_amd64.deb
```

- Mount the AIK image

```
   mkdir waik
   sudo mount -o loop,ro KB3AIK_EN.iso waik
```

- Create the WinPE image (with drivers extracted by wine)

```
   mkwinpeimg --iso --waik-dir=$PWD/waik winpe3_x86.iso --overlay=$HOME/.wine/drive_c/DRIVERS
```

- Unmount the AIK image

```
   sudo umount waik
```

