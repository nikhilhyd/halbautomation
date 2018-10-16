#!/usr/bin/python
import re
import os
import ssh
import sys
import time
import config
import commands
import vmfunctions
import globalvariables

## Get List of Interfaces present in the Host Machine
def getInterface(host):
    write_file(globalvariables.result_scriptlog,"Retrieving List of OnBaord Interfaces")
    config.hosts[host]["interfaces"]=[config.hosts[host]["hostInterface1"],config.hosts[host]["hostInterface2"]]
#    exec_remote_cmd("ifconfig -a | grep %s | grep UP"%config.hostInterface,ipaddr)

## Configure Virtual Bridge based on the Host Machine Interfaces
def configurebridge(host):
    ipaddr=config.hosts[host]["hostIP"]
    globalvariables.maclist1=[]
    globalvariables.iplist1=[]
    globalvariables.maclist2=[]
    globalvariables.iplist2=[]
    #### Preparing Bridge Configuration File ####
    for x in range(len(config.hosts[host]["interfaces"])):
        iface=config.hosts[host]["interfaces"][x]
        temp = int(config.uuid[len(config.uuid)-5:len(config.uuid)])+x
        uuid = config.uuid[:-5] + str(temp)
        bridgeip = config.hosts[host]["bridgeIP1"] if x else config.hosts[host]["bridgeIP0"]
        ip = config.hosts[host]["ipAddress2"] if x else config.hosts[host]["ipAddress1"]
        xmlfile="%s%s%s.xml"%(config.cwd,config.bridgename,x)
        samplexml="%s/dataBase/sample.xml"%(config.cwd)
        exec_remote_cmd("cp -rv %s %s"%(samplexml,xmlfile),ipaddr)
        exec_remote_cmd("sed -i \"s/CH1/%s%s/g\" %s"%(config.bridgename,x,xmlfile),ipaddr)
        exec_remote_cmd("sed -i \"s/CH2/%s/g\" %s"%(uuid,xmlfile),ipaddr)
        exec_remote_cmd("sed -i \"s/CH3/%s/g\" %s"%(iface,xmlfile),ipaddr)
        exec_remote_cmd("sed -i \"s/CH4/%s/g\" %s"%(iface,xmlfile),ipaddr)
        exec_remote_cmd("sed -i \"s/CH5/%s%s/g\" %s"%(config.natbridgename,x,xmlfile),ipaddr)
        exec_remote_cmd("sed -i \"s/CH6/%s/g\" %s"%(bridgeip,xmlfile),ipaddr)
        exec_remote_cmd("sed -i \"s/CH7/%s/g\" %s"%(ip,xmlfile),ipaddr)
        summ = int(ip.split(".")[3]) + int(config.num_of_vms-1)
        last_position = ip.rfind(ip.split(".")[3])
        new  = ip[:last_position] + str(summ)
        exec_remote_cmd("sed -i \"s/CH8/%s/g\" %s"%(new,xmlfile),ipaddr)

        #### Configuring MAC based Static IP Addresses to all VMs ####
        temp1=int(config.hosts[host]["macInterface1"].split(":")[5])
        temp2=int(config.hosts[host]["ipAddress1"].split(".")[3])
        #for z in range(1,config.num_of_vms+1):
        for z in range(config.num_of_vms):
            if x == 0:
                mac=config.hosts[host]["macInterface1"].replace(str(temp1),'%s',1)%(temp1+z)
                last_position = config.hosts[host]["ipAddress1"].rfind(ip.split(".")[3])
                ipaddress = ip[:last_position] + str(temp2+z)
                globalvariables.maclist1.append(mac)
                globalvariables.iplist1.append(ipaddress)
            else:
                mac=config.hosts[host]["macInterface2"].replace(str(temp1),'%s',1)%(temp1+z)
                last_position = config.hosts[host]["ipAddress2"].rfind(ip.split(".")[3])
                ipaddress = ip[:last_position] + str(temp2+z)
                globalvariables.maclist2.append(mac)
                globalvariables.iplist2.append(ipaddress)

            vmname="%s%s"%(config.vmname,z+1)
            cmd="<host mac='%s' name='%s' ip='%s'/>"%(mac,vmname,ipaddress)
            exec_remote_cmd("sed -i \"/\/dhcp/i\      %s\" %s"%(cmd,xmlfile),ipaddr)

        config.hosts[host]["maclist1"]=globalvariables.maclist1
        config.hosts[host]["maclist2"]=globalvariables.maclist2
        config.hosts[host]["iplist1"]=globalvariables.iplist1
        config.hosts[host]["iplist2"]=globalvariables.iplist2


