class nics:
    def __init__ (self , ip, netmask, gateway ):
        self.ip = ip 
	self.nic = None
	self.netmask = netmask
	self.gateway = gateway 

    def test(self):
        print(self.ip)
        print(self.netmask)
	print(self.gateway)
	
