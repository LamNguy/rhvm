import logging 
import os
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
    def test(self,logger):
	logger.info('---------------VM: {}-------------'.format(self.name))
	logger.info('cluster: {}'.format(self.cluster))
	logger.info('host: {}'.format(self.host))
	logger.info('vcpu: {}'.format(self.vcpu))
	logger.info('memory: {}'.format(self.ram))
	logger.info('vcpu: {}'.format(self.vcpu))
	logger.info('network vlan: {}'.format(self.vlan))
	logger.info('ip: {}'.format(self.ip.ip))
	logger.info('netmask: {}'.format(self.ip.netmask))
	logger.info('gateway: {}'.format(self.ip.gateway))
	 

	for lun in self.luns:
		logger.info('Lun {},os={},alias={},size={}'.format(lun.id,lun.bootable,lun.alias,lun.size))