#### Creating the actual Bridge using virsh Command
def createbridge(host):
    print "Creating Virtual Bridges on Srever %s"%host
    ipaddr=config.hosts[host]["hostIP"]
    sshobj=globalvariables.SSHObj[ipaddr]["obj"]
    for x in range(len(config.hosts[host]["interfaces"])):
        bridgepath="%s%s%s.xml"%(config.cwd,config.bridgename,x)
        name="%s%s"%(config.bridgename,x)
        exec_remote_cmd("virsh net-list | grep %s"%name,ipaddr)
        if "bridge%s"%x not in str(sshobj.output):
            exec_remote_cmd("virsh net-define %s"%bridgepath,ipaddr)
            exec_remote_cmd("virsh net-start %s"%name,ipaddr)
            exec_remote_cmd("virsh net-autostart %s"%name,ipaddr)
            exec_remote_cmd("virsh net-list | grep %s"%name,ipaddr)
            if name not in str(sshobj.output):
                print "Failed: Cretaing new Bridge %s"%name
                globalvariables.retVal=1
            else:
                iface=config.hosts[host]["interfaces"][x]
                exec_remote_cmd("brctl addif %s%s %s"%(config.natbridgename,x,iface),ipaddr)
        else:
            removebridge(x,ipaddr)
            exec_remote_cmd("virsh net-define %s"%bridgepath,ipaddr)
            exec_remote_cmd("virsh net-start %s"%name,ipaddr)
            exec_remote_cmd("virsh net-autostart %s"%name,ipaddr)
            exec_remote_cmd("virsh net-list | grep %s"%name,ipaddr)
            if name not in str(sshobj.output):
                print "Failed: Creating %s"%name
            else:
                print "Success: Creating %s"%name
                iface=config.hosts[host]["interfaces"][x]
                exec_remote_cmd("brctl addif %s%s %s"%(config.natbridgename,x,iface),ipaddr)

## Removing Bridge
def removebridge(bridgeid,ipaddr):
    name="%s%s"%(config.bridgename,bridgeid)
    sshobj=globalvariables.SSHObj[ipaddr]["obj"]
    exec_remote_cmd("virsh net-destroy %s"%name,ipaddr)
    exec_remote_cmd("virsh net-undefine %s"%name,ipaddr)
    exec_remote_cmd("virsh net-list | grep %s"%name,ipaddr)
    if "Network %s has been undefined"%name in str(sshobj.output):
        write_both(globalvariables.result_scriptlog,"Success: Removing %s"%name)
    else:
        write_both(globalvariables.result_scriptlog,"Failed: Removing %s"%name)

## Commands to compile Sources
def pkgInstallcmds(option,mac="host"):
    if mac=="host":
        compiledir = config.install_Dir
    if mac=="vm":
        compiledir = "\/".join(config.install_Dir.split("/"))

    if option=="drivercmd":
        write_file(globalvariables.result_scriptlog," ******** BUILDING DRIVER ******** ")
        cmd="make LIQUID_SECURITY_DIR={0}; make install LIQUID_SECURITY_DIR={0}".format(compiledir)
        return (cmd)

    if option=="apicmd":
        write_file(globalvariables.result_scriptlog," ******** BUILDING API IOCTL ******** ")
        cmd1="make distclean"
        cmd2="aclocal; automake --add-missing; autoconf; libtoolize"
        cmd3="./configure --prefix=%s --enable-liquidsec_api_ioctl"%compiledir+ "; make all; make install"
        return (cmd1,cmd2,cmd3)

    if option=="utilscmd":
        write_file(globalvariables.result_scriptlog," ******** BUILDING UTILS ******** ")
        cmd1="aclocal; automake --add-missing; autoconf; libtoolize"
        cmd2="./configure --prefix={0} --with-liquidsec_api_include_dir={0}/include/ --with-liquidsec_api_lib_dir={0}/lib/".format(compiledir) + "; make all; make install"
        return (cmd1,cmd2)

    if option=="servercmd":
        write_file(globalvariables.result_scriptlog," ******** BUILDING API SERVER and BUILDING SERVER ******** ")
        cmd1="make distclean"
        cmd2="aclocal; automake --add-missing; autoconf; libtoolize"
        cmd3="./configure --prefix={0} --enable-liquidsec_api_server --with-event_lib_dir={0}/lib/".format(compiledir) + "; make all; make install"
        cmd4="aclocal; automake --add-missing; autoconf; libtoolize"
        cmd5="./configure --prefix={0} --with-liquidsec_api_include_dir={0}/include/  --with-liquidsec_api_lib_dir={0}/lib/ --with-event_lib_dir={0}/lib/".format(compiledir) + "; make all; make install"
        return (cmd1,cmd2,cmd3,cmd4,cmd5)

