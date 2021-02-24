class VM:
    def __init__ (self , vm ):
        self.name = vm['name']
	self.id = vm['id']
        self.ips  =  vm['ips']
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
       	for ip in self.ips:
		print('IP:{},NETMASK:{},GATEWAY:{}').format(ip.ip, ip.netmask, ip.gateway)
        print('VCPU:{}').format(self.vcpu)
        print('RAM:{}').format(self.ram)
	print('HOST:{}').format(self.host)
	for lun in self.luns:
		print('ID:{},BOOTALBE:{}').format(lun.id, lun.bootable)	
	print('Cluster: {}').format(self.cluster)
