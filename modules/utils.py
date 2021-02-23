from modules.vm import *
from modules.lun import *
from modules.ip import *
import ovirtsdk4.types as types
import time
import sys
class Utils:
    def __init__ (self, conn):
        self.conn = conn
        self.instance_types_service = self.conn.system_service().instance_types_service()
        self.disk_service = self.conn.system_service().disks_service()
        self.vms_service = self.conn.system_service().vms_service()
        self.clusters_service = self.conn.system_service().clusters_service()
	self.profiles_service = self.conn.system_service().vnic_profiles_service()
	self.networks_service = self.conn.system_service().networks_service()
	self.dcs_service = self.conn.system_service().data_centers_service()
	self.data = open('/home/centos/rhvm/modules/user_script', 'r').read()

    def vms_data (self,data):
	vms = []
	for index,row in data.iterrows():
        	vm = {}
        	vm['luns'] = []
        	vm['ips'] = []

        	pre_vm = next((i for i in vms if i.id == row['id']),None)
        	if pre_vm is not None:
                	pre_vm.luns.append(LUN(row['os'],row['bootable']))
                	continue

        	vm['luns'].append(LUN(row['os'],row['bootable']))
        	vm['ips'].append( nics(row['ip'], row['subnet'], row['gateway'] ))
        	vm['id'] = row['id']
        	vm['name'] = row['name']
        	vm['ram'] = row['ram']
        	vm['vcpu'] = row['vcpu']
        	vm['cluster'] = 'managed'
        	vm['vlan'] = row['vlan']
        	vms.append(VM(vm))
	return vms 
    def user_script (self, data,  mac, ip , mask , gateway):
	return  self.data.format(mac,ip,mask,gateway,'{print $2}','{a%?}')


    def create_vm (self, vm):
 	cpu = types.CpuTopology( cores=vm.vcpu )
	_vm = self.vms_service.add(
			types.Vm(
				name=vm.name,
				memory=vm.ram*1024*1024*1024,
				cpu=types.Cpu(topology=cpu),
				cluster=types.Cluster(
					name=vm.cluster,
				),
				template=types.Template(
					name='Blank',
				),
			),
		)	
	

 
	
	#
	# VM_SERVICE
	# 

	vm_service = self.vms_service.vm_service(_vm.id)
	
	#
 	# ADD VM_NICS 	
	#
	nics_service = vm_service.nics_service()
	network = next(( i for i in self.networks_service.list() if i.vlan is not None and i.vlan.id == vm.vlan),None)
	profile = next((i for i in self.profiles_service.list() if i.name == network.name),None)
	
	i = 0 		
        for ip in vm.ips:
		nics_service.add(
			types.Nic(
				name = 'nic{}'.format(i),
				interface=types.NicInterface.VIRTIO,
				vnic_profile=types.VnicProfile(id=profile.id)
			),
		)
		ip.nic = 'nic{}'.format(i)
		i= i+1
	
	
	#
	#  ADD DISK 
	#
	for lun in vm.luns:
		disk_attachments_service = vm_service.disk_attachments_service()
		disk_attachment = disk_attachments_service.add(
			types.DiskAttachment(
				disk= types.Disk(
					id = lun.id,
				),
				interface=types.DiskInterface.VIRTIO,
				active = True,
				bootable = lun.bootable,
			),
		)	
		_disk_service = self.disk_service.disk_service(disk_attachment.id)
		while True:
			time.sleep(3)
			disk = _disk_service.get()
			print(disk.status)
			break	

	#
	# Cloud-init
	#	
	
	for nic in nics_service.list():	
		_nic = next((ip for ip in vm.ips if ip.nic == nic.name ),None)
		scontent = self.user_script(self.data, nic.mac.address, _nic.ip ,_nic.netmask , _nic.gateway)
		vm_service.start(
			use_cloud_init=True,
			vm = types.Vm(
				initialization=types.Initialization(
					custom_script = scontent,
				)
			)
		)
		
		while True:
			time.sleep(5)
			done_vm = vm_service.get()
			if done_vm.status == types.VmStatus.UP :
				print('done')
				break
			print(done_vm.status)