## Loading Module
def hostPkgInstaller():
    write_both(globalvariables.result_scriptlog,"Starting Driver Compilation on Host")
    p=runcmd(cmd="cp %s/nfbe0/pek.key_master /home/"%config.install_Dir)
    p=runcmd(cmd="rm -rf %s*"%config.install_Dir)
    p=runcmd(cmd="cd %s && tar -zxf %s"%(config.install_Dir,config.liquidsecPkg))
    p=runcmd(cmd="cd %s && tar -zxf %s"%(config.liquidsecDir,config.driverPkg))

    drivercmd=pkgInstallcmds("drivercmd")
    p=runcmd(cmd="cd %s && %s"%(config.driversrc,drivercmd))

    p=runcmd(cmd="cd %s && tar -zxf %s"%(config.liquidsecDir,config.apiPkg))
    apicmd=pkgInstallcmds("apicmd")
    p=runcmd(cmd="cd %s && %s"%(config.apisrc,apicmd[0]))
    p=runcmd(cmd="cd %s && %s"%(config.apisrc,apicmd[1]))
    p=runcmd(cmd="cd %s && %s"%(config.apisrc,apicmd[2]))

    p=runcmd(cmd="cd %s && tar -zxf %s"%(config.liquidsecDir,config.utilsPkg))
    utilcmd=pkgInstallcmds("utilscmd")
    p=runcmd(cmd="cd %s && %s"%(config.utilsrc,utilcmd[0]))
    p=runcmd(cmd="cd %s && %s"%(config.utilsrc,utilcmd[1]))

    p=runcmd(cmd="cd %s && tar -zxf %s"%(config.liquidsecDir,config.serverPkg))
    servercmd=pkgInstallcmds("servercmd")
    p=runcmd(cmd="cd %s && %s"%(config.apisrc,servercmd[0]))
    p=runcmd(cmd="cd %s && %s"%(config.apisrc,servercmd[1]))
    p=runcmd(cmd="cd %s && %s"%(config.apisrc,servercmd[2]))
    p=runcmd(cmd="cd %s && %s"%(config.serversrc,servercmd[3]))
    p=runcmd(cmd="cd %s && %s"%(config.serversrc,servercmd[4]))

    p=runcmd(cmd="cp /home/pek.key_master %s/nfbe0/pek.key_master"%config.install_Dir)
    write_both(globalvariables.result_scriptlog,"Successfully Compiled Driver On Host")
    p=commands.getstatusoutput("cp -rv pek.key_master %s/nfbe0/pek.key_master ."%config.install_Dir)

