---
layout: post
title: Vagrant使用的几个简单例子
date: 2018-03-17 12:00
author: felo
tags: vagrant virtualbox
categories: public
typora-root-url: ..
---

![](/images/vagrant/vagrant.jpeg)

# 1. Vagrant

Vagrant是一个基于Ruby的工具，用于创建和部署虚拟化开发环境。它默认可以使用Oracle的开源VirtualBox虚拟化系统，简单的部署需要的测试或者开发环境。

- 官网：[Vagrant](https://www.vagrantup.com/)
- 下载：[download](https://www.vagrantup.com/downloads.html)
- 文档：[docs](https://www.vagrantup.com/docs/index.html)



# 2. 简单的例子

## 2.1 创建虚拟机

想用`vagrant`创建虚拟机，首先需要有`box`，可以到网上下载现成的`box`也可以自己创建。

### 2.1.1 下载`box`或者创建`box`

可以到`https://app.vagrantup.com/boxes/search`挑选自己喜欢的镜像，其中还有使用的方法等。

```bash
$ mkdir new_dir
$ cd new_dir
$ vagrant init ubuntu/trusty64   # 自动下载，并初始化生成Vagrantfile
$ vagrant up # 启动虚拟机
```
在我的`vrtualbox`里有一个在用的虚拟机`new-lfs`，使用它来创建一个名为`LFS`的`box`。

```bash
localhost:my_lfs$ vagrant package -h
Usage: vagrant package [options] [name|id]

Options:

        --base NAME                  Name of a VM in VirtualBox to package as a base box (VirtualBox Only)
        --output NAME                Name of the file to output
        --include FILE,FILE..        Comma separated additional files to package with the box
        --vagrantfile FILE           Vagrantfile to package with the box
    -h, --help                       Print this help
localhost:my_lfs$ vagrant package --base new-lfs --output lfs.box
==> new-lfs: Attempting graceful shutdown of VM...
    new-lfs: Guest communication could not be established! This is usually because
    new-lfs: SSH is not running, the authentication information was changed,
    new-lfs: or some other networking issue. Vagrant will force halt, if
    new-lfs: capable.
==> new-lfs: Forcing shutdown of VM...
==> new-lfs: Exporting VM...
==> new-lfs: Compressing package to: /my_lfs/lfs.box
localhost:my_lfs$ du -sh lfs.box 
1.1G	lfs.box
```

### 2.1.2 导入`box`

也可以直接下载别人创建好的`box`，然后导入到自己的`vagrant`环境中。

```bash
直接下载一个box文件
$ wget http://box_url/box_name.box
# 将这个box导入到自己的环境中
$ vagrant box add ./box_name.box
or 需要自定义box名称的话，增加--name
$ vagrant box add --name box_name ./box_name.box
查看box状态
$ vagrant box status
```
`vagrant box add` 用法
```bash
localhost:vag_test$ vagrant box add
This command was not invoked properly. The help for this command is
available below.

Usage: vagrant box add [options] <name, url, or path>

Options:

    -c, --clean                      Clean any temporary download files
    -f, --force                      Overwrite an existing box if it exists
        --insecure                   Do not validate SSL certificates
        --cacert FILE                CA certificate for SSL download
        --capath DIR                 CA certificate directory for SSL download
        --cert FILE                  A client SSL cert, if needed
        --location-trusted           Trust 'Location' header from HTTP redirects and use the same credentials for subsequent urls as for the initial one
        --provider PROVIDER          Provider the box should satisfy
        --box-version VERSION        Constrain version of the added box

The box descriptor can be the name of a box on HashiCorp's Vagrant Cloud,
or a URL, or a local .box file, or a local .json file containing
the catalog metadata.

The options below only apply if you're adding a box file directly,
and not using a Vagrant server or a box structured like 'user/box':

        --checksum CHECKSUM          Checksum for the box
        --checksum-type TYPE         Checksum type (md5, sha1, sha256)
        --name BOX                   Name of the box
    -h, --help                       Print this help

```
导入测试：
```bash
localhost:my_lfs$ vagrant box add --name LFS ./lfs.box 
==> box: Box file was not detected as metadata. Adding it directly...
==> box: Adding box 'LFS' (v0) for provider: 
    box: Unpacking necessary files from: file:///Users/myname/GitHub/my_lfs/lfs.box
==> box: Successfully added box 'LFS' (v0) for 'virtualbox'!
localhost:my_lfs$ vagrant box list
LFS              (virtualbox, 0)
```

### 2.1.3 启动虚拟机

```bash
# 使用init来创建Vagrantfile
localhost:my_lfs$ vagrant init
# 修改Vagrantfile，这里就修改一下box的名称，默认为base，修改为LFS
localhost:my_lfs$ cat Vagrantfile |grep vm.box
  config.vm.box = "base"
localhost:my_lfs$ vim Vagrantfile 
localhost:my_lfs$ cat Vagrantfile |grep vm.box
  config.vm.box = "LFS"
# 启动虚拟机
localhost:my_lfs$ vagrant up
Bringing machine 'default' up with 'virtualbox' provider...
==> default: Importing base box 'LFS'...
==> default: Matching MAC address for NAT networking...
==> default: Setting the name of the VM: my_lfs_default_1521257880384_55206
==> default: Fixed port collision for 22 => 2222. Now on port 2200.
==> default: Clearing any previously set network interfaces...
==> default: Preparing network interfaces based on configuration...
    default: Adapter 1: nat
==> default: Forwarding ports...
    default: 22 (guest) => 2200 (host) (adapter 1)
==> default: Booting VM...
==> default: Waiting for machine to boot. This may take a few minutes...
    default: SSH address: 127.0.0.1:2200
    default: SSH username: vagrant
    default: SSH auth method: private key
    some error...
```
虽然能启动虚拟机，但是仍有一些问题，需要`安装增强功能` 。



# 3. Vagrantfile编写



## 3.1 一个`vagrantfile`

```bash
######## 定义一些全局参数 ############
io1_disk1 = './vdisk/io1_disk1.vdi'
io2_disk1 = './vdisk/io2_disk1.vdi'
io3_disk1 = './vdisk/io3_disk1.vdi'
io4_disk1 = './vdisk/io4_disk1.vdi'

######## 开始配置
Vagrant.configure("2") do |config|
  ### 定义一些其他配置
  config.ssh.username = "vagrant"
  config.ssh.password = "vagrant"
  
################################ 开始配置虚拟机 #####################
################################ io1 ###############################
    config.vm.define :"io1" do |io|
      io.vm.box = "centos7-standard-v2"
      io.vm.network :private_network, ip: "192.168.56.191"
      io.vm.hostname = "io1"
      io.ssh.shell = "bash -c 'BASH_ENV=/etc/profile exec bash'"
      io.vm.provider "virtualbox" do |v|
        v.name = "io1"
        #v.gui = true
        unless File.exist?(io1_disk1)
        v.customize ['createhd', '--filename', io1_disk1,'--size', 1 * 20480]
        v.customize ['storageattach', :id,  '--storagectl', 'SATA', '--port', 1, '--device', 0, '--type', 'hdd', '--medium', io1_disk1]
        end
      end
    end
################################ end ################################
# io2...
# io3...
# io4...
end
```



# 4. 对虚拟机的基本操作

```bash
$ vagrant up   # 启动虚拟机
$ vagrant halt  # 关闭虚拟机
$ vagrant destroy   # 删除虚拟机
$ vagrant ssh vm_name # 连接虚拟机
```



# 5. 一个例子

## 5.1 使用centos6.5创建一个vagrant box

- 安装操作系统

```bash
最小安装
```

- 安装virtualbox增强功能

```bash
[root@cio ~]# mount /dev/sr0 /mnt/
mount: block device /dev/sr0 is write-protected, mounting read-only
[root@cio ~]# cd /mnt/
[root@cio mnt]# ls
32Bit        cert          VBoxLinuxAdditions.run          VBoxWindowsAdditions-x86.exe
64Bit        OS2           VBoxSolarisAdditions.pkg
AUTORUN.INF  runasroot.sh  VBoxWindowsAdditions-amd64.exe
autorun.sh   TRANS.TBL     VBoxWindowsAdditions.exe
[root@cio mnt]# ./VBoxLinuxAdditions.run 
# 注意需要安装make，perl，gcc等，使用echo $?安装结果
```

- 创建vagrant用户

```bash
# 创建用户vagrant
[root@cio mnt] useradd -m vagrant
# 修改密码为vagrant
[root@cio mnt] passwd vagrant
```

- 修改sudo配置

```bash
[root@cio mnt] visudo
# visudo，在root ALL行下增加两行
vagrant ALL=(ALL) NOPASSWD:ALL
Defaults:vagrant !requiretty
```

- 创建box 并导入

```bash
# 在宿主机操作
localhost:~$ vagrant package --base c65-base 
==> c65-base: Attempting graceful shutdown of VM...
    c65-base: Guest communication could not be established! This is usually because
    c65-base: SSH is not running, the authentication information was changed,
    c65-base: or some other networking issue. Vagrant will force halt, if
    c65-base: capable.
==> c65-base: Forcing shutdown of VM...
==> c65-base: Exporting VM...
==> c65-base: Compressing package to: /Users/package.box
localhost:~$ vagrant box add --name centos-6.5-base ./package.box 
==> box: Box file was not detected as metadata. Adding it directly...
==> box: Adding box 'centos-6.5-base' (v0) for provider: 
    box: Unpacking necessary files from: file:///Users/package.box
==> box: Successfully added box 'centos-6.5-base' (v0) for 'virtualbox'!
localhost:~$ vagrant box list
centos-6.5-base     (virtualbox, 0)
```

- 创建一个vagrantfile

```bash
localhost:cluster2$ cat Vagrantfile 

cio1_disk1 = './vdisk/cio1_disk1.vdi'

Vagrant.configure("2") do |config|
  config.ssh.username = "vagrant"
  config.ssh.password = "vagrant"
################################ cio1 ###############################
    config.vm.define :"cio1" do |io|
      io.vm.box = "centos-6.5-base"
      io.vm.network :private_network, ip: "192.168.56.181"
      io.vm.hostname = "cio1"
      io.ssh.shell = "bash -c 'BASH_ENV=/etc/profile exec bash'"
      io.vm.provider "virtualbox" do |v|
        v.name = "cio1"
        #v.gui = true
        unless File.exist?(cio1_disk1)
        v.customize ['createhd', '--filename', cio1_disk1,'--size', 1 * 20480]
        v.customize ['storageattach', :id,  '--storagectl', 'SATA', '--port', 1, '--device', 0, '--type', 'hdd', '--medium', cio1_disk1]
        end
      end
    end
################################ end ##############################
end
```

- 启动虚拟机

```bash
localhost:lustre_cluster2$ vagrant up cio1
Bringing machine 'cio1' up with 'virtualbox' provider...
==> cio1: Importing base box 'centos-6.5-base'...
==> cio1: Matching MAC address for NAT networking...
==> cio1: Setting the name of the VM: cio1
==> cio1: Clearing any previously set network interfaces...
==> cio1: Preparing network interfaces based on configuration...
    cio1: Adapter 1: nat
    cio1: Adapter 2: hostonly
==> cio1: Forwarding ports...
    cio1: 22 (guest) => 2222 (host) (adapter 1)
==> cio1: Running 'pre-boot' VM customizations...
==> cio1: Booting VM...
==> cio1: Waiting for machine to boot. This may take a few minutes...
    cio1: SSH address: 127.0.0.1:2222
    cio1: SSH username: vagrant
    cio1: SSH auth method: password
    cio1: 
    cio1: Inserting generated public key within guest...
    cio1: Removing insecure key from the guest if it's present...
    cio1: Key inserted! Disconnecting and reconnecting using new SSH key...
==> cio1: Machine booted and ready!
==> cio1: Checking for guest additions in VM...
==> cio1: Setting hostname...
==> cio1: Configuring and enabling network interfaces...
    cio1: SSH address: 127.0.0.1:2222
    cio1: SSH username: vagrant
    cio1: SSH auth method: password
==> cio1: Mounting shared folders...
    cio1: /vagrant => /Users/GitHub/cluster2
```



# 6.vagrantfile

```bash
Vagrant.configure("2") do |config|


    config.vm.define :"mn01" do |io|
      io.vm.box = "rhel6.9"
      io.vm.network :private_network, ip: "192.168.56.103"
      io.vm.hostname = "mn01"
      io.ssh.shell = "bash -c 'BASH_ENV=/etc/profile exec bash'"
    end

    config.vm.define :"io1" do |io|
      io.vm.box = "rhel6.9-v2"
      io.vm.network :private_network, ip: "192.168.56.101"
      io.vm.hostname = "io1"
      io.ssh.shell = "bash -c 'BASH_ENV=/etc/profile exec bash'"
    end
    config.vm.define :"io2" do |io|
      io.vm.box = "rhel6.9-v2"
      io.vm.network :private_network, ip: "192.168.56.102"
      io.vm.hostname = "io2"
      io.ssh.shell = "bash -c 'BASH_ENV=/etc/profile exec bash'"
    end

# for i in 1..8 do  有报错
  (1..8).each do |i|
    config.vm.define :"cn#{i}" do |io|
      io.vm.box = "rhel6.9"
      io.vm.network :private_network, ip: "192.168.56.11#{i}"
      io.vm.hostname = "cn#{i}"
      io.ssh.shell = "bash -c 'BASH_ENV=/etc/profile exec bash'"
    end
  end

end

```

