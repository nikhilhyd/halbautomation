#!/usr/bin/bash
k=0
j=11
for i in {1..4}
do

name="fedora$i"".qcow2"
mac="04:05:06:00:e1:""$j"
tap="tap$i"
dev="02:10.$k"
echo $name, $mac, $tap, $dev

/home/qemu-kvm-1.2.0/x86_64-softmmu//qemu-system-x86_64 -hda /halb_home/HALB/images//$name -smp 2 -m 2048 -net nic,model=virtio,macaddr=$mac,vlan=1 -net tap,vlan=1,ifname=$tap,script=/etc/qemu-ifup-br0,downscript=/etc/qemu-ifdown-br0 -boot c -device pci-assign,host=$dev &

sleep 15
j=`expr $j + 1`
k=`expr $k + 2`
done

k=0
for i in {5..8}
do

name="fedora$i"".qcow2"
mac="04:05:06:00:e1:""$j"
tap="tap$i"
dev="02:11.$k"
echo $name, $mac, $tap, $dev

/home/qemu-kvm-1.2.0/x86_64-softmmu//qemu-system-x86_64 -hda /halb_home/HALB/images//$name -smp 2 -m 2048 -net nic,model=virtio,macaddr=$mac,vlan=1 -net tap,vlan=1,ifname=$tap,script=/etc/qemu-ifup-br0,downscript=/etc/qemu-ifdown-br0 -boot c -device pci-assign,host=$dev &

sleep 15
j=`expr $j + 1`
k=`expr $k + 2`
done

k=0
for i in {9..12}
do

name="fedora$i"".qcow2"
mac="04:05:06:00:e1:""$j"
tap="tap$i"
dev="02:12.$k"
echo $name, $mac, $tap, $dev

/home/qemu-kvm-1.2.0/x86_64-softmmu//qemu-system-x86_64 -hda /halb_home/HALB/images//$name -smp 2 -m 2048 -net nic,model=virtio,macaddr=$mac,vlan=1 -net tap,vlan=1,ifname=$tap,script=/etc/qemu-ifup-br0,downscript=/etc/qemu-ifdown-br0 -boot c -device pci-assign,host=$dev &

sleep 15
j=`expr $j + 1`
k=`expr $k + 2`
done

k=0
for i in {13..16}
do

name="fedora$i"".qcow2"
mac="04:05:06:00:e1:""$j"
tap="tap$i"
dev="02:13.$k"
echo $name, $mac, $tap, $dev

/home/qemu-kvm-1.2.0/x86_64-softmmu//qemu-system-x86_64 -hda /halb_home/HALB/images//$name -smp 2 -m 2048 -net nic,model=virtio,macaddr=$mac,vlan=1 -net tap,vlan=1,ifname=$tap,script=/etc/qemu-ifup-br0,downscript=/etc/qemu-ifdown-br0 -boot c -device pci-assign,host=$dev &

sleep 15
j=`expr $j + 1`
k=`expr $k + 2`
done

k=0
for i in {17..20}
do

name="fedora$i"".qcow2"
mac="04:05:06:00:e1:""$j"
tap="tap$i"
dev="02:14.$k"
echo $name, $mac, $tap, $dev

/home/qemu-kvm-1.2.0/x86_64-softmmu//qemu-system-x86_64 -hda /halb_home/HALB/images//$name -smp 2 -m 2048 -net nic,model=virtio,macaddr=$mac,vlan=1 -net tap,vlan=1,ifname=$tap,script=/etc/qemu-ifup-br0,downscript=/etc/qemu-ifdown-br0 -boot c -device pci-assign,host=$dev &

sleep 15
j=`expr $j + 1`
k=`expr $k + 2`
done

k=0
for i in {21..24}
do

name="fedora$i"".qcow2"
mac="04:05:06:00:e1:""$j"
tap="tap$i"
dev="02:15.$k"
echo $name, $mac, $tap, $dev

/home/qemu-kvm-1.2.0/x86_64-softmmu//qemu-system-x86_64 -hda /halb_home/HALB/images//$name -smp 2 -m 2048 -net nic,model=virtio,macaddr=$mac,vlan=1 -net tap,vlan=1,ifname=$tap,script=/etc/qemu-ifup-br0,downscript=/etc/qemu-ifdown-br0 -boot c -device pci-assign,host=$dev &

sleep 15
j=`expr $j + 1`
k=`expr $k + 2`
done

k=0
for i in {25..28}
do

name="fedora$i"".qcow2"
mac="04:05:06:00:e1:""$j"
tap="tap$i"
dev="02:16.$k"
echo $name, $mac, $tap, $dev

/home/qemu-kvm-1.2.0/x86_64-softmmu//qemu-system-x86_64 -hda /halb_home/HALB/images//$name -smp 2 -m 2048 -net nic,model=virtio,macaddr=$mac,vlan=1 -net tap,vlan=1,ifname=$tap,script=/etc/qemu-ifup-br0,downscript=/etc/qemu-ifdown-br0 -boot c -device pci-assign,host=$dev &

sleep 15
j=`expr $j + 1`
k=`expr $k + 2`
done

k=0
for i in {29..31}
do

name="fedora$i"".qcow2"
mac="04:05:06:00:e1:""$j"
tap="tap$i"
dev="02:17.$k"
echo $name, $mac, $tap, $dev

/home/qemu-kvm-1.2.0/x86_64-softmmu//qemu-system-x86_64 -hda /halb_home/HALB/images//$name -smp 2 -m 2048 -net nic,model=virtio,macaddr=$mac,vlan=1 -net tap,vlan=1,ifname=$tap,script=/etc/qemu-ifup-br0,downscript=/etc/qemu-ifdown-br0 -boot c -device pci-assign,host=$dev &

sleep 15
j=`expr $j + 1`
k=`expr $k + 2`
done