def remote_hostPkgInstaller(ipaddr):
    write_both(globalvariables.result_scriptlog,"Starting Driver Compilation on Host %s"%ipaddr)

    exec_remote_cmd("cp %s/nfbe0/pek.key_master /home/"%config.install_Dir,ipaddr)
    write_file(globalvariables.result_scriptlog,"Deleting and Creating Build Folder")
    cmd="rm -rf %s"%config.install_Dir
    exec_remote_cmd(cmd,ipaddr)
    cmd="mkdir %s"%config.install_Dir
    exec_remote_cmd(cmd,ipaddr)

    write_file(globalvariables.result_scriptlog,"Copying LiquidSecurity Package to VM")
    vmfunctions.remote_file_copy(ipaddr, config.liquidsecPkg, config.liquidsecPkg2)
    exec_remote_cmd("cd %s && tar -zxf %s"%(config.install_Dir,config.liquidsecPkg2),ipaddr)
    exec_remote_cmd("cd %s && tar -zxf %s"%(config.liquidsecDir,config.driverPkg),ipaddr)

    drivercmd=pkgInstallcmds("drivercmd")
    exec_remote_cmd("cd %s && %s"%(config.driversrc,drivercmd),ipaddr)

    exec_remote_cmd("cd %s && tar -zxf %s"%(config.liquidsecDir,config.apiPkg),ipaddr)
    apicmd=pkgInstallcmds("apicmd")
    exec_remote_cmd("cd %s && %s"%(config.apisrc,apicmd[0]),ipaddr)
    exec_remote_cmd("cd %s && %s"%(config.apisrc,apicmd[1]),ipaddr)
    exec_remote_cmd("cd %s && %s"%(config.apisrc,apicmd[2]),ipaddr)

    exec_remote_cmd("cd %s && tar -zxf %s"%(config.liquidsecDir,config.utilsPkg),ipaddr)
    utilcmd=pkgInstallcmds("utilscmd")
    exec_remote_cmd("cd %s && %s"%(config.utilsrc,utilcmd[0]),ipaddr)
    exec_remote_cmd("cd %s && %s"%(config.utilsrc,utilcmd[1]),ipaddr)

    exec_remote_cmd("cd %s && tar -zxf %s"%(config.liquidsecDir,config.serverPkg),ipaddr)
    servercmd=pkgInstallcmds("servercmd")
    exec_remote_cmd("cd %s && %s"%(config.apisrc,servercmd[0]),ipaddr)
    exec_remote_cmd("cd %s && %s"%(config.apisrc,servercmd[1]),ipaddr)
    exec_remote_cmd("cd %s && %s"%(config.apisrc,servercmd[2]),ipaddr)
    exec_remote_cmd("cd %s && %s"%(config.serversrc,servercmd[3]),ipaddr)
    exec_remote_cmd("cd %s && %s"%(config.serversrc,servercmd[4]),ipaddr)

    exec_remote_cmd("cp /home/pek.key_master %s/nfbe0/pek.key_master"%config.install_Dir,ipaddr)

    cmd="ls %ssrc/liquidsec_pf_vf_driver.ko"%(config.driversrc)
    output=exec_remote_cmd(cmd,ipaddr)
    string = config.driverName+".ko"
    if string in output:
        write_file(globalvariables.result_scriptlog,"Sucessfully compiled Driver")
    else:
        write_file(globalvariables.result_scriptlog,"Failed to Compile Driver")

def driverload(host,drivercmd):
    ipaddr=config.hosts[host]["hostIP"]
    write_both(globalvariables.result_scriptlog,"Loading Driver")

    if 'hsm_reload' not in drivercmd:
        cmd="lsmod | grep %s"%config.driverName
        exec_remote_cmd(cmd,ipaddr)
        string="liquidsec_pf_vf_driver"
        sshobj=globalvariables.SSHObj[ipaddr]["obj"]
        if string in str(sshobj.output):
            write_file(globalvariables.result_scriptlog,"Driver is Already Loaded");
            return 0;

    if 'hsm_reload' in drivercmd:
        exec_remote_cmd(globalvariables.driverunload,ipaddr)
    time.sleep(2)

    cmd="dmesg -c >/dev/null"
    exec_remote_cmd(cmd,ipaddr)
    exec_remote_cmd(drivercmd,ipaddr)

    found=""
    for number in range(30):
        output=exec_remote_cmd("cat /proc/cavium_n3fips/driver_state",ipaddr)
        time.sleep(5)
        string="SECURE_OPERATIONAL_STATE"
        if string in output:
            found=1
            break

    if found:
        write_both(globalvariables.result_scriptlog,"Successfully loaded Driver")
    else:
        write_both(globalvariables.result_scriptlog,"Driver load Failed")

globalvariables.PARTITIONS=[]
def checkPartitions(host):
    ipaddr=config.hosts[host]["hostIP"]
    sshobj=globalvariables.SSHObj[ipaddr]["obj"]

    exec_remote_cmd("%s getAllPartitionInfo | grep name | wc -l"%globalvariables.masterlogin,ipaddr)
    if int(sshobj.output) < int(config.num_of_vms):
        print "HSM is not configured for %s Partitions. Please configure manually and re-start script."%config.num_of_vms
        return 1
    else:
        ### Get all the Partition Names into an Array Variable
        exec_remote_cmd("%s getAllPartitionInfo | grep name | awk '{print $2}' | tr -d :"%globalvariables.masterlogin,ipaddr)
        globalvariables.PARTITIONS=str(sshobj.output).split()
        return 0
    
