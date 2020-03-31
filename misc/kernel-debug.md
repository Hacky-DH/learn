# Debug linux kernel on Centos 7

```bash
uname -r
# 3.10.0-1062.9.1
```

## install dependences

```bash
yum install -y crash kernel-debug-devel kernel-debug rpm-build
# install kernel-debuginfo
debuginfo-install glibc
debuginfo_url="http://debuginfo.centos.org/7/x86_64"
rpm -ivh $debuginfo_url/kernel-debuginfo-$(uname -r).el7.x86_64.rpm $debuginfo_url/kernel-debuginfo-common-x86_64-$(uname -r).el7.x86_64.rpm
# install kernel src rpm
rpm -ivh http://vault.centos.org/7.4.1708/updates/Source/SPackages/kernel-$(uname -r).el7.src.rpm
# or other url http://archive.kernel.org/centos-vault/7.4.1708/...
```

## locate the Bug

use vmlinux to debug vmcore

```bash
crash /usr/lib/debug/lib/modules/$(uname -r).el7.x86_64/vmlinux /var/crash/{date}/vmcore
bt
```

find the bug source file

use gdb find the source location, e.g. ceph module

```bash
cp /lib/modules/$(uname -r).el7.x86_64/kernel/fs/ceph/ceph.ko.xz .
xz -d ceph.ko.xz
gdb ceph.ko
list * addr
```

## build a fixed kernel module

```bash
cd ~/rpmbuild/SOURCES
tar Jxf linux-$(uname -r).el7.tar.xz
cd linux-$(uname -r).el7
make mrproper
#edit Makefile
cp /usr/src/kernels/$(uname -r)/Module.symvers .
cp /boot/config-$(uname -r) .config
make oldconfig
make prepare
make modules_prepare
make scripts
# edit source
make -C . M=fs/ceph
modprobe ceph
modinfo ceph
```
