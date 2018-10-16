from paramiko import client

class sshConnection:
    client = None
    file_object = ""
    output=""
    def __init__(self, address, username, password):
        # Let the user know we're connecting to the host
        # print("Connecting to host.")
        # Create a new SSH client
        self.client = client.SSHClient()
        # The following line is required if you want the script to be able to access a host that's not yet in the known_hosts file
        self.client.set_missing_host_key_policy(client.AutoAddPolicy())
        # Make the connection
        self.client.connect(address, username=username, password=password, look_for_keys=False)

    def sendCommand(self, command):
        # Check if connection is made previously
        if(self.client):
            stdin, stdout, stderr = self.client.exec_command(command)
            while not stdout.channel.exit_status_ready():
                # Print stdout data when available
                if stdout.channel.recv_ready():
                    # Retrieve the first 1024 bytes
                    alldata = stdout.channel.recv(1024)
                    while stdout.channel.recv_ready():
                        # Retrieve the next 1024 bytes
                        alldata += stdout.channel.recv(1024)
 
                    # Print as string with utf8 encoding #print(str(alldata, "utf8"))
                    #print(str(alldata))
                    self.output=str(alldata)
        else:
            print("Connection not opened.")