## Get List of PCI Devices
def getpcidevices(host):
    ipaddr=config.hosts[host]["hostIP"]
    write_both(globalvariables.result_scriptlog,"Accumulating Information of available PCI Devices")
    cmd=("lspci | grep -i unprogrammed | awk '{if(NR>1)print}' | awk '{print $1}'")
    config.hosts[host]["pcilist"]=exec_remote_cmd(cmd,ipaddr)

#### Launching VMs using qemu command ####
def launchVMs(host):
    ipaddr=config.hosts[host]["hostIP"]
    exec_remote_cmd("killall qemu",ipaddr)
    checkprocessstatus("qemu",ipaddr)
    tapcounter=1
    write_file(globalvariables.result_vmdetails,"Lauching VM's on host - %s"%host)
    for x in range(config.num_of_vms):
        dev=config.hosts[host]["pcilist"].split()[x]
        tap1="tap%s"%tapcounter
        tap2="tap%s"%(tapcounter+1)
        mac1=config.hosts[host]["maclist1"][x]
        mac2=config.hosts[host]["maclist2"][x]
        vmname="%s%s"%(config.vmname,x+1)

        string="VM: " + vmname + " ,mac1: " + mac1 + ", mac2: " + mac2 ; write_file(globalvariables.result_vmdetails,string)
        cmd="%s/qemu-system-x86_64 -hda %s/%s.qcow2 -smp 2 -m 2048 -net nic,model=virtio,macaddr=%s,vlan=1 -net tap,vlan=1,ifname=%s,script=/etc/qemu-ifup-virbr0,downscript=/etc/qemu-ifdown-virbr0 -net nic,model=virtio,macaddr=%s,vlan=2 -net tap,vlan=2,ifname=%s,script=/etc/qemu-ifup-virbr1,downscript=/etc/qemu-ifdown-virbr1 -boot c -device pci-assign,host=%s --nographic > /dev/null"%(config.qemupath,config.hosts[host]["vmStore"],vmname,mac1,tap1,mac2,tap2,dev)
        write_file(globalvariables.result_cmds,cmd)
        write_file(globalvariables.result_cmds,"\n")

        tapcounter=tapcounter+2
#        os.system("%s &"%cmd)
        exec_remote_cmd("%s &"%cmd,ipaddr)
        time.sleep(25)
        write_file(globalvariables.result_scriptlog,"Launched VM : "+vmname)

    output=exec_remote_cmd("pgrep -l qemu | wc -l",ipaddr)
    if (int(output) >= config.num_of_vms):
        write_both(globalvariables.result_scriptlog,"Successfully Launched " + str(config.num_of_vms) + " VMs. Waiting for all VM's to get up and Running.")
    else:
        write_both(globalvariables.result_scriptlog, "Launched Only " + str(p1[1]) + " VMs. Waiting for all VM's to get up and Running.")

