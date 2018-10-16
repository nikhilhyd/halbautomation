#!/usr/bin/python
import config

iplist1		= []
iplist2		= []
maclist1	= []
maclist2	= []
SSHObj		= {}
VmSSHObj	= {}
HostSSHObj	= {}
SCPObj		= {}
retVal		= ""
vmflag		= 0
PARTITIONS	= ""
backupdir	= ""
FileHandler	= {}
SSHOutput	= []

result_cmds		= ""
result_debuglog		= ""
result_vmdetails	= ""
result_scriptlog	= ""
result_mainchannelIp	= ""
result_backchannelIp	= ""
onboardInterfaces	= {}

pf_driverload	= "sh %sdriver_load.sh hsm_load %s"%(config.driversrc, config.bindir)
pf_driverreload = "sh %sdriver_load.sh hsm_reload %s"%(config.driversrc, config.bindir)
vf_driverload   = "sh %sdriver_load.sh hsm_load %s 32"%(config.driversrc, config.bindir)
vf_driverreload = "sh %sdriver_load.sh hsm_reload %s 32"%(config.driversrc, config.bindir)
driverunload 	= "sh %sdriver_load.sh hsm_unload %s"%(config.driversrc, config.bindir)
cologin  	= "%sbin/Cfm2Util singlecmd loginHSM -u CO -s %s -p %s"%(config.install_Dir, config.co_user,config.co_pass)
culogin  	= "%sbin/Cfm2Util singlecmd loginHSM -u CU -s %s -p %s"%(config.install_Dir, config.cu_user,config.cu_pass)
aulogin  	= "%sbin/Cfm2Util singlecmd loginHSM -u AU -s %s -p %s"%(config.install_Dir, config.au_user,config.au_pass)
nologin  	= "%sbin/Cfm2Util -p PARTITION singlecmd "%config.install_Dir
defaultlogin 	= "%sbin/Cfm2Util -p PARTITION singlecmd loginHSM -u CO -s cavium -p default"%config.install_Dir
masterlogin  	= "%sbin/Cfm2MasterUtil singlecmd loginHSM -u CO -s %s -p %s"%(config.install_Dir, config.master_user,config.master_pass)
