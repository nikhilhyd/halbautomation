#!/usr/bin/python
import re
import time
import config
import commands
import functions
import globalvariables
import ssh
from scp import SCPConnection

def configvm(host):
    ipaddr=config.hosts[host]["hostIP"]
    srcpek="pek.key_1"
    for x in range(config.num_of_vms):
        ipaddr=config.hosts[host]["iplist1"][x]
        vmname="%s%s"%(config.vmname,x+1)
        functions.write_both(globalvariables.result_scriptlog,"Compiling and Loading Driver for VM %s"%vmname)

        functions.remote_hostPkgInstaller(ipaddr)
        loadDriverModule(ipaddr)
        partition=getPartitionName(ipaddr)
        functions.write_file(globalvariables.SSHObj[ipaddr]["fh"],"Coptying pek for partition %s to VM %s"%(partition,vmname))
        dstpek="pek.key_" + str(x+1)
        remote_file_copy(ipaddr, "%s/nfbe0/%s"%(config.install_Dir,srcpek),"%s/nfbe0/%s"%(config.install_Dir,dstpek))
        functions.exec_remote_cmd("/home/nikhil/bin/Cfm2Util -p %s singlecmd loginHSM -u CU -s crypto_user -p user123"%partition, ipaddr)

def remote_file_copy(ipaddr,origin,dst):
    scpconn=""
    if globalvariables.SCPObj.get(ipaddr,"none") == "none":
        functions.write_file(globalvariables.result_scriptlog,"Opening SCP Connection for ip %s"%ipaddr)
        scpconn = SCPConnection(ipaddr, config.vm_username, config.vm_password)
        globalvariables.SCPObj[ipaddr]=scpconn
    else:
        scpconn=globalvariables.SCPObj[ipaddr]
    functions.write_file(globalvariables.SSHObj[ipaddr]["fh"],"copying %s to %s"%(origin,dst))
    scpconn.put(origin, dst)

def loadDriverModule(ipaddr):
    functions.exec_remote_cmd("dmesg -c > /dev/null",ipaddr)
    loadcommand = "sh %s/driver_load.sh hsm_load %sbin/ > /dev/null"%(config.driversrc,config.install_Dir)
    functions.exec_remote_cmd(loadcommand,ipaddr)
    found=""
    for number in range(10):
        output=functions.exec_remote_cmd("cat /proc/cavium_n3fips/driver_state",ipaddr)
        time.sleep(5)
        string="SECURE_OPERATIONAL_STATE"
        if string in output:
            found=1
            time.sleep(2);
            break;

    if found:
        functions.write_file(globalvariables.result_scriptlog,"Successfully loaded Driver")
    else:
        functions.write_file(globalvariables.result_scriptlog,"Driver load Failed")
        functions.retVal=1


def getPartitionName(ipaddr):
    output=functions.exec_remote_cmd("dmesg",ipaddr)
    p=re.compile("completed for partition (.*)")
    partname=p.findall(output)[0]
    return partname

def part_init(host,partname):
    ipaddr=config.hosts[host]["hostIP"]
    sshobj=globalvariables.SSHObj[ipaddr]["obj"]
    login=globalvariables.nologin.replace("PARTITION", partname)
    zeroize="%s zeroizeHSM"%(login)
    functions.exec_remote_cmd(zeroize,ipaddr)
    if 'Cfm2Zeroize returned: 0x00 : HSM Return: SUCCESS' not in str(sshobj.output):
        return 1

    login=globalvariables.defaultlogin.replace("PARTITION", partname)
    inithsm="%s initHSM -sO %s -p %s -sU %s -u %s -a 0 -f %s"%(login,config.co_user,config.co_pass,config.cu_user,config.cu_pass,config.hsm_config)
    functions.exec_remote_cmd(inithsm,ipaddr)
    if 'Cfm2InitHSMDone returned: 0x00 : HSM Return: SUCCESS' not in str(sshobj.output):
        return 1

    login=globalvariables.cologin.replace("PARTITION", partname)
    genkek="%s generateKEK"%(login)
    functions.exec_remote_cmd(genkek,ipaddr)
    if 'Cfm2GenKeyEncKeyNew returned: 0x00 : HSM Return: SUCCESS' not in str(sshobj.output):
        return 1

    createau="%s createUser -u AU -s %s -p %s"%(login,config.au_user,config.au_pass)
    functions.exec_remote_cmd(createau,ipaddr)
    if 'Cfm2createUser returned: 0x00 : HSM Return: SUCCESS' not in str(sshobj.output):
        return 1

    getcsr="%s getCertReq -f %s"%(login,config.csr)
    functions.exec_remote_cmd(getcsr,ipaddr)
    if 'Cfm2GetCertReq() returned 0 :HSM Return: SUCCESS' not in str(sshobj.output):
        return 1

    storecert="%s storeCert -f %s -s 4"%(login,config.pocert)
    functions.exec_remote_cmd(storecert,ipaddr)
    if 'Cfm2StoreCert() returned 0 :HSM Return: SUCCESS' not in str(sshobj.output):
        return 1

    signcert="openssl x509 -days 365 -req -in %s -CA %s -CAkey %s -set_serial 01 -out %s"%(config.csr,config.pocert,config.pokey,config.signedcert)
    functions.exec_remote_cmd(signcert,ipaddr)

    storesignedcert="%s storeCert -f %s -s 8"%(login,config.signedcert)
    functions.exec_remote_cmd(storesignedcert,ipaddr)
    if 'Cfm2StoreCert() returned 0 :HSM Return: SUCCESS' not in str(sshobj.output):
        return 1