#### Doing ping to check if the Interfaces are up and running ####
def checkvmstate(host):
    result=""
    write_both(globalvariables.result_mainchannelIp,"Checking Ping Status of VMs on host - %s"%host)
    write_file(globalvariables.result_backchannelIp,"Checking Ping Status of VMs on host - %s"%host)
    for x in range(config.num_of_vms):
        ipadd1 = config.hosts[host]["iplist1"][x]
        ipadd2 = config.hosts[host]["iplist2"][x]
        vmname = config.vmname+"%s"%(x+1)
        config.hosts[host][vmname]={}
        globalvariables.SSHObj[ipadd1]={}

        for number in range(20):
            time.sleep(5)
            ## Testing ping On Main Channel VM Interface
            p1=runcmd(cmd="ping -c 2 %s"%(ipadd1))
            if int(p1[0])==0:
                result_string1="Ping %s : Success for vm %s"%(ipadd1,vmname);
                openssh_connection(ipadd1, config.vm_username, config.vm_password)
                logfile="%s/%s_%s"%(config.logdir,host,vmname)
                fo=open_file("%s"%logfile)
                config.hosts[host][vmname]["logfile"]=logfile
                config.hosts[host][vmname]["fh"]=fo
                globalvariables.SSHObj[ipadd1]["fh"]=fo
                globalvariables.SSHObj[ipadd1]["logfile"]=logfile

                ## Testing ping On Back Channel VM Interface
                p2=runcmd(cmd="ping -c 2 %s"%(ipadd2))
                if int(p2[0])==0:
                    result_string2="Ping %s : Success for vm %s"%(ipadd2,vmname);
                    write_file(globalvariables.result_mainchannelIp,p1[1])
                    write_file(globalvariables.result_backchannelIp,p2[1])
                    write_file(globalvariables.result_mainchannelIp,"\t\t\t\t\t********** "+result_string1)
                    write_file(globalvariables.result_backchannelIp,"\t\t\t\t\t********** "+result_string2)
                    break
            else:
                if number==20:
                    result=1

        if result:
            result_string1="Ping %s : Failed for vm %s"%(ipadd1,vmname);
            result_string2="Ping %s : Failed for vm %s"%(ipadd2,vmname);
            write_file(globalvariables.result_mainchannelIp,"\t\t\t\t\t********** "+result_string1)
            write_file(globalvariables.result_backchannelIp,"\t\t\t\t\t********** "+result_string2)

## Opening a File
def open_file(file_name):
    file_object=open(file_name,"w")
    p1=commands.getstatusoutput("date")
    write_file(file_object, p1[1])
    write_file(file_object, "\n")
    return file_object

## Write to a File
def write_file(file_object, message):
    date=time.strftime("%c")
    file_object.write(date+" "+message+"\n")
    file_object.flush()

def write_both(file_object, message):
    print message
#    sys.stdout.write(message)
    date=time.strftime("%c")
    file_object.write(date+" "+message+"\n")
    file_object.flush()

## Closing a File
def close_file(file_object):
    p1=commands.getstatusoutput("date")
    write_file(file_object, "\n")
    write_file(file_object, p1[1])
    file_object.close()

## GraceFully shutdown VMs
def stopvms(ipaddr,x,option="normal"):
    if option=="force":
        write_file(globalvariables.result_scriptlog, "Force Stopping any Running VMs");
        output=exec_remote_cmd("pgrep -l qemu | wc -l",ipaddr)
        if '0' in output:
            write_both(globalvariables.result_scriptlog,"Successfully stopped all the VMs")
        else:
            a=commands.getoutput("pgrep -l qemu | awk '{print $1}'")
            for x in range(len(a.split())):
                commands.getoutput("kill -9 "+ a.split()[x])
            a=runcmd(cmd="pgrep -l qemu | wc -l")
            if a[0]==0:
                write_both(globalvariables.result_scriptlog,"Successfully stopped all the VMs")

    if option=="normal":
        write_file(globalvariables.result_scriptlog, "Trying to Stop all the Running VMs");
#        for x in range(config.num_of_vms):
#            ipadd1 = globalvariables.iplist1[x]
#        ipadd = config.hosts[host]["iplist1"][x]
        vmname = config.vmname+"%s"%(x+1)
        p1=runcmd(cmd="ping -c 2 %s"%(ipaddr))
        if int(p1[0])==0:
            a=os.system("sshpass -p %s ssh -o StrictHostKeyChecking=no %s \"nohup shutdown -h now &>/dev/null & exit\" "%(config.vm_password,ipaddr))
            time.sleep(2)
            p2=runcmd(cmd="ping -c 2 %s"%(ipaddr))
            if int(p2[0]):
                write_file(globalvariables.result_scriptlog, "Successfully stopped VM %s"%vmname)
            else:
                write_file(globalvariables.result_scriptlog, "Failed stopping VM %s"%vmname)

        a=runcmd(cmd="pgrep -l qemu | wc -l")
        if a[1]==0:
            write_both(globalvariables.result_scriptlog,"Successfully stopped all the VMs")
        else:
            write_both(globalvariables.result_scriptlog,"Some Qemu process is still Running, Please check manually.")

