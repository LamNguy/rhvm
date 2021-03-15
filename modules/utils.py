from modules.vm import *
from modules.lun import *
from modules.ip import *
import ovirtsdk4.types as types
import time
import logging
import os

formatter = logging.Formatter(
                '%(asctime)s - %(name)s - Level:%(levelname)s - %(message)s')

# class Utils provide process action to start a virtual machine
#
#

class Utils:
    def __init__ (self, conn):
        self.conn = conn
        self.disk_service = self.conn.system_service().disks_service()
        self.vms_service = self.conn.system_service().vms_service()
	self.profiles_service = self.conn.system_service().vnic_profiles_service()
	self.networks_service = self.conn.system_service().networks_service()
	self.hosts_service = self.conn.system_service().hosts_service()
	#self.data = open('/home/centos/rhvm/modules/user_script', 'r').read()
	#self.instance_types_service = self.conn.system_service().instance_types_service()
	#self.clusters_service = self.conn.system_service().clusters_service
	#self.dcs_service = self.conn.system_service().data_centers_service()


    # cloud init config network for nic 'eth0' at centos 
    def start_vm_cloud_init( self, vm_service , vm  , use_cloud_init = True ):
	vm_service.start(
                        use_cloud_init= use_cloud_init,
                        vm = types.Vm(
                                initialization=types.Initialization(
                                        nic_configurations=[
                                                types.NicConfiguration(
                                                        name= 'eth0',
                                                        on_boot=True,
                                                        boot_protocol=types.BootProtocol.STATIC,
                                                        ip= types.Ip(
                                                                version=types.IpVersion.V4,
                                                                address = vm.ip.ip,
                                                                netmask = vm.ip.netmask,
                                                                gateway = vm.ip.gateway
                                                        )
                                                )
                                        ],
                                        dns_servers = '8.8.8.8',
                                )
                        )
                )


    # start vm with user script
    def start_vm (self, vm_service , cloud_init=True , scontent=None):

	vm_service.start(
                use_cloud_init = cloud_init ,
                vm = types.Vm(
                        initialization=types.Initialization(
                                custom_script = scontent,
                        )
                )
        )

        #if vm no start down    
        while True:
      	        break
                #time.sleep(5)
                #if vm_service.get().status == types.VmStatus.UP :
                #        print('done')
                #        break
                #print(vm_service.get().status)  


    # create disk 
    def create_disk (self, lun, host, logger):

	try :
		logger.info('Trying to create disk with lun {} in host {}'.format(lun.id, host))
		# create disk template
		disk = types.Disk(
           		name=lun.alias,
            		lun_storage=types.HostStorage(
               			type=types.StorageType.FCP,
               			#host=types.Host(name=host),
               			logical_units= [
                        		types.LogicalUnit(
                                		id=lun.id,
                        		)
              			],
            		),
        	)
		
		# add disk template 
		new_disk = self.disk_service.add(disk)
		# assert real-size equals with size in excel
		assert (new_disk.lun_storage.logical_units[0].size == lun.size*1024*1024*1024),'size not match'
		logger.info('Success mapping lun {} with disk {}, bootable {}'.format(lun.id, new_disk.id, lun.bootable))
		return new_disk
		
	except Exception as e:
		raise Exception(e)	


    # return cluster id based on host name
    def get_id_cluster_host (self, _host):
	host = self.hosts_service.list(search='name={}'.format(_host))
	return host[0].cluster.id if host else 'Not-found-host' 

    # tranform vms data excel into vms instance <class VM>
    def vms_data (self,data):
	try :
		vms = []
		for index,row in data.iterrows():
        		vm = {}
        		vm['luns'] = []
        		pre_vm = next((i for i in vms if i.id == row['id']),None)
        		if pre_vm is not None:
                		pre_vm.luns.append(LUN(row['lun_id'],row['bootable'],row['lun_name'],row['size']))
                		continue

        		vm['luns'].append(LUN(row['lun_id'],row['bootable'],row['lun_name'],row['size']))
			vm['ip'] = nics(row['ip'], row['subnet'], row['gateway'])
        		vm['id'] = row['id']
        		vm['name'] = row['name']
        		vm['ram'] = row['ram']
        		vm['vcpu'] = row['vcpu']
        		vm['cluster'] = self.get_id_cluster_host(row['host']) 
        		vm['vlan'] = row['vlan']
			vm['host'] = row['host']
        		vms.append(VM(vm))
		return vms 
	except Exception as e:
		print(e)
	

    def user_script (self, data,  mac, ip , mask , gateway):
	return  self.data.format(mac,ip,mask,gateway,'{print $2}','{a%?}')


    def create_vm_template(self,vm,logger):
	
	try:

		# hosts specified
    		placement_policy = types.VmPlacementPolicy(
                	hosts =[
                        	types.Host(name=vm.host)
               		]
        	)
		# cpu number 
        	cpu = types.CpuTopology( cores=vm.vcpu )	
		# template 	
		template =  types.Vm(
        			name=vm.name,
                        	memory=vm.ram*1024*1024,   #MB
                        	cpu=types.Cpu(topology=cpu),
                        	cluster=types.Cluster(
                       			id=vm.cluster,
                        	),
                        	template=types.Template(
                        		name='Blank',
                        	),
                        	placement_policy = placement_policy
       		)

		logger.info('Successfully created vm template')
		logger.info('Instance properties: name:{}, host:{}, cluster:{}, vcpu:{}, ram:{}'.format(vm.name, vm.host, vm.cluster, vm.vcpu, vm.ram))
		return template
	except Exception as e:
		logger.error('Can not add vm template')
                logger.error(e)
		return { "name": vm.name,"status":'fail,template'}
		
 

    def create_vm_nic (self,vlan,logger):
	try:
		network = next(( i for i in self.networks_service.list() if i.vlan is not None and i.vlan.id == vlan ),None)
		if network is None: raise Exception('Can not find network with vlan{}'.format(vlan))
		profile = next((i for i in self.profiles_service.list() if i.name == network.name),None)
		if profile is None: raise Exception('Can not find profiles name {}'.format(network.name))
	
		# create nic template
		return types.Nic(
               			name ='nic',
                        	interface=types.NicInterface.VIRTIO,
                        	vnic_profile=types.VnicProfile(id=profile.id)
        	)
	except Exception as e:
		raise Exception(e)


    # luns = [ i for i in disks if i.storage_type == types.DiskStorageType.LUN  and i.lun_storage.logical_units[0].id == '3600507680c8002d9480000000000082f' ]/
    # luu y: all luns thuoc host cua vm
    def create_and_attach_vm_lun (self, luns , host , logger):
	# create disks attaching to vm
	res = []
	try:
		res = []
		for lun in luns:
			check = [ i for i in self.disk_service.list() if i.storage_type == types.DiskStorageType.LUN  and i.lun_storage.logical_units[0].id == lun.id ]
			if check:
				_bootable = (lun.bootable == 1)
				logger.info('Found existing disk {} with lun id {}'.format(check[0].id,lun.id))
				disk =  types.DiskAttachment(
                                                	disk= types.Disk(
                                                        	id = check[0].id,
                                                	),
                                                	interface=types.DiskInterface.VIRTIO,
                                                	active = True,
                                                	bootable = _bootable,
                               	)
				res.append(disk)
			else:
				logger.info('No disk has created with lun id {} yet, so is creating...'.format(lun.id))
				vm_disk  = self.create_disk(lun,host,logger)
				if vm_disk is not None:
					_bootable = (lun.bootable == 1)
					disk =	types.DiskAttachment(
                                				disk= types.Disk(
                                        				id = vm_disk.id,
                                				),
                                				interface=types.DiskInterface.VIRTIO,
                                				active = True,
                                				bootable = _bootable,
                        			)
					res.append(disk)	
	except Exception as e:
		logger.error('Can not attached disk with lun_id {} to vm'.format(lun.id))
		logger.error(e)
	finally:
		return res

    def create_vm (self, vm):
	message = 'success'	
	#search vm name 
	vmx = self.vms_service.list(search='name={}'.format(vm.name))	
	
        logger = logging.getLogger(vm.name)
        filename = os.getcwd() + '/vms/{}'.format(vm.name)
        handler = logging.FileHandler(filename)
	handler.setFormatter(formatter)
        logger.addHandler(handler)
	logger.info('--------------------------------------------------------')
	
	if not vmx :
		logger.info('Create vm')
			
	#1 CREATE VM 

		logger.info('# CREATE VM TEMPLATE PHASE')
                vm_template = self.create_vm_template(vm,logger)
                # create vm template
		_vm = self.vms_service.add(vm_template)
		# vm service
		vm_service = self.vms_service.vm_service(_vm.id)
		
	#2 ADD VM NIC 			
		logger.info('# CREAT VM NIC PHASE')
		# vm nic service
		nics_service = vm_service.nics_service()
		try:
			nic = self.create_vm_nic(vm.vlan, logger)	
			nic_vm = nics_service.add(nic)
			logger.info('Successfully created vm nic at vlan {} with mac {}'.format(vm.vlan,nic_vm.mac.address))
		except Exception as e:
			logger.error('Failed create nic for vm')
			logger.error(e)
			message = message +  ',fail_create_nic'

	#3 CREATE & ATTACH DISK
		logger.info('# CREATE & ATTACH DISK PHASE')	
		# disk attachments service
		disk_attachments_service = vm_service.disk_attachments_service()
		# get luns attachments
		luns = self.create_and_attach_vm_lun(vm.luns, vm.host, logger)
		
		# check if any lun failed
		if len(luns) != len(vm.luns):
			message = message + ',fail_create_disk'	

		# attach luns
		for lun in luns:
			try:
				disk_attachment = disk_attachments_service.add(lun)
				vm_disk_service = self.disk_service.disk_service(disk_attachment.id)
                        	logger.info('Successfully attach disk {} to {}'.format(disk_attachment.id,vm.name))
                         	#print(vm_disk_service.get().status) #since rhvm does not manage lun so volume status is None 
					
			except Exception as e:
				logger.debug('Fail at disk attachment')	
				logger.error(e)
				message = message + 'disk_attachment_fail'


	#4 START VM	
		logger.info('Vm created with status {}'.format(vm_service.get().status))
		try:
			logger.info('Trying to start vm...')
			#vm_service.start()	
		except Exception as e: 
			logger.debug('Vm can not boot')
			logger.error(e)
			message = message + ',vm_boot_error'
		finally:
			return {'name':vm.name,'status':message}
		#scontent = self.data.format(mac,ip,mask,gateway,'{print $2}','{a%?}')
		#self.start_vm(vm_service, True,scontent)
	else:
		message = 'fail,vm_existed'
		logger.debug('Vm existed')
		return {'name':vm.name,'status':message}
	
