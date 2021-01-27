from modules.vm import *
import ovirtsdk4.types as types
import time
class Utils:
    def __init__ (self, conn):
        self.conn = conn.connection()
        self.instance_types_service = self.conn.system_service().instance_types_service()
        self.disk_service = self.conn.system_service().disks_service()
        self.vms_service = self.conn.system_service().vms_service()
        self.clusters_service = self.conn.system_service().clusters_service()
	self.profiles_service = self.conn.system_service().vnic_profiles_service()
	
    def list_network (self, _cluster):
	cluster = self.clusters_service.list(search='name={}'.format(_cluster))[0]
	cluster_service = self.clusters_service.cluster_service(cluster.id)
	networks_service = cluster_service.networks_service()
	networks = networks_service.list()
	for network in networks:
		print(network.name)

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
	    
	vm_service = self.vms_service.vm_service(_vm.id)


	# add nic in "ovirtmgmt" management network
	_network = 'ovirtmgmt'
	nics_service = vm_service.nics_service()
        profile_id = None

        for profile in self.profiles_service.list():
                if profile.name == _network:
                        profile_id = profile.id
                        break
        for ip in vm.ips:
		nics_service.add(
			types.Nic(
				name=ip.nic,
				interface=types.NicInterface.VIRTIO,
				vnic_profile=types.VnicProfile(id=profile_id)
			),
		)
	
	#
	#  ADD DISK 
	#
	for lun in vm.luns:
		print(lun.id)
		print(lun.bootable) 
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
			time.sleep(5)
			disk = _disk_service.get()
			print(disk.status)
			break
	#
	# Cloud-init
	#	
	_netmask = '255.255.0.0'
	_gateway = '10.1.0.1'
	
	for _ip in vm.ips:
		vm_service.start(
			use_cloud_init=True,
			vm = types.Vm(
				initialization=types.Initialization(
					nic_configurations=[
						types.NicConfiguration(
							name= _ip.nic,
							on_boot=True,
							boot_protocol=types.BootProtocol.STATIC,
							ip= types.Ip(
								version=types.IpVersion.V4,
								address = _ip.ip,
								netmask = _netmask,
								gateway = _gateway
							)
						)
					],
					dns_servers = '8.8.8.8',
					dns_search ='example.com',
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

