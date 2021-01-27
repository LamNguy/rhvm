class VM:
    def __init__ (self , vm ):
        self.name = vm['name']
        self.ips  =  vm['ips']
        self.vcpu = vm['vcpu']
        self.ram = vm['ram']
	self.luns = vm['luns']
	self.cluster = vm['cluster']
    def test(self):
        print('VM_NAME:{}').format(self.name)
       	for ip in self.ips:
		print('NIC:{},IP:{}').format(ip.nic, ip.ip)
        print('VCPU:{}').format(self.vcpu)
        print('RAM:{}').format(self.ram)
	for lun in self.luns:
		print('ID:{},BOOTALBE:{}').format(lun.id, lun.bootable)	
	print('Cluster: {}').format(self.cluster)
