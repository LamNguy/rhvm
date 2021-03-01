class VM:

# Class VM provide vm struct 
#

    def __init__ (self , vm ):
        self.name = vm['name']
	self.id = vm['id'] 
        self.ip  =  vm['ip']
        self.vcpu = vm['vcpu']
        self.ram = vm['ram']
	self.luns = vm['luns']
	self.cluster = vm['cluster']
	self.vlan = vm['vlan']
	self.host = vm['host']
	 
    # Print vm properties 
    def test(self):
        print('VM_NAME:{}').format(self.name)
	print('VM_CLUSTER:{}').format(self.cluster)
	print('VM_VLAN:{}').format(self.vlan)
	print('IP:{},NETMASK:{},GATEWAY:{}').format(self.ip.ip, self.ip.netmask, self.ip.gateway)
        print('VCPU:{}').format(self.vcpu)
        print('RAM:{}').format(self.ram)
	print('HOST:{}').format(self.host)
	for lun in self.luns:
		print('ID:{},BOOTALBE:{},NAME:{}').format(lun.id, lun.bootable,lun.alias)	
	print('Cluster: {}').format(self.cluster)