def scriptStartup():
    p = commands.getstatusoutput("cp -rv %s/nfbe0/pek.key_master ./temp" %config.install_Dir)
    os.system("rm -rf %s" %config.logdir)
    os.system("mkdir %s" %config.logdir)
    os.system("rm -rf %s" %config.tempdir)
    os.system("mkdir %s" %config.tempdir)

    ## Opening New File Handles
    globalvariables.result_scriptlog	 = open_file("%s/scriptlog.txt" %config.logdir)
    globalvariables.result_debuglog	 = open_file("%s/debuglog.txt" %config.logdir)
    globalvariables.result_cmds 	 = open_file("%s/cmds.txt" %config.logdir)
    globalvariables.result_vmdetails	 = open_file("%s/vmdetails.txt" %config.logdir)
    globalvariables.result_mainchannelIp = open_file("%s/MainChannelIP.txt" %config.logdir)
    globalvariables.result_backchannelIp = open_file("%s/BackChannelIP.txt" %config.logdir)
    write_both(globalvariables.result_scriptlog, "Calling script Startup Function")

    write_file(globalvariables.result_scriptlog,"Copying qemu Network Config files to /etc/")
    p = commands.getstatusoutput("cp -rv %s/qemu-if* /etc" %config.dataBase)
    write_file(globalvariables.result_scriptlog,"\n"+p[1])

    for host in config.hosts.keys():
        ip = config.hosts[host]["hostIP"]
        p1 = runcmd(cmd = "ping -c 2 %s" %(ip))

        if int(p1[0]) == 0:
            result_string1 = "Ping Host %s : Success" %ip;
            openssh_connection(ip, config.vm_username, config.vm_password)
            logfile = "%s/%s" %(config.logdir, host)
            fo = open_file("%s"%logfile)
            globalvariables.SSHObj[ip]["logfile"] = logfile
            globalvariables.SSHObj[ip]["fh"] = fo

        else:
            print "Ping to Host %s failed" %ip
            return 1

def cl_closeAllFDs():
    ## Remove all .pyc
    write_file(globalvariables.result_scriptlog,"Cleaning All *.pyc")
    p=commands.getstatusoutput("rm -rf *.pyc")

    ## Closing All Opened File Handles
    write_file(globalvariables.result_scriptlog,"Closing All File Handles")
    close_file(globalvariables.result_mainchannelIp)
    close_file(globalvariables.result_backchannelIp)
    close_file(globalvariables.result_scriptlog)
    close_file(globalvariables.result_vmdetails)
    close_file(globalvariables.result_cmds)


def scriptCleanup(host):
    hostipaddr=config.hosts[host]["hostIP"]
    if globalvariables.retVal==1:
        print "Failed : Script exeution. Check Logs more details."
    write_both(globalvariables.result_scriptlog, "Calling script Cleanup Function")
    ## Stopping VMs
    for x in range(config.num_of_vms):
        ipaddr = config.hosts[host]["iplist1"][x]
        stopvms(ipaddr,x)
    ## Removing User created Bridges
    for x in range(len(config.hosts[host]["interfaces"])):
        removebridge(x,hostipaddr)

def runcmd(cmd):
    write_file(globalvariables.result_scriptlog,cmd)
    p=commands.getstatusoutput(cmd)

    write_file(globalvariables.result_debuglog,p[1])
    return (p[0],p[1])

def backupPartition(host):
    ipaddr=config.hosts[host]["hostIP"]
    write_both(globalvariables.result_scriptlog,"Performing Backup of a Parition form Backup Host")
    config.hosts[host]["fh"]={}
    for x in range(len(config.hosts[host]["partition_list"])):
        partition=config.hosts[host]["partition_list"][x]
        if x==0:
            vmfunctions.part_init(host,partition)
            ## Creating Backup Directory
            exec_remote_cmd("rm -rf %s"%config.backupdir,ipaddr)
            exec_remote_cmd("mkdir %s"%config.backupdir,ipaddr)

            ## performing backup of PARTITION
            cmd="%s backupPartition -d %s -n %s"%(globalvariables.masterlogin,config.backupdir,partition)
            exec_remote_cmd(cmd,ipaddr)
    
    return 0

