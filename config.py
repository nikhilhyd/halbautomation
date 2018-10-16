
import os

## CONFIGURABLE PARAMETERS
num_of_vms      = 4         #Pre Host
vmname          = "fedora"  #Vm's name starting with, ex- fedora01, fedora02..
bridgename      = "bridge"
natbridgename   = "virbr"
vm_username     = "root"
vm_password     = "a"
uuid            = "7fbd32b4-6707-4ec9-b520-eb4aaca87225" #Random Unique no.

## HSM Specific Configurations
master_user     = "crypto_officer"
master_pass     = "so12345"
co_user         = "crypto_officer"
co_pass         = "so12345"
cu_user         = "crypto_user"
cu_pass         = "user123"
au_user         = "app_user"
au_pass         = "user1234567890123456789012345678"

## System Path to driver sources on Host and Vm
cwd             = os.getcwd()
logdir          = os.path.join(cwd,"Logs")
tempdir         = os.path.join(cwd,"temp")
dataBase        = os.path.join(cwd,"dataBase")

qemupath        = "/home/qemu-kvm-1.2.0/x86_64-softmmu/"

mainVer         = "2.05"
subVer          = "02-tag-04"
install_Dir     = "/home/nikhil/"

driverName      = "liquidsec_pf_vf_driver"
bindir          = "%s/bin/" %install_Dir
hsm_config      = "%s/data/hsm_config" %install_Dir


## SDK - Package paths
liquidsecDir    = os.path.join(install_Dir,"LiquidSecurity-NFBE-%s-%s" %(mainVer, subVer))
liquidsecPkg    = os.path.join(cwd,"LiquidSecurity-NFBE-%s-%s.tgz" %(mainVer, subVer))
liquidsecPkg2   = os.path.join(install_Dir,"LiquidSecurity-NFBE-%s-%s.tgz" %(mainVer, subVer))

apiPkg          = "CNL35XX-NFBE-API-%s-%s.tgz" %(mainVer, subVer)
serverPkg       = "CNL35XX-NFBE-Cav-Server-%s-%s.tgz" %(mainVer, subVer)
utilsPkg        = "CNL35XX-NFBE-Linux-Driver-Utils-%s-%s.tgz" %(mainVer, subVer)
driverPkg       = "CNL35XX-NFBE-Linux-Driver-KVM-XEN-PF-%s-%s.tgz" %(mainVer, subVer)

apisrc          = os.path.join(install_Dir,"LiquidSecurity-NFBE-%s-%s/liquidsec_api/" %(mainVer, subVer))
utilsrc         = os.path.join(install_Dir,"LiquidSecurity-NFBE-%s-%s/liquidsec_utils/" %(mainVer, subVer))
serversrc       = os.path.join(install_Dir,"LiquidSecurity-NFBE-%s-%s/liquidsec_cav_server/" %(mainVer, subVer))
driversrc       = os.path.join(install_Dir,"LiquidSecurity-NFBE-%s-%s/liquidsec_pf_vf_driver/" %(mainVer, subVer))

## Certificate Names
csr             = os.path.join(cwd,"dataBase/P1.csr")
pokey           = os.path.join(cwd,"dataBase/PO.key")
pocert          = os.path.join(cwd,"dataBase/PO.crt")
signedcert      = os.path.join(cwd,"dataBase/POsigned.crt")

## BackUp/Restore 
backup          = "host01"              #Backup From.
backupdir       = "/tmp/backup"
#restore         = ['host01','host02']   #Restore To.
restore         = ['host01']   #Restore To.

## Host Configurations
hosts={
    #"enableHosts"      : ["host01",],

    "host01":{
        #Machine Serial - 487
        "hostIP"        : "10.89.229.123",
        "bridgeIP0"     : "30.0.0.11",
        "bridgeIP1"     : "40.0.0.11",

        "hostInterface1": "em1",
        "hostInterface2": "em2",
        "ipAddress1"    : "30.0.0.12",
        "ipAddress2"    : "40.0.0.12",
        "macInterface1" : "04:05:06:00:e1:11",
        "macInterface2" : "04:05:06:00:e2:11",

        "vmStore"       : "/halb_home/HALB/images/"
    },
#    "host02":{
#        #Machine Serial - 487
#        "hostIP"        : "10.89.xx.xx",
#        "bridgeIP0"     : "30.0.0.21",
#        "bridgeIP1"     : "40.0.0.21",
#
#        "hostInterface1": "em1",
#        "hostInterface2": "em2",
#        "ipAddress1"    : "30.0.0.22",
#        "ipAddress2"    : "40.0.0.22",
#        "macInterface1" : "04:05:06:00:e3:11",
#        "macInterface2" : "04:05:06:00:e4:11",
#
#        "vmStore"       : "/home/halb_home/HALB/images/"
#    },
}
