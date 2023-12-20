#!/bin/bash
#Run following command to determine volume group
vgdisplay
#  VG Name               centos_lacviet-vm18
#  System ID
#  Format                lvm2
#  Metadata Areas        1
#  Metadata Sequence No  4
#  VG Access             read/write
#  VG Status             resizable
#  MAX LV                0
#  Cur LV                3
#  Open LV               2
#  Max PV                0
#  Cur PV                1
#  Act PV                1
#  VG Size               <399,00 GiB
#  PE Size               4,00 MiB
#  Total PE              102143
#  Alloc PE / Size       102142 / 398,99 GiB
#  Free  PE / Size       1 / 4,00 MiB
#  VG UUID               RKCptz-nJOb-PdWe-buUi-skCV-DEQF-bHkELC
#-------------------------------------------------------
# run following command to determine logical volume
#-------------------------------------------------------
lvdisplay
# --- Logical volume ---
 #  LV Path                /dev/centos_lacviet-vm18/root
#--- Logical volume ---
#  LV Path                /dev/centos_lacviet-vm18/home
#--------------------------------------------------------
# Run following command to reduce home
# lvreduce /dev/<volume_group>/<home_volume_name> -L -300G
#-----------------------------------
lvreduce  /dev/centos_lacviet-vm18/home -L -300G
#run following command line to extent root
vgextend /dev/centos_lacviet-vm18 /dev/sda -L +300G
lvextend /dev/centos_lacviet-vm18/root -L +300G