def restorePartition():
    ipaddr_bkphost=config.hosts[config.backup]["hostIP"]
    sshobj_bkphost=globalvariables.SSHObj[ipaddr_bkphost]["obj"]
    srcpek="pek.key_1"
    for x in range(len(config.restore)):
        host=config.restore[x]
        write_both(globalvariables.result_scriptlog,"Performing Restore on '%s' and Copying PEK for each partition."%host)
        ipaddr=config.hosts[host]["hostIP"]
        sshobj=globalvariables.SSHObj[ipaddr]["obj"]
        if host != config.backup:
            ## Creating Remote Backup Directory
            exec_remote_cmd("rm -rf %s"%config.backupdir,ipaddr)
            exec_remote_cmd("mkdir %s"%config.backupdir,ipaddr)

            ## Copying files to remote backup directory
            write_file(globalvariables.SSHObj[ipaddr_bkphost]["fh"],"Gettling list of files in Backup Directory")
            exec_remote_cmd("ls %s"%config.backupdir,ipaddr_bkphost)
            a=str(sshobj_bkphost.output).split()
            for y in range(len(a)):
                vmfunctions.remote_file_copy(ipaddr, "%s/%s"%(config.backupdir,a[y]),"%s/%s"%(config.backupdir,a[y]))

        for x in range(len(config.hosts[host]["partition_list"])):
            partition=config.hosts[host]["partition_list"][x]
            if host==config.backup and x==0:
                continue
            write_file(globalvariables.SSHObj[ipaddr]["fh"],"Performing Restore on Partition %s for host %s"%(partition,host))
            login=globalvariables.nologin.replace("PARTITION", partition)
            zeroize="%s zeroizeHSM"%(login)
            exec_remote_cmd(zeroize,ipaddr)
            if 'Cfm2Zeroize returned: 0x00 : HSM Return: SUCCESS' not in str(sshobj.output):
                return 1

            ## performing restore of PARTITION
            cmd="%s restorePartition -d %s -n %s"%(globalvariables.masterlogin,config.backupdir,partition)
            exec_remote_cmd(cmd,ipaddr)

            write_file(globalvariables.SSHObj[ipaddr]["fh"],"Copying pek for partition %s on host - %s"%(partition,host))
            dstpek="pek.key_" + str(x+1)
            copycmd="cp -rv %s/nfbe0/%s %s/nfbe0/%s"%(config.install_Dir,srcpek,config.install_Dir,dstpek)
            if host==config.backup and x!=0:
                vmfunctions.remote_file_copy(ipaddr_bkphost, "%s/nfbe0/%s"%(config.install_Dir,srcpek),"%s/nfbe0/%s"%(config.install_Dir,dstpek))
            if host!=config.backup:
                vmfunctions.remote_file_copy(ipaddr, "%s/nfbe0/%s"%(config.install_Dir,srcpek),"%s/nfbe0/%s"%(config.install_Dir,dstpek))

def openssh_connection(ipaddr,username,password):
    write_file(globalvariables.result_scriptlog,"Opening SSH Connection to IP %s"%(ipaddr))
    sshconn=""
    globalvariables.SSHObj[ipaddr]={}
    if globalvariables.SSHObj.get(ipaddr).get("obj","none") == "none":
        sshconn=ssh.sshConnection(ipaddr, username, password)
        globalvariables.SSHObj[ipaddr]["obj"]=sshconn
    else:
        sshconn=globalvariables.SSHObj[ipaddr]["obj"]

    return sshconn

def exec_remote_cmd(cmd,ipaddr):
    if globalvariables.SSHObj.get(ipaddr).get("obj","none") == "none":
        openssh_connection(ipaddr1, config.vm_username, config.vm_password)
    else:
        sshobj=globalvariables.SSHObj[ipaddr]["obj"]
        FH=globalvariables.SSHObj[ipaddr]["fh"]
        sshobj.sendCommand(cmd)
        write_file(FH,cmd)
        write_file(FH,str(sshobj.output))
        return str(sshobj.output)

def checkprocessstatus(process,ipaddr):
    cmd="pgrep -l %s | wc -l"%(process)
    a=exec_remote_cmd(cmd,ipaddr)
    sshobj=globalvariables.SSHObj[ipaddr]["obj"]
    if "0" in str(sshobj.output):
        write_both(globalvariables.result_scriptlog,"No process with name %s is Running"%process)
        return 0
    else:
        write_both(globalvariables.result_scriptlog,"A process with name %s is already running. Please Kill it and re-run the script"%process)
        return 1
