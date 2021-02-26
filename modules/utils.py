from modules.vm import *
from modules.lun import *
from modules.ip import *
import ovirtsdk4.types as types
import time
import json
import sys

# class Utils provide process action to start a virtual machine
#
#

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
	self.hosts_service = self.conn.system_service().hosts_service()
	self.data = open('/home/centos/rhvm/modules/user_script', 'r').read()



    # start vm with user_script
    def start_vm (self, vm_service , cloud_init=True , scontent=None):

	vm_service.start(
                use_cloud_init= cloud_init ,
                vm = types.Vm(
                        initialization=types.Initialization(
                                custom_script = scontent,
                        )
                )
        )

        #if vm no start down    
        while True:
                break
                time.sleep(5)
                if vm_service.get().status == types.VmStatus.UP :
                        print('done')
                        break
                print(vm_service.get().status)  


    # create disk 
    def create_disk (self,lun,vm_host):
	disk=types.Disk(
            name='test',
            lun_storage=types.HostStorage(
               type=types.StorageType.FCP,
	       #host=types.Host(name=vm_host),
	       logical_units= [
	    		types.LogicalUnit(
                        	id=lun.id,
               	    	 )
	       ],
            ),
        )
	try :
		new_disk = self.disk_service.add(disk)
	except:
		return None
	return new_disk 	

    def list_host (self, _name):
	host = self.hosts_service.list(search='name={}'.format(_name))[0]
	return host.cluster.id

    def vms_data (self,data):
	vms = []
	for index,row in data.iterrows():
        	vm = {}
        	vm['luns'] = []
        	pre_vm = next((i for i in vms if i.id == row['id']),None)
        	if pre_vm is not None:
                	pre_vm.luns.append(LUN(row['os'],row['bootable'],row['lun_name']))
                	continue

        	vm['luns'].append(LUN(row['os'],row['bootable'],row['lun_name']))
		vm['ip'] = nics(row['ip'], row['subnet'], row['gateway'])
        	vm['id'] = row['id']
        	vm['name'] = row['name']
        	vm['ram'] = row['ram']
        	vm['vcpu'] = row['vcpu']
        	vm['cluster'] = self.list_host(row['host']) 
        	vm['vlan'] = row['vlan']
		vm['host'] = row['host']
        	vms.append(VM(vm))
	return vms 

    def user_script (self, data,  mac, ip , mask , gateway):
	return  self.data.format(mac,ip,mask,gateway,'{print $2}','{a%?}')


    def create_vm_template(self,vm):

    	placement_policy = types.VmPlacementPolicy(
                hosts =[
                        types.Host(name=vm.host)
                ]
        )
        cpu = types.CpuTopology( cores=vm.vcpu )	

	return  types.Vm(
        		name=vm.name,
                        memory=vm.ram*1024*1024*1024,
                        cpu=types.Cpu(topology=cpu),
                        cluster=types.Cluster(
                       		id=vm.cluster,
                        ),
                        template=types.Template(
                        	name='Blank',
                        ),
                        placement_policy = placement_policy
        )
 

    def create_vm_nic (self,vlan):
	network = next(( i for i in self.networks_service.list() if i.vlan is not None and i.vlan.id == vlan ),None)
	profile = next((i for i in self.profiles_service.list() if i.name == network.name),None)
	return types.Nic(
               		name ='nic',
                        interface=types.NicInterface.VIRTIO,
                        vnic_profile=types.VnicProfile(id=profile.id)
        )


    # luu y: all luns thuoc host cua vm
    def create_and_attach_vm_lun (self, luns , host):
	# create disks attaching to vm
	res = []
	for lun in luns:
		vm_disk  = self.create_disk(lun,host)
		if vm_disk is not None:
			disk =	types.DiskAttachment(
                                		disk= types.Disk(
                                        		id = vm_disk.id,
                                		),
                                		interface=types.DiskInterface.VIRTIO,
                                		active = True,
                                		bootable = lun.bootable,
                        	)
			res.append(disk)	
		else:
			print('{} is attached to a volume').format(lun.id)
	return res 




    def create_vm (self, vm):
	
	#search vm name 
	vmx = self.vms_service.list(search='name={}'.format(vm.name))
	
	if not vmx :
		print('Create vm')

	#1 CREATE VM 

		# get template server {name,ram,cpu}
		vm_template = self.create_vm_template(vm)
		# create vm (only template)
		_vm = self.vms_service.add(vm_template)
		# vm service
		vm_service = self.vms_service.vm_service(_vm.id)
		
	#2 ADD VM NIC 			

		# vm nic service
		nics_service = vm_service.nics_service()
		# create nic	
		nic = self.create_vm_nic( vm.vlan )	
		# add nic to vm
		nic_vm = nics_service.add(nic)		
	#3 CREATE & ATTACH DISK
		
		# disk attachments service
		disk_attachments_service = vm_service.disk_attachments_service()
		# get luns attachments
		luns = self.create_and_attach_vm_lun(vm.luns,vm.host)
		
		# attach luns
		for lun in luns:
			disk_attachment = disk_attachments_service.add(lun)
			vm_disk_service = self.disk_service.disk_service(disk_attachment.id)  
			while True:
				time.sleep(5)
				print(vm_disk_service.get().status)
				break
	#4 START VM
		#scontent = self.data.format(mac,ip,mask,gateway,'{print $2}','{a%?}')
		#self.start_vm(vm_service, True,scontent)
	else:
		print('VM:{} existed').format(vm.name)	
	
