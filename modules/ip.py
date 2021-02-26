class nics:

# nics class provide network interface card for vm
# with info: ipaddress, netmask, gateway, nameserver
#
    def __init__ (self , ip, netmask, gateway ):
        self.ip = ip 
	self.nic = None
	self.netmask = netmask
	self.gateway = gateway 

    # Print nics properties
    def test(self):
        print(self.ip)
        print(self.netmask)
	print(self.gateway)
	
