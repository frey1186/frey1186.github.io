

TMP := $(shell mktemp -d)


all: initramfs rootfs


initramfs:
	mkdir -p build/initramfs/bin
	cp rdinit build/initramfs/init
	cp busybox build/initramfs/bin/
	cd build/initramfs && \
		find . -print0 \
		| cpio --null -ov --format=newc \
		| gzip -9 > ../initramfs.cpio.gz

rootfs:
	dd if=/dev/zero of=build/disk.img bs=1M count=64
	mkfs.ext2 build/disk.img
	sudo mount build/disk.img ${TMP}
	mkdir -p rootfs/{bin,sbin,modules}
	cp busybox rootfs/bin/
	cp init rootfs/sbin/init
	cp e1000.ko rootfs/modules/
	sudo cp -a rootfs/* ${TMP}
	sudo umount ${TMP}

run:
#	sudo qemu-system-x86_64 \
		-serial mon:stdio -nographic\
		-drive format=raw,file=build/disk.img  \
		-netdev user,id=net0  -device e1000,netdev=net0 -net tap,ifname=tap0 \
		-kernel vmlinuz \
		-initrd build/initramfs.cpio.gz \
		-machine accel=kvm:tcg \
		-append "console=ttyS0 quiet"
	sudo qemu-system-x86_64 \
		-serial mon:stdio -nographic \
		-drive format=raw,file=build/disk.img  \
		-netdev tap,id=net0,script=start-net.sh  -device e1000,netdev=net0 \
		-kernel vmlinuz \
		-initrd build/initramfs.cpio.gz \
		-machine accel=kvm:tcg \
		-append "console=ttyS0 quiet"

clean:
	rm -rf build rootfs


.PHONY: initramfs rootfs clean run
