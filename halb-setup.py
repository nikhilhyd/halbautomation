#!/usr/bin/python
import os
import sys
import time
import config
import commands
import functions
import vmfunctions
import globalvariables

try:
    functions.scriptStartup()

    for host in config.hosts.keys():
        functions.remote_hostPkgInstaller(config.hosts[host]["hostIP"])
        functions.driverload(host,globalvariables.pf_driverreload)

        if functions.checkPartitions(host) != 0:
            raise ValueError("Partitions is/are not available to launch VM's")

        config.hosts[host]["partition_list"] = globalvariables.PARTITIONS

        functions.getInterface(host)
        functions.configurebridge(host)
        functions.createbridge(host)

    functions.backupPartition(config.backup)
    functions.restorePartition()

    for host in config.hosts.keys():
        functions.driverload(host,globalvariables.vf_driverreload)
        functions.getpcidevices(host)

        functions.launchVMs(host)
        functions.checkvmstate(host)
        vmfunctions.configvm(host)

    ## Cleaning, Closing All Opened File Handles
    for host in config.hosts.keys():
        functions.scriptCleanup(host)
    functions.cl_closeAllFDs()

except Exception as e:
    print("\nException!!")
    print(str(e))
    functions.write_file(globalvariables.result_scriptlog,"Exception Occured, Exitting..")

    if (globalvariables.retVal):
        for host in config.hosts.keys():
            functions.scriptCleanup(host)
    functions.cl_closeAllFDs()